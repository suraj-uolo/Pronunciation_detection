from phonemizer import phonemize

def text_to_phonemes(sentence: str):
    """Convert a sentence into phonemes word by word using phonemizer."""
    words = sentence.split()
    phonemes_dict = {}

    try:
        for word in words:
            phonemes = phonemize(word, language="en-us", backend="espeak", strip=True)
            phonemes_dict[word] = phonemes
    except Exception as e:
        print(f"❌ Error converting text to phonemes: {e}")
        raise

    return phonemes_dict