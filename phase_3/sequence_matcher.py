from difflib import SequenceMatcher

def find_phoneme_matches(expected_text, transcribed_text, timestamps, phoneme_timestamps):
    results = {}
    for word, expected_phonemes in expected_text:
        if word in timestamps:
            # Get the time range for the word (+/- 2 words for context)
            start_time, end_time = timestamps[word]
            time_range = (
                max(0.0, start_time - 2.0),  # Start time minus 2 seconds
                end_time + 2.0               # End time plus 2 seconds
            )

            # Extract phonemes in the time range
            phonemes_in_range = [
                (phoneme_info['phoneme'], float(phoneme_info['start']), float(phoneme_info['end']))
                for phoneme_info in phoneme_timestamps
                if float(phoneme_info['start']) >= time_range[0] and float(phoneme_info['end']) <= time_range[1]
            ]

            # Match expected phonemes with extracted phonemes
            matched_phonemes = []
            phoneme_index = 0
            for expected_phoneme in expected_phonemes:
                while phoneme_index < len(phonemes_in_range):
                    audio_phoneme, p_start, p_end = phonemes_in_range[phoneme_index]
                    if audio_phoneme == expected_phoneme:
                        matched_phonemes.append(audio_phoneme)
                        phoneme_index += 1
                        break
                    phoneme_index += 1

            # Calculate match percentage
            match_percentage = (len(matched_phonemes) / len(expected_phonemes)) * 100 if expected_phonemes else 0

            # Store results
            results[word] = {
                "matched_phonemes": matched_phonemes,
                "match_percentage": match_percentage,
                "details": f"Matched {len(matched_phonemes)} out of {len(expected_phonemes)} phonemes."
            }

        else:
            # If word isn't in the timestamps, return no match
            results[word] = {
                "matched_phonemes": [],
                "match_percentage": 0,
                "details": "Word not found in transcribed text."
            }

    return results
