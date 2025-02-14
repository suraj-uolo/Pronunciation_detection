import os
import shutil
import subprocess
from praatio import textgrid
class ForcedAligner:
    def __init__(self, mfa_model="english_mfa", dict_path=r"C:\Users\suraj\.conda\envs\mfa\Lib\site-packages\montreal_forced_aligner\tests\data\dictionaries\english_us_mfa_reduced.dict", recordings_dir="recordings"):
        self.mfa_model = mfa_model
        self.dict_path = dict_path
        self.recordings_dir = recordings_dir
        self.textgrid_dir = os.path.join(self.recordings_dir, "textgrids")
        os.makedirs(self.textgrid_dir, exist_ok=True)

    def force_align_audio(self, audio_path: str, transcript: str) -> dict:
        """Perform forced alignment using MFA."""
        corpus_dir = os.path.join(self.recordings_dir, 'corpus')
        os.makedirs(corpus_dir, exist_ok=True)

        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        corpus_audio = os.path.join(corpus_dir, f"{base_name}.wav")
        shutil.copy2(audio_path, corpus_audio)

        lab_path = os.path.join(corpus_dir, f"{base_name}.lab")
        with open(lab_path, 'w', encoding='utf-8') as f:
            f.write(transcript.strip())

        try:
            mfa_command = ["mfa", "align", corpus_dir, self.dict_path, self.mfa_model, self.textgrid_dir, "--clean"]
            result = subprocess.run(mfa_command, capture_output=True, text=True, encoding='utf-8', errors='ignore')

            # Debugging: Log outputs
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")

            if result.returncode != 0:
                print(f"❌ MFA Error: {result.stderr}")
                return None

            textgrid_path = os.path.join(self.textgrid_dir, f"{base_name}.TextGrid")
            return self._parse_textgrid(textgrid_path) if os.path.exists(textgrid_path) else None

        except Exception as e:
            print(f"❌ Alignment error: {e}")
            return None

    def _parse_textgrid(self, textgrid_path: str) -> dict:
        """Parse MFA's TextGrid output and return word/phone alignments."""
        tg = textgrid.openTextgrid(textgrid_path, includeEmptyIntervals=True)

        alignment_data = {'words': [], 'phones': []}
        words_tier = tg.getTier('words')
        phones_tier = tg.getTier('phones')

        print(f"Parsed Words Tier: {words_tier.entries}")
        print(f"Parsed Phones Tier: {phones_tier.entries}")

        for interval in words_tier.entries:
            if interval.label:
                alignment_data['words'].append({
                    'word': interval.label,
                    'start': interval.start,
                    'end': interval.end,
                    'duration': interval.end - interval.start
                })

        for interval in phones_tier.entries:
            if interval.label:
                alignment_data['phones'].append({
                    'phone': interval.label,
                    'start': interval.start,
                    'end': interval.end,
                    'duration': interval.end - interval.start
                })

        return alignment_data
    
if __name__ == "__main__":
    aligner = ForcedAligner()
    audio_path = r"C:\Users\suraj\Desktop\Pronunciation_detection\recordings\recording_20250206_160912.wav"
    transcript = "this is a sample sentence"
    aligner.force_align_audio(audio_path, transcript)
