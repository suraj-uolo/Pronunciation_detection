import logging
import re
from allosaurus.app import read_recognizer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class AudioPhonemeProcessor:
    def __init__(self, model_name="eng2102"):
        self.model = read_recognizer(model_name)

    def process_audio(self, filepath: str):
        """Processes the audio file and extracts phonemes with timestamps."""
        try:
            result = self.model.recognize(filepath, timestamp=True)
            phoneme_data = []
            
            for line in result.strip().split("\n"):
                match = re.match(r"([\d.]+)\s+([\d.]+)\s+(\S+)", line)
                if match:
                    start_time, duration, phoneme = match.groups()
                    phoneme_data.append({
                        "start": float(start_time),
                        "end": float(start_time) + float(duration),
                        "phoneme": phoneme
                    })

            logging.info(f"🔍 Extracted {len(phoneme_data)} phonemes from audio.")
            return phoneme_data

        except Exception as e:
            logging.error(f"❌ Error processing audio phonemes: {e}")
            raise