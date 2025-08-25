"""
Simple Wyoming TTS service compatible with wyoming 1.5.4
"""
import asyncio
import io
import struct
from wyoming.client import AsyncTcpClient
from wyoming.tts import Synthesize, SynthesizeVoice
from wyoming.audio import AudioChunk
from app.utils.debug import debug_print


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
        """Simple async synthesis for wyoming 1.5.4 with OS-specific fixes"""
        audio_chunks = []
        client = None
        
        try:
            debug_print(f"Connecting to Wyoming at {self.host}:{self.port}")
            client = AsyncTcpClient(self.host, self.port)
            
            # Longer timeout for Linux compatibility
            await asyncio.wait_for(client.connect(), timeout=10.0)
            debug_print("Connected successfully")
            
            # Send synthesis request
            synthesize_request = Synthesize(
                text=text,
                voice=SynthesizeVoice(name=voice)
            )
            
            debug_print("Sending synthesis request")
            await asyncio.wait_for(client.write_event(synthesize_request.event()), timeout=5.0)
            
            # Collect audio chunks with timeout
            chunk_count = 0
            max_wait_time = 30.0  # Max 30 seconds for entire synthesis
            start_time = asyncio.get_event_loop().time()
            
            debug_print("Waiting for audio chunks")
            while True:
                # Check for overall timeout
                if asyncio.get_event_loop().time() - start_time > max_wait_time:
                    debug_print(f"Overall timeout reached after {max_wait_time}s")
                    break
                
                try:
                    # Adaptive timeout - shorter for quick detection of end
                    timeout = 1.5 if chunk_count > 0 else 5.0
                    event = await asyncio.wait_for(client.read_event(), timeout=timeout)
                except asyncio.TimeoutError:
                    debug_print(f"Timeout ({timeout}s) waiting for next event, got {chunk_count} chunks so far")
                    if chunk_count > 0:  # We got some audio, probably done
                        break
                    else:  # No audio yet, might be starting - wait longer
                        continue
                
                if event is None:
                    debug_print("Received None event, ending")
                    break
                    
                if AudioChunk.is_type(event.type):
                    chunk = AudioChunk.from_event(event)
                    audio_chunks.append(chunk.audio)
                    chunk_count += 1
                    chunk_size = len(chunk.audio)
                    # Only log every 20th chunk or last chunk to reduce overhead
                    if chunk_count % 20 == 0 or chunk_size < 2048:
                        debug_print(f"Received audio chunk {chunk_count}, size: {chunk_size}")
                    
                    # If we get a partial chunk (< 2048), it's likely the last one
                    if chunk_size < 2048 and chunk_count > 5:
                        debug_print(f"Got partial chunk ({chunk_size} < 2048), probably last chunk")
                        # Wait a bit more for potential tts-done, but with short timeout
                        try:
                            final_event = await asyncio.wait_for(client.read_event(), timeout=0.5)
                            if final_event and final_event.type == "tts-done":
                                debug_print("Got tts-done after partial chunk")
                        except asyncio.TimeoutError:
                            debug_print("No tts-done after partial chunk, assuming complete")
                        break
                        
                elif event.type == "tts-done":
                    debug_print("TTS done event received")
                    break
            
            debug_print(f"Synthesis complete, got {len(audio_chunks)} chunks")
            
        except Exception as e:
            debug_print(f"Wyoming synthesis error: {e}")
            raise
        finally:
            if client:
                try:
                    await asyncio.wait_for(client.disconnect(), timeout=2.0)
                    debug_print("Disconnected from Wyoming")
                except Exception as e:
                    debug_print(f"Error disconnecting: {e}")
            
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