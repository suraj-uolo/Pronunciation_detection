import logging
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# OpenAI model configuration
OPENAI_MODEL = "gpt-4o-mini-2024-07-18"

def evaluate_pronunciation_open_ai(transcribed_text: str, expected_text: str, audio_phonemes: str, expected_phonemes: str):
    """
    Evaluates pronunciation by comparing transcribed phonemes with expected phonemes.
    
    Args:
        transcribed_text (str): The user's spoken text after transcription.
        expected_text (str): The correct expected text.
        audio_phonemes (str):Top 3 probable Phonemes for each phoneme extracted from the user's speech.
        expected_phonemes (str): The correct phonemes for comparison.

    Returns:
        dict: Contains AI-generated pronunciation feedback and token usage details.
    """
    prompt = (f"Compare the user's pronunciation with the expected text and phonemes."
              f"Check first if the trancribed text matches the expected text. Then only focus on phoneme comparison for matched words."
              f"A word is considered correctly pronounced if any of the top three probable phonemes for each expected phoneme match."
              f"Ignore minor variations, background noise, and natural deviations (e.g., 'J' for 'I')."
              f"Focus on meaningful mismatches. Provide a crisp comparison per word with a phoneme and percentage match."
              f"Output only the phoneme comparison and percentage match per word—nothing else."
              f"Expected Text: `{expected_text}` "
              f"Transcribed Text: `{transcribed_text}` "
              f"Expected Phonemes: `{expected_phonemes}` "
              f"Audio Phonemes: `{audio_phonemes}` "
            )   

    try:
        logging.info("Sending request to OpenAI...")
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a pronunciation coach."},
                {"role": "user", "content": prompt}
            ]
        )

        feedback = response.choices[0].message.content
        usage = response.usage  # Extract token usage details

        logging.info(f"Tokens Used - Input: {usage.prompt_tokens}, Output: {usage.completion_tokens}, Total: {usage.total_tokens}")

        return {
            "feedback": feedback,
            "tokens_used": {
                "input_tokens": usage.prompt_tokens,
                "output_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            }
        }

    except Exception as e:
        logging.error(f"Error in OpenAI API call: {e}")
        return {"error": "Failed to process pronunciation evaluation."}