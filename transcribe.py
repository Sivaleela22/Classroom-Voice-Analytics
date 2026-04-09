import os
from groq import Groq

GROQ_API_KEY = " "  # ← Your Groq API key

client = Groq(api_key=GROQ_API_KEY)


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe a classroom audio file using Groq's Whisper large-v3 model.

    Supports Hindi (language='hi'). Returns plain text transcript.
    Returns an error string starting with 'ERROR:' on failure.
    """
    if not os.path.exists(audio_path):
        return f"ERROR: File not found – {audio_path}"
    if os.path.getsize(audio_path) == 0:
        return "ERROR: Audio file is empty."
    try:
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(audio_path), audio_file.read()),
                model="whisper-large-v3",
                language="hi",
                response_format="text",
                temperature=0.0
            )
        return transcription.strip() if transcription else "ERROR: Empty transcript."
    except Exception as e:
        return f"ERROR: {str(e)}"