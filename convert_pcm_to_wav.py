#!/usr/bin/env python3

import struct
import io

def pcm_to_wav(pcm_data, sample_rate=22050, bits_per_sample=16, channels=1):
    """Convert raw PCM data to WAV format"""
    
    # Calculate parameters
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    
    # Create WAV file
    wav_data = io.BytesIO()
    
    # RIFF header
    wav_data.write(b'RIFF')
    wav_data.write(struct.pack('<I', 36 + len(pcm_data)))  # File size
    wav_data.write(b'WAVE')
    
    # fmt chunk
    wav_data.write(b'fmt ')
    wav_data.write(struct.pack('<I', 16))  # Subchunk1 size
    wav_data.write(struct.pack('<H', 1))   # Audio format (PCM)
    wav_data.write(struct.pack('<H', channels))   # Num channels
    wav_data.write(struct.pack('<I', sample_rate))  # Sample rate
    wav_data.write(struct.pack('<I', byte_rate))  # Byte rate
    wav_data.write(struct.pack('<H', block_align))   # Block align
    wav_data.write(struct.pack('<H', bits_per_sample))  # Bits per sample
    
    # data chunk
    wav_data.write(b'data')
    wav_data.write(struct.pack('<I', len(pcm_data)))  # Data size
    wav_data.write(pcm_data)  # Raw audio data
    
    return wav_data.getvalue()

# Convert reference PCM to WAV
if __name__ == "__main__":
    # Read raw PCM data
    with open('/tmp/wyoming_raw_pcm.bin', 'rb') as f:
        pcm_data = f.read()
    
    print(f"Converting {len(pcm_data)} bytes of PCM data to WAV")
    
    # Convert to WAV
    wav_data = pcm_to_wav(pcm_data)
    
    # Save WAV file
    with open('/tmp/reference_converted.wav', 'wb') as f:
        f.write(wav_data)
    
    print(f"Saved WAV file with {len(wav_data)} bytes")
    
    # Also try different sample rates in case Wyoming uses different one
    for rate in [16000, 22050, 44100]:
        wav_data_alt = pcm_to_wav(pcm_data, sample_rate=rate)
        with open(f'/tmp/reference_{rate}hz.wav', 'wb') as f:
            f.write(wav_data_alt)
        print(f"Also saved version for {rate}Hz")