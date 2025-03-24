import json
from dataclasses import dataclass
from typing import Literal
from rapidfuzz import fuzz, process
from itertools import product

@dataclass
class SpokenWord:
    word: str
    start: float
    end: float
    phonemes: list[str]
    expected_phonemes: list[str]
    is_missing: bool
    is_match: bool
    is_extra: bool

def load_data():
    """Load the required JSON files."""
    with open('phoneme_timestamps.json', 'r') as f:
        phoneme_timestamps = json.load(f)
    with open('text_phonemes_expected.json', 'r') as f:
        text_phonemes_expected = json.load(f)
    with open('timestamped_transcript.json', 'r') as f:
        timestamped_transcript = json.load(f)
    return phoneme_timestamps, text_phonemes_expected, timestamped_transcript

def get_spoken_words(timestamped_transcript):
    """Extract spoken words with their timestamps."""
    spoken_words = []
    for segment in timestamped_transcript['segments']:
        for word in segment['words']:
            spoken_words.append((word['word'].strip(), word['start'], word['end']))
    return spoken_words

def match_words_to_expected(spoken_words, text_phonemes_expected):
    """Match spoken words to expected words and create SpokenWord objects."""
    result = []
    i, j = 0, 0
    expected_words = list(text_phonemes_expected.keys())
    
    while j < len(text_phonemes_expected):
        expected_word = expected_words[j]
        expected_phonemes = list(text_phonemes_expected[expected_word])
        expected_word = expected_words[j].lower()
        
        st = i
        while st < len(spoken_words):
            spoken_word_tuple = spoken_words[st]
            spoken_word = spoken_word_tuple[0][:len(expected_word)].lower()
            if spoken_word == expected_word:
                result.append(SpokenWord(
                    word=spoken_word,
                    start=spoken_word_tuple[1],
                    end=spoken_word_tuple[2],
                    phonemes=[],
                    expected_phonemes=expected_phonemes,
                    is_missing=False,
                    is_extra=False,
                    is_match=True
                ))
                break
            else:
                st += 1
        else:
            i = st + 1
            result.append(SpokenWord(
                word=expected_word,
                start=0,
                end=0,
                phonemes=[],
                expected_phonemes=expected_phonemes,
                is_missing=True,
                is_extra=False,
                is_match=False
            ))
        j += 1
    return result

def match_word_phoneme(word: SpokenWord, phoneme_timestamps: list[dict[Literal['start', 'end', 'phonemes'], float | list[str]]]):
    """Match phonemes to a specific word based on timestamps."""
    start, end = word.start, word.end
    candidate_phonemes = []
    
    for phoneme in phoneme_timestamps:
        phoneme_start, phoneme_end = phoneme['start'], phoneme['end']
        if phoneme_start >= start and (phoneme_end <= end or (phoneme_start <= end)):
            candidate_phonemes.append(phoneme['phonemes'])
        
        if phoneme_start >= end:
            break
    
    return candidate_phonemes

def get_best_match(correct_ipa: str, phoneme_options: list[list[str]]):
    """Find the best matching phoneme sequence."""
    generated_sequences = ["".join(seq) for seq in product(*phoneme_options)]
    best_match = process.extractOne(correct_ipa, generated_sequences, scorer=fuzz.ratio)
    return best_match

def main():
    # Load data
    phoneme_timestamps, text_phonemes_expected, timestamped_transcript = load_data()
    
    # Get spoken words
    spoken_words = get_spoken_words(timestamped_transcript)
    
    # Match words to expected
    result = match_words_to_expected(spoken_words, text_phonemes_expected)
    
    # Match phonemes for each word
    matched_word_phonemes = []
    for word in result:
        phoneme_matches = match_word_phoneme(word, phoneme_timestamps)
        matched_word_phonemes.append({word.word: phoneme_matches})
    
    # Save results
    with open('matched_word_phonemes.json', 'w') as f:
        json.dump(matched_word_phonemes, f, indent=4, ensure_ascii=False)
    
    summary = ""
    # Example of getting best match for each word
    for word_dict in matched_word_phonemes:
        word = list(word_dict.keys())[0]
        phoneme_options = word_dict[word]
        if phoneme_options:
            candidate_phonemes = [
                [phoneme[0], phoneme[2], phoneme[4]] 
                for phoneme in phoneme_options
            ]
            correct_ipa = text_phonemes_expected[word]
            best_match = get_best_match(correct_ipa, candidate_phonemes)
            print(f"Word: {word}")
            print(f"Expected IPA: {correct_ipa}")
            print(f"Best match: {best_match}")
            print("---")

            summary += f"Word: {word}\n"
            summary += f"Expected IPA: {correct_ipa}\n"
            summary += f"Best match: {best_match}\n"
            summary += "---\n"

            # yield {
            #     'word': word,
            #     'expected_ipa': correct_ipa,
            #     'best_match': best_match
            # }

    return summary

if __name__ == "__main__":
    main()