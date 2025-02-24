import streamlit as st
# st.set_option("server.fileWatcherType", "none")
import os
import logging
import re
from audio_recorder import AudioRecorder
from transcription import Transcriber
from audio_to_phoneme import AudioPhonemeProcessor
from text_to_phoneme import TextToPhonemeConverter
from analysis_open_ai import evaluate_pronunciation_open_ai
from analysis_open_llm import evaluate_pronunciation_llama

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Streamlit Page Configuration
st.set_page_config(page_title="Speech Pronunciation Analysis", layout="wide")

# Custom Styling for Improved UI
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
            display: block;
            white-space: pre-line;
        }
        .section-title {
            color: #2e7d32;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# Helper Function to Create a Styled Container
def create_container(title, content):
    return f"""
        <div class="container">
            <div class="section-title">{title}</div>
            <div class="scrollable-content">
                {content}
            </div>
        </div>
    """

# Function to Format LLM Feedback for Proper Display
def format_llm_feedback(feedback):
    """Cleans and formats LLM feedback for proper HTML rendering in Streamlit."""
    feedback = re.sub(r"[*•]", "", feedback)  # Remove asterisks and bullet points
    feedback = re.sub(r"###\s*", "", feedback)  # Remove '###' headers
    feedback = feedback.replace("\n", "<br>")  # Convert newlines to HTML line breaks
    feedback = re.sub(r"</div>\s*$", "", feedback, flags=re.MULTILINE)
    return feedback.strip()

# Initialize Session State
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None

st.title("🎙️ Speech Pronunciation Analysis")

# **Editable Reference Text**
st.subheader("📖 Reference Text")
reference_text = st.text_input("Enter reference text for pronunciation comparison:", "hello good morning")

# **Audio Input Section**
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎤 Record Live Audio")
    recorder = AudioRecorder()
    if st.button("🔴 Start Recording"):
        st.write("Recording... Please wait ⏳")
        st.session_state.audio_path = recorder.record_audio(duration=10)
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

# Ensure Audio is Available
if not st.session_state.audio_path:
    st.warning("Please record or upload an audio file to proceed.")
    st.stop()

# **Model Selection with Persistence**
st.subheader("⚙️ Choose Model for Evaluation")

if "model_choice" not in st.session_state:
    st.session_state.model_choice = "OpenAI"  # Default to OpenAI

st.session_state.model_choice = st.radio("Select Model:", ["OpenAI", "Local LLM"], index=0 if st.session_state.model_choice == "OpenAI" else 1)

# **Process Audio**
try:
    # **Transcription**
    transcriber = Transcriber()
    transcript = transcriber.transcribe_audio(st.session_state.audio_path)
    if not transcript:
        st.error("No transcription available. Please try again.")
        st.stop()

    st.subheader("📝 Transcribed Text")
    st.write(f"**{transcript}**")

    # **Expected Phonemes Extraction**
    text_phoneme_converter = TextToPhonemeConverter()
    expected_phonemes = text_phoneme_converter.text_to_phonemes(reference_text)
    if not expected_phonemes:
        st.error("Could not generate expected phonemes. Please try again.")
        st.stop()

    expected_phoneme_str = {word: " ".join(phonemes) for word, phonemes in expected_phonemes.items()}

    # **Extracted Phonemes from Audio**
    phoneme_processor = AudioPhonemeProcessor()
    phoneme_timestamps = phoneme_processor.process_audio(st.session_state.audio_path)
    if not phoneme_timestamps:
        st.error("No phoneme data extracted. Please try again.")
        st.stop()

    extracted_audio_phonemes = [" | ".join(p["phonemes"]) for p in phoneme_timestamps]  # Include all top 3 phonemes

    # **Display Results in Three Columns**
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    expected_phoneme_content = "".join([
        f'<div class="item-row">🔹 <b>{word}</b>: <span class="highlight">{" ".join(phonemes)}</span></div>'
        for word, phonemes in expected_phonemes.items()
    ])

    extracted_phoneme_content = "".join([
        f'<div class="item-row">🔊 <b>{", ".join(p["phonemes"])}</b> - <span class="highlight">{p["start"]:.2f}s → {p["end"]:.2f}s</span></div>'
        for p in phoneme_timestamps
    ])

    with col1:
        st.markdown(create_container("📖 Expected Phonemes", expected_phoneme_content), unsafe_allow_html=True)
    with col2:
        st.markdown(create_container("🔊 Extracted Audio Phonemes", extracted_phoneme_content), unsafe_allow_html=True)

    # **Evaluate Pronunciation**
    evaluation_result = None
    if st.session_state.model_choice == "OpenAI":
        evaluation_result = evaluate_pronunciation_open_ai(
            transcribed_text=transcript,
            expected_text=reference_text,
            audio_phonemes=" | ".join(extracted_audio_phonemes),  # Now includes top-3 phonemes
            expected_phonemes=", ".join(expected_phoneme_str.values())
        )
    else:
        evaluation_result = evaluate_pronunciation_llama(
            transcribed_text=transcript,
            expected_text=reference_text,
            audio_phonemes=" | ".join(extracted_audio_phonemes),  # Now includes top-3 phonemes
            expected_phonemes=", ".join(expected_phoneme_str.values())
        )

    # **Display LLM Output in the Third Column**
    formatted_feedback = format_llm_feedback(evaluation_result.get("feedback", "No feedback received."))

    feedback_content = f"""
        <div class="item-row">💬 Feedback:<br>
        <span class="highlight">{formatted_feedback}</span>
        </div>
    """

    with col3:
        st.markdown(create_container("📢 Pronunciation Feedback", feedback_content), unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ An error occurred: {e}")