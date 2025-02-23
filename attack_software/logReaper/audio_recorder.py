import sounddevice as sd
import wave
import os
from datetime import datetime
import logging

class AudioRecorder:
    def __init__(self, directory="audio_logs", duration=10, samplerate=44100):
        self.directory = directory
        self.duration = duration
        self.samplerate = samplerate
        os.makedirs(self.directory, exist_ok=True)

    def record_audio(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(self.directory, f"audio_{timestamp}.wav")
        logging.info(f"Recording audio to {filename}...")
        recording = sd.rec(int(self.duration * self.samplerate), samplerate=self.samplerate, channels=2, dtype='int16')
        sd.wait()
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(self.samplerate)
            wf.writeframes(recording.tobytes())
        logging.info("Audio recording completed.")
