"""
Wyoming TTS client.

Works with any Wyoming-protocol TTS server (wyoming-piper, wyoming_openai, ...).
Available voices are discovered from the server via `describe`, so no voice
names are hard-coded here.
"""

import asyncio
import io
import logging
import os
import threading
import time
import wave
from dataclasses import dataclass

from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.client import AsyncTcpClient
from wyoming.error import Error
from wyoming.info import Describe, Info
from wyoming.tts import Synthesize, SynthesizeVoice

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT = 5.0
# wyoming-piper downloads a voice on first use, so the first event can take a while
EVENT_TIMEOUT = 90.0
VOICES_TTL = 300.0
MAX_TEXT_LENGTH = 5000


class TTSError(Exception):
    """Raised when speech synthesis fails."""


class TTSVoiceNotFound(TTSError):
    """Raised when the server has no voice for the requested language."""


@dataclass
class Voice:
    name: str
    languages: list[str]


def get_tts_address():
    """Return (host, port) of the configured Wyoming TTS server, or (None, None)."""
    host = os.getenv("WYOMING_TTS_HOST") or os.getenv("WYOMING_PIPER_HOST")
    port = os.getenv("WYOMING_TTS_PORT") or os.getenv("WYOMING_PIPER_PORT") or "10200"
    if not host:
        return None, None
    return host, int(port)


# Piper-style quality suffixes; lower rank is preferred
_QUALITY_RANK = {"medium": 0, "high": 1, "low": 2, "x_low": 3}


def _voice_overrides() -> dict[str, str]:
    """Parse WYOMING_TTS_VOICES, e.g. 'pl=pl_PL-gosia-medium,en=en_US-lessac-medium'."""
    overrides = {}
    for item in os.getenv("WYOMING_TTS_VOICES", "").split(","):
        lang, sep, voice = item.partition("=")
        if sep and lang.strip() and voice.strip():
            overrides[_lang_base(lang.strip())] = voice.strip()
    return overrides


def _quality_rank(voice_name: str) -> int:
    return _QUALITY_RANK.get(voice_name.rsplit("-", 1)[-1], 1)


def _lang_base(code: str) -> str:
    """'pl_PL' / 'pl-PL' / 'PL' -> 'pl'."""
    return code.replace("-", "_").split("_")[0].lower()


class WyomingTTSService:
    """Synthesize speech through a Wyoming TTS server."""

    _voices_cache: dict[tuple, tuple] = {}
    _cache_lock = threading.Lock()

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    # ---------------------------------------------------------------- voices
    def get_voices(self) -> list[Voice]:
        """Return installed voices, cached for VOICES_TTL seconds."""
        key = (self.host, self.port)
        with self._cache_lock:
            cached = self._voices_cache.get(key)
            if cached and time.monotonic() - cached[0] < VOICES_TTL:
                return cached[1]

        voices = self._run(self._describe())
        with self._cache_lock:
            self._voices_cache[key] = (time.monotonic(), voices)
        return voices

    def get_languages(self) -> list[str]:
        """Return base language codes that have at least one voice."""
        return sorted({_lang_base(lang) for v in self.get_voices() for lang in v.languages})

    def find_voice(self, language: str) -> Voice:
        """Pick a voice for the given language code (e.g. 'pl')."""
        wanted = _lang_base(language)
        voices = self.get_voices()

        override = _voice_overrides().get(wanted)
        if override:
            for voice in voices:
                if voice.name == override:
                    return voice
            logger.warning(f"Configured TTS voice '{override}' not offered by server")

        candidates = [v for v in voices if any(_lang_base(lang) == wanted for lang in v.languages)]
        if not candidates:
            raise TTSVoiceNotFound(f"No TTS voice available for language '{language}'")
        return min(candidates, key=lambda v: _quality_rank(v.name))

    async def _describe(self) -> list[Voice]:
        client = await self._connect()
        try:
            await client.write_event(Describe().event())
            while True:
                event = await asyncio.wait_for(client.read_event(), timeout=EVENT_TIMEOUT)
                if event is None:
                    raise TTSError("TTS server closed connection during describe")
                if Info.is_type(event.type):
                    info = Info.from_event(event)
                    return [
                        Voice(name=v.name, languages=list(v.languages or []))
                        for program in info.tts
                        if program.installed
                        for v in program.voices
                        if v.installed
                    ]
        finally:
            await client.disconnect()

    # ------------------------------------------------------------- synthesis
    def synthesize(self, text: str, language: str) -> bytes:
        """Synthesize text and return a complete WAV file."""
        if len(text) > MAX_TEXT_LENGTH:
            raise TTSError(f"Text too long for TTS (max {MAX_TEXT_LENGTH} characters)")
        voice = self.find_voice(language)
        return self._run(self._synthesize(text, voice.name))

    @staticmethod
    def _run(coro):
        try:
            return asyncio.run(coro)
        except TimeoutError as e:
            raise TTSError("TTS server timed out") from e
        except (OSError, ConnectionError) as e:
            raise TTSError(f"TTS connection error: {e}") from e

    async def _synthesize(self, text: str, voice: str) -> bytes:
        audio = bytearray()
        fmt = None

        client = await self._connect()
        try:
            await client.write_event(Synthesize(text=text, voice=SynthesizeVoice(name=voice)).event())
            while True:
                event = await asyncio.wait_for(client.read_event(), timeout=EVENT_TIMEOUT)
                if event is None:
                    break
                if AudioStart.is_type(event.type):
                    start = AudioStart.from_event(event)
                    fmt = (start.rate, start.width, start.channels)
                elif AudioChunk.is_type(event.type):
                    chunk = AudioChunk.from_event(event)
                    fmt = fmt or (chunk.rate, chunk.width, chunk.channels)
                    audio.extend(chunk.audio)
                elif AudioStop.is_type(event.type):
                    break
                elif Error.is_type(event.type):
                    raise TTSError(f"TTS server error: {Error.from_event(event).text}")
        finally:
            await client.disconnect()

        if not audio or fmt is None:
            raise TTSError("TTS server returned no audio")
        return _to_wav(bytes(audio), *fmt)

    async def _connect(self) -> AsyncTcpClient:
        client = AsyncTcpClient(self.host, self.port)
        try:
            await asyncio.wait_for(client.connect(), timeout=CONNECT_TIMEOUT)
        except (TimeoutError, OSError) as e:
            raise TTSError(f"Cannot connect to TTS server {self.host}:{self.port}: {e}") from e
        return client


def _to_wav(pcm: bytes, rate: int, width: int, channels: int) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(width)
        wav.setframerate(rate)
        wav.writeframes(pcm)
    return buf.getvalue()


def get_tts_service() -> WyomingTTSService | None:
    """Return a TTS service for the configured server, or None if TTS is disabled."""
    host, port = get_tts_address()
    if not host:
        return None
    return WyomingTTSService(host, port)
