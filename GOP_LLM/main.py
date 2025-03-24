import logging
from audio_recorder import AudioRecorder
from audio_cleaner import AudioCleaner  # ✅ New import
from transcription import Transcriber
from audio_to_phoneme import AudioPhonemeProcessor
from text_to_phoneme import TextToPhonemeConverter
from analysis_open_ai import evaluate_pronunciation_open_ai  # ✅ OpenAI evaluation
from analysis_open_llm import evaluate_pronunciation_llama  # ✅ Local LLM evaluation
import json
from matching_score import main as generate_match_summary
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    try:
        # Step 1: Record Audio
        logging.info("\n🎤 Recording audio...")
        recorder = AudioRecorder()
        audio_path = recorder.record_audio(duration=5)
        logging.info(f"✅ Audio recorded: {audio_path}")

        # Step 2: Clean the Recorded Audio
        logging.info("\n🧼 Cleaning audio to reduce noise...")
        cleaner = AudioCleaner()
        cleaned_audio_path = cleaner.clean_audio(audio_path)
        logging.info(f"✅ Cleaned audio saved: {cleaned_audio_path}")

        # Step 3: Transcribe Audio (Using Cleaned Audio)
        logging.info("\n📝 Transcribing cleaned audio...")
        transcriber = Transcriber(engine='whisper')
        # transcriber = Transcriber(engine='google')  # Use Google Speech API
        # transcript = transcriber.transcribe_audio(cleaned_audio_path)

        timestamped_transcript, transcript = transcriber.transcribe_audio(cleaned_audio_path)

        json.dump(timestamped_transcript, open("timestamped_transcript.json", "w", encoding='utf-8'), indent=2, ensure_ascii=False)

        if not transcript:
            logging.warning("❌ No transcription available. Exiting.")
            return

        # Step 4: Extract Expected Phonemes from Reference Text
        reference_text = sys.argv[1]
        logging.info(f"\n📖 Reference Text: {reference_text}")  # Display reference text
        text_phoneme_converter = TextToPhonemeConverter()
        expected_phonemes = text_phoneme_converter.text_to_phonemes(reference_text)
        json.dump(expected_phonemes, open("text_phonemes_expected.json", "w", encoding='utf-8'), indent=2, ensure_ascii=False)

        if not expected_phonemes:
            logging.warning("❌ Could not generate expected phonemes. Exiting.")
            return

        logging.info("\n🔍 Expected Phonemes:")
        formatted_expected_phonemes = {
            word: " ".join(phonemes) for word, phonemes in expected_phonemes.items()
        }
        for word, phoneme_str in formatted_expected_phonemes.items():
            logging.info(f"  📖 {word}: {phoneme_str}")

        # Step 5: Process Cleaned Audio to Extract Top-3 Phonemes per Timestamp
        logging.info("\n🎵 Extracting phonemes from cleaned audio...")
        phoneme_processor = AudioPhonemeProcessor()
        phoneme_timestamps = phoneme_processor.process_audio(cleaned_audio_path)

        json.dump(phoneme_timestamps, open("phoneme_timestamps.json", "w", encoding='utf-8'), indent=2, ensure_ascii=False)

        if not phoneme_timestamps:
            logging.warning("❌ No phoneme data extracted. Exiting.")
            return

        logging.info("\n🔊 Extracted Audio Phonemes:")
        extracted_audio_phonemes = []
        for phoneme_info in phoneme_timestamps:
            top_phonemes = ", ".join(phoneme_info["phonemes"])  # Include all top 3 phonemes
            extracted_audio_phonemes.append(top_phonemes)  # Collect all phonemes for evaluation
            logging.info(f"  🔊 {top_phonemes} - Start: {phoneme_info['start']}s, End: {phoneme_info['end']}s")

         # Generate match summary
        logging.info("\n📝 Generating word-level correctness summary...")
        logging.info(f"\n📝 Word-level correctness summary:\n")
        generate_match_summary()

        # json.dump(expected_phonemes, open("expected_phonemes.json", "w"), indent=4)
        # json.dump(extracted_audio_phonemes, open("extracted_audio_phonemes.json", "w"), indent=4)
        # Step 6: Choose LLM for Pronunciation Evaluation
        logging.info("\n⚙️ Select LLM: [1] OpenAI | [2] Local LLM")
        choice = input("Enter 1 or 2: ").strip()

        if choice == "1":
            logging.info("\n🗣️ Evaluating pronunciation with OpenAI...")
            evaluation_result = evaluate_pronunciation_open_ai(
                transcribed_text=transcript,
                expected_text=reference_text,
                audio_phonemes=" | ".join(extracted_audio_phonemes),  # Now includes top-3 phonemes
                expected_phonemes=", ".join(formatted_expected_phonemes.values())
            )
        elif choice == "2":
            logging.info("\n🗣️ Evaluating pronunciation with Local LLM...")
            evaluation_result = evaluate_pronunciation_llama(
                transcribed_text=transcript,
                expected_text=reference_text,
                audio_phonemes=" | ".join(extracted_audio_phonemes),  # Now includes top-3 phonemes
                expected_phonemes=", ".join(formatted_expected_phonemes.values())
            )
        else:
            logging.warning("❌ Invalid choice. Exiting.")
            return

        # Display feedback
        logging.info("\n📢 Pronunciation Feedback:")
        logging.info(evaluation_result.get("feedback", "No feedback received."))

       

    except Exception as e:
        logging.error(f"❌ Critical error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
