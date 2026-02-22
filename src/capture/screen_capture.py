# src/capture/screen_capture.py
from mss import mss  # Requires 'mss' library: pip install mss
from PIL import Image  # Requires 'Pillow' library: pip install Pillow

def capture_screen_area(x, y, width, height):
    with mss() as sct:
        monitor = {"top": y, "left": x, "width": width, "height": height}
        sct_img = sct.grab(monitor)
        return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")