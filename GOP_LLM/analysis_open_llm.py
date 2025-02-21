import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Local LLM configuration
LOCAL_LLM_URL = "http://10.36.27.187:1234/v1/chat/completions"
MODEL_NAME = "deepseek-r1-distill-qwen-7b"

def evaluate_pronunciation_llama(transcribed_text: str, expected_text: str, audio_phonemes: str, expected_phonemes: str):
    """
    You are a expert in phonetics and phonology. You are tasked with evaluating the pronunciation of a user's speech.
    Evaluates pronunciation by comparing transcribed phonemes with expected phonemes.
    
    Args:
        transcribed_text (str): The user's spoken text after transcription.
        expected_text (str): The correct expected text.
        audio_phonemes (str): Phonemes extracted from the user's speech.
        expected_phonemes (str): The correct phonemes for comparison.

    Returns:
        dict: Contains AI-generated pronunciation feedback.
    """
    prompt = (f"Analyze the user's pronunciation accuracy compared to the expected text and phonemes. "
            f"Ignore minor variations and background noise. Focus on significant phoneme mismatches. "
            f"Allow natural deviations if the speech remains intelligible.\n\n"
            
            f"Expected Text: {expected_text}\n"
            f"Transcribed Text: {transcribed_text}\n"
            f"Expected Phonemes: {expected_phonemes}\n"
            f"Audio Phonemes: {audio_phonemes}\n\n"
            
            f"Evaluation Criteria:\n"
            f"- Did the user say the expected words?\n"
            f"- Do key phonemes match?\n"
            f"- Ignore extra/unnecessary phonemes from noise.\n"
            f"- Provide a clear word-by-word assessment for each word.\n\n"

            f"Example Analysis:\n"
            f"✅ Transcription: I woke up\n"
            f"all expected words are not available in the transcription\n"
            
            f"🔍 Expected Phonemes:\n"
            f"   - i: a ɪ\n"
            f"   - woke: w o ʊ k\n"
            f"   - up: ʌ p\n"
            f"   - at: æ t\n"
            f"   - 6: s ɪ k s\n"
            f"   - am: e ɪ ɛ m\n"
            f"   - in: ɪ n ð ə\n"
            f"   - the: m ɔ ː ɹ n ɪ ŋ\n\n"

            f"🎵 Extracted Audio Phonemes:\n"
            f"   - 🔊 a (Start: 0.53s, End: 0.555s)\n"
            f"   - 🔊 j (Start: 0.54s, End: 0.565s)\n"
            f"   - 🔊 l (Start: 0.73s, End: 0.755s)\n"
            f"   - 🔊 ʊ (Start: 0.77s, End: 0.795s)\n"
            f"   - 🔊 k (Start: 0.94s, End: 0.965s)\n"
            f"   - 🔊 ʌ (Start: 1.0s, End: 1.025s)\n"
            f"   - 🔊 p (Start: 1.11s, End: 1.135s)\n\n"

            f"📊 Word-by-Word Analysis:\n"
            f"1️⃣ **'i'**\n"
            f"   - ✅ Expected Phoneme: a ɪ\n"
            f"   - 🔊 Audio Phoneme: a (Start: 0.53s, End: 0.555s)\n"
            f"   - ✅ Pronunciation is correct.\n\n"

            f"2️⃣ **'woke'**\n"
            f"   - ✅ Expected Phoneme: w o ʊ k\n"
            f"   - 🔊 Audio Phoneme: j l ʊ k (Start: 0.54s - 0.965s)\n"
            f"   - ⚠️ Incorrect pronunciation: Missing 'w' sound, 'j' and 'l' detected instead.\n\n"

            f"3️⃣ **'up'**\n"
            f"   - ✅ Expected Phoneme: ʌ p\n"
            f"   - 🔊 Audio Phoneme: ʌ p (Start: 1.0s - 1.135s)\n"
            f"   - ✅ Pronunciation is correct.\n\n"
            
            f"4️⃣ Rest all expected words are missing in the transcription.\n\n"

            f"🎯 Summary: The pronunciation was mostly accurate, but there were some phoneme mismatches in 'woke' and '6'. "
            f"Consider focusing on the 'w' sound in 'woke' and avoiding unnecessary sounds in '6'.")


    try:
        logging.info("Sending request to local LLM...")

        response = requests.post(
            LOCAL_LLM_URL,
            json={
                "model": MODEL_NAME,
                "messages": [
                    #{"role": "system", "content": "You are a pronunciation coach."},
                    {"role": "user", "content": prompt}
                ]
            }
        )

        if response.status_code == 200:
            result = response.json()
            feedback = result["choices"][0]["message"]["content"]
            return {"feedback": feedback}
        else:
            logging.error(f"Local LLM error: {response.status_code}, {response.text}")
            return {"error": "Failed to process pronunciation evaluation."}

    except Exception as e:
        logging.error(f"Error in local LLM API call: {e}")
        return {"error": "Failed to connect to local LLM."}