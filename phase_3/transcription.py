import speech_recognition as sr

class Transcriber:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio using Google Speech Recognition."""
        try:
            with sr.AudioFile(audio_path) as source:
                audio = self.recognizer.record(source)
                transcript = self.recognizer.recognize_google(audio)
                print(f"✅ Transcription: {transcript}")
                return transcript
        except sr.UnknownValueError:
            print("❌ Could not understand the audio.")
            return ""
        except sr.RequestError as e:
            print(f"❌ Could not request results from Google Speech Recognition service; {e}")
            return ""
        #commet