# src/capture/screen_capture.py
from mss import mss  # Requires 'mss' library: pip install mss
from PIL import Image  # Requires 'Pillow' library: pip install Pillow
import ctypes

def get_scale_factor():
    """Lấy DPI scale factor của Windows (vd: 1.25, 1.5)"""
    try:
        # Yêu cầu Windows trả về physical DPI thay vì logical
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    except:
        pass
    try:
        hdc = ctypes.windll.user32.GetDC(0)
        dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
        ctypes.windll.user32.ReleaseDC(0, hdc)
        return dpi / 96.0  # 96 DPI = 100% scale
    except:
        return 1.0

def capture_screen_area(x, y, width, height):
    scale = get_scale_factor()
    
    # Chuyển từ logical sang physical pixels
    px = int(x * scale)
    py = int(y * scale)
    pw = int(width * scale)
    ph = int(height * scale)
    
    print(f"Scale factor: {scale}, Physical region: {px}, {py}, {pw}, {ph}")

    with mss() as sct:
        monitor = {"top": py, "left": px, "width": pw, "height": ph}
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        return img
    
def capture_screen_area(x, y, width, height):
    print("Capture region:", x, y, width, height)

    with mss() as sct:
        monitor = {"top": y, "left": x, "width": width, "height": height}
        sct_img = sct.grab(monitor)

        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        print("Captured size:", img.size)

        img.save("debug_capture.png")  # Lưu lại để xem thật sự chụp được gì

        return img