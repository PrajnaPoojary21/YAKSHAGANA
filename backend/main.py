# from fastapi import FastAPI, UploadFile, File, HTTPException
# import os
# import shutil

# from backend.speech_to_text import transcribe_audio
# from backend.text_processing import clean_text
# from backend.story_generator import generate_story, correct_transcription
# from backend.evaluation import evaluate_story
# from backend.config import settings
# from backend.logger import get_logger

# app = FastAPI()
# logger = get_logger()

# os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
# os.makedirs(settings.OUTPUT_DIR, exist_ok=True)


# @app.post("/upload")
# async def upload_file(file: UploadFile = File(...)):
#     if not file.filename.endswith((".mp3", ".wav")):
#         raise HTTPException(status_code=400, detail="Invalid file type")

#     file_path = os.path.join(settings.UPLOAD_DIR, file.filename)

#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     return {"file_path": file_path}


# @app.post("/process")
# async def process_audio(file_path: str):
#     try:
#         if not os.path.exists(file_path):
#             raise HTTPException(status_code=404, detail="File not found")

#         # Step 1: Transcription
#         result = transcribe_audio(file_path)
#         text = result["text"]
#         confidence = result["confidence"]

#         # Step 2: Correction loop
#         if confidence < 0.6:
#             text = correct_transcription(text)

#         # Step 3: Cleaning
#         cleaned = clean_text(text)

#         # Step 4: Story generation
#         story = generate_story(cleaned)

#         # Step 5: Evaluation
#         evaluation = evaluate_story(story)

#         return {
#             "transcription": text,
#             "confidence": confidence,
#             "clean_text": cleaned,
#             "story": story,
#             "score": evaluation["score"],
#             "feedback": evaluation["feedback"]
#         }

#     except Exception as e:
#         logger.error(f"Processing failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))
from fastapi import FastAPI, UploadFile, File, HTTPException
import os
import shutil

from backend.speech_to_text import transcribe_audio
from backend.text_processing import clean_text
from backend.story_generator import generate_story, correct_transcription
from backend.evaluation import evaluate_story
from backend.config import settings
from backend.logger import get_logger

app = FastAPI()
logger = get_logger()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)


# =========================
# Upload Endpoint
# =========================
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith((".mp3", ".wav")):
            raise HTTPException(status_code=400, detail="Invalid file type")

        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"File uploaded: {file_path}")

        return {"file_path": file_path}

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# Process Endpoint
# =========================
@app.post("/process")
async def process_audio(file_path: str):
    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        logger.info("Starting transcription...")

        # Step 1: Transcription
        result = transcribe_audio(file_path)
        text = result.get("text", "")
        confidence = result.get("confidence", 0)

        logger.info(f"Transcription complete. Confidence: {confidence}")

        # Step 2: Correction (only if low confidence)
        if confidence < 0.6:
            try:
                text = correct_transcription(text)
                logger.info("Applied correction to transcription")
            except Exception as e:
                logger.warning(f"Correction failed: {e}")

        # Step 3: Cleaning
        cleaned = clean_text(text)

        # =========================
        # Step 4: Story generation (SAFE)
        # =========================
        try:
            story = generate_story(cleaned)
        except Exception as e:
            logger.error(f"Story generation failed: {e}")
            story = "Story generation skipped due to API issue"

        # =========================
        # Step 5: Evaluation (SAFE)
        # =========================
        try:
            evaluation = evaluate_story(story)
            score = evaluation.get("score", 0)
            feedback = evaluation.get("feedback", "No feedback")
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            score = 0
            feedback = "Evaluation skipped"

        # =========================
        # Always return result
        # =========================
        return {
            "transcription": text,
            "confidence": confidence,
            "clean_text": cleaned,
            "story": story,
            "score": score,
            "feedback": feedback
        }

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))