import re

def clean_text(text: str) -> str:
    # Remove repeated phrases
    text = re.sub(r'(\b.+?\b)( \1\b)+', r'\1', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Merge broken sentences
    text = text.replace("\n", " ")

    return text.strip()


def segment_text(text: str):
    # Simple segmentation by punctuation
    sentences = re.split(r'(?<=[.!?]) +', text)
    return sentences