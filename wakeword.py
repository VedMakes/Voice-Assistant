import pvporcupine
from SECRETS import WAKE_WORDS, PORCUPINE_ACCESS_KEY


class WakeWordDetector:
    def __init__(self):
        self.porcupine = pvporcupine.create(
            access_key=PORCUPINE_ACCESS_KEY,
            keywords=WAKE_WORDS
        )
        self.frame_length = self.porcupine.frame_length
    
    def detect(self, frame):
        return self.porcupine.process(frame) >= 0