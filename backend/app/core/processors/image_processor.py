import io
from dataclasses import dataclass
from typing import List
from PIL import Image, ImageOps, ImageEnhance


@dataclass
class PageImage:
    page_num: int         # 1-indexed
    image_bytes: bytes    # JPEG bytes
    width: int
    height: int
    source_type: str      # pdf | image | video


def _to_jpeg(pil_img: Image.Image, quality: int = 85) -> bytes:
    buf = io.BytesIO()
    pil_img.convert("RGB").save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def normalize_for_ocr(image_bytes: bytes) -> bytes:
    """
    Preprocess an image for better Tesseract OCR:
      - Convert to grayscale
      - Auto-equalize histogram (deskew approximation)
      - Sharpen slightly
    Returns JPEG bytes.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("L")
    img = ImageOps.autocontrast(img, cutoff=1)
    img = ImageEnhance.Sharpness(img.convert("RGB")).enhance(1.5)
    return _to_jpeg(img, quality=90)


def resize_for_vlm(image_bytes: bytes, max_side: int = 2048) -> bytes:
    """
    Resize so the longest side is ≤ max_side (Gemini Vision limit).
    Returns JPEG bytes.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    if max(w, h) > max_side:
        ratio = max_side / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    return _to_jpeg(img)
