import ctypes
import tkinter as tk
import ctypes
from .ui.interface import ScreenTranslatorUI
from .utils.logging import setup_logging

def main():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except:
        pass
    setup_logging()
    root = tk.Tk()
    # root.withdraw()  # Hide the main window
    app = ScreenTranslatorUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()