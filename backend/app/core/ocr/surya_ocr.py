import io
from typing import Tuple

# Surya is a heavy PyTorch model — only loaded if SURYA_ENABLED=true
_surya_model = None
_surya_processor = None


def _load_surya():
    global _surya_model, _surya_processor
    if _surya_model is None:
        from surya.model.detection.model import load_model as load_det_model
        from surya.model.detection.processor import load_processor as load_det_processor
        _surya_model = load_det_model()
        _surya_processor = load_det_processor()
    return _surya_model, _surya_processor


def run_surya(image_bytes: bytes) -> Tuple[str, float]:
    """
    Run Surya OCR on image bytes.
    Returns (text, confidence). Only usable when SURYA_ENABLED=true and
    sufficient RAM is available (≥2 GB recommended).
    """
    try:
        from PIL import Image
        from surya.ocr import run_ocr
        from surya.model.recognition.model import load_model as load_rec_model
        from surya.model.recognition.processor import load_processor as load_rec_processor

        model, processor = _load_surya()
        rec_model = load_rec_model()
        rec_processor = load_rec_processor()

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        results = run_ocr([img], [["en"]], model, processor, rec_model, rec_processor)

        lines = []
        confidences = []
        for page_result in results:
            for block in page_result.text_lines:
                lines.append(block.text)
                confidences.append(block.confidence)

        text = "\n".join(lines)
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
        return text.strip(), round(avg_conf, 3)

    except Exception as exc:
        return "", 0.0
