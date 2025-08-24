from flask import request, jsonify, current_app, Response
from app.routes import api_bp
from app.services.translator import TranslationService
from app.models.history import history_manager
import logging
import socket
import io
import json

logger = logging.getLogger(__name__)
translation_service = TranslationService()


@api_bp.route("/translate", methods=["POST"])
def translate():
    """Main translation endpoint."""
    try:
        data = request.get_json(silent=True) or {}
        
        source_text = (data.get("source_text") or "").strip()
        if not source_text:
            return jsonify({"error": "EMPTY", "translated": ""})
        
        source_lang = (data.get("source_lang") or "auto").strip()
        target_lang = (data.get("target_lang") or "de").strip()
        tone = (data.get("tone") or "neutral").strip()
        
        # Perform translation
        translated, detected = translation_service.translate(
            source_text, source_lang, target_lang, tone
        )
        
        return jsonify({
            "translated": translated,
            "detected": detected
        })
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return jsonify({"error": f"Translation error: {str(e)}"})


@api_bp.route("/history/save", methods=["POST"])
def save_history():
    """Save translation to history."""
    try:
        data = request.get_json(silent=True) or {}
        
        source_text = (data.get("source_text") or "").strip()
        translated = (data.get("translated") or "").strip()
        target_lang = (data.get("target_lang") or "de").strip()
        
        if not source_text or not translated:
            return jsonify({"ok": False, "error": "EMPTY"})
        
        success = history_manager.add_item(source_text, translated, target_lang)
        
        return jsonify({"ok": success})
        
    except Exception as e:
        logger.error(f"History save error: {e}")
        return jsonify({"ok": False, "error": str(e)})


@api_bp.route("/alternatives", methods=["POST"])
def get_alternatives():
    """Get alternative translations for a word."""
    try:
        data = request.get_json(silent=True) or {}
        
        source_text = (data.get("source_text") or "").strip()
        current_translation = (data.get("current_translation") or "").strip()
        clicked_word = (data.get("clicked_word") or "").strip()
        target_lang = (data.get("target_lang") or "de").strip()
        tone = (data.get("tone") or "neutral").strip()
        
        if not all([source_text, current_translation, clicked_word]):
            return jsonify({"alternatives": []})
        
        alternatives = translation_service.get_alternatives(
            source_text, current_translation, clicked_word, target_lang, tone
        )
        
        return jsonify({"alternatives": alternatives})
        
    except Exception as e:
        logger.error(f"Alternatives error: {e}")
        return jsonify({"alternatives": []})


@api_bp.route("/refine", methods=["POST"])
def refine_translation():
    """Refine translation with user constraints."""
    try:
        data = request.get_json(silent=True) or {}
        
        source_text = (data.get("source_text") or "").strip()
        current_translation = (data.get("current_translation") or "").strip()
        target_lang = (data.get("target_lang") or "de").strip()
        tone = (data.get("tone") or "neutral").strip()
        
        # Process enforced phrases
        enforced_phrases = [
            p.strip() for p in (data.get("enforced_phrases") or [])
            if isinstance(p, str) and p.strip()
        ]
        
        # Process replacements
        raw_replacements = data.get("replacements") or []
        replacements = []
        for r in raw_replacements:
            if isinstance(r, dict):
                from_word = (r.get("from") or "").strip()
                to_word = (r.get("to") or "").strip()
                if from_word and to_word:
                    replacements.append({"from": from_word, "to": to_word})
        
        if not source_text:
            return jsonify({"translated": ""})
        
        translated, faithful = translation_service.refine_translation(
            source_text, current_translation, target_lang, tone,
            enforced_phrases, replacements
        )
        
        return jsonify({
            "translated": translated,
            "faithful": faithful
        })
        
    except Exception as e:
        logger.error(f"Refinement error: {e}")
        return jsonify({
            "translated": current_translation,
            "faithful": False,
            "error": str(e)
        })


# Simple in-memory cache for TTS
tts_cache = {}

@api_bp.route("/tts", methods=["POST"])
def text_to_speech():
    """Convert text to speech using Wyoming Piper TTS."""
    from flask import request as flask_request
    print("DEBUG: TTS endpoint called!", flush=True)
    try:
        print("DEBUG: In try block", flush=True)
        data = flask_request.get_json(silent=True) or {}
        
        text = (data.get("text") or "").strip()
        print(f"DEBUG: TTS request for text: {text}", flush=True)
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Get language from text, default to polish
        language = data.get("language", "pl")
        print(f"DEBUG: TTS language: {language}", flush=True)
        
        # Map languages to Wyoming TTS voices (back to medium quality for better audio)
        voice_map = {
            "pl": "pl_PL-darkman-medium",
            "en": "en_US-lessac-medium", 
            "de": "de_DE-thorsten-medium",
            "fr": "fr_FR-siwis-medium",
            "es": "es_ES-male-glow",
            "it": "it_IT-male-glow",
            "ru": "ru_RU-male",
            "cs": "cs_CZ-male"
        }
        
        voice = voice_map.get(language, "pl_PL-darkman-medium")
        
        # Check cache first
        cache_key = f"{text}:{voice}"
        if cache_key in tts_cache:
            print("DEBUG: Found in cache, returning cached audio", flush=True)
            return Response(
                tts_cache[cache_key],
                mimetype="audio/wav",
                headers={
                    "Content-Disposition": "attachment; filename=tts.wav",
                    "Content-Length": str(len(tts_cache[cache_key]))
                }
            )
        
        # Connect to Wyoming Piper TTS
        logger.info(f"TTS: Connecting to Wyoming for text: '{text}', voice: '{voice}'")
        print(f"DEBUG: Connecting to Wyoming for text: '{text}', voice: '{voice}'", flush=True)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # Reduced timeout for faster response
            logger.info("TTS: Attempting to connect to Wyoming...")
            sock.connect(("10.0.20.134", 10200))
            logger.info("TTS: Connected to Wyoming successfully")
            
            # Send synthesize request
            wyoming_request = {
                "type": "synthesize", 
                "data": {
                    "text": text,
                    "voice": voice
                }
            }
            
            request_line = json.dumps(wyoming_request) + "\n"
            print(f"DEBUG: Sending to Wyoming: {request_line.strip()}", flush=True)
            sock.send(request_line.encode())
            
            # Read all response data (back to simple approach for now)
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
            print(f"DEBUG: Received {len(all_data)} bytes from Wyoming", flush=True)
            
            # Debug first few lines to see structure
            print(f"DEBUG: Starting to parse {len(all_data)} bytes", flush=True)
            print("DEBUG: First 500 chars:")
            print(all_data[:500])
            
            # Go back to the working regex approach
            import re
            
            raw_pcm_data = bytearray()
            
            # Find all audio-chunk messages and their payload lengths
            chunk_pattern = rb'"type": "audio-chunk"[^}]*"payload_length": (\d+)'
            chunks = list(re.finditer(chunk_pattern, all_data))
            print(f"DEBUG: Found {len(chunks)} audio-chunk matches", flush=True)
            
            chunk_count = 0
            for match in chunks:
                payload_length = int(match.group(1))
                chunk_count += 1
                print(f"DEBUG: Processing chunk {chunk_count} with payload {payload_length}", flush=True)
                
                # Find the end of this JSON message + metadata
                search_start = match.end()
                
                # Look for the start of binary data (after metadata JSON)
                # Binary data typically starts after 2 newlines from the audio-chunk message
                newlines_found = 0
                binary_start = search_start
                
                while binary_start < len(all_data) and newlines_found < 2:
                    if all_data[binary_start] == ord('\n'):
                        newlines_found += 1
                    binary_start += 1
                
                # Extract binary audio data
                if binary_start + payload_length <= len(all_data):
                    audio_chunk = all_data[binary_start:binary_start + payload_length]
                    raw_pcm_data.extend(audio_chunk)
                    print(f"DEBUG: Chunk {chunk_count}: Added {payload_length} bytes, total: {len(raw_pcm_data)}", flush=True)
                else:
                    print(f"DEBUG: Chunk {chunk_count}: Not enough data remaining ({binary_start} + {payload_length} > {len(all_data)})", flush=True)
            
            print(f"DEBUG: Found {chunk_count} audio chunks, total PCM data: {len(raw_pcm_data)} bytes", flush=True)
            
            if not raw_pcm_data:
                print("DEBUG: No audio data found", flush=True)
                return jsonify({"error": "No audio data received from TTS"}), 500
            
            print(f"DEBUG: Extracted {len(raw_pcm_data)} bytes of PCM data", flush=True)
            
            # Parse audio parameters from Wyoming response
            import struct
            import array
            import re
            import json
            
            # Extract actual audio parameters from Wyoming response
            sample_rate = 22050  # default fallback
            bits_per_sample = 16
            channels = 1
            
            # Look for audio parameters in Wyoming response
            # They appear as: {"rate": 22050, "width": 2, "channels": 1, "timestamp": null}
            rate_pattern = rb'"rate": (\d+)'
            rate_match = re.search(rate_pattern, all_data)
            if rate_match:
                sample_rate = int(rate_match.group(1))
                print(f"DEBUG: Found sample rate from Wyoming: {sample_rate}", flush=True)
            
            width_pattern = rb'"width": (\d+)'
            width_match = re.search(width_pattern, all_data)
            if width_match:
                bits_per_sample = int(width_match.group(1)) * 8
                print(f"DEBUG: Found bit depth from Wyoming: {bits_per_sample}", flush=True)
            
            channels_pattern = rb'"channels": (\d+)'
            channels_match = re.search(channels_pattern, all_data)
            if channels_match:
                channels = int(channels_match.group(1))
                print(f"DEBUG: Found channels from Wyoming: {channels}", flush=True)
            
            print(f"DEBUG: Audio params - rate: {sample_rate}, bits: {bits_per_sample}, channels: {channels}", flush=True)
            byte_rate = sample_rate * channels * bits_per_sample // 8
            block_align = channels * bits_per_sample // 8
            
            # Audio processing and normalization to reduce crackling
            if len(raw_pcm_data) % 2 != 0:
                raw_pcm_data = raw_pcm_data[:-1]  # Remove last byte if odd
            
            # Convert to signed 16-bit samples for processing
            samples = array.array('h')  # signed short (16-bit)
            samples.frombytes(raw_pcm_data)
            
            # Audio normalization and noise reduction
            if len(samples) > 0:
                # Find peak amplitude
                max_amplitude = max(abs(s) for s in samples)
                
                if max_amplitude > 0:
                    # Normalize to prevent clipping (use 90% of max range to avoid distortion)
                    target_max = int(32767 * 0.9)
                    if max_amplitude > target_max:
                        gain = target_max / max_amplitude
                        samples = array.array('h', [int(s * gain) for s in samples])
                        print(f"DEBUG: Applied gain normalization: {gain:.3f}", flush=True)
                    
                    # Simple low-pass filter to reduce high-frequency noise/crackling
                    # This helps reduce digital artifacts that cause crackling
                    if len(samples) > 2:
                        filtered_samples = array.array('h')
                        filtered_samples.append(samples[0])  # First sample unchanged
                        
                        for i in range(1, len(samples) - 1):
                            # Simple 3-point moving average filter
                            filtered_value = (samples[i-1] + 2*samples[i] + samples[i+1]) // 4
                            filtered_samples.append(filtered_value)
                        
                        filtered_samples.append(samples[-1])  # Last sample unchanged
                        samples = filtered_samples
                        print("DEBUG: Applied anti-crackling filter", flush=True)
            
            # Convert back to bytes
            raw_pcm_data = samples.tobytes()
            print(f"DEBUG: Final processed PCM data: {len(raw_pcm_data)} bytes", flush=True)
            
            # Create WAV header
            wav_data = io.BytesIO()
            
            # RIFF header
            wav_data.write(b'RIFF')
            wav_data.write(struct.pack('<I', 36 + len(raw_pcm_data)))  # File size
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
            wav_data.write(struct.pack('<I', len(raw_pcm_data)))  # Data size
            wav_data.write(raw_pcm_data)  # Raw audio data
            
            wav_content = wav_data.getvalue()
            wav_data.close()
            
            print(f"DEBUG: Created WAV file with {len(wav_content)} bytes", flush=True)
            
            # Cache the result (limit cache size to prevent memory issues)
            if len(tts_cache) > 50:  # Simple cache eviction
                tts_cache.clear()
            tts_cache[cache_key] = wav_content
            print("DEBUG: Cached TTS result", flush=True)
            
            # Return WAV audio
            return Response(
                wav_content,
                mimetype="audio/wav",
                headers={
                    "Content-Disposition": "attachment; filename=tts.wav",
                    "Content-Length": str(len(wav_content))
                }
            )
            
        except Exception as e:
            print(f"DEBUG: Wyoming TTS error: {e}", flush=True)
            return jsonify({"error": f"TTS service error: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"TTS endpoint error: {e}")
        return jsonify({"error": f"TTS error: {str(e)}"}), 500