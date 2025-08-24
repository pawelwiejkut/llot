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
        """Simple async synthesis for wyoming 1.5.4 with OS-specific fixes"""
        audio_chunks = []
        client = None
        
        try:
            print(f"DEBUG: Connecting to Wyoming at {self.host}:{self.port}", flush=True)
            client = AsyncTcpClient(self.host, self.port)
            
            # Longer timeout for Linux compatibility
            await asyncio.wait_for(client.connect(), timeout=10.0)
            print(f"DEBUG: Connected successfully", flush=True)
            
            # Send synthesis request
            synthesize_request = Synthesize(
                text=text,
                voice=SynthesizeVoice(name=voice)
            )
            
            print(f"DEBUG: Sending synthesis request", flush=True)
            await asyncio.wait_for(client.write_event(synthesize_request.event()), timeout=5.0)
            
            # Collect audio chunks with timeout
            chunk_count = 0
            max_wait_time = 30.0  # Max 30 seconds for entire synthesis
            start_time = asyncio.get_event_loop().time()
            
            print(f"DEBUG: Waiting for audio chunks", flush=True)
            while True:
                # Check for overall timeout
                if asyncio.get_event_loop().time() - start_time > max_wait_time:
                    print(f"DEBUG: Overall timeout reached after {max_wait_time}s", flush=True)
                    break
                
                try:
                    # Adaptive timeout - shorter for quick detection of end
                    timeout = 1.5 if chunk_count > 0 else 5.0
                    event = await asyncio.wait_for(client.read_event(), timeout=timeout)
                except asyncio.TimeoutError:
                    print(f"DEBUG: Timeout ({timeout}s) waiting for next event, got {chunk_count} chunks so far", flush=True)
                    if chunk_count > 0:  # We got some audio, probably done
                        break
                    else:  # No audio yet, might be starting - wait longer
                        continue
                
                if event is None:
                    print(f"DEBUG: Received None event, ending", flush=True)
                    break
                    
                if AudioChunk.is_type(event.type):
                    chunk = AudioChunk.from_event(event)
                    audio_chunks.append(chunk.audio)
                    chunk_count += 1
                    chunk_size = len(chunk.audio)
                    # Only log every 20th chunk or last chunk to reduce overhead
                    if chunk_count % 20 == 0 or chunk_size < 2048:
                        print(f"DEBUG: Received audio chunk {chunk_count}, size: {chunk_size}", flush=True)
                    
                    # If we get a partial chunk (< 2048), it's likely the last one
                    if chunk_size < 2048 and chunk_count > 5:
                        print(f"DEBUG: Got partial chunk ({chunk_size} < 2048), probably last chunk", flush=True)
                        # Wait a bit more for potential tts-done, but with short timeout
                        try:
                            final_event = await asyncio.wait_for(client.read_event(), timeout=0.5)
                            if final_event and final_event.type == "tts-done":
                                print(f"DEBUG: Got tts-done after partial chunk", flush=True)
                        except asyncio.TimeoutError:
                            print(f"DEBUG: No tts-done after partial chunk, assuming complete", flush=True)
                        break
                        
                elif event.type == "tts-done":
                    print(f"DEBUG: TTS done event received", flush=True)
                    break
            
            print(f"DEBUG: Synthesis complete, got {len(audio_chunks)} chunks", flush=True)
            
        except Exception as e:
            print(f"DEBUG: Wyoming synthesis error: {e}", flush=True)
            raise
        finally:
            if client:
                try:
                    await asyncio.wait_for(client.disconnect(), timeout=2.0)
                    print(f"DEBUG: Disconnected from Wyoming", flush=True)
                except Exception as e:
                    print(f"DEBUG: Error disconnecting: {e}", flush=True)
            
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