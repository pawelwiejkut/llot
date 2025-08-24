import socket
import json
import re

def test_wyoming_better():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    sock.settimeout(15)
    
    try:
        sock.connect(('10.0.20.134', 10200))
        print("Connected to Wyoming server")
        
        # Send synthesize request
        request_data = json.dumps({
            "type": "synthesize", 
            "data": {
                "text": "Test",
                "voice": "pl_PL-darkman-medium"
            }
        }) + "\n"
        
        print(f"Sending: {request_data.strip()}")
        sock.send(request_data.encode('utf-8'))
        
        # Read response in chunks
        audio_started = False
        audio_data = b""
        raw_data = b""
        
        while True:
            try:
                chunk = sock.recv(1024)
                if not chunk:
                    break
                raw_data += chunk
                
                # Look for audio-start marker
                if b'"type": "audio-start"' in chunk:
                    print("Found audio-start")
                    audio_started = True
                    
                # Look for audio-stop marker  
                if b'"type": "audio-stop"' in chunk:
                    print("Found audio-stop")
                    break
                    
                # After audio-start, look for non-JSON data
                if audio_started:
                    # Split by newlines and check each part
                    parts = chunk.split(b'\n')
                    for part in parts:
                        # Skip JSON lines
                        if part.startswith(b'{"') or not part.strip():
                            continue
                        # This should be audio data
                        audio_data += part
                        
            except socket.timeout:
                print("Timeout")
                break
        
        print(f"Total raw data: {len(raw_data)} bytes")
        print(f"Extracted audio data: {len(audio_data)} bytes")
        
        # Try different approach - extract everything after first audio chunk header
        lines = raw_data.split(b'\n')
        pure_audio = b""
        found_first_audio = False
        
        for line in lines:
            if b'"type": "audio-chunk"' in line:
                found_first_audio = True
                continue
            if b'"rate":' in line and found_first_audio:
                continue  # Skip audio metadata
            if found_first_audio and not line.startswith(b'{"'):
                pure_audio += line
                
        print(f"Pure audio approach: {len(pure_audio)} bytes")
        
        # Save different approaches
        with open('/tmp/test_raw.bin', 'wb') as f:
            f.write(raw_data)
            
        with open('/tmp/test_audio1.wav', 'wb') as f:
            f.write(audio_data)
            
        with open('/tmp/test_audio2.wav', 'wb') as f:
            f.write(pure_audio)
            
        print("Saved test files")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    test_wyoming_better()