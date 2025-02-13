from allosaurus.app import read_recognizer
#commet
def process_audio(filepath: str):
    """Process the recorded audio file and return phoneme data."""
    try:
        model = read_recognizer("eng2102")
        result = model.recognize(filepath, timestamp=True)

        phoneme_data = []
        for line in result.strip().split("\n"):
            parts = line.split()
            if len(parts) == 3:
                start_time = float(parts[0])
                duration = float(parts[1])
                phoneme = parts[2]
                phoneme_data.append({
                    "start": start_time,
                    "end": start_time + duration,
                    "phoneme": phoneme
                })

        print("\n🔍 Extracted Phoneme Data:")
        for phoneme in phoneme_data:
            print(f"  🕒 {phoneme['start']:.2f} - {phoneme['end']:.2f} | 🔤 {phoneme['phoneme']}")

        return phoneme_data

    except Exception as e:
        print(f"❌ Error processing audio: {e}")
        raise