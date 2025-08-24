"""
Simple Wyoming TTS service compatible with wyoming 1.5.4
"""
import asyncio
import io
import struct
from wyoming.client import AsyncTcpClient
from wyoming.tts import Synthesize, SynthesizeVoice
from wyoming.audio import AudioChunk


class SimpleWyomingTTSService:
    def __init__(self, host=None, port=None):
        import os
        self.host = host or os.getenv("WYOMING_PIPER_HOST")
        self.port = port or int(os.getenv("WYOMING_PIPER_PORT", "10200"))
        
        if not self.host:
            raise ValueError("WYOMING_PIPER_HOST environment variable is required")
    
    def synthesize(self, text, voice):
        """Simple synthesis compatible with wyoming 1.5.4"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_chunks = loop.run_until_complete(self._synthesize_async(text, voice))
            return self._create_wav_from_chunks(audio_chunks)
        finally:
            loop.close()
    
    async def _synthesize_async(self, text, voice):
        """Simple async synthesis for wyoming 1.5.4"""
        audio_chunks = []
        
        try:
            client = AsyncTcpClient(self.host, self.port)
            await asyncio.wait_for(client.connect(), timeout=5.0)
            
            # Send synthesis request
            synthesize_request = Synthesize(
                text=text,
                voice=SynthesizeVoice(name=voice)
            )
            
            await client.write_event(synthesize_request.event())
            
            # Collect audio chunks
            while True:
                event = await client.read_event()
                
                if event is None:
                    break
                    
                if AudioChunk.is_type(event.type):
                    chunk = AudioChunk.from_event(event)
                    audio_chunks.append(chunk.audio)
                elif event.type == "tts-done":
                    break
            
            await client.disconnect()
            
        except Exception as e:
            print(f"DEBUG: Wyoming synthesis error: {e}")
            raise
            
        return audio_chunks
    
    def _create_wav_from_chunks(self, audio_chunks):
        """Create WAV file from audio chunks"""
        if not audio_chunks:
            raise ValueError("No audio chunks received")
        
        # Combine all chunks
        combined_audio = b''.join(audio_chunks)
        
        # WAV header parameters
        sample_rate = 22050
        bits_per_sample = 16
        channels = 1
        
        # Create WAV file
        wav_buffer = io.BytesIO()
        
        # WAV header
        wav_buffer.write(b'RIFF')
        wav_buffer.write(struct.pack('<I', len(combined_audio) + 36))
        wav_buffer.write(b'WAVE')
        wav_buffer.write(b'fmt ')
        wav_buffer.write(struct.pack('<I', 16))  # PCM format size
        wav_buffer.write(struct.pack('<H', 1))   # PCM format
        wav_buffer.write(struct.pack('<H', channels))
        wav_buffer.write(struct.pack('<I', sample_rate))
        wav_buffer.write(struct.pack('<I', sample_rate * channels * bits_per_sample // 8))
        wav_buffer.write(struct.pack('<H', channels * bits_per_sample // 8))
        wav_buffer.write(struct.pack('<H', bits_per_sample))
        wav_buffer.write(b'data')
        wav_buffer.write(struct.pack('<I', len(combined_audio)))
        wav_buffer.write(combined_audio)
        
        return wav_buffer.getvalue()