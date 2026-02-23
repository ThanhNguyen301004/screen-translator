# src/ocr/ocr_engine.py
import pytesseract
import cv2
import numpy as np
from PIL import Image
from ..utils.logging import logger

pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'

def _preprocess(img_bgr: np.ndarray) -> np.ndarray:
    """
    Tiền xử lý ảnh để OCR nhận diện tốt cả text tối-nền-sáng
    lẫn text sáng-nền-tối.
    """
    # 1. Resize x3
    img = cv2.resize(img_bgr, None, fx=3, fy=3,
                     interpolation=cv2.INTER_CUBIC)

    # 2. Chuyển sang grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. Tăng contrast bằng CLAHE (tốt hơn convertScaleAbs vì thích nghi vùng)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # 4. Khử nhiễu nhẹ
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # 5. AUTO-INVERT: nếu nền tối thì invert để text luôn là màu tối
    mean_brightness = np.mean(gray)
    if mean_brightness < 127:
        gray = cv2.bitwise_not(gray)

    # 6. Adaptive threshold
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,   # Gaussian mượt hơn MEAN_C
        cv2.THRESH_BINARY,
        11, 4
    )

    return thresh


def extract_text_from_image(image: Image.Image, lang: str = 'eng+vie') -> str:
    try:
        img_bgr = np.array(image)

        # PIL trả về RGB, OpenCV cần BGR
        if img_bgr.ndim == 3 and img_bgr.shape[2] == 3:
            img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_RGB2BGR)

        thresh = _preprocess(img_bgr)

        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(thresh, lang=lang,
                                           config=custom_config)

        print("OCR RAW TEXT:", repr(text))
        return text.strip()

    except Exception as e:
        logger.error(f"OCR error: {e}")
        return ""