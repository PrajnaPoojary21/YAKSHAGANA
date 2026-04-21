from openai import OpenAI
from backend.config import settings
from backend.logger import get_logger

logger = get_logger()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_story(text: str):
    try:
        prompt = f"""
You are an expert in Kannada literature and Yakshagana.

Convert the following Yakshagana padya into a structured story.

STRICT RULES:
- DO NOT summarize
- DO NOT omit any content
- Preserve original meaning and cultural context
- Convert poetic lines into clear prose
- Maintain chronological order
- Identify characters and actions clearly
- Expand implicit meaning where needed
- Use proper paragraph format
- Make it readable like a short story

INPUT:
{text}

OUTPUT:
A complete, well-structured story in Kannada.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Story generation failed: {e}")
        raise


def correct_transcription(text: str):
    prompt = f"Correct Kannada transcription errors while preserving meaning:\n{text}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content