import logging
import speech_recognition as sr

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Transcriber:
    def __init__(self, verbose: bool = True, engine="google"):
        """Initialize Transcriber with optional verbose mode and engine."""
        self.recognizer = sr.Recognizer()
        self.verbose = verbose
        self.engine = engine  # Allows future extensions to other APIs

    def transcribe_audio(self, audio_path: str) -> str:
        """Transcribes audio using Google Speech Recognition (or other engines)."""
        try:
            with sr.AudioFile(audio_path) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(source)
                transcript = self.recognizer.recognize_google(audio)

                if self.verbose:
                    logging.info(f"✅ Transcription: {transcript}")
                return transcript

        except sr.UnknownValueError:
            logging.warning("❌ Could not understand the audio.")
            return ""
        except sr.RequestError as e:
            logging.error(f"❌ API request error: {e}")
            return ""
        except Exception as e:
            logging.error(f"⚠️ Unexpected error: {e}")
            return ""