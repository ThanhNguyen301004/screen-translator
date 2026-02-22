# src/overlay/display_overlay.py
import tkinter as tk
from ..utils.logging import logger

def show_overlay(text, x, y, width, height):
    try:
        overlay = tk.Toplevel()
        overlay.overrideredirect(True)
        overlay.attributes('-topmost', True)
        overlay.attributes('-alpha', 0.8)
        overlay.geometry(f"{width}x{height}+{x}+{y}")
        label = tk.Label(overlay, text=text, bg='white', fg='black', wraplength=width-20, justify='left')
        label.pack(expand=True, fill='both')
        overlay.after(5000, overlay.destroy)  # Auto-hide after 5 seconds
    except Exception as e:
        logger.error(f"Overlay error: {e}")