import whisper

model = whisper.load_model("medium")
def transcribe_audio(file_path):
    result = model.transcribe(
        file_path,
        language="kn",
        task="transcribe",
        temperature=0,
        beam_size=5,
        best_of=5,
        condition_on_previous_text=False,
        initial_prompt="ಇದು ಯಕ್ಷಗಾನ ಪದ, ಕನ್ನಡ ಭಕ್ತಿ ಗೀತೆಯಾಗಿದೆ, ಸ್ಪಷ್ಟವಾಗಿ ಕೇಳಿ ಬರೆಯಿರಿ"    )
    return result["text"]