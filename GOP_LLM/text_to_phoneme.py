import logging
from phonemizer import phonemize

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class TextToPhonemeConverter:
    def __init__(self, language="en-us", backend="espeak"):
        self.language = language
        self.backend = backend

    def text_to_phonemes(self, sentence: str):
        """Converts a sentence into phonemes using batch phonemization."""
        try:
            phonemes = phonemize(sentence, language=self.language, backend=self.backend, strip=True, njobs=4)
            word_phoneme_mapping = dict(zip(sentence.split(), phonemes.split()))
            logging.info(f"🔠 Converted text to phonemes: {word_phoneme_mapping}")
            return word_phoneme_mapping
        except Exception as e:
            logging.error(f"❌ Error in text phonemization: {e}")
            raise
