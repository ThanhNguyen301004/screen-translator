# src/ui/interface.py
import tkinter as tk
from tkinter import messagebox
import keyboard  # pip install keyboard

from ..capture.screen_capture import capture_screen_area
from ..ocr.ocr_engine import extract_text_from_image
from ..translation.translator import translate_text
from ..overlay.display_overlay import show_overlay
from ..ui.settings import get_settings, save_settings
from ..utils.helpers import handle_error
from ..utils.logging import logger

# Mapping: googletrans lang code  →  Tesseract lang code
_GT_TO_TESS = {
    "en": "eng", "vi": "vie", "zh-cn": "chi_sim", "zh-tw": "chi_tra",
    "ja": "jpn", "ko": "kor", "fr": "fra", "de": "deu", "es": "spa",
    "ru": "rus", "ar": "ara", "th": "tha", "hi": "hin", "pt": "por",
    "it": "ita", "pl": "pol", "tr": "tur", "nl": "nld", "sv": "swe",
    "da": "dan", "no": "nor", "fi": "fin", "cs": "ces", "ro": "ron",
    "hu": "hun", "uk": "ukr", "ca": "cat", "id": "ind", "ms": "msa",
    "hr": "hrv", "sk": "slk", "bg": "bul", "el": "ell", "he": "heb",
}

def gt_to_tess(lang_code: str) -> str:
    """Chuyển mã googletrans → mã Tesseract. Fallback: 'eng'."""
    return _GT_TO_TESS.get(lang_code, "eng")


class ScreenTranslatorUI:
    def __init__(self, root: tk.Tk):
        self.root        = root
        self.settings    = get_settings()

        # Vùng chụp gần nhất (để dùng chụp lại)
        self._last_region: tuple | None = None   # (x, y, w, h)

        # Overlay đang hiển thị (nếu có)
        self._overlay = None

        # Canvas selection
        self.start_x     = None
        self.start_y     = None
        self.rect        = None
        self.canvas      = None
        self.selection_window = None
        self._last_overlay_pos = (100, 100)
        self._register_hotkey()

    # ── Hotkey ────────────────────────────────────────────────────────────────
    def _register_hotkey(self):
        keyboard.add_hotkey("ctrl+shift+l", self._start_selection)

    # ── Screen selection ──────────────────────────────────────────────────────
    def _start_selection(self):
        """Mở cửa sổ toàn màn hình để người dùng kéo chọn vùng chụp."""
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.attributes("-fullscreen", True)
        self.selection_window.attributes("-alpha", 0.25)
        self.selection_window.attributes("-topmost", True)
        self.canvas = tk.Canvas(self.selection_window, cursor="cross",
                                bg="#000000")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<ButtonPress-1>",   self._on_press)
        self.canvas.bind("<B1-Motion>",        self._on_drag)
        self.canvas.bind("<ButtonRelease-1>",  self._on_release)
        # Esc để hủy
        self.selection_window.bind("<Escape>",
                                   lambda _: self.selection_window.destroy())

    def _on_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="#1a73e8", width=2, dash=(4, 2))

    def _on_drag(self, event):
        self.canvas.coords(self.rect,
                           self.start_x, self.start_y,
                           self.canvas.canvasx(event.x),
                           self.canvas.canvasy(event.y))

    def _on_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        self.selection_window.destroy()

        x = int(min(self.start_x, end_x))
        y = int(min(self.start_y, end_y))
        w = int(abs(end_x - self.start_x))
        h = int(abs(end_y - self.start_y))

        if w < 10 or h < 10:
            return   # vùng quá nhỏ, bỏ qua

        self._last_region = (x, y, w, h)
        self._run_pipeline(x, y, w, h)

    # ── Pipeline: capture → OCR → translate → overlay ─────────────────────────
    def _run_pipeline(self, x: int, y: int, w: int, h: int):
        src  = self.settings.get("source_lang", "en")
        dest = self.settings.get("target_lang", "vi")
        ocr  = self.settings.get("ocr_lang") or gt_to_tess(src)

        try:
            image = capture_screen_area(x, y, w, h)
            text  = extract_text_from_image(image, lang=ocr)

            if not text:
                messagebox.showinfo("Thông báo", "Không nhận diện được chữ.")
                return

            translated = translate_text(text, src=src, dest=dest)

            # Đóng overlay cũ nếu còn
            if self._overlay and self._overlay.winfo_exists():
                self._last_overlay_pos = (
                    self._overlay.winfo_x(),
                    self._overlay.winfo_y(),
                )
                self._overlay.destroy()

            self._overlay = show_overlay(
                original_text   = text,
                translated      = translated,
                src_lang        = src,
                dest_lang       = dest,
                ocr_lang        = ocr,
                on_retranslate  = self._on_retranslate,
                on_recapture    = self._on_recapture,
                root            = self.root,
                spawn_x        = self._last_overlay_pos[0],  # ← dùng vị trí cũ
                spawn_y        = self._last_overlay_pos[1],
            )

        except Exception as e:
            handle_error(e)
            logger.error(f"Pipeline error: {e}")

    # ── Callbacks từ overlay ──────────────────────────────────────────────────
    def _on_recapture(self):
        """Chụp lại vùng cũ."""
        if self._last_region:
            x, y, w, h = self._last_region
            self._run_pipeline(x, y, w, h)

    def _on_retranslate(self, src_lang: str, dest_lang: str, ocr_lang: str):
        """
        Người dùng thay đổi ngôn ngữ trên overlay →
        lưu settings và chạy lại pipeline với vùng cũ.
        """
        self.settings["source_lang"] = src_lang
        self.settings["target_lang"] = dest_lang
        self.settings["ocr_lang"]    = ocr_lang
        save_settings(self.settings)

        if self._last_region:
            x, y, w, h = self._last_region
            self._run_pipeline(x, y, w, h)