import logging
import re
from allosaurus.app import read_recognizer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class AudioPhonemeProcessor:
    def __init__(self, model_name="eng2102"):
        self.model = read_recognizer(model_name)

    def process_audio(self, filepath: str):
        """Processes the audio file and extracts top 3 phonemes with timestamps using GPU."""
        try:
            result = self.model.recognize(filepath, timestamp=True, topk=3)  # Request top 3 phonemes
            phoneme_data = []

            for line in result.strip().split("\n"):
                # Adjust regex to capture multiple phonemes per timestamp
                match = re.match(r"([\d.]+)\s+([\d.]+)\s+(.+)", line)
                if match:
                    start_time, duration, phonemes = match.groups()
                    
                    # Split phonemes based on spaces (since multiple phonemes are returned)
                    phoneme_list = phonemes.split()
                    
                    phoneme_data.append({
                        "start": float(start_time),
                        "end": float(start_time) + float(duration),
                        "phonemes": phoneme_list  # Store multiple phonemes
                    })

            logging.info(f"🔍 Extracted {len(phoneme_data)} phoneme timestamps from audio using GPU.")
            return phoneme_data

        except Exception as e:
            logging.error(f"❌ Error processing audio phonemes: {e}")
            raise

def test_audio_processing(filepath):
    """Test function to check phoneme extraction from an audio file."""
    processor = AudioPhonemeProcessor()
    phonemes = processor.process_audio(filepath)

    if phonemes:
        logging.info("✅ Phoneme extraction successful!")
        for p in phonemes[:10]:  # Show only first 10 phoneme entries
            print(f"Start: {p['start']:.2f}s, End: {p['end']:.2f}s, Phonemes: {', '.join(p['phonemes'])}")
    else:
        logging.warning("⚠️ No phonemes extracted.")

# Example usage
if __name__ == "__main__":
    test_audio_processing(r"recordings\recording_20250221_175834.wav")  # Update with actual file path
