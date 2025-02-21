import logging
from audio_recorder import AudioRecorder
from transcription import Transcriber
from audio_to_phoneme import AudioPhonemeProcessor
from text_to_phoneme import TextToPhonemeConverter
from analysis_open_ai import evaluate_pronunciation_open_ai  # ✅ OpenAI evaluation
from analysis_open_llm import evaluate_pronunciation_llama  # ✅ Local LLM evaluation

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    try:
        # Step 1: Record Audio
        logging.info("\n🎤 Recording audio...")
        recorder = AudioRecorder()
        audio_path = recorder.record_audio(duration=3)
        logging.info(f"✅ Audio recorded: {audio_path}")

        # Step 2: Transcribe Audio
        logging.info("\n📝 Transcribing audio...")
        transcriber = Transcriber()
        transcript = transcriber.transcribe_audio(audio_path)

        if not transcript:
            logging.warning("❌ No transcription available. Exiting.")
            return

        # Step 3: Extract Expected Phonemes from Reference Text
        reference_text = "hello good morning"
        logging.info(f"\n📖 Reference Text: {reference_text}")  # Display reference text
        text_phoneme_converter = TextToPhonemeConverter()
        expected_phonemes = text_phoneme_converter.text_to_phonemes(reference_text)

        if not expected_phonemes:
            logging.warning("❌ Could not generate expected phonemes. Exiting.")
            return

        logging.info("\n🔍 Expected Phonemes:")
        formatted_expected_phonemes = {
            word: " ".join(phonemes) for word, phonemes in expected_phonemes.items()
        }
        for word, phoneme_str in formatted_expected_phonemes.items():
            logging.info(f"  📖 {word}: {phoneme_str}")

        # Step 4: Process Recorded Audio to Extract Phonemes
        logging.info("\n🎵 Extracting phonemes from audio...")
        phoneme_processor = AudioPhonemeProcessor()
        phoneme_timestamps = phoneme_processor.process_audio(audio_path)

        if not phoneme_timestamps:
            logging.warning("❌ No phoneme data extracted. Exiting.")
            return

        logging.info("\n🔊 Extracted Audio Phonemes:")
        extracted_audio_phonemes = [p["phoneme"] for p in phoneme_timestamps]
        for phoneme_info in phoneme_timestamps:
            logging.info(f"  🔊 {phoneme_info['phoneme']} - Start: {phoneme_info['start']}s, End: {phoneme_info['end']}s")

        # Step 5: Choose LLM for Pronunciation Evaluation
        logging.info("\n⚙️ Select LLM: [1] OpenAI | [2] Local LLM")
        choice = input("Enter 1 or 2: ").strip()

        if choice == "1":
            logging.info("\n🗣️ Evaluating pronunciation with OpenAI...")
            evaluation_result = evaluate_pronunciation_open_ai(
                transcribed_text=transcript,
                expected_text=reference_text,
                audio_phonemes=", ".join(extracted_audio_phonemes),
                expected_phonemes=", ".join(formatted_expected_phonemes.values())
            )
        elif choice == "2":
            logging.info("\n🗣️ Evaluating pronunciation with Local LLM...")
            evaluation_result = evaluate_pronunciation_llama(
                transcribed_text=transcript,
                expected_text=reference_text,
                audio_phonemes=", ".join(extracted_audio_phonemes),
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