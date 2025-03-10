import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Local LLM configuration
LOCAL_LLM_URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL_NAME = "llama-3.2-1b-instruct"

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
    prompt = (f"Evaluate the user's pronunciation accuracy by comparing it to the expected text and phonemes. "
            f"Prioritize significant phoneme mismatches while disregarding minor variations and background noise. "
            f"Accept natural deviations as long as the speech remains intelligible.\n\n"

            f"### Input Data:\n"
            f"- **Expected Text:** {expected_text}\n"
            f"- **Transcribed Text:** {transcribed_text}\n"
            f"- **Expected Phonemes:** {expected_phonemes}\n"
            f"- **Extracted Audio Phonemes:** {audio_phonemes}\n\n")

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