import re
import shutil
from pathlib import Path

import cv2
import numpy as np
import pytesseract
from PIL import Image

from services.config import TESSERACT_CANDIDATES


def configure_tesseract() -> None:
    if shutil.which("tesseract"):
        return

    for candidate in TESSERACT_CANDIDATES:
        if candidate.exists():
            pytesseract.pytesseract.tesseract_cmd = str(candidate)
            return


def resize_for_analysis(image: np.ndarray, max_dimension: int = 1800) -> np.ndarray:
    height, width = image.shape[:2]
    largest_side = max(height, width)

    if largest_side <= max_dimension:
        return image

    scale = max_dimension / largest_side
    new_size = (int(width * scale), int(height * scale))
    return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)


def correct_contrast(gray_image: np.ndarray) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray_image)


def detect_rotation_angle(gray_image: np.ndarray) -> float:
    edges = cv2.Canny(gray_image, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=80, maxLineGap=12)

    if lines is None:
        return 0.0

    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        if -20 <= angle <= 20:
            angles.append(angle)

    if not angles:
        return 0.0

    return float(np.median(angles))


def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    if abs(angle) < 0.5:
        return image

    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, rotation_matrix, (width, height), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def crop_text_area(gray_image: np.ndarray) -> np.ndarray:
    threshold_image = cv2.adaptiveThreshold(
        gray_image,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31,
        8,
    )
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 5))
    dilated = cv2.dilate(threshold_image, kernel, iterations=2)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    image_area = gray_image.shape[0] * gray_image.shape[1]
    for contour in contours:
        x, y, width, height = cv2.boundingRect(contour)
        area = width * height
        if area > image_area * 0.002 and width > 30 and height > 8:
            boxes.append((x, y, width, height))

    if not boxes:
        return gray_image

    x_min = max(min(box[0] for box in boxes) - 18, 0)
    y_min = max(min(box[1] for box in boxes) - 18, 0)
    x_max = min(max(box[0] + box[2] for box in boxes) + 18, gray_image.shape[1])
    y_max = min(max(box[1] + box[3] for box in boxes) + 18, gray_image.shape[0])

    return gray_image[y_min:y_max, x_min:x_max]


def sharpen_edges(gray_image: np.ndarray) -> np.ndarray:
    blurred = cv2.GaussianBlur(gray_image, (0, 0), 1.0)
    return cv2.addWeighted(gray_image, 1.55, blurred, -0.55, 0)


def build_ocr_variants(image: Image.Image) -> list[np.ndarray]:
    rgb_image = np.array(image.convert("RGB"))
    resized_image = resize_for_analysis(rgb_image)
    gray_image = cv2.cvtColor(resized_image, cv2.COLOR_RGB2GRAY)
    contrasted_image = correct_contrast(gray_image)
    rotation_angle = detect_rotation_angle(contrasted_image)
    rotated_image = rotate_image(contrasted_image, rotation_angle)
    cropped_image = crop_text_area(rotated_image)
    denoised_image = cv2.fastNlMeansDenoising(cropped_image, None, 18, 7, 21)
    sharpened_image = sharpen_edges(denoised_image)
    scaled_image = cv2.resize(sharpened_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    threshold_image = cv2.adaptiveThreshold(
        scaled_image,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        2,
    )
    otsu_threshold = cv2.threshold(scaled_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    inverted_image = cv2.bitwise_not(threshold_image)

    return [scaled_image, threshold_image, otsu_threshold, inverted_image]


def extract_ocr_numbers(image: Image.Image) -> list[str]:
    numbers = []
    configs = [
        "--psm 6 -c tessedit_char_whitelist=0123456789",
        "--psm 11 -c tessedit_char_whitelist=0123456789",
        "--psm 12 -c tessedit_char_whitelist=0123456789",
    ]

    for variant in build_ocr_variants(image):
        for config in configs:
            raw_text = pytesseract.image_to_string(variant, config=config)
            numbers.extend(re.findall(r"\d{3,}", raw_text))

    return sorted(set(numbers), key=len, reverse=True)


def extract_ocr_text_items(image: Image.Image) -> list[str]:
    items = []
    configs = [
        "--psm 6",
        "--psm 11",
        "--psm 12",
    ]
    patterns = [
        r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+",
        r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b",
        r"\b\d{4}[./-]\d{1,2}[./-]\d{1,2}\b",
        r"\+?\d[\d\s().-]{6,}\d",
        r"\b[A-Z]{2,}[-_/]?[A-Z0-9]{3,}\b",
        r"\b\d{8,14}\b",
    ]

    for variant in build_ocr_variants(image):
        for config in configs:
            raw_text = pytesseract.image_to_string(variant, config=config)
            for pattern in patterns:
                items.extend(re.findall(pattern, raw_text, flags=re.IGNORECASE))

    cleaned_items = [item.strip() for item in items if item.strip()]
    return sorted(set(cleaned_items), key=len, reverse=True)
