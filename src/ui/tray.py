# src/ui/tray.py
import threading
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

def _create_icon_image():
    """Tạo icon mặc định nếu không có file icon."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, 60, 60], fill="#1a73e8")
    draw.text((20, 18), "T", fill="white")
    return img

def run_tray(on_quit, icon_path: str = None):
    """
    Chạy system tray icon trong thread riêng.
    - Click vào icon: không làm gì (hotkey vẫn hoạt động ngầm)
    - Menu: chỉ có Exit
    """
    try:
        icon_img = Image.open(icon_path) if icon_path else _create_icon_image()
    except Exception:
        icon_img = _create_icon_image()

    def do_quit(icon, _item):
        icon.stop()
        on_quit()

    tray = pystray.Icon(
        name="ScreenTranslator",
        icon=icon_img,
        title="Screen Translator\nCtrl+Shift+L để chụp",
        menu=pystray.Menu(
            item("Screen Translator", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            item("Thoát", do_quit),
        ),
    )

    thread = threading.Thread(target=tray.run, daemon=True)
    thread.start()
    return tray