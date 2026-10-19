import os
from google import genai

_client = None


def _get_client():
    global _client

    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY not set in environment."
            )

        _client = genai.Client(api_key=api_key)

    return _client


# Use the model that is currently available for your API key.
TRANSLATION_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.8-flash"
]


TRANSLATION_PROMPT = """
You are a professional Kannada-to-English translator.

Translate the Kannada text given below into English.

IMPORTANT:
- The input is a Kannada Yakshagana narrative.
- Translate ONLY the provided text.
- Do NOT summarize it.
- Do NOT rewrite it.
- Do NOT generate a new story.
- Do NOT add information.
- Do NOT remove information.
- Preserve the exact sequence of events.
- Preserve character names and mythological names.
- Preserve the meaning of every sentence.
- Use natural, simple English.
- The final answer MUST be written entirely in English.
- Do NOT output Kannada.
- Do NOT output Kannada transliteration.
- Do NOT provide explanations.
- Do NOT use labels such as "Translation:".
- Return ONLY the English translation.

Kannada text:
{text}
"""


def translate_summary(kannada_text):

    if not kannada_text or not kannada_text.strip():
        return {
            "success": False,
            "translated_text": None,
            "error": "Empty input text."
        }

    try:
        client = _get_client()

    except Exception as e:
        return {
            "success": False,
            "translated_text": None,
            "error": str(e)
        }

    prompt = TRANSLATION_PROMPT.format(
        text=kannada_text.strip()
    )

    last_error = None

    for model_name in TRANSLATION_MODELS:

        print(f"\n[TRANSLATE] Trying model: {model_name}")

        try:

            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            translated = (response.text or "").strip()

            print(f"[TRANSLATE] Input Kannada:")
            print(kannada_text)

            print(f"[TRANSLATE] Gemini response:")
            print(translated)

            if not translated:
                last_error = "Gemini returned an empty response."
                continue

            # Basic protection against Gemini returning Kannada
            kannada_chars = sum(
                1 for ch in translated
                if '\u0C80' <= ch <= '\u0CFF'
            )

            total_letters = sum(
                1 for ch in translated
                if ch.isalpha()
            )

            # If a significant portion is Kannada,
            # do not treat it as a valid English translation.
            if total_letters > 0 and (
                kannada_chars / total_letters > 0.20
            ):
                last_error = (
                    "Gemini returned Kannada instead of "
                    "an English translation."
                )

                print(
                    "[TRANSLATE] Invalid response: "
                    "Kannada detected in output."
                )

                continue

            print(
                f"[TRANSLATE] Translation successful "
                f"using {model_name}"
            )

            return {
                "success": True,
                "translated_text": translated,
                "error": None
            }

        except Exception as e:

            last_error = str(e)

            print(
                f"[TRANSLATE] {model_name} failed: "
                f"{last_error}"
            )

            if (
                "503" in last_error
                or "UNAVAILABLE" in last_error
            ):
                print(
                    f"[TRANSLATE] {model_name} "
                    f"temporarily unavailable."
                )
                continue

            break

    return {
        "success": False,
        "translated_text": None,
        "error": last_error
    }