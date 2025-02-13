import speech_recognition as sr
import pyttsx3
import nltk
from nltk.corpus import cmudict
import difflib

class PronunciationFeedbackSystem:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.CMUdict = cmudict.dict()  # Load CMU Pronouncing Dictionary
        self.engine = pyttsx3.init()

        # Set voice (Choose a default available voice)
        voices = self.engine.getProperty('voices')
        if voices:
            self.engine.setProperty('voice', voices[0].id)  # Use first available voice

    def text_to_speech(self, text):
        """Convert text to speech."""
        self.engine.say(text)
        self.engine.runAndWait()

    def capture_audio(self):
        """Capture audio input from the microphone once."""
        with self.microphone as source:
            print("\n[Step 1] Listening... Speak now.")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=5)
                transcript = self.recognizer.recognize_google(audio, language='en-US')
                print(f"[Step 2] You said: {transcript}")
                return transcript
            except sr.UnknownValueError:
                print("[Error] Could not understand audio.")
                return None
            except sr.RequestError:
                print("[Error] Speech recognition service is unavailable.")
                return None

    def detect_pronunciation_errors(self, word):
        """Check if the word exists in CMUdict and return phoneme breakdown."""
        word = word.lower()  # CMUdict stores words in lowercase
        if word in self.CMUdict:
            return self.CMUdict[word][0]  # First pronunciation option
        else:
            return None

    def compare_pronunciation(self, word):
        """Compare user's pronunciation with correct phonemes."""
        correct_phonemes = self.detect_pronunciation_errors(word)
        if correct_phonemes is None:
            return None, f"[Error] '{word}' not found in CMU Dictionary."

        return correct_phonemes, f"✅ Correct phoneme breakdown: {' '.join(correct_phonemes)}"

    def process_sentence(self, sentence):
        """Break sentence into words, check pronunciation for each, and give a report."""
        words = sentence.split()
        overall_report = []

        for word in words:
            correct_phonemes, feedback = self.compare_pronunciation(word)
            if correct_phonemes is None:
                overall_report.append(f"❌ '{word}' not found in dictionary.")
                continue

            spoken_phonemes = self.detect_pronunciation_errors(word)
            if spoken_phonemes == correct_phonemes:
                overall_report.append(f"✅ '{word}' pronounced correctly.")
            else:
                # Highlight the mispronounced phonemes
                diff = list(difflib.ndiff(spoken_phonemes, correct_phonemes))
                incorrect_parts = [d[2:] for d in diff if d.startswith('-')]
                correct_parts = [d[2:] for d in diff if d.startswith('+')]

                report = f"⚠️ '{word}' mispronounced.\n"
                report += f"   ❌ Incorrect: {' '.join(incorrect_parts)}\n"
                report += f"   ✅ Correct: {' '.join(correct_parts)}"
                overall_report.append(report)

        full_report = "\n".join(overall_report)
        print("\n[Step 3] Pronunciation Report:")
        print(full_report)

        self.text_to_speech("Pronunciation report generated. Check the screen for details.")

    def run_once(self):
        """Take input once and analyze pronunciation for the entire sentence."""
        print("\n[Speak a full sentence to analyze pronunciation]")
        sentence = self.capture_audio()
        if sentence:
            self.process_sentence(sentence)
        else:
            print("[Error] No valid input received.")

# Run the pronunciation feedback system once
if __name__ == "__main__":
    nltk.download('cmudict')  # Ensure CMUdict is available
    system = PronunciationFeedbackSystem()
    system.run_once()