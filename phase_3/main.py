import os
from audio_recorder import AudioRecorder
from transcription import Transcriber
from alignment import ForcedAligner
from audio_to_phoneme import process_audio
from text_phoneme_extraction import text_to_phonemes
from phone_grouper import PhonemeGrouper
from compare_visualize import compare_phonemes, visualize_phoneme_comparison
from sequence_matcher import find_phoneme_matches  # Import the new functionality

# Set Paths
MFA_DICTIONARY_PATH = r"C:\Users\suraj\.conda\envs\mfa\Lib\site-packages\montreal_forced_aligner\tests\data\dictionaries\english_us_mfa_reduced.dict"
MFA_MODEL = "english_mfa"  # Ensure this model is installed

def main():
    # Step 1: Record Audio
    recorder = AudioRecorder()
    audio_path = recorder.record_audio(duration=4)

    # Step 2: Transcribe the Recorded Audio
    transcriber = Transcriber()
    transcript = transcriber.transcribe_audio(audio_path)

    if not transcript:
        print("❌ No transcription available. Exiting.")
        return

    print(f"\n🎤 Transcribed Text: {transcript}")

    # Step 3: Perform Forced Alignment
    aligner = ForcedAligner(mfa_model=MFA_MODEL, dict_path=MFA_DICTIONARY_PATH)
    alignment_data = aligner.force_align_audio(audio_path, transcript)

    if not alignment_data:
        print("❌ Forced alignment failed. Exiting.")
        return

    word_timestamps = alignment_data['words']  # List of word timings

    print("\n⏳ Forced Alignment Data:")
    for word_info in word_timestamps:
        print(f"  📌 {word_info['word']} - Start: {word_info['start']}s, End: {word_info['end']}s")

    # Step 4: Extract Phonemes from Audio
    phoneme_timestamps = process_audio(audio_path)

    print("\n🎵 Extracted Audio Phonemes:")
    for phoneme_info in phoneme_timestamps:
        print(f"  🔊 {phoneme_info['phoneme']} - Start: {phoneme_info['start']}s, End: {phoneme_info['end']}s")

    # Step 5: Extract Expected Phonemes from Reference Text
    reference_text = "hello good morning"  # Replace with the actual text you want to analyze against
    expected_phonemes = text_to_phonemes(reference_text)

    print("\n🔍 Expected Phonemes for Reference Text:")
    for word, phonemes in expected_phonemes.items():
        print(f"  📖 {word}: {' '.join(phonemes)}")

    # Step 6: Group Phonemes for Each Word Based on Alignment
    grouper = PhonemeGrouper(mfa_model=MFA_MODEL, dict_path=MFA_DICTIONARY_PATH)
    grouped_phonemes = grouper.group_phonemes(audio_path, transcript)

    print("\n🔍 Grouped Phonemes for Each Word:")
    for word_group in grouped_phonemes:
        word = word_group['word']
        phoneme_list = [p['phoneme'] for p in word_group['phonemes']]
        print(f"  📖 {word}: {' '.join(phoneme_list) if phoneme_list else 'No phonemes detected'}")

    # Step 7: Compare Pronunciation
    print("\n🗣️ Pronunciation Analysis:")
    actual_phoneme_map = {}
    for word_group in grouped_phonemes:
        word = word_group['word']
        actual_phonemes = [p['phoneme'] for p in word_group['phonemes']]
        expected = expected_phonemes.get(word, "N/A")
        actual_phoneme_map[word] = ' '.join(actual_phonemes) if actual_phonemes else "No phonemes detected"

        print(f"\nWord: {word}")
        print(f"  🎙️ Actual  : {actual_phoneme_map[word]}")
        print(f"  📖 Expected: {expected if expected != 'N/A' else 'No expected phonemes available'}")

    # Step 8: Visualize Pronunciation Comparison
    print("\n📊 Visualizing pronunciation comparison...")
    comparison_results = compare_phonemes(actual_phoneme_map, expected_phonemes)
    visualize_phoneme_comparison(comparison_results)

    # Step 9: Measure Phoneme Sequence Matching
    print("\n🔗 Phoneme Sequence Matching:")

    # Prepare data for `find_phoneme_matches`
    transcribed_text = transcript.split()  # Split the transcribed text into words
    timestamps = {word_info['word']: (word_info['start'], word_info['end']) for word_info in word_timestamps}
    expected_text = [(word, expected_phonemes[word]) for word in transcribed_text if word in expected_phonemes]

    sequence_match_results = find_phoneme_matches(
        expected_text=expected_text,
        transcribed_text=transcribed_text,
        timestamps=timestamps,
        phoneme_timestamps=phoneme_timestamps
    )

    # Display results
    for word, result in sequence_match_results.items():
        print(f"\nWord: {word}")
        print(f"  ✅ Match Percentage: {result['match_percentage']:.2f}%")
        print(f"  🎯 Matched Phonemes: {result['matched_phonemes']}")
        print(f"  ℹ️ Details: {result['details']}")


if __name__ == "__main__":
    main()