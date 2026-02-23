import tkinter as tk
from .ui.interface import ScreenTranslatorUI
from .utils.logging import setup_logging

def main():
    setup_logging()
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    app = ScreenTranslatorUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()