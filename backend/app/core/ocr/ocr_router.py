from typing import Tuple
from app.config import settings

OCR_FALLBACK_THRESHOLD = 0.6


async def extract_text(
    image_bytes: bytes,
    vlm_analyzer=None,
) -> Tuple[str, float, str]:
    """
    Route OCR request based on OCR_ENGINE config.
    Returns (text, confidence, engine_name).

    Strategy:
      - surya:     always use Surya (if SURYA_ENABLED)
      - tesseract: always use Tesseract
      - auto:      try Tesseract; if confidence < threshold, fall back to Gemini Vision OCR
    """
    engine = settings.OCR_ENGINE

    if engine == "surya" and settings.SURYA_ENABLED:
        from app.core.ocr.surya_ocr import run_surya
        text, conf = run_surya(image_bytes)
        return text, conf, "surya"

    if engine == "tesseract" or engine == "auto":
        from app.core.ocr.tesseract_ocr import run_tesseract
        text, conf = run_tesseract(image_bytes)

        if engine == "tesseract":
            return text, conf, "tesseract"

        # auto: fall back to Gemini if confidence is too low
        if conf < OCR_FALLBACK_THRESHOLD and vlm_analyzer is not None:
            gemini_text = await vlm_analyzer.ocr_fallback(image_bytes)
            return gemini_text, 0.85, "gemini"

        return text, conf, "tesseract"

    # Final fallback
    from app.core.ocr.tesseract_ocr import run_tesseract
    text, conf = run_tesseract(image_bytes)
    return text, conf, "tesseract"
