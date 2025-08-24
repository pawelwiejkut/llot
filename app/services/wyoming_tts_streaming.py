"""
Streaming Wyoming TTS service for real-time audio playback
"""
import asyncio
import io
import struct
from flask import Response
from wyoming.client import AsyncTcpClient
from wyoming.tts import Synthesize, SynthesizeVoice, SynthesizeStart, SynthesizeChunk, SynthesizeStop
from wyoming.audio import AudioChunk
import threading
import queue


class StreamingWyomingTTSService:
    def __init__(self, host=None, port=None):
        import os
        self.host = host or os.getenv("WYOMING_PIPER_HOST", "10.0.20.134")
        self.port = port or int(os.getenv("WYOMING_PIPER_PORT", "10200"))
    
    def synthesize_streaming(self, text, voice):
        """Stream TTS audio in real-time as chunks arrive"""
        # Use a queue to pass chunks from async to sync context
        chunk_queue = queue.Queue()
        
        def run_async_synthesis():
            """Run the async synthesis in a separate thread"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._synthesize_streaming_async(text, voice, chunk_queue))
            finally:
                loop.close()
                chunk_queue.put(None)  # Signal end of stream
        
        # Start synthesis in background thread
        synthesis_thread = threading.Thread(target=run_async_synthesis)
        synthesis_thread.start()
        
        # Generator function for Flask streaming response
        def generate_audio_stream():
            chunks_received = []
            total_audio_size = 0
            sample_rate = 22050  # Default
            bits_per_sample = 16
            channels = 1
            
            # Collect chunks as they arrive (streaming on Wyoming protocol level)
            while True:
                try:
                    chunk = chunk_queue.get(timeout=45)  # Increased timeout for longer texts
                    if chunk is None:  # End of stream
                        break
                        
                    chunks_received.append(chunk)
                    
                    # Get audio parameters from first chunk
                    if len(chunks_received) == 1:
                        sample_rate = chunk.rate
                        bits_per_sample = chunk.width * 8
                        channels = chunk.channels
                    
                    total_audio_size += len(chunk.audio)
                    
                except queue.Empty:
                    break
            
            # Wait for synthesis thread to complete
            synthesis_thread.join(timeout=5)
            
            print(f"DEBUG: Streamed {len(chunks_received)} chunks, {total_audio_size} bytes audio", flush=True)
            
            # Build complete WAV file with slower playback
            if chunks_received:
                combined_audio = b''.join(chunk.audio for chunk in chunks_received)
                
                slowed_audio = combined_audio
                
                header = io.BytesIO()
                # RIFF header
                header.write(b'RIFF')
                header.write(struct.pack('<I', 36 + len(slowed_audio)))
                header.write(b'WAVE')
                
                # fmt chunk
                byte_rate = sample_rate * channels * bits_per_sample // 8
                header.write(b'fmt ')
                header.write(struct.pack('<I', 16))
                header.write(struct.pack('<H', 1))  # PCM
                header.write(struct.pack('<H', channels))
                header.write(struct.pack('<I', sample_rate))
                header.write(struct.pack('<I', byte_rate))
                header.write(struct.pack('<H', channels * bits_per_sample // 8))
                header.write(struct.pack('<H', bits_per_sample))
                
                # data chunk
                header.write(b'data')
                header.write(struct.pack('<I', len(slowed_audio)))
                
                # Yield complete, valid WAV file with slowed audio
                yield header.getvalue() + slowed_audio
        
        return generate_audio_stream()
    
    def _create_fmt_chunk(self, sample_rate, bits_per_sample, channels):
        """Create WAV format chunk"""
        byte_rate = sample_rate * channels * bits_per_sample // 8
        block_align = channels * bits_per_sample // 8
        
        fmt_data = io.BytesIO()
        fmt_data.write(b'fmt ')
        fmt_data.write(struct.pack('<I', 16))  # fmt chunk size
        fmt_data.write(struct.pack('<H', 1))   # PCM format
        fmt_data.write(struct.pack('<H', channels))
        fmt_data.write(struct.pack('<I', sample_rate))
        fmt_data.write(struct.pack('<I', byte_rate))
        fmt_data.write(struct.pack('<H', block_align))
        fmt_data.write(struct.pack('<H', bits_per_sample))
        
        return fmt_data.getvalue()
    
    async def _synthesize_streaming_async(self, text, voice, chunk_queue):
        """Official Wyoming streaming synthesis using SynthesizeStart/Chunk/Stop protocol"""
        client = AsyncTcpClient(self.host, self.port)
        
        try:
            await asyncio.wait_for(client.connect(), timeout=5.0)
            print(f"DEBUG: Connected to Wyoming for official streaming synthesis", flush=True)
            
            # Official Wyoming streaming protocol:
            # 1. Send synthesize-start (speaking_rate not supported by this Wyoming version)
            voice_obj = SynthesizeVoice(name=voice)
            start_event = SynthesizeStart(voice=voice_obj).event()
            await client.write_event(start_event)
            print(f"DEBUG: Sent synthesize-start with voice: {voice}", flush=True)
            
            # 2. Send text as sentence chunks for natural streaming with slower speech
            import re
            
            # Use original text without comma modifications for cleaner speech
            slower_text = text
            print(f"DEBUG: Using original text for cleaner speech: '{slower_text}'", flush=True)
            
            # Split by sentence endings but keep them with their sentences
            sentences = re.split(r'([.!?]+)', slower_text)
            sentence_chunks = []
            current_sentence = ""
            
            for part in sentences:
                if re.match(r'[.!?]+', part):
                    # This is punctuation, add to current sentence and complete it
                    current_sentence += part
                    if current_sentence.strip():
                        sentence_chunks.append(current_sentence.strip())
                    current_sentence = ""
                else:
                    # This is text, accumulate it
                    current_sentence += part
            
            # Add any remaining text as final chunk
            if current_sentence.strip():
                sentence_chunks.append(current_sentence.strip())
            
            # Send each sentence as a separate chunk (without pause markers that cause truncation)
            for i, sentence in enumerate(sentence_chunks):
                if sentence:
                    chunk_event = SynthesizeChunk(text=sentence).event()
                    await client.write_event(chunk_event)
                    print(f"DEBUG: Sent sentence chunk: '{sentence}'", flush=True)
                    await asyncio.sleep(0.3)  # Longer delay between sentences for clearer pacing
            
            # 3. Send synthesize-stop
            stop_event = SynthesizeStop().event()
            await client.write_event(stop_event)
            print(f"DEBUG: Sent synthesize-stop", flush=True)
            
            # 4. Read streaming audio response with sentence pause insertion
            chunk_count = 0
            audio_started = False
            sentence_chunks_sent = len(sentence_chunks)
            current_sentence_index = 0
            chunks_for_current_sentence = []
            
            # Calculate dynamic timeout based on text length (like Home Assistant does)
            # Assume ~150 words per minute average speech, add safety margin
            estimated_duration = len(text.split()) / 2.5  # words per second
            dynamic_timeout = max(30.0, estimated_duration + 10.0)  # minimum 30s, plus 10s buffer
            print(f"DEBUG: Using dynamic timeout: {dynamic_timeout:.1f}s for text length: {len(text)} chars", flush=True)
            
            while chunk_count < 500:  # Even higher limit for sentence-based chunks
                try:
                    event = await asyncio.wait_for(client.read_event(), timeout=dynamic_timeout)
                    if event is None:
                        print("DEBUG: No more events, breaking", flush=True)
                        break
                    
                    print(f"DEBUG: Received event: {event.type}", flush=True)
                        
                    if event.type == "audio-start":
                        audio_started = True
                        print("DEBUG: Audio stream started", flush=True)
                        
                    elif AudioChunk.is_type(event.type) and audio_started:
                        chunk = AudioChunk.from_event(event)
                        chunk_count += 1
                        print(f"DEBUG: Streaming audio chunk {chunk_count}: {len(chunk.audio)} bytes", flush=True)
                        
                        # Collect chunks for current sentence
                        chunks_for_current_sentence.append(chunk)
                        
                        # Put chunk in queue for immediate streaming
                        chunk_queue.put(chunk)
                        
                    elif event.type == "audio-stop":
                        print("DEBUG: Audio stream stopped", flush=True)
                        
                        # Add silence pause after sentence (except for last sentence)
                        if current_sentence_index < sentence_chunks_sent - 1 and chunks_for_current_sentence:
                            print(f"DEBUG: Adding 2 second silence pause after sentence {current_sentence_index + 1}", flush=True)
                            
                            # Get audio parameters from last chunk
                            last_chunk = chunks_for_current_sentence[-1] if chunks_for_current_sentence else None
                            if last_chunk:
                                # Generate 1 second of silence with same parameters
                                sample_rate = last_chunk.rate
                                channels = last_chunk.channels
                                width = last_chunk.width
                                
                                # Calculate silence duration (2 seconds for longer pauses)
                                silence_samples = sample_rate * channels * 2
                                silence_bytes = silence_samples * width
                                silence_audio = b'\x00' * silence_bytes
                                
                                # Create silence chunk
                                silence_chunk = AudioChunk(
                                    rate=sample_rate,
                                    width=width, 
                                    channels=channels,
                                    audio=silence_audio
                                )
                                
                                print(f"DEBUG: Generated silence chunk: {len(silence_audio)} bytes", flush=True)
                                chunk_queue.put(silence_chunk)
                        
                        # Move to next sentence
                        current_sentence_index += 1
                        chunks_for_current_sentence = []
                        
                        # If we've processed all sentences, we're done
                        if current_sentence_index >= sentence_chunks_sent:
                            break
                        
                    elif event.type == "synthesize-stopped":
                        print("DEBUG: Synthesis officially stopped", flush=True)
                        break
                        
                except asyncio.TimeoutError:
                    print("DEBUG: Streaming timeout", flush=True)
                    break
                    
        except Exception as e:
            print(f"DEBUG: Streaming synthesis error: {e}", flush=True)
        finally:
            await client.disconnect()


# Alternative non-streaming optimized version for comparison
class FastWyomingTTSService:
    def __init__(self, host=None, port=None):
        import os
        self.host = host or os.getenv("WYOMING_PIPER_HOST", "10.0.20.134")
        self.port = port or int(os.getenv("WYOMING_PIPER_PORT", "10200"))
    
    def synthesize_fast(self, text, voice):
        """Fast synthesis with connection pooling and optimizations"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_chunks = loop.run_until_complete(self._synthesize_fast_async(text, voice))
            return self._create_wav_from_chunks_fast(audio_chunks)
        finally:
            loop.close()
    
    async def _synthesize_fast_async(self, text, voice):
        """Optimized async synthesis with slower speech"""
        
        # Use original text for cleaner speech
        slower_text = text
        print(f"DEBUG: Fast TTS using original text: '{slower_text}'", flush=True)
        
        client = AsyncTcpClient(self.host, self.port)
        audio_chunks = []
        
        try:
            # Faster connection with shorter timeout
            await asyncio.wait_for(client.connect(), timeout=3.0)
            
            # Send request immediately with slower text (speaking_rate not supported by this Wyoming version)
            voice_obj = SynthesizeVoice(name=voice)
            synthesize_obj = Synthesize(text=slower_text, voice=voice_obj)  # Use processed slower text
            await client.write_event(synthesize_obj.event())
            
            # Collect chunks with shorter timeout for faster response
            while len(audio_chunks) < 100:  # Safety limit
                try:
                    event = await asyncio.wait_for(client.read_event(), timeout=8.0)
                    if event is None:
                        break
                        
                    if AudioChunk.is_type(event.type):
                        chunk = AudioChunk.from_event(event)
                        audio_chunks.append(chunk)
                    elif event.type == "synthesize-stop":
                        break
                        
                except asyncio.TimeoutError:
                    break
                    
        finally:
            await client.disconnect()
        
        return audio_chunks
    
    def _create_wav_from_chunks_fast(self, chunks):
        """Optimized WAV creation"""
        if not chunks:
            raise Exception("No audio chunks")
            
        # Get params from first chunk
        first = chunks[0]
        
        # Pre-allocate and combine audio data efficiently
        combined_audio = b''.join(chunk.audio for chunk in chunks)
        
        # Build WAV header efficiently
        header = io.BytesIO()
        
        # RIFF header
        header.write(b'RIFF')
        header.write(struct.pack('<I', 36 + len(combined_audio)))
        header.write(b'WAVE')
        
        # fmt chunk
        byte_rate = first.rate * first.channels * first.width
        header.write(b'fmt ')
        header.write(struct.pack('<I', 16))
        header.write(struct.pack('<H', 1))  # PCM
        header.write(struct.pack('<H', first.channels))
        header.write(struct.pack('<I', first.rate))
        header.write(struct.pack('<I', byte_rate))
        header.write(struct.pack('<H', first.channels * first.width))
        header.write(struct.pack('<H', first.width * 8))
        
        # data chunk
        header.write(b'data')
        header.write(struct.pack('<I', len(combined_audio)))
        
        return header.getvalue() + combined_audio