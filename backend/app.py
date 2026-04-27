from flask import Flask, request, jsonify
import os
from whisper_model import transcribe_audio
from utils import clean_text

app = Flask(__name__)

UPLOAD_FOLDER = "audio_temp"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "Yakshagana Backend Running!"

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["audio"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    file.save(file_path)

    try:
        raw_text = transcribe_audio(file_path)
        cleaned_text = clean_text(raw_text)

        return jsonify({
            "raw_text": raw_text,
            "cleaned_text": cleaned_text
        })

    except Exception as e:
        return jsonify({"error": str(e)})

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    app.run(debug=True)



# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import os
# import uuid
# from whisper_model import transcribe_audio
# from utils import clean_text

# app = Flask(__name__)
# CORS(app)

# UPLOAD_FOLDER = "audio_temp"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# @app.route("/")
# def home():
#     return "Yakshagana Backend Running!"

# @app.route("/upload", methods=["POST"])
# def upload():
#     if "audio" not in request.files:
#         return jsonify({"error": "No file uploaded"}), 400

#     file = request.files["audio"]
#     file_path = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + ".wav")

#     file.save(file_path)

#     try:
#         raw_text = transcribe_audio(file_path)
#         cleaned_text = clean_text(raw_text)

#         return jsonify({
#             "text": cleaned_text
#         })

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

#     finally:
#         if os.path.exists(file_path):
#             os.remove(file_path)

# if __name__ == "__main__":
#     app.run(debug=True)