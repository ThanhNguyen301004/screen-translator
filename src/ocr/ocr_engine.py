from email.mime import image

import pytesseract
import cv2
import numpy as np
from PIL import Image
from ..utils.logging import logger

pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image: Image, lang='eng+vie'):
    try:
        img = np.array(image)

        # Resize x3 để tăng độ rõ
        img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Tăng contrast
        gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        # Adaptive threshold (tốt hơn threshold thường)
        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            15,
            10
        )

        custom_config = r'--oem 3 --psm 6'

        text = pytesseract.image_to_string(thresh, lang=lang, config=custom_config)

        print("OCR RAW TEXT:", repr(text))

        return text.strip()

    except Exception as e:
        logger.error(f"OCR error: {e}")
        return ""