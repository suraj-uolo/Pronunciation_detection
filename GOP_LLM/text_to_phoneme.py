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
            # Get the words from the input sentence and clean them
            words = sentence.split()
            # Remove punctuation from words
            cleaned_words = [word.strip('.,!?:;') for word in words]
            
            # Phonemize each word individually to maintain correct mapping
            word_phoneme_mapping = {}
            for word in cleaned_words:
                if word:  # Skip empty strings
                    phonemes = phonemize(word, language=self.language, backend=self.backend, strip=True, njobs=1)
                    word_phoneme_mapping[word] = phonemes.strip()
            
            logging.info(f"🔠 Converted text to phonemes: {word_phoneme_mapping}")
            return word_phoneme_mapping
        except Exception as e:
            logging.error(f"❌ Error in text phonemization: {e}")
            raise

# Convert text to phonemes
converter = TextToPhonemeConverter(language="en-us", backend="espeak")
phonemes = converter.text_to_phonemes("Hello world")
print(phonemes)
