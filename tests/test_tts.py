import asyncio
import io
import threading
import wave

import pytest
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import async_read_event, async_write_event
from wyoming.info import Attribution, Describe, Info, TtsProgram, TtsVoice
from wyoming.tts import Synthesize

from app.services.tts import TTSError, TTSVoiceNotFound, WyomingTTSService

ATTR = Attribution(name="test", url="")
VOICES = [
    ("pl_PL-gosia-x_low", ["pl_PL"]),
    ("pl_PL-gosia-medium", ["pl_PL"]),
    ("en_US-lessac-medium", ["en"]),
]


class FakeWyomingServer:
    """Minimal Wyoming TTS server running in a background thread."""

    def __init__(self, rate=24000):
        self.rate = rate
        self.requests = []
        self.loop = asyncio.new_event_loop()
        started = threading.Event()

        def run():
            asyncio.set_event_loop(self.loop)
            self.server = self.loop.run_until_complete(asyncio.start_server(self._handle, "127.0.0.1", 0))
            self.port = self.server.sockets[0].getsockname()[1]
            started.set()
            self.loop.run_forever()

        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()
        started.wait(5)

    async def _handle(self, reader, writer):
        event = await async_read_event(reader)
        if Describe.is_type(event.type):
            info = Info(
                tts=[
                    TtsProgram(
                        name="fake",
                        attribution=ATTR,
                        installed=True,
                        description="",
                        version="1",
                        voices=[
                            TtsVoice(
                                name=n,
                                attribution=ATTR,
                                installed=True,
                                description="",
                                version=None,
                                languages=langs,
                            )
                            for n, langs in VOICES
                        ],
                    )
                ]
            )
            await async_write_event(info.event(), writer)
        elif Synthesize.is_type(event.type):
            synth = Synthesize.from_event(event)
            self.requests.append(synth)
            await async_write_event(AudioStart(rate=self.rate, width=2, channels=1).event(), writer)
            for _ in range(3):
                await async_write_event(
                    AudioChunk(rate=self.rate, width=2, channels=1, audio=b"\x01\x00" * 100).event(), writer
                )
            await async_write_event(AudioStop().event(), writer)
        writer.close()

    def close(self):
        self.loop.call_soon_threadsafe(self.server.close)
        self.loop.call_soon_threadsafe(self.loop.stop)


@pytest.fixture
def server():
    srv = FakeWyomingServer()
    WyomingTTSService._voices_cache.clear()
    yield srv
    srv.close()


def test_languages_discovered(server):
    tts = WyomingTTSService("127.0.0.1", server.port)
    assert tts.get_languages() == ["en", "pl"]


def test_prefers_medium_quality_voice(server):
    tts = WyomingTTSService("127.0.0.1", server.port)
    assert tts.find_voice("pl").name == "pl_PL-gosia-medium"


def test_voice_override(server, monkeypatch):
    monkeypatch.setenv("WYOMING_TTS_VOICES", "pl=pl_PL-gosia-x_low")
    tts = WyomingTTSService("127.0.0.1", server.port)
    assert tts.find_voice("pl").name == "pl_PL-gosia-x_low"


def test_unknown_language(server):
    tts = WyomingTTSService("127.0.0.1", server.port)
    with pytest.raises(TTSVoiceNotFound):
        tts.find_voice("de")


def test_synthesize_uses_server_audio_format(server):
    tts = WyomingTTSService("127.0.0.1", server.port)
    wav_bytes = tts.synthesize("Cześć", "pl")
    with wave.open(io.BytesIO(wav_bytes)) as wav:
        assert wav.getframerate() == 24000
        assert wav.getsampwidth() == 2
        assert wav.getnframes() == 300
    assert server.requests[-1].voice.name == "pl_PL-gosia-medium"


def test_connection_error_raises_tts_error():
    WyomingTTSService._voices_cache.clear()
    tts = WyomingTTSService("127.0.0.1", 1)
    with pytest.raises(TTSError):
        tts.get_languages()


def test_api_tts_endpoint(server, monkeypatch):
    from app import create_app

    monkeypatch.setenv("WYOMING_TTS_HOST", "127.0.0.1")
    monkeypatch.setenv("WYOMING_TTS_PORT", str(server.port))
    client = create_app().test_client()

    assert client.get("/api/tts/languages").get_json()["languages"] == ["en", "pl"]

    response = client.post("/api/tts", json={"text": "Cześć", "language": "pl"})
    assert response.status_code == 200
    assert response.mimetype == "audio/wav"

    assert client.post("/api/tts", json={"text": "Hallo", "language": "de"}).status_code == 404
