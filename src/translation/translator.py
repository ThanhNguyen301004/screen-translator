# src/translation/translator.py
from googletrans import Translator  # Requires 'googletrans==4.0.0-rc1' library: pip install googletrans==4.0.0-rc1
from ..utils.logging import logger

def translate_text(text, src='auto', dest='vi'):
    try:
        translator = Translator()
        translation = translator.translate(text, src=src, dest=dest)
        return translation.text
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text  # Return original if failed