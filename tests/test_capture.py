# tests/test_capture.py
import unittest
from src.capture.screen_capture import capture_screen_area
from PIL import Image

class TestCapture(unittest.TestCase):
    def test_capture_screen_area(self):
        # Test with a small area (adjust coordinates as needed)
        image = capture_screen_area(0, 0, 100, 100)
        self.assertIsInstance(image, Image.Image)
        self.assertEqual(image.size, (100, 100))

if __name__ == '__main__':
    unittest.main()