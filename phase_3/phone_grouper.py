from alignment import ForcedAligner
from audio_to_phoneme import process_audio

class PhonemeGrouper:
    def __init__(self, mfa_model="english_mfa", dict_path = r"C:\Users\suraj\.conda\envs\mfa\Lib\site-packages\montreal_forced_aligner\tests\data\dictionaries\english_us_mfa_reduced.dict"):
        self.aligner = ForcedAligner(mfa_model, dict_path)

    def group_phonemes(self, audio_path: str, transcript: str) -> list:
        """Groups phonemes based on word timestamps from forced alignment."""
        
        # Step 1: Perform forced alignment to get word timestamps
        alignment_data = self.aligner.force_align_audio(audio_path, transcript)
        if not alignment_data:
            print("❌ Alignment failed, cannot group phonemes.")
            return []

        word_timestamps = alignment_data['words']
#commet
        # Step 2: Extract phonemes from audio
        phoneme_timestamps = process_audio(audio_path)

        # Step 3: Group phonemes based on word timestamps
        grouped_phonemes = []
        for word in word_timestamps:
            word_start = word["start"]
            word_end = word["end"]

            phonemes_for_word = [
                phoneme for phoneme in phoneme_timestamps
                if word_start <= phoneme["start"] < word_end
            ]

            grouped_phonemes.append({
                "word": word["word"],
                "phonemes": phonemes_for_word
            })

        return grouped_phonemes