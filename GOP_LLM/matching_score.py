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
    expected_words = list(text_phonemes_expected.keys())
    spoken_word_index = 0
    
    # Convert all spoken words to lowercase for comparison
    processed_spoken_words = [(word[0].lower(), word[1], word[2]) for word in spoken_words]
    
    for expected_word in expected_words:
        expected_word_lower = expected_word.lower()
        expected_phonemes = text_phonemes_expected[expected_word_lower]
        
        # Look for the word in remaining spoken words
        found = False
        for i in range(spoken_word_index, len(processed_spoken_words)):
            spoken_word, start, end = processed_spoken_words[i]
            
            # Clean up spoken word (remove punctuation, etc)
            spoken_word = spoken_word.strip('.,?!')
            
            if spoken_word == expected_word_lower:
                result.append(SpokenWord(
                    word=spoken_word,
                    start=start,
                    end=end,
                    phonemes=[],
                    expected_phonemes=expected_phonemes,
                    is_missing=False,
                    is_extra=False,
                    is_match=True
                ))
                spoken_word_index = i + 1
                found = True
                break
        
        if not found:
            # Word was expected but not found in speech
            result.append(SpokenWord(
                word=expected_word_lower,
                start=0,
                end=0,
                phonemes=[],
                expected_phonemes=expected_phonemes,
                is_missing=True,
                is_extra=False,
                is_match=False
            ))
    
    # Check for any extra spoken words
    for i in range(spoken_word_index, len(processed_spoken_words)):
        spoken_word, start, end = processed_spoken_words[i]
        if spoken_word.strip('.,?!') not in text_phonemes_expected:
            result.append(SpokenWord(
                word=spoken_word,
                start=start,
                end=end,
                phonemes=[],
                expected_phonemes=[],
                is_missing=False,
                is_extra=True,
                is_match=False
            ))
    
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
    
    # Create case-insensitive version of the dictionary
    text_phonemes_expected = {word.lower(): phonemes 
                            for word, phonemes in text_phonemes_expected.items()}
    
    # Get spoken words
    spoken_words = get_spoken_words(timestamped_transcript)
    
    # Match words to expected
    result = match_words_to_expected(spoken_words, text_phonemes_expected)
    
    # Match phonemes for each word
    matched_word_phonemes = []
    for word in result:
        if not word.is_missing and not word.is_extra:  # Only process words that were actually spoken
            phoneme_matches = match_word_phoneme(word, phoneme_timestamps)
            matched_word_phonemes.append({word.word: phoneme_matches})
    
    # Save results
    with open('matched_word_phonemes.json', 'w') as f:
        json.dump(matched_word_phonemes, f, indent=4, ensure_ascii=False)
    
    summary = ""
    processed_count = 0
    total_words = len(text_phonemes_expected)
    
    # Process each word's phonemes
    for word_dict in matched_word_phonemes:
        word = list(word_dict.keys())[0]
        phoneme_options = word_dict[word]
        
        if phoneme_options:
            try:
                candidate_phonemes = []
                for phoneme in phoneme_options:
                    phoneme_subset = phoneme[:3] if len(phoneme) >= 3 else phoneme
                    candidate_phonemes.append(phoneme_subset)
                
                correct_ipa = text_phonemes_expected[word.lower()]
                best_match = get_best_match(correct_ipa, candidate_phonemes)
                
                print(f"Word: {word}")
                print(f"Expected IPA: {correct_ipa}")
                print(f"Best match: {best_match}")
                print("---")
                
                summary += f"Word: {word}\n"
                summary += f"Expected IPA: {correct_ipa}\n"
                summary += f"Best match: {best_match}\n"
                summary += "---\n"
                
                processed_count += 1
            except (IndexError, KeyError) as e:
                print(f"Skipping word '{word}' due to error: {e}")
                continue
    
    print(f"\nProcessed {processed_count} out of {total_words} words")
    return summary

if __name__ == "__main__":
    main()