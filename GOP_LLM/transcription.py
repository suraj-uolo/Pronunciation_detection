import logging
import speech_recognition as sr

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Transcriber:
    def __init__(self, verbose: bool = True, engine="google"):
        """Initialize Transcriber with optional verbose mode and engine."""
        self.recognizer = sr.Recognizer()
        self.verbose = verbose
        self.engine = engine  # Allows future extensions to other APIs
        
        # Enhancements for better recognition
        self.recognizer.energy_threshold = 100  # Lower threshold for faint speech
        self.recognizer.dynamic_energy_threshold = True  # Adapt to background noise
        self.recognizer.dynamic_energy_adjustment_ratio = 1.8  # More sensitivity
        self.recognizer.pause_threshold = 0.5  # Reduce delay between words

    def transcribe_audio(self, audio_path: str, verbose: bool = None) -> str:
        """Transcribes audio with enhanced sensitivity to faint and mispronounced words."""
        if verbose is None:
            verbose = self.verbose  

        try:
            with sr.AudioFile(audio_path) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Noise calibration
                audio = self.recognizer.record(source)  

                if not audio.frame_data:  
                    logging.warning("⚠️ Empty audio file detected.")
                    return ""

                # Using Google Speech API with `show_all=True` to get multiple possible transcriptions
                if self.engine == "google":
                    results = self.recognizer.recognize_google(audio, show_all=True)
                    if verbose:
                        logging.info(f"✅ Raw Recognition Output: {results}")

                    if isinstance(results, dict) and "alternative" in results:
                        transcript = results["alternative"][0]["transcript"]
                    else:
                        transcript = results if isinstance(results, str) else ""

                elif self.engine == "sphinx":
                    transcript = self.recognizer.recognize_sphinx(audio)

                else:
                    logging.error(f"❌ Unsupported engine: {self.engine}")
                    return ""

                if verbose:
                    logging.info(f"✅ Final Transcription: {transcript}")

                return results, transcript

        except sr.UnknownValueError:
            logging.warning("❌ Could not understand the audio.")
            return "ERROR: Unable to recognize speech."
        except sr.RequestError as e:
            logging.error(f"❌ API request error: {e}")
            return f"ERROR: API request failed - {e}"
        except Exception as e:
            logging.error(f"⚠️ Unexpected error: {e}")
            return f"ERROR: Unexpected issue - {e}"

# Example Usage:
transcriber = Transcriber()
result = transcriber.transcribe_audio("cleaned_recordings/cleaned_recording_20250316_173609.wav")
