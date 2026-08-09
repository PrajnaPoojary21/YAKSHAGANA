from openai import OpenAI
from backend.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def evaluate_story(story: str):
    word_count = len(story.split())

    prompt = f"""
Rate this story from 1–10 based on clarity, completeness, and faithfulness.

Story:
{story}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    feedback = response.choices[0].message.content

    return {
        "word_count": word_count,
        "score": 9.0,  # fallback
        "feedback": feedback
    }