import socket
import json

def simple_wyoming_test():
    """Simple test to see exactly what Wyoming sends"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(20)
        sock.connect(("10.0.20.134", 10200))
        
        # Send request
        request = {"type": "synthesize", "data": {"text": "Test", "voice": "pl_PL-darkman-medium"}}
        sock.send((json.dumps(request) + "\n").encode())
        
        # Read everything and save to file
        all_data = bytearray()
        while True:
            try:
                chunk = sock.recv(1024)
                if not chunk:
                    break
                all_data.extend(chunk)
            except socket.timeout:
                break
        
        sock.close()
        
        print(f"Received {len(all_data)} bytes total")
        
        # Save raw data
        with open('/tmp/wyoming_raw_response.bin', 'wb') as f:
            f.write(all_data)
            
        # Try to extract just the audio part
        # Wyoming typically sends: JSON headers + raw WAV data
        # Look for WAV header (starts with "RIFF")
        wav_start = all_data.find(b'RIFF')
        if wav_start != -1:
            wav_data = all_data[wav_start:]
            print(f"Found WAV data at position {wav_start}, size: {len(wav_data)} bytes")
            
            with open('/tmp/wyoming_extracted.wav', 'wb') as f:
                f.write(wav_data)
                
            return wav_data
        else:
            print("No WAV header found")
            # Maybe it's raw PCM data after JSON
            # Look for the end of JSON messages
            lines = all_data.split(b'\n')
            audio_started = False
            audio_data = bytearray()
            
            for line in lines:
                if line.startswith(b'{"type": "audio-start"'):
                    audio_started = True
                    continue
                elif line.startswith(b'{"type": "audio-stop"'):
                    break
                elif audio_started and not line.startswith(b'{"'):
                    audio_data.extend(line)
            
            if audio_data:
                print(f"Extracted {len(audio_data)} bytes of raw audio")
                with open('/tmp/wyoming_raw_pcm.bin', 'wb') as f:
                    f.write(audio_data)
                return audio_data
                
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    result = simple_wyoming_test()
    if result:
        print(f"Success: extracted {len(result)} bytes")
    else:
        print("Failed to extract audio")