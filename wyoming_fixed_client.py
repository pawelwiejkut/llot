import socket
import json
import struct

def synthesize_with_wyoming(text, voice="pl_PL-darkman-medium", host="10.0.20.134", port=10200):
    """
    Communicate with Wyoming Piper TTS server using proper protocol
    """
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
        print(f"Sending: {request_line.strip()}")
        sock.send(request_line.encode('utf-8'))
        
        # Read response
        audio_data = bytearray()
        buffer = bytearray()
        in_audio_stream = False
        
        while True:
            # Read data from socket
            data = sock.recv(4096)
            if not data:
                break
                
            buffer.extend(data)
            
            # Process complete lines
            while b'\n' in buffer:
                line_end = buffer.find(b'\n')
                line = buffer[:line_end]
                buffer = buffer[line_end + 1:]
                
                if not line:
                    continue
                
                try:
                    # Try to decode as JSON message
                    line_str = line.decode('utf-8')
                    if line_str.startswith('{'):
                        msg = json.loads(line_str)
                        print(f"Received message: {msg.get('type', 'unknown')}")
                        
                        if msg.get("type") == "audio-start":
                            in_audio_stream = True
                            print("Audio stream started")
                            
                        elif msg.get("type") == "audio-chunk":
                            # Audio chunk message - next line should contain metadata
                            # Then comes the actual audio data
                            continue
                            
                        elif msg.get("type") == "audio-stop":
                            print("Audio stream stopped")
                            break
                            
                    else:
                        # Not JSON - this might be audio metadata or data
                        if in_audio_stream:
                            try:
                                # Try to parse as audio metadata
                                metadata = json.loads(line_str)
                                print(f"Audio metadata: {metadata}")
                            except:
                                # This is raw audio data
                                audio_data.extend(line)
                                
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # This is binary audio data
                    if in_audio_stream:
                        audio_data.extend(line)
            
            # If we have leftover buffer and we're in audio stream, it's probably audio data
            if in_audio_stream and buffer and not buffer.startswith(b'{'):
                audio_data.extend(buffer)
                buffer = bytearray()
        
        sock.close()
        
        print(f"Total audio data collected: {len(audio_data)} bytes")
        return bytes(audio_data) if audio_data else None
        
    except Exception as e:
        print(f"Wyoming TTS error: {e}")
        return None

# Test the client
if __name__ == "__main__":
    print("Testing Wyoming TTS client...")
    audio = synthesize_with_wyoming("Test polskiego głosu", "pl_PL-darkman-medium")
    
    if audio and len(audio) > 100:  # Should be more than just headers
        with open('/tmp/wyoming_real.wav', 'wb') as f:
            f.write(audio)
        print(f"Audio saved to /tmp/wyoming_real.wav ({len(audio)} bytes)")
        
        # Check if it's a valid audio file
        import subprocess
        try:
            result = subprocess.run(['file', '/tmp/wyoming_real.wav'], capture_output=True, text=True)
            print(f"File type: {result.stdout.strip()}")
        except:
            pass
    else:
        print("No audio data received or data too small")