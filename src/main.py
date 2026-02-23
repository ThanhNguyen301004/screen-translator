# src/main.py
import tkinter as tk
import ctypes
import os
from .ui.interface import ScreenTranslatorUI
from .ui.tray import run_tray
from .utils.logging import setup_logging

def main():
    # DPI awareness
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

    setup_logging()

    root = tk.Tk()
    root.withdraw()  # Ẩn hoàn toàn, chỉ chạy ngầm

    app = ScreenTranslatorUI(root)

    # Icon path (đặt file icon.png vào thư mục gốc)
    base_dir  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    icon_path = os.path.join(base_dir, "icon.png")

    run_tray(
        on_quit    = root.destroy,
        icon_path  = icon_path if os.path.exists(icon_path) else None,
    )

    root.mainloop()

if __name__ == "__main__":
    main()