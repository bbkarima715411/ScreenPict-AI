import re
from pathlib import Path

import cv2


def extract_barcode_numbers(image_path: Path) -> list[str]:
    barcode_detector = cv2.barcode.BarcodeDetector()
    image = cv2.imread(str(image_path))

    if image is None:
        return []

    try:
        decoded_texts, _, _ = barcode_detector.detectAndDecode(image)
    except ValueError:
        decoded_text, _, _ = barcode_detector.detectAndDecode(image)
        decoded_texts = [decoded_text]

    if isinstance(decoded_texts, str):
        decoded_texts = [decoded_texts]

    barcode_numbers = []
    for decoded_text in decoded_texts:
        barcode_numbers.extend(re.findall(r"\d{3,}", decoded_text or ""))

    return sorted(set(barcode_numbers), key=len, reverse=True)
