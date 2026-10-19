# from dotenv import load_dotenv
# load_dotenv()
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import os
# from whisper_model import transcribe_audio
# from utils import clean_text, split_into_lines

# # ============ pipeline stages ============
# from matcher import find_top_k_matches
# from validator import validate_match
# from story_generator import generate_story
# from translator import translate_summary
# # ==========================================

# app = Flask(__name__)
# CORS(app)
# app.json.ensure_ascii = False   # Flask 3.x: this is the only line that works

# UPLOAD_FOLDER = "audio_temp"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'ogg', 'webm', 'flac'}

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# @app.route("/")
# def home():
#     return "Yakshagana Backend Running!"


# @app.route("/transcribe", methods=["POST"])
# def transcribe():
#     if "audio" not in request.files:
#         return jsonify({"error": "No audio file uploaded"}), 400

#     file = request.files["audio"]

#     if file.filename == '':
#         return jsonify({"error": "Empty filename"}), 400

#     if not allowed_file(file.filename):
#         return jsonify({"error": "Unsupported file format"}), 400

#     file_path = os.path.join(UPLOAD_FOLDER, file.filename)
#     file.save(file_path)

#     try:
#         raw_text = transcribe_audio(file_path)

#         cleaned_text = clean_text(raw_text) if raw_text else ""
#         formatted_text = split_into_lines(cleaned_text) if cleaned_text else ""

#         # Default: show what the ASR actually heard. This gets overridden
#         # below ONLY when we have a confidently-verified match — at that
#         # point the dataset's verse text is known-correct and the raw ASR
#         # guess is strictly worse to display, so prefer the verified text.
#         display_padya = formatted_text if formatted_text.strip() else raw_text

#         # ============ padya matching + confidence validation + story ============
#         # NOTE: this only covers "is this specific FAISS candidate reliable?"
#         # (validator.py). It does NOT check whether the audio is Yakshagana at
#         # all, or whether the transcription itself is trustworthy before it
#         # ever reaches FAISS — that's a separate module that isn't built yet.
#         # See the chat message for what's still needed there.
#         if cleaned_text.strip():
#             top_matches = find_top_k_matches(cleaned_text, top_k=5)
#             validation = validate_match(cleaned_text, top_matches)

#             matched_padya = validation["padya"]           # None if rejected
#             match_confidence = validation["confidence"]
#             match_status = validation["status"]            # matched / low_confidence / medium_confidence / ...

#             if validation["success"]:
#                 story = generate_story(validation["summary"])
#                 # CHANGED: on a confirmed match, show the verified dataset
#                 # text instead of the raw ASR guess — this is the fix for
#                 # transcripts like "ಮುದದನ್ನ ಮಿಂನ" reading as noisy/wrong:
#                 # once we know which verse it actually is, show that verse,
#                 # not what Whisper mis-heard.
#                 display_padya = matched_padya
#             else:
#                 story = validation["message"]
#         else:
#             matched_padya = None
#             match_confidence = None
#             match_status = "empty_transcription"
#             story = "ಆಡಿಯೊದಿಂದ ಪಠ್ಯ ಗುರುತಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ."
#         # ===========================================================================

#         return jsonify({
#             "raw_text": raw_text,
#             "cleaned_text": cleaned_text,
#             "formatted_padya": display_padya,
#             "matched_padya": matched_padya,       # None when rejected — don't show a guess
#             "match_confidence": match_confidence, # 0..1, safe to show to users as e.g. a %
#             "match_status": match_status,
#             "story": story
#             # Intentionally NOT included: raw FAISS distance, per-component
#             # confidence breakdown — those stay server-side (see validator.py
#             # "_components", which is deliberately left out of this response).
#         })

#     except Exception as e:
#         return jsonify({"error": f"Transcription failed: {str(e)}"}), 500

#     finally:
#         if os.path.exists(file_path):
#             os.remove(file_path)


# if __name__ == "__main__":
#     app.run(debug=False, host="0.0.0.0", port=5000, use_reloader=False)




from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from whisper_model import transcribe_audio
from utils import clean_text, split_into_lines

# ============ pipeline stages ============
from matcher import find_top_k_matches
from validator import validate_match
from story_generator import generate_story
from translator import translate_summary
# ==========================================


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)
CORS(app)

# Flask 3.x: keep Unicode characters such as Kannada visible
app.json.ensure_ascii = False


# ============================================================
# UPLOAD CONFIGURATION
# ============================================================

UPLOAD_FOLDER = "audio_temp"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {
    'wav',
    'mp3',
    'm4a',
    'ogg',
    'webm',
    'flac'
}


def allowed_file(filename):
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# ============================================================
# HOME ROUTE
# ============================================================

@app.route("/")
def home():
    return "Yakshagana Backend Running!"


# ============================================================
# EXISTING TRANSCRIPTION + PADYA MATCHING PIPELINE
# ============================================================

