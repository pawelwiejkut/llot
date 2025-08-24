import socket
import json

def test_wyoming():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
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
        
        # Read all response
        all_data = b""
        while True:
            try:
                chunk = sock.recv(1024)
                if not chunk:
                    break
                all_data += chunk
                print(f"Received chunk: {len(chunk)} bytes")
                
                # Try to decode and see structure
                try:
                    readable = chunk.decode('utf-8', errors='ignore')
                    if '{"type":' in readable:
                        print(f"JSON part: {readable}")
                except:
                    pass
                    
            except socket.timeout:
                break
        
        print(f"\nTotal received: {len(all_data)} bytes")
        
        # Try to save as WAV file
        with open('/tmp/test_wyoming.wav', 'wb') as f:
            f.write(all_data)
        print("Saved as /tmp/test_wyoming.wav")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    test_wyoming()