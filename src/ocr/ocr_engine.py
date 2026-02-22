import pytesseract
import cv2
import numpy as np
from PIL import Image
from ..utils.logging import logger

pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image: Image, lang='eng+vie'):
    try:
        # Convert PIL image to OpenCV format
        img = np.array(image)

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Increase contrast
        thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

        text = pytesseract.image_to_string(thresh, lang=lang)
        return text.strip()

    except Exception as e:
        logger.error(f"OCR error: {e}")
        return ""