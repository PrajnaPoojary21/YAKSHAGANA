import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    MODEL_SIZE: str = "medium"  # or large-v2

settings = Settings()