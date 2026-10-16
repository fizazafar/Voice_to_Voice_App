# Voice-to-Voice Assistant

A simple Streamlit voice assistant using:

- **Speech-to-text:** OpenAI Whisper (`base`, downloaded at runtime)
- **LLM:** Groq API (`openai/gpt-oss-120b`, as used in the supplied Colab notebook)
- **Text-to-speech:** Google Text-to-Speech (`gTTS`)
- **UI:** Streamlit

## Run locally

1. Install Python 3.10 or newer and FFmpeg.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set your Groq key as an environment variable, or create `.streamlit/secrets.toml` using `.streamlit/secrets.toml.example` as a template.

   Linux/macOS:

   ```bash
   export GROQ_API_KEY="your-key"
   streamlit run app.py
   ```

   Windows PowerShell:

   ```powershell
   $env:GROQ_API_KEY="your-key"
   streamlit run app.py
   ```

## Deploy to Streamlit Community Cloud

1. Upload `app.py`, `requirements.txt`, `packages.txt`, `README.md`, and `.gitignore` to a GitHub repository.
2. In Streamlit Community Cloud, create an app from that repository and select `app.py`.
3. Open the app's **Settings → Secrets** and add:

   ```toml
   GROQ_API_KEY = "your-real-groq-api-key"
   ```

4. Save and redeploy.

`packages.txt` asks the deployment environment to install FFmpeg, which Whisper needs for audio decoding.

## Notes

- The Whisper `base` model weights download the first time the app starts. This may make the first startup slow and uses disk space.
- Streamlit Community Cloud resources are limited; Whisper transcription can be slow on CPU. If performance is insufficient, consider a hosted speech-to-text API or a smaller/faster local transcription setup.
- `gTTS` calls Google's online TTS service, so internet access is required. It is not an offline TTS engine.
- Groq model availability and free-tier limits can change. If the model ID in `app.py` is unavailable for your account, replace it with a currently supported model ID from Groq's model documentation.
- Do not commit API keys, audio recordings, or downloaded model weights to GitHub.
