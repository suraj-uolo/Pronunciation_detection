import speech_recognition as sr

def test_microphone():
    recognizer = sr.Recognizer()

    # Check if microphone is available
    try:
        with sr.Microphone() as source:
            print("Adjusting for ambient noise... Please wait.")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print("Listening... Please say something.")

            audio = recognizer.listen(source, timeout=5)
            print("Processing...")

            # Attempt to recognize speech
            try:
                text = recognizer.recognize_google(audio)
                print(f"Microphone is working! You said: {text}")
            except sr.UnknownValueError:
                print("Microphone is working, but speech was not recognized.")
            except sr.RequestError:
                print("Microphone detected, but API error occurred.")

    except OSError:
        print("No microphone detected. Please check your audio settings.")

# Run the microphone test
test_microphone()
