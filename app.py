import os
import tempfile
from pathlib import Path

import streamlit as st
import whisper
from groq import Groq
from gtts import gTTS

st.set_page_config(page_title="Voice-to-Voice Assistant", page_icon="🎙️", layout="centered")
st.title("🎙️ Voice-to-Voice Assistant")
st.caption("Whisper STT · Groq LLM · Google Text-to-Speech")

# Read the key from Streamlit secrets first, then environment variables.
def get_saved_api_key():
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY", "")

saved_key = get_saved_api_key()
groq_api_key = saved_key or st.text_input(
    "Groq API key", type="password", help="For deployment, set GROQ_API_KEY in Streamlit Secrets."
)

@st.cache_resource
def load_whisper_model():
    # Downloads the Whisper 'base' weights on first run.
    return whisper.load_model("base")

with st.spinner("Loading Whisper model (first startup may take a while)…"):
    whisper_model = load_whisper_model()

st.subheader("1. Provide audio")
input_method = st.radio("Input method", ["Record audio", "Upload audio file"], horizontal=True)

if input_method == "Record audio":
    audio_source = st.audio_input("Record your voice")
else:
    audio_source = st.file_uploader(
        "Upload an audio file",
        type=["wav", "mp3", "m4a", "ogg", "webm", "mp4", "mpeg", "mpga"],
    )

if audio_source is not None:
    st.audio(audio_source)

    if st.button("Transcribe and respond", type="primary", disabled=not bool(groq_api_key)):
        input_path = None
        output_path = None
        try:
            client = Groq(api_key=groq_api_key)
            suffix = Path(getattr(audio_source, "name", "recording.wav")).suffix or ".wav"

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as input_file:
                input_file.write(audio_source.getvalue())
                input_path = input_file.name

            with st.spinner("Transcribing your audio…"):
                transcription = whisper_model.transcribe(input_path)
                user_text = transcription.get("text", "").strip()

            if not user_text:
                st.warning("I couldn't detect any speech. Please try recording again.")
                st.stop()

            st.subheader("2. Transcription")
            st.write(user_text)

            with st.spinner("Generating a response with Groq…"):
                completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a helpful AI voice assistant. Give clear, concise answers suitable for spoken conversation."},
                        {"role": "user", "content": user_text},
                    ],
                    model="openai/gpt-oss-120b",
                )
                response_text = completion.choices[0].message.content or ""

            st.subheader("3. Assistant response")
            st.write(response_text)

            with st.spinner("Generating speech with Google TTS…"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as output_file:
                    output_path = output_file.name
                gTTS(text=response_text, lang="en").save(output_path)

            st.subheader("4. Voice response")
            with open(output_path, "rb") as audio_file:
                st.audio(audio_file.read(), format="audio/mpeg")

        except Exception as exc:
            st.error(f"Something went wrong: {exc}")
            st.info("Check that your Groq API key is valid, the selected Groq model is available to your account, and the app has internet access.")
        finally:
            for path in (input_path, output_path):
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except OSError:
                        pass
elif not groq_api_key:
    st.info("Enter a Groq API key above, or configure GROQ_API_KEY in Streamlit Community Cloud → App settings → Secrets.")
