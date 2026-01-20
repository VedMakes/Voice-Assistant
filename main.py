import asyncio
import numpy as np
import queue

from audio import audio_q, AudioInput
from wakeword import WakeWordDetector
from vad import VADGate
from asr import ASR
from ws_client import WSClient
from config import SAMPLE_RATE


async def run():
    ws = WSClient()
    await ws.connect()
    wake = WakeWordDetector()
    frame_len = wake.frame_length
    frame_ms = int(frame_len / SAMPLE_RATE * 1000)
    vad = VADGate(frame_ms)
    asr = ASR()
    print("assistant started, waiting for wake word")
    
    try:
        while True:
            try:
                pcm = audio_q.get(timeout=1)  # Add timeout to detect issues
            except queue.Empty:
                print("No audio data for 1 second")
                continue
            
            pcm_np = np.frombuffer(pcm, dtype=np.int16)
            for i in range(0, len(pcm_np), frame_len):
                frame = pcm_np[i:i + frame_len]
                if len(frame) < frame_len:
                    continue
                
                try:
                    if wake.detect(frame):
                        print("wake word detected")
                        asr.reset()
                        vad.reset()
                        
                        while True:
                            try:
                                pcm2 = audio_q.get(timeout=5)  # Timeout for command
                            except queue.Empty:
                                print("Timeout waiting for command")
                                break
                            
                            pcm2_np = np.frombuffer(pcm2, dtype=np.int16)
                            for j in range(0, len(pcm2_np), frame_len):
                                f = pcm2_np[j:j + frame_len]
                                if len(f) < frame_len:
                                    continue
                                
                                try:
                                    asr.accept(f.tobytes())
                                    vad.is_speech(f.tobytes())
                                except Exception as e:
                                    print(f"ASR/VAD error: {e}")
                                    break
                                
                                if vad.is_timeout():
                                    text = asr.finalize()
                                    print("recognized:", text)
                                    if text.strip():
                                        try:
                                            await ws.send_text(text)
                                            await asyncio.sleep(0.1)  # slight delay to ensure send completes
                                            print("sent to WS")
                                        except Exception as e:
                                            print(f"WS send error: {e}")
                                    break
                            else:
                                continue
                            break
                        
                        print("Command processing complete, resuming wake word detection")
                        
                except Exception as e:
                    print(f"Wake word processing error: {e}")
                    import traceback
                    traceback.print_exc()
                    
    except Exception as e:
        print(f"FATAL ERROR in main loop: {e}")
        import traceback
        traceback.print_exc()
        raise

def main():
    audio = AudioInput()
    audio.start()
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("Interrupted by user")
    except Exception as e:
        print(f"Main exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Stopping audio...")
        audio.stop()
        print("Cleanup complete")

if __name__ == "__main__":
    main()


