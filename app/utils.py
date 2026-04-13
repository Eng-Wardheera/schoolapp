from datetime import datetime

from googletrans import Translator


def get_academic_year():
    """Return current academic year in format '2026 - 2027'."""
    year = datetime.now().year
    return f"{year} - {year + 1}"


# utils.py
translator = Translator()

def translate_to_somali(text):
    """
    English text dynamically ugu beddel Af-Soomaali.
    Haddii text-ka uu already Somali yahay ama translation fails, text-ka as-is ayuu ahaanayaa.
    """
    if not text:
        return ""
    
    try:
        result = translator.translate(text, src='en', dest='so')
        return result.text
    except Exception as e:
        print("Translation error:", e)
        return text
