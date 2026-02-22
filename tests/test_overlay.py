# tests/test_overlay.py
import unittest
from src.overlay.display_overlay import show_overlay
import tkinter as tk

class TestOverlay(unittest.TestCase):
    def test_show_overlay(self):
        # This is tricky to test without GUI, so just check if it runs without error
        root = tk.Tk()
        root.withdraw()
        try:
            show_overlay("Test Overlay", 100, 100, 200, 100)
            self.assertTrue(True)
        except Exception:
            self.fail("Overlay raised an exception")

if __name__ == '__main__':
    unittest.main()