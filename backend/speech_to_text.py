# from faster_whisper import WhisperModel
from backend.config import settings
from backend.logger import get_logger

logger = get_logger()

# Load model once
model = WhisperModel(
    settings.MODEL_SIZE, 
    compute_type="int8"
)

def transcribe_audio(file_path: str):
    try:
        logger.info(f"Transcribing: {file_path}")

        segments, info = model.transcribe(
            file_path,
            beam_size=5,
            vad_filter=True,              # 🔥 removes silence/music
            vad_parameters=dict(min_silence_duration_ms=500)
        )

        full_text = []
        valid_probs = []

        for segment in segments:
            text = segment.text.strip()

            # 🔥 Skip garbage / very short text
            if len(text) < 3:
                continue

            full_text.append(text)

            # Convert logprob → usable confidence
            prob = pow(10, segment.avg_logprob)
            valid_probs.append(prob)

        final_text = " ".join(full_text)

        # Average confidence
        confidence = (
            sum(valid_probs) / len(valid_probs)
            if valid_probs else 0
        )

        logger.info(f"Transcription done | Confidence: {confidence}")

        return {
            "text": final_text,
            "confidence": float(confidence)
        }

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise