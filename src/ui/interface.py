import tkinter as tk
from tkinter import messagebox
import keyboard  # Requires 'keyboard' library: pip install keyboard
from ..capture.screen_capture import capture_screen_area
from ..ocr.ocr_engine import extract_text_from_image
from ..translation.translator import translate_text
from ..overlay.display_overlay import show_overlay
from ..ui.settings import get_settings
from ..utils.helpers import handle_error
from ..utils.logging import logger

class ScreenTranslatorUI:
    def __init__(self, root):
        self.root = root
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.canvas = None
        self.settings = get_settings()
        self.register_hotkey()

    def register_hotkey(self):
        keyboard.add_hotkey('ctrl+shift+t', self.start_selection)

    def start_selection(self):
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.attributes('-fullscreen', True)
        self.selection_window.attributes('-alpha', 0.3)
        self.selection_window.attributes('-topmost', True)
        self.canvas = tk.Canvas(self.selection_window, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

    def on_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        self.selection_window.destroy()
        try:
            image = capture_screen_area(int(self.start_x), int(self.start_y), int(end_x), int(end_y))
            text = extract_text_from_image(image, self.settings['source_lang'])
            print("OCR RAW TEXT:", repr(text))
            if text:
                translated = translate_text(text, self.settings['source_lang'], self.settings['target_lang'])
                show_overlay(translated, int(self.start_x), int(self.start_y), int(end_x - self.start_x), int(end_y - self.start_y))
            else:
                messagebox.showinfo("Info", "No text detected.")
        except Exception as e:
            handle_error(e)
            logger.error(f"Error during translation: {e}")
