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
    prompt = (
        "Compare the user's pronunciation with the expected phonemes. Follow these steps:\n"
        "1. Verify if the transcribed text matches the expected text.\n"
        "2. For matching words, compare their phonemes. If words are missing in the transcription, check if their phonemes appear in the audio.\n"
        "3. For each expected phoneme, identify three probable phonemes list from the audio.\n"
        "4. A phoneme is correct if it appears in any of the three probable phonemes.\n"
        "5. Do not miss any phonemes in the audio if it is present, Recheck present audio phonemes if there is trancription but no or less matched phonemes.\n"
        "6. Calculate the match percentage per word based on  number of correct phonemes per word (ignore stress markers).\n"
        "7. Provide a clear comparison per word, including:\n"
        "   - Expected phonemes\n"
        "   - Detected phonemes\n"
        "   - Percentage match\n"
        "8. If a word has a 0% match, recheck its phonemes again.\n"
        f"Expected Text: `{expected_text}`\n"
        f"Transcribed Text: `{transcribed_text}`\n"
        f"Expected Phonemes: `{expected_phonemes}`\n"
        f"Audio Phonemes: `{audio_phonemes}`"
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