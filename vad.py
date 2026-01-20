import webrtcvad
from config import VAD_MODE, SILENCE_TIMEOUT_MS, SAMPLE_RATE


class VADGate:
    def __init__(self, frame_ms):
        self.vad = webrtcvad.Vad(VAD_MODE)
        self.silence_ms = 0
        self.frame_ms = frame_ms

    def is_speech(self, frame_bytes):
        speech = self.vad.is_speech(frame_bytes, SAMPLE_RATE)
        if speech:
            self.silence_ms = 0
        else:
            self.silence_ms += self.frame_ms
        return speech

    def is_timeout(self):
        return self.silence_ms > SILENCE_TIMEOUT_MS

    def reset(self):
        self.silence_ms = 0
