# import re

# def clean_text(text):
#     # remove long repeated characters
#     text = re.sub(r'(.)\1{2,}', r'\1', text)

#     # remove non-Kannada
#     text = re.sub(r'[^\u0C80-\u0CFF\s]', '', text)

#     # remove extra spaces
#     text = re.sub(r'\s+', ' ', text).strip()

#     return text

import re

def clean_text(text):
    if not text:
        return ""

    # Remove repeated character runs (ಲಿಲಿಲಿಲಿ → ಲಿ)
    text = re.sub(r'(.{1,3}?)\1{3,}', r'\1', text)

    # Remove non-Kannada except spaces and punctuation
    text = re.sub(r'[^\u0C80-\u0CFF\s।\.\,]', '', text)

    # Collapse spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def split_into_lines(text, max_words_per_line=6):
    """
    Splits transcribed text into padya-style lines
    for better readability on the result page.
    """
    words = text.split()
    lines = []
    for i in range(0, len(words), max_words_per_line):
        lines.append(' '.join(words[i:i + max_words_per_line]))
    return '\n'.join(lines)