# src/capture/screen_capture.py
from mss import mss  # Requires 'mss' library: pip install mss
from PIL import Image  # Requires 'Pillow' library: pip install Pillow

def capture_screen_area(x, y, width, height):
    print("Capture region:", x, y, width, height)

    with mss() as sct:
        monitor = {"top": y, "left": x, "width": width, "height": height}
        sct_img = sct.grab(monitor)

        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        print("Captured size:", img.size)

        img.save("debug_capture.png")  # Lưu lại để xem thật sự chụp được gì

        return img