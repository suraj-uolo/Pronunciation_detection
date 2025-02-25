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
    prompt = (f"Compare the user's pronunciation with the expected phonemes."
              f"1. First, check if the transcribed text matches the expected text."  
              f"2. For words that match, compare their phonemes. Also Check if missing trancripted words have some phonemes in the audio."
              f"3. Each expected phoneme there is a list of three probable phonemes from the audio."  
              f"4. A phoneme is considered correct if it appears in any of the three probable phonemes."  
              f"5. Calculate the match percentage per word based on the number of correct phonemes. Ignore stress markers."  
              f"6. Provide a clear comparison per word, including expected phonemes, detected phonemes, and percentage match."  
              f" 7. Focus only on meaningful mismatches—skip redundant details."  
              f"Return only the phoneme comparison and percentage match per word—nothing else."
              f"Expected Text:`{expected_text}`"
              f"Transcribed Text: `{transcribed_text}`"
              f"Expected Phonemes: `{expected_phonemes}`" 
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