import re

def clean_text(text):
    # remove long repeated characters
    text = re.sub(r'(.)\1{2,}', r'\1', text)

    # remove non-Kannada
    text = re.sub(r'[^\u0C80-\u0CFF\s]', '', text)

    # remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text