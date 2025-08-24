import socket
import json
import io

def create_wyoming_tts_client():
    """Create a simple Wyoming TTS client that properly parses the protocol"""
    
    def synthesize_text(text, voice="pl_PL-darkman-medium", host="10.0.20.134", port=10200):
        try:
            # Connect to Wyoming server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)
            sock.connect((host, port))
            
            # Send synthesize request
            request = {
                "type": "synthesize",
                "data": {
                    "text": text,
                    "voice": voice
                }
            }
            
            request_line = json.dumps(request) + "\n"
            sock.send(request_line.encode('utf-8'))
            
            # Read response - collect all binary audio data
            audio_buffer = io.BytesIO()
            in_audio = False
            buffer = b""
            
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                
                buffer += chunk
                
                # Process line by line
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    
                    try:
                        # Try to decode as JSON
                        line_str = line.decode('utf-8', errors='ignore')
                        if line_str.startswith('{"'):
                            msg = json.loads(line_str)
                            
                            if msg.get("type") == "audio-start":
                                in_audio = True
                                print("Audio stream started")
                                continue
                            elif msg.get("type") == "audio-stop":
                                print("Audio stream ended")
                                break
                            elif msg.get("type") == "audio-chunk":
                                # Skip this - actual audio data follows
                                continue
                        
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # This is binary audio data
                        if in_audio and line:
                            audio_buffer.write(line)
                            continue
                
                # Add any remaining buffer as audio if in audio mode
                if in_audio and buffer and not b'{"' in buffer:
                    audio_buffer.write(buffer)
                    buffer = b""
            
            sock.close()
            
            # Return the collected audio data
            audio_data = audio_buffer.getvalue()
            print(f"Collected {len(audio_data)} bytes of audio data")
            
            return audio_data if len(audio_data) > 0 else None
            
        except Exception as e:
            print(f"Wyoming TTS error: {e}")
            return None
    
    return synthesize_text

# Test the client
if __name__ == "__main__":
    tts_client = create_wyoming_tts_client()
    audio = tts_client("Test", "pl_PL-darkman-medium")
    
    if audio:
        with open('/tmp/wyoming_test.wav', 'wb') as f:
            f.write(audio)
        print(f"Audio saved to /tmp/wyoming_test.wav ({len(audio)} bytes)")
    else:
        print("No audio data received")