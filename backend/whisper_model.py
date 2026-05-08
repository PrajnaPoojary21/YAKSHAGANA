import os
import librosa
import soundfile as sf
import numpy as np
from scipy.signal import butter, filtfilt
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def preprocess_audio(input_path):
    print(f"[PREPROCESS] Loading: {input_path}")
    y, sr = librosa.load(input_path, sr=16000, mono=True)

    print(f"[PREPROCESS] Duration: {len(y)/sr:.2f}s | Sample rate: {sr}Hz")

    if len(y) == 0:
        raise ValueError("Audio file is empty")

    # High-pass filter — removes chende/maddale low-frequency percussion
    def highpass_filter(audio, cutoff=150, fs=16000, order=4):
        nyq = fs / 2
        b, a = butter(order, cutoff / nyq, btype='high', analog=False)
        return filtfilt(b, a, audio)

    y = highpass_filter(y)

    # Normalize
    max_val = np.max(np.abs(y))
    if max_val > 0:
        y = y / max_val * 0.95
    else:
        raise ValueError("Audio is completely silent after filtering")

    cleaned_path = os.path.splitext(input_path)[0] + "_cleaned.wav"
    sf.write(cleaned_path, y, sr)
    print(f"[PREPROCESS] Cleaned audio saved: {cleaned_path}")

    return cleaned_path


def transcribe_audio(file_path):
    cleaned_path = None
    try:
        cleaned_path = preprocess_audio(file_path)

        print("[TRANSCRIBE] Sending to Groq Whisper large-v3...")
        with open(cleaned_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(cleaned_path), audio_file.read()),
                model="whisper-large-v3",
                language="kn",
                response_format="verbose_json",
                prompt="ಯಕ್ಷಗಾನ ಭಾಗವತಿಕೆ ಪದ್ಯ"
            )

        final_text = transcription.text.strip()
        print(f"[TRANSCRIBE] FINAL TEXT: '{final_text}'")
        return final_text

    finally:
        if cleaned_path and os.path.exists(cleaned_path):
            os.remove(cleaned_path)