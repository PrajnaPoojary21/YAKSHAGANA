
import re

def clean_text(text):
    # remove repeated characters
    cleaned = re.sub(r'(.)\1+', r'\1', text)
    return cleaned