@app.route("/transcribe", methods=["POST"])
def transcribe():

    # --------------------------------------------------------
    # Check whether audio file was uploaded
    # --------------------------------------------------------

    if "audio" not in request.files:
        return jsonify({
            "error": "No audio file uploaded"
        }), 400

    file = request.files["audio"]

    # --------------------------------------------------------
    # Check filename
    # --------------------------------------------------------

    if file.filename == '':
        return jsonify({
            "error": "Empty filename"
        }), 400

    # --------------------------------------------------------
    # Check supported audio format
    # --------------------------------------------------------

    if not allowed_file(file.filename):
        return jsonify({
            "error": "Unsupported file format"
        }), 400

    # --------------------------------------------------------
    # Save uploaded audio
    # --------------------------------------------------------

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    file.save(file_path)

    try:

        # ====================================================
        # STEP 1: SPEECH TO TEXT
        # ====================================================

        raw_text = transcribe_audio(file_path)

        # ====================================================
        # STEP 2: TEXT CLEANING
        # ====================================================

        cleaned_text = (
            clean_text(raw_text)
            if raw_text
            else ""
        )

        # ====================================================
        # STEP 3: FORMAT TEXT INTO PADYA LINES
        # ====================================================

        formatted_text = (
            split_into_lines(cleaned_text)
            if cleaned_text
            else ""
        )

        # ----------------------------------------------------
        # Default display:
        # Show the actual ASR output unless a reliable
        # Padya match is found.
        # ----------------------------------------------------

        display_padya = (
            formatted_text
            if formatted_text.strip()
            else raw_text
        )

        # ====================================================
        # STEP 4: PADYA MATCHING + VALIDATION + STORY
        # ====================================================

        if cleaned_text.strip():

            # ------------------------------------------------
            # Find top matching Padyas
            # ------------------------------------------------

            top_matches = find_top_k_matches(
                cleaned_text,
                top_k=5
            )

            # ------------------------------------------------
            # Validate similarity match
            # ------------------------------------------------

            validation = validate_match(
                cleaned_text,
                top_matches
            )

            # ------------------------------------------------
            # Extract validation information
            # ------------------------------------------------

            matched_padya = validation["padya"]

            match_confidence = validation["confidence"]

            match_status = validation["status"]

            # ------------------------------------------------
            # If match is reliable
            # ------------------------------------------------

            if validation["success"]:

                # --------------------------------------------
                # Retrieve/generate the corresponding story
                # --------------------------------------------

                story = generate_story(
                    validation["summary"]
                )

                # --------------------------------------------
                # Once the match is confidently verified,
                # display the verified Padya instead of
                # noisy raw Whisper output.
                # --------------------------------------------

                display_padya = matched_padya

            # ------------------------------------------------
            # If match is rejected
            # ------------------------------------------------

            else:

                story = validation["message"]

        # ====================================================
        # EMPTY TRANSCRIPTION
        # ====================================================

        else:

            matched_padya = None

            match_confidence = None

            match_status = "empty_transcription"

            story = (
                "ಆಡಿಯೊದಿಂದ ಪಠ್ಯ ಗುರುತಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ."
            )

        # ====================================================
        # RETURN EXISTING TRANSCRIPTION RESULT
        # ====================================================

        return jsonify({

            "raw_text": raw_text,

            "cleaned_text": cleaned_text,

            "formatted_padya": display_padya,

            "matched_padya": matched_padya,

            "match_confidence": match_confidence,

            "match_status": match_status,

            "story": story

        })

    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as e:

        return jsonify({
            "error": f"Transcription failed: {str(e)}"
        }), 500

    # ========================================================
    # DELETE TEMPORARY AUDIO FILE
    # ========================================================

    finally:

        if os.path.exists(file_path):
            os.remove(file_path)


# ============================================================
# KANNADA → ENGLISH TRANSLATION API
# ============================================================
#
# This is an ADDITIONAL endpoint.
#
# It does NOT modify the existing /transcribe pipeline.
#
# The existing system continues to:
#
# Audio
#   ↓
# Whisper
#   ↓
# Text Cleaning
#   ↓
# Padya Matching
#   ↓
# Validation
#   ↓
# Story Retrieval
#
# The translation endpoint is called separately by the
# frontend only when the user selects English.
#
# ============================================================

@app.route("/api/translate", methods=["POST"])
def translate_story():

    try:

        # ----------------------------------------------------
        # Read JSON request
        # ----------------------------------------------------

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "error": "No JSON data received."
            }), 400

        # ----------------------------------------------------
        # Get Kannada narrative
        # ----------------------------------------------------

        kannada_text = data.get(
            "text",
            ""
        ).strip()

        if not kannada_text:

            return jsonify({
                "success": False,
                "error": "No Kannada narrative provided."
            }), 400

        # ----------------------------------------------------
        # Send Kannada narrative to translator.py
        # ----------------------------------------------------

        result = translate_summary(
            kannada_text
        )

        # ----------------------------------------------------
        # Gemini translation failed
        # ----------------------------------------------------

        if not result["success"]:

            return jsonify({
                "success": False,
                "error": result["error"]
            }), 500

        # ----------------------------------------------------
        # Successful translation
        # ----------------------------------------------------

        return jsonify({

            "success": True,

            "english": result["translated_text"]

        })

    # ========================================================
    # TRANSLATION ERROR
    # ========================================================

    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# ============================================================
# START FLASK SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=False,
        host="0.0.0.0",
        port=5000,
        use_reloader=False
    )