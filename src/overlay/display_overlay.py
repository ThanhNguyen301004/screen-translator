# src/overlay/display_overlay.py
import tkinter as tk
from tkinter import ttk
import threading
import pyperclip  # pip install pyperclip
from ..utils.logging import logger

# ── TTS ──────────────────────────────────────────────────────────────────────
def _speak(text: str, lang: str = "vi"):
    """Phát âm thanh bằng gTTS trong thread riêng để không block UI."""
    try:
        from gtts import gTTS          # pip install gtts
        import pygame                   # pip install pygame
        import tempfile, os

        tts = gTTS(text=text, lang=lang, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tmp_path = fp.name
        tts.save(tmp_path)

        pygame.mixer.init()
        pygame.mixer.music.load(tmp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()
        os.unlink(tmp_path)
    except Exception as e:
        logger.error(f"TTS error: {e}")


# ── LANGUAGE LIST ─────────────────────────────────────────────────────────────
LANGUAGES = {
    "af": "Afrikaans", "sq": "Albanian", "ar": "Arabic", "hy": "Armenian",
    "az": "Azerbaijani", "eu": "Basque", "be": "Belarusian", "bn": "Bengali",
    "bs": "Bosnian", "bg": "Bulgarian", "ca": "Catalan", "zh-cn": "Chinese (Simplified)",
    "zh-tw": "Chinese (Traditional)", "hr": "Croatian", "cs": "Czech", "da": "Danish",
    "nl": "Dutch", "en": "English", "eo": "Esperanto", "et": "Estonian",
    "fi": "Finnish", "fr": "French", "gl": "Galician", "ka": "Georgian",
    "de": "German", "el": "Greek", "gu": "Gujarati", "ht": "Haitian Creole",
    "ha": "Hausa", "he": "Hebrew", "hi": "Hindi", "hu": "Hungarian",
    "is": "Icelandic", "ig": "Igbo", "id": "Indonesian", "ga": "Irish",
    "it": "Italian", "ja": "Japanese", "jw": "Javanese", "kn": "Kannada",
    "kk": "Kazakh", "km": "Khmer", "ko": "Korean", "ku": "Kurdish",
    "ky": "Kyrgyz", "lo": "Lao", "la": "Latin", "lv": "Latvian",
    "lt": "Lithuanian", "lb": "Luxembourgish", "mk": "Macedonian", "mg": "Malagasy",
    "ms": "Malay", "ml": "Malayalam", "mt": "Maltese", "mi": "Maori",
    "mr": "Marathi", "mn": "Mongolian", "my": "Myanmar (Burmese)", "ne": "Nepali",
    "no": "Norwegian", "or": "Odia", "ps": "Pashto", "fa": "Persian",
    "pl": "Polish", "pt": "Portuguese", "pa": "Punjabi", "ro": "Romanian",
    "ru": "Russian", "sm": "Samoan", "gd": "Scots Gaelic", "sr": "Serbian",
    "st": "Sesotho", "sn": "Shona", "sd": "Sindhi", "si": "Sinhala",
    "sk": "Slovak", "sl": "Slovenian", "so": "Somali", "es": "Spanish",
    "su": "Sundanese", "sw": "Swahili", "sv": "Swedish", "tg": "Tajik",
    "ta": "Tamil", "te": "Telugu", "th": "Thai", "tr": "Turkish",
    "uk": "Ukrainian", "ur": "Urdu", "ug": "Uyghur", "uz": "Uzbek",
    "vi": "Vietnamese", "cy": "Welsh", "xh": "Xhosa", "yi": "Yiddish",
    "yo": "Yoruba", "zu": "Zulu",
}

# OCR Tesseract language codes (tesseract_code: display_name)
OCR_LANGUAGES = {
    "eng":          "English",
    "vie":          "Vietnamese",
    "chi_sim":      "Chinese (Simplified)",
    "chi_tra":      "Chinese (Traditional)",
    "jpn":          "Japanese",
    "kor":          "Korean",
    "fra":          "French",
    "deu":          "German",
    "spa":          "Spanish",
    "rus":          "Russian",
    "ara":          "Arabic",
    "tha":          "Thai",
    "hin":          "Hindi",
    "por":          "Portuguese",
    "ita":          "Italian",
    "pol":          "Polish",
    "tur":          "Turkish",
    "nld":          "Dutch",
    "swe":          "Swedish",
    "dan":          "Danish",
    "nor":          "Norwegian",
    "fin":          "Finnish",
    "ces":          "Czech",
    "ron":          "Romanian",
    "hun":          "Hungarian",
    "ukr":          "Ukrainian",
    "cat":          "Catalan",
    "ind":          "Indonesian",
    "msa":          "Malay",
    "hrv":          "Croatian",
    "slk":          "Slovak",
    "bul":          "Bulgarian",
    "ell":          "Greek",
    "heb":          "Hebrew",
}


# ── LANGUAGE PICKER POPUP ─────────────────────────────────────────────────────
class LanguagePickerPopup(tk.Toplevel):
    """Dropdown-style popup để chọn ngôn ngữ từ danh sách có tìm kiếm."""

    def __init__(self, parent, lang_dict: dict, current_code: str,
                 on_select, title="Chọn ngôn ngữ"):
        super().__init__(parent)
        self.on_select = on_select
        self.lang_dict = lang_dict          # {code: name}
        self.filtered = list(lang_dict.items())

        self.title(title)
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.grab_set()                     # modal

        self._build_ui(current_code)
        self._center(parent)

    def _build_ui(self, current_code):
        BG      = "#1e1e2e"
        FG      = "#cdd6f4"
        ACCENT  = "#89b4fa"
        ENTRY_BG = "#313244"
        HOVER   = "#45475a"

        self.configure(bg=BG)

        # ── Search bar ────────────────────────────────────────────────────────
        search_frame = tk.Frame(self, bg=BG, padx=10, pady=8)
        search_frame.pack(fill="x")

        tk.Label(search_frame, text="🔍", bg=BG, fg=FG,
                 font=("Segoe UI", 11)).pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search)

        entry = tk.Entry(search_frame, textvariable=self.search_var,
                         bg=ENTRY_BG, fg=FG, insertbackground=FG,
                         relief="flat", font=("Segoe UI", 11), bd=0)
        entry.pack(side="left", fill="x", expand=True, padx=(6, 0))
        entry.focus_set()

        # Separator
        tk.Frame(self, bg=ACCENT, height=1).pack(fill="x")

        # ── Scrollable list ───────────────────────────────────────────────────
        list_frame = tk.Frame(self, bg=BG)
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, bg=BG, troughcolor=BG,
                                 relief="flat", width=8)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            list_frame,
            bg=BG, fg=FG,
            selectbackground=ACCENT, selectforeground="#1e1e2e",
            activestyle="none",
            font=("Segoe UI", 10),
            relief="flat", bd=0,
            highlightthickness=0,
            width=30, height=14,
            yscrollcommand=scrollbar.set,
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        self.listbox.bind("<Double-Button-1>", self._on_select)
        self.listbox.bind("<Return>", self._on_select)

        self._populate(current_code)

    def _populate(self, select_code=None):
        self.listbox.delete(0, "end")
        select_idx = 0
        for i, (code, name) in enumerate(self.filtered):
            self.listbox.insert("end", f"  {name}")
            if code == select_code:
                select_idx = i
        if self.filtered:
            self.listbox.selection_set(select_idx)
            self.listbox.see(select_idx)

    def _on_search(self, *_):
        q = self.search_var.get().lower()
        self.filtered = [(c, n) for c, n in self.lang_dict.items()
                         if q in n.lower() or q in c.lower()]
        self._populate()

    def _on_select(self, _event=None):
        sel = self.listbox.curselection()
        if sel:
            code, name = self.filtered[sel[0]]
            self.on_select(code, name)
        self.destroy()

    def _center(self, parent):
        self.update_idletasks()
        pw = parent.winfo_rootx()
        py = parent.winfo_rooty()
        w  = self.winfo_width()
        h  = self.winfo_height()
        self.geometry(f"+{pw}+{py + parent.winfo_height()}")


# ── MAIN OVERLAY WINDOW ───────────────────────────────────────────────────────
class TranslationOverlay(tk.Toplevel):
    """
    Popup hiển thị kết quả dịch với thanh công cụ.

    Tham số
    -------
    root          : tk.Tk  – cửa sổ gốc
    original_text : str    – văn bản gốc (OCR)
    translated    : str    – văn bản đã dịch
    src_lang      : str    – mã ngôn ngữ nguồn  (googletrans code, vd 'en')
    dest_lang     : str    – mã ngôn ngữ đích   (googletrans code, vd 'vi')
    ocr_lang      : str    – mã ngôn ngữ Tesseract (vd 'eng')
    on_retranslate: callable(src_lang, dest_lang, ocr_lang) -> None
                            – callback khi user thay đổi ngôn ngữ / chụp lại
    on_recapture  : callable() -> None
                            – callback khi nhấn nút chụp lại
    """

    # ── Palette ───────────────────────────────────────────────────────────────
    BG          = "#ffffff"
    TOOLBAR_BG  = "#1a73e8"          # Google-blue toolbar
    TOOLBAR_FG  = "#ffffff"
    SEP_COLOR   = "#e8eaed"
    SRC_FG      = "#202124"
    DEST_FG     = "#1a73e8"
    BTN_HOVER   = "#1558b0"
    FONT_BODY   = ("Segoe UI", 11)
    FONT_SMALL  = ("Segoe UI", 9)
    MIN_W       = 700
    MIN_H       = 110

    def __init__(self, root, original_text: str, translated: str,
                 src_lang: str = "en", dest_lang: str = "vi",
                 ocr_lang: str = "eng",
                 on_retranslate=None, on_recapture=None,
                 spawn_x=100, spawn_y=100):

        super().__init__(root)
        self.root           = root
        self.original_text  = original_text
        self.translated     = translated
        self.src_lang       = src_lang
        self.dest_lang      = dest_lang
        self.ocr_lang       = ocr_lang
        self.on_retranslate = on_retranslate
        self.on_recapture   = on_recapture
        self._spawn_x = spawn_x   # ← thêm 2 dòng này trước self._build()
        self._spawn_y = spawn_y

        self._build()
        self._position()

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build(self):
        self.overrideredirect(True)        # no native title bar
        self.attributes("-topmost", True)
        self.configure(bg=self.BG)
        self.minsize(self.MIN_W, self.MIN_H)

        # ── Drop-shadow simulation via outer frame ────────────────────────────
        outer = tk.Frame(self, bg="#c0c0c0", padx=1, pady=1)
        outer.pack(fill="both", expand=True)

        inner = tk.Frame(outer, bg=self.BG)
        inner.pack(fill="both", expand=True)

        # ── Toolbar ───────────────────────────────────────────────────────────
        self._build_toolbar(inner)

        # ── Separator ─────────────────────────────────────────────────────────
        tk.Frame(inner, bg=self.SEP_COLOR, height=1).pack(fill="x")

        # ── Source text ───────────────────────────────────────────────────────
        src_frame = tk.Frame(inner, bg=self.BG, padx=12, pady=6)
        src_frame.pack(fill="x")

        tk.Label(src_frame, text=self.original_text,
                 bg=self.BG, fg=self.SRC_FG,
                 font=self.FONT_BODY,
                 justify="left", anchor="w",
                 wraplength=self.MIN_W - 24).pack(fill="x")

        # ── Separator ─────────────────────────────────────────────────────────
        tk.Frame(inner, bg=self.SEP_COLOR, height=1).pack(fill="x")

        # ── Translated text ───────────────────────────────────────────────────
        dest_frame = tk.Frame(inner, bg=self.BG, padx=12, pady=8)
        dest_frame.pack(fill="x")

        tk.Label(dest_frame, text=self.translated,
                 bg=self.BG, fg=self.DEST_FG,
                 font=("Segoe UI", 12, "bold"),
                 justify="left", anchor="w",
                 wraplength=self.MIN_W - 24).pack(fill="x")

        # ── Close button (×) ─────────────────────────────────────────────────
        close_btn = tk.Button(
            inner, text="×",
            bg=self.BG, fg="#c00000",
            activebackground=self.SEP_COLOR, activeforeground="#525560",
            relief="flat", bd=0,
            font=("Segoe UI", 8),
            cursor="hand2",
            width=2,    # ← chiều rộng (tính theo số ký tự)
            height=1,
            command=self.destroy,
            
        )
        close_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-4, y=4)

        # ── Dragging ──────────────────────────────────────────────────────────
        for widget in (inner, src_frame, dest_frame):
            widget.bind("<ButtonPress-1>",   self._drag_start)
            widget.bind("<B1-Motion>",       self._drag_move)

    def _build_toolbar(self, parent):
        tb = tk.Frame(parent, bg=self.TOOLBAR_BG, height=36)
        tb.pack(fill="x")
        tb.pack_propagate(False)

        # ── Left: action buttons ──────────────────────────────────────────────
        left = tk.Frame(tb, bg=self.TOOLBAR_BG)
        left.pack(side="left", padx=4)

        icons = [
            ("🔄", "Chụp lại",           self._on_recapture),
            ("🔊", "Phát âm thanh",       self._on_speak),
            ("📋", "Sao chép bản dịch",   self._on_copy),
            ("⚙️",  "Chọn model dịch",    self._on_model),
        ]
        for icon, tip, cmd in icons:
            self._toolbar_btn(left, icon, tip, cmd)

        # ── Separator ─────────────────────────────────────────────────────────
        tk.Frame(tb, bg="#5094ed", width=1).pack(side="left", fill="y",
                                                  padx=4, pady=6)

        # ── Right: language selector ──────────────────────────────────────────
        right = tk.Frame(tb, bg=self.TOOLBAR_BG)
        right.pack(side="left")

        src_name  = LANGUAGES.get(self.src_lang,  self.src_lang)
        dest_name = LANGUAGES.get(self.dest_lang, self.dest_lang)

        self.src_btn = tk.Button(
            right,
            text=self._short(src_name),
            bg=self.TOOLBAR_BG, fg=self.TOOLBAR_FG,
            activebackground=self.BTN_HOVER, activeforeground=self.TOOLBAR_FG,
            relief="flat", bd=0, padx=6,
            font=self.FONT_SMALL, cursor="hand2",
            command=self._pick_src_lang,
        )
        self.src_btn.pack(side="left")

        tk.Label(right, text="⇄", bg=self.TOOLBAR_BG, fg=self.TOOLBAR_FG,
                 font=("Segoe UI", 10)).pack(side="left")

        self.dest_btn = tk.Button(
            right,
            text=self._short(dest_name),
            bg=self.TOOLBAR_BG, fg=self.TOOLBAR_FG,
            activebackground=self.BTN_HOVER, activeforeground=self.TOOLBAR_FG,
            relief="flat", bd=0, padx=6,
            font=self.FONT_SMALL, cursor="hand2",
            command=self._pick_dest_lang,
        )
        self.dest_btn.pack(side="left")

        # OCR lang button (nhỏ hơn, màu khác một chút)
        tk.Frame(tb, bg="#5094ed", width=1).pack(side="left", fill="y",
                                                  padx=4, pady=6)

        ocr_name = OCR_LANGUAGES.get(self.ocr_lang, self.ocr_lang)
        self.ocr_btn = tk.Button(
            tb,
            text=f"OCR: {self._short(ocr_name)}",
            bg=self.TOOLBAR_BG, fg="#d0e4ff",
            activebackground=self.BTN_HOVER, activeforeground=self.TOOLBAR_FG,
            relief="flat", bd=0, padx=6,
            font=self.FONT_SMALL, cursor="hand2",
            command=self._pick_ocr_lang,
        )
        self.ocr_btn.pack(side="left")

    def _toolbar_btn(self, parent, icon, tooltip, command):
        btn = tk.Button(
            parent, text=icon,
            bg=self.TOOLBAR_BG, fg=self.TOOLBAR_FG,
            activebackground=self.BTN_HOVER, activeforeground=self.TOOLBAR_FG,
            relief="flat", bd=0, padx=5, pady=2,
            font=("Segoe UI Emoji", 13),
            cursor="hand2",
            command=command,
        )
        btn.pack(side="left")
        self._add_tooltip(btn, tooltip)
        return btn

    # ── Tooltip ───────────────────────────────────────────────────────────────
    def _add_tooltip(self, widget, text: str):
        tip_win = None

        def enter(_):
            nonlocal tip_win
            x = widget.winfo_rootx() + 2
            y = widget.winfo_rooty() + widget.winfo_height() + 4
            tip_win = tk.Toplevel(widget)
            tip_win.overrideredirect(True)
            tip_win.attributes("-topmost", True)
            tip_win.geometry(f"+{x}+{y}")
            lbl = tk.Label(tip_win, text=text, bg="#202124", fg="#ffffff",
                           font=("Segoe UI", 9), padx=6, pady=3, relief="flat")
            lbl.pack()

        def leave(_):
            nonlocal tip_win
            if tip_win:
                tip_win.destroy()
                tip_win = None

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    # ── Actions ───────────────────────────────────────────────────────────────
    def _on_recapture(self):
        self.destroy()
        if self.on_recapture:
            self.root.after(100, self.on_recapture)

    def _on_speak(self):
        threading.Thread(
            target=_speak,
            args=(self.translated, self.dest_lang),
            daemon=True,
        ).start()

    def _on_copy(self):
        try:
            pyperclip.copy(self.translated)
        except Exception as e:
            logger.error(f"Copy error: {e}")

    def _on_model(self):
        """Hiện thị thông tin model dịch (hiện chỉ Google Translate)."""
        popup = tk.Toplevel(self)
        popup.title("Model dịch")
        popup.resizable(False, False)
        popup.attributes("-topmost", True)
        popup.grab_set()
        popup.configure(bg="#1e1e2e")

        tk.Label(popup, text="🌐  Translation Engine",
                 bg="#1e1e2e", fg="#cdd6f4",
                 font=("Segoe UI", 11, "bold"),
                 padx=20, pady=12).pack()

        # Single option: Google Translate (selected)
        var = tk.StringVar(value="google")
        rb = tk.Radiobutton(popup, text="Google Translate  ✓",
                            variable=var, value="google",
                            bg="#1e1e2e", fg="#89b4fa",
                            selectcolor="#313244",
                            activebackground="#1e1e2e",
                            font=("Segoe UI", 10),
                            padx=20)
        rb.pack(anchor="w")

        tk.Label(popup, text="Thêm engine sẽ được hỗ trợ trong tương lai.",
                 bg="#1e1e2e", fg="#6c7086",
                 font=("Segoe UI", 9),
                 padx=20, pady=8).pack()

        tk.Button(popup, text="Đóng",
                  bg="#89b4fa", fg="#1e1e2e",
                  activebackground="#74c7ec",
                  relief="flat", padx=16, pady=4,
                  font=("Segoe UI", 10),
                  command=popup.destroy).pack(pady=(0, 12))

        # center over overlay
        popup.update_idletasks()
        px = self.winfo_rootx() + (self.winfo_width()  - popup.winfo_width())  // 2
        py = self.winfo_rooty() + (self.winfo_height() - popup.winfo_height()) // 2
        popup.geometry(f"+{px}+{py}")

    # ── Language pickers ──────────────────────────────────────────────────────
    def _pick_src_lang(self):
        def on_select(code, name):
            self.src_lang = code
            self.src_btn.config(text=self._short(name))
            self._retranslate()

        LanguagePickerPopup(self, LANGUAGES, self.src_lang,
                            on_select, title="Ngôn ngữ nguồn")

    def _pick_dest_lang(self):
        def on_select(code, name):
            self.dest_lang = code
            self.dest_btn.config(text=self._short(name))
            self._retranslate()

        LanguagePickerPopup(self, LANGUAGES, self.dest_lang,
                            on_select, title="Ngôn ngữ đích")

    def _pick_ocr_lang(self):
        def on_select(code, name):
            self.ocr_lang = code
            self.ocr_btn.config(text=f"OCR: {self._short(name)}")
            self._retranslate()

        LanguagePickerPopup(self, OCR_LANGUAGES, self.ocr_lang,
                            on_select, title="Ngôn ngữ OCR")

    def _retranslate(self):
        if self.on_retranslate:
            self.on_retranslate(self.src_lang, self.dest_lang, self.ocr_lang)

    # ── Drag ──────────────────────────────────────────────────────────────────
    def _drag_start(self, event):
        self._dx = event.x_root - self.winfo_x()
        self._dy = event.y_root - self.winfo_y()

    def _drag_move(self, event):
        self.geometry(f"+{event.x_root - self._dx}+{event.y_root - self._dy}")

    # ── Position ──────────────────────────────────────────────────────────────
    # mới
    def _position(self):
        self.update_idletasks()
        w = max(self.winfo_width(), self.MIN_W)
        h = max(self.winfo_height(), self.MIN_H)
        self.geometry(f"{w}x{h}+{self._spawn_x}+{self._spawn_y}")

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _short(name: str, max_len: int = 12) -> str:
        return name if len(name) <= max_len else name[:max_len - 1] + "…"


# ── Public API (thay thế hàm show_overlay cũ) ─────────────────────────────────
def show_overlay(original_text: str, translated: str,
                 src_lang: str = "en", dest_lang: str = "vi",
                 ocr_lang: str = "eng",
                 on_retranslate=None, on_recapture=None,
                 root: tk.Tk = None,
                 spawn_x=100, spawn_y=100):
    """
    Tạo và hiển thị overlay dịch thuật.

    Nếu `root` là None, hàm sẽ tìm cửa sổ Tk mặc định qua tk._default_root.
    """
    if root is None:
        root = tk._default_root
    if root is None:
        raise RuntimeError("Không tìm thấy cửa sổ Tk gốc. Hãy truyền root=...")

    overlay = TranslationOverlay(
        root,
        original_text=original_text,
        translated=translated,
        src_lang=src_lang,
        dest_lang=dest_lang,
        ocr_lang=ocr_lang,
        on_retranslate=on_retranslate,
        on_recapture=on_recapture,
        spawn_x        = spawn_x,    
        spawn_y        = spawn_y,   
    )
    return overlay