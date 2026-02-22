# tests/test_ocr.py
import unittest
from src.ocr.ocr_engine import extract_text_from_image
from PIL import Image, ImageDraw, ImageFont
import os

class TestOCR(unittest.TestCase):
    def setUp(self):
        self.test_image = Image.new('RGB', (400, 200), color=(255, 255, 255))
        draw = ImageDraw.Draw(self.test_image)

        # Dùng font TrueType lớn hơn
        font = ImageFont.truetype("arial.ttf", 40)

        draw.text((50, 80), "Test Text", fill=(0, 0, 0), font=font)
        self.test_image.save('test_image.png')

    def test_extract_text_from_image(self):
        text = extract_text_from_image(self.test_image, lang='eng')
        self.assertIn("Test Text", text)

    def tearDown(self):
        os.remove('test_image.png')

if __name__ == '__main__':
    unittest.main()