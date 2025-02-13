import os
import wave
import sounddevice as sd
import numpy as np
from datetime import datetime
#commet
class AudioRecorder:
    def __init__(self, recordings_dir="recordings", samplerate=16000):
        self.recordings_dir = recordings_dir
        self.samplerate = samplerate
        os.makedirs(self.recordings_dir, exist_ok=True)

    def record_audio(self, duration: int = 5, filename: str = None) -> str:
        """Record audio and save to file."""
        if not filename:
            filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        filepath = os.path.join(self.recordings_dir, filename)

        try:
            print(f"🎙️ Recording for {duration} seconds...")
            audio = sd.rec(int(self.samplerate * duration), samplerate=self.samplerate, channels=1, dtype=np.int16, blocking=True)
            sd.wait()

            with wave.open(filepath, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.samplerate)
                wf.writeframes(audio.tobytes())

            print(f"✅ Recording saved to {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Error recording audio: {e}")
            raise