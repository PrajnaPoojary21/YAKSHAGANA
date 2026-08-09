# from flask import Flask, request, jsonify
# import os
# from whisper_model import transcribe_audio
# from utils import clean_text

# app = Flask(__name__)

# UPLOAD_FOLDER = "audio_temp"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# @app.route("/")
# def home():
#     return "Yakshagana Backend Running!"

# @app.route("/transcribe", methods=["POST"])
# def transcribe():
#     if "audio" not in request.files:
#         return jsonify({"error": "No file uploaded"}), 400

#     file = request.files["audio"]
#     file_path = os.path.join(UPLOAD_FOLDER, file.filename)

#     file.save(file_path)

#     try:
#         raw_text = transcribe_audio(file_path)
#         cleaned_text = clean_text(raw_text)

#         return jsonify({
#             "raw_text": raw_text,
#             "cleaned_text": cleaned_text
#         })

#     except Exception as e:
#         return jsonify({"error": str(e)})

#     finally:
#         if os.path.exists(file_path):
#             os.remove(file_path)

# if __name__ == "__main__":
#     app.run(debug=True)


from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from whisper_model import transcribe_audio
from utils import clean_text, split_into_lines

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "audio_temp"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'ogg', 'webm', 'flac'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return "Yakshagana Backend Running!"


@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files["audio"]

    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file format"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        raw_text = transcribe_audio(file_path)

        # ✅ FIXED: don't block on empty — return whatever we got
        cleaned_text = clean_text(raw_text) if raw_text else ""
        formatted_text = split_into_lines(cleaned_text) if cleaned_text else ""

        # If cleaned_text is empty but raw_text has something, use raw_text directly
        display_padya = formatted_text if formatted_text.strip() else raw_text

        


        response = {
            "raw_text": raw_text,
            "cleaned_text": cleaned_text,
            "formatted_padya": display_padya,
            "story": "ಡೇಟಾಸೆಟ್ ತಯಾರಾದ ನಂತರ ಕಥೆ ಇಲ್ಲಿ ತೋರಿಸಲಾಗುತ್ತದೆ."
            }
        print("API Response:", response)
        return jsonify(response)




    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000, use_reloader=False)