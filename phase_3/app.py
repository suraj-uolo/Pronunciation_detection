import streamlit as st
import os
from audio_recorder import AudioRecorder
from transcription import Transcriber
from alignment import ForcedAligner
from audio_to_phoneme import process_audio
from text_phoneme_extraction import text_to_phonemes
from phone_grouper import PhonemeGrouper
from compare_visualize import compare_phonemes, visualize_phoneme_comparison
from sequence_matcher import find_phoneme_matches

# Constants
MFA_DICTIONARY_PATH = r"C:\Users\suraj\.conda\envs\mfa\Lib\site-packages\montreal_forced_aligner\tests\data\dictionaries\english_us_mfa_reduced.dict"
MFA_MODEL = "english_mfa"

# Set Streamlit Page Configuration
st.set_page_config(page_title="Speech Pronunciation Analysis", layout="wide")

# Custom CSS for consistent styling
st.markdown("""
    <style>
        .container {
            padding: 1rem;
            border-radius: 0.5rem;
            background: #f8f9fa;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        .scrollable-content {
            max-height: 300px;
            overflow-y: auto;
            padding: 0.5rem;
        }
        .item-row {
            padding: 0.5rem;
            border-bottom: 1px solid #dee2e6;
            margin: 0.25rem 0;
        }
        .highlight {
            background: #e9ecef;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
        }
        .section-title {
            color: #2e7d32;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

def create_container(title, content):
    """Helper function to create a styled container"""
    return f"""
        <div class="container">
            <div class="section-title">{title}</div>
            <div class="scrollable-content">
                {content}
            </div>
        </div>
    """

def main():
    st.title("🎙️ Speech Pronunciation Analysis")

    # Initialize session state if needed
    if 'audio_path' not in st.session_state:
        st.session_state.audio_path = None

    # Audio Input Section
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎤 Record Live Audio")
        recorder = AudioRecorder()
        if st.button("🔴 Start Recording"):
            st.write("Recording... Please wait ⏳")
            st.session_state.audio_path = recorder.record_audio(duration=4)
            st.success("Recording Complete ✅")
            st.audio(st.session_state.audio_path, format="audio/wav")

    with col2:
        st.subheader("📂 Upload an Audio File")
        uploaded_file = st.file_uploader("Choose a file", type=["wav", "mp3"])
        if uploaded_file:
            file_path = "temp_audio.wav"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state.audio_path = file_path
            st.audio(st.session_state.audio_path, format="audio/wav")

    if not st.session_state.audio_path:
        st.warning("Please record or upload an audio file to proceed.")
        return

    # Process Audio and Generate Data
    try:
        # Transcription
        transcriber = Transcriber()
        transcript = transcriber.transcribe_audio(st.session_state.audio_path)
        if not transcript:
            st.error("No transcription available. Please try again.")
            return

        st.subheader("📝 Transcribed Text")
        st.write(f"**{transcript}**")

        # Forced Alignment
        aligner = ForcedAligner(mfa_model=MFA_MODEL, dict_path=MFA_DICTIONARY_PATH)
        alignment_data = aligner.force_align_audio(st.session_state.audio_path, transcript)
        if not alignment_data:
            st.error("Forced alignment failed. Please try again.")
            return

        word_timestamps = alignment_data['words']
        
        # Extract Phonemes
        phoneme_timestamps = process_audio(st.session_state.audio_path)
        if not phoneme_timestamps:
            st.error("Phoneme extraction failed. Please try again.")
            return

        # Get Expected Phonemes
        expected_phonemes = text_to_phonemes(transcript)
        if not expected_phonemes:
            st.error("Could not generate expected phonemes. Please try again.")
            return

        # Display Results in Three Column Layout
        st.markdown("---")
        
        # First Row
        col1, col2, col3 = st.columns(3)

        # Build content for first row
        forced_alignment_content = "".join([
            f'<div class="item-row">🔹 <b>{word["word"]}</b> - '
            f'<span class="highlight">{word["start"]:.2f}s</span> to '
            f'<span class="highlight">{word["end"]:.2f}s</span></div>'
            for word in word_timestamps
        ])

        phoneme_content = "".join([
            f'<div class="item-row">🔊 <b>{p["phoneme"]}</b> - '
            f'<span class="highlight">{p["start"]:.2f}s → {p["end"]:.2f}s</span></div>'
            for p in phoneme_timestamps
        ])

        expected_phonemes_content = "".join([
            f'<div class="item-row">🔹 <b>{word}</b>: '
            f'<span class="highlight">{" ".join(phonemes)}</span></div>'
            for word, phonemes in expected_phonemes.items()
        ])

        with col1:
            st.markdown(create_container("⏳ Forced Alignment", forced_alignment_content), unsafe_allow_html=True)
        with col2:
            st.markdown(create_container("🎵 Extracted Phonemes", phoneme_content), unsafe_allow_html=True)
        with col3:
            st.markdown(create_container("📖 Expected Phonemes", expected_phonemes_content), unsafe_allow_html=True)

        # Second Row
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        # Process data for second row
        phoneme_grouper = PhonemeGrouper(mfa_model=MFA_MODEL, dict_path=MFA_DICTIONARY_PATH)
        grouped_phonemes = phoneme_grouper.group_phonemes(st.session_state.audio_path, transcript)

        # Build content for grouped phonemes
        grouped_content = "".join([
            f'<div class="item-row">📌 <b>{group["word"]}</b>: '
            f'<span class="highlight">{" ".join([p["phoneme"] for p in group["phonemes"]])}</span></div>'
            for group in grouped_phonemes
        ])

        # Build pronunciation analysis content
        analysis_content = ""
        actual_phoneme_map = {}

        for word_group in word_timestamps:
            word = word_group['word']
            word_start = word_group['start']
            word_end = word_group['end']
            
            # Get phonemes within the word's time window
            word_phonemes = [
                p['phoneme'] for p in phoneme_timestamps 
                if word_start <= p['start'] and p['end'] <= word_end
            ]
            
            actual_phoneme_map[word] = ' '.join(word_phonemes) if word_phonemes else "No phonemes detected"
            expected = expected_phonemes.get(word, "N/A")
            
            # Calculate match percentage
            expected_set = set(expected.split()) if expected != "N/A" else set()
            actual_set = set(word_phonemes)
            match_percentage = (len(expected_set & actual_set) / max(len(expected_set), len(actual_set)) * 100) if actual_set else 0
            match_status = "✅" if match_percentage > 70 else "⚠️"
            
            analysis_content += f"""
                <div class="item-row">
                    🔍 <b>{word}</b> {match_status}<br>
                    Actual: <span class="highlight">{actual_phoneme_map[word]}</span><br>
                    Expected: <span class="highlight">{expected}</span><br>
                    Match: <span class="highlight">{match_percentage:.1f}%</span>
                </div>
            """


        # Prepare comparison visualization
        comparison_results = compare_phonemes(actual_phoneme_map, expected_phonemes)
        visualization = visualize_phoneme_comparison(comparison_results)

        # Sequence matching
        transcribed_text = transcript.split()
        timestamps = {word_info['word']: (word_info['start'], word_info['end']) 
                     for word_info in word_timestamps}
        expected_text = [(word, expected_phonemes[word]) 
                        for word in transcribed_text if word in expected_phonemes]

        sequence_match_results = find_phoneme_matches(
            expected_text=expected_text,
            transcribed_text=transcribed_text,
            timestamps=timestamps,
            phoneme_timestamps=phoneme_timestamps
        )

        # Build visualization content
        visualization_content = "".join([
            f'<div class="item-row">🟢 <b>{word}</b><br>'
            f'Match: <span class="highlight">{result["match_percentage"]:.2f}%</span><br>'
            f'Matched: <span class="highlight">{result["matched_phonemes"]}</span><br>'
            f'Details: <span class="highlight">{result["details"]}</span></div>'
            for word, result in sequence_match_results.items()
        ])

        with col1:
            st.markdown(create_container("🗂️ Grouped Phonemes", grouped_content), unsafe_allow_html=True)
        with col2:
            st.markdown("<h3>📊 Pronunciation Analysis</h3>", unsafe_allow_html=True)
            st.markdown(analysis_content, unsafe_allow_html=True)
        with col3:
            st.markdown(create_container("📈 Comparison Results", visualization_content), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return

if __name__ == "__main__":
    main()