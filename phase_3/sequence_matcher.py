from difflib import SequenceMatcher

def find_phoneme_matches(expected_text, transcribed_text, timestamps, phoneme_timestamps):
    results = {}

    if not phoneme_timestamps:
        return results  # No phoneme data, return empty results

    # Get the first and last phoneme timestamps
    first_phoneme_time = float(phoneme_timestamps[0]['start'])  
    last_phoneme_time = float(phoneme_timestamps[-1]['end'])  

    words = list(timestamps.keys())  # Ordered words from the transcribed text

    for i, (word, expected_phonemes) in enumerate(expected_text):
        if word not in timestamps:
            results[word] = {
                "matched_phonemes": [],
                "match_percentage": 0,
                "details": "Word not found in transcribed text."
            }
            continue

        start_time, end_time = timestamps[word]

        # Adjust time range based on word position
        if word == words[0]:  # First word
            time_range = (first_phoneme_time, end_time + 1.0)
        elif word == words[-1]:  # Last word
            time_range = (max(0.0, start_time - 1.0), last_phoneme_time)
        else:  # Any other word
            time_range = (max(0.0, start_time - 1.0), end_time + 1.0)

        # 🔍 **Extract phonemes within the selected time range**
        phonemes_in_range = [
            (phoneme_info['phoneme'], phoneme_info['start'], phoneme_info['end'])
            for phoneme_info in phoneme_timestamps
            if time_range[0] <= float(phoneme_info['start']) <= time_range[1] or
               time_range[0] <= float(phoneme_info['end']) <= time_range[1]
        ]

        # 📌 **Print extracted phonemes for debugging**
        print(f"\n🔍 Word: {word}")
        print(f"   ⏳ Selected Time Range: {time_range[0]:.2f}s - {time_range[1]:.2f}s")
        print(f"   🎧 Extracted Phonemes: {[p[0] for p in phonemes_in_range]}")
        
        # **Fixed Phoneme Sequence Matching (Skipping Non-Matches)**
        matched_phonemes = []
        phoneme_index = 0
        phonemes_in_range_only = [p[0] for p in phonemes_in_range]  # Extract just phoneme symbols

        for expected_phoneme in expected_phonemes:
            while phoneme_index < len(phonemes_in_range_only):
                if phonemes_in_range_only[phoneme_index] == expected_phoneme:
                    matched_phonemes.append(expected_phoneme)
                    phoneme_index += 1  # Move to next phoneme in sequence
                    break  # Stop looking for this expected phoneme
                phoneme_index += 1  # Skip over non-matching phoneme

        # 🧮 **Calculate match percentage correctly**
        match_percentage = (len(matched_phonemes) / len(expected_phonemes)) * 100 if expected_phonemes else 0

        # 📌 **Store results**
        results[word] = {
            "matched_phonemes": matched_phonemes,
            "match_percentage": round(match_percentage, 2),
            "details": f"Matched {len(matched_phonemes)} out of {len(expected_phonemes)} phonemes."
        }

        # 📌 **Print comparison result for debugging**
        print(f"   📖 Expected Phonemes : {expected_phonemes}")
        print(f"   🎯 Matched Phonemes  : {matched_phonemes}")
        print(f"   ✅ Match Percentage  : {match_percentage:.2f}%\n")

    return results
