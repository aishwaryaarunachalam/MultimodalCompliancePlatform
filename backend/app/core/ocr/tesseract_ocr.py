import io
from typing import Tuple
from PIL import Image
from app.core.processors.image_processor import normalize_for_ocr


def run_tesseract(image_bytes: bytes) -> Tuple[str, float]:
    """
    Run pytesseract OCR on image bytes.
    Returns (text, confidence) where confidence is 0.0–1.0.
    """
    try:
        import pytesseract
    except ImportError:
        return "", 0.0

    preprocessed = normalize_for_ocr(image_bytes)
    img = Image.open(io.BytesIO(preprocessed))

    # Get word-level data for confidence scoring
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    confidences = [
        c for c in data["conf"]
        if isinstance(c, (int, float)) and c >= 0
    ]
    avg_conf = (sum(confidences) / len(confidences) / 100.0) if confidences else 0.0

    text = pytesseract.image_to_string(img, config="--psm 3")
    return text.strip(), round(avg_conf, 3)
