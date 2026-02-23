# src/translation/translator.py
from googletrans import Translator  # Requires 'googletrans==4.0.0-rc1' library: pip install googletrans==4.0.0-rc1
from ..utils.logging import logger


translator = Translator()

def translate_text(text, src='en', dest='vi'):
    try:
        result = translator.translate(text, src=src, dest=dest)
        return result.text
    except Exception as e:
        print("Translation error:", e)
        return text