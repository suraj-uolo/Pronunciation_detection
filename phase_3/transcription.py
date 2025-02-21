import speech_recognition as sr

class Transcriber:
    def __init__(self, verbose: bool = True):
        """Initialize Transcriber with optional verbose mode."""
        self.recognizer = sr.Recognizer()
        self.verbose = verbose  # Control printing behavior

    def transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio using Google Speech Recognition."""
        try:
            with sr.AudioFile(audio_path) as source:
                audio = self.recognizer.record(source)
                transcript = self.recognizer.recognize_google(audio)
                
                if self.verbose:
                    print(f"✅ Transcription: {transcript}")
                
                return transcript

        except (sr.UnknownValueError, sr.RequestError) as e:
            error_message = f"❌ Error: {e}" if isinstance(e, sr.RequestError) else "❌ Could not understand the audio."
            
            if self.verbose:
                print(error_message)
            
            return ""

        except Exception as e:
            if self.verbose:
                print(f"⚠️ Unexpected error: {e}")
            return ""