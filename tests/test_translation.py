# tests/test_translation.py
import unittest
from src.translation.translator import translate_text

class TestTranslation(unittest.TestCase):
    def test_translate_text(self):
        translated = translate_text("Hello", src='en', dest='vi')
        self.assertNotEqual(translated, "Hello")  # Note: Actual translation may vary slightly

if __name__ == '__main__':
    unittest.main()