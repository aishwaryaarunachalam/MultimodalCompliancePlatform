from typing import List
from app.core.processors.image_processor import PageImage, resize_for_vlm
from app.config import settings


def route_file(mime_type: str, file_bytes: bytes) -> List[PageImage]:
    """
    Detect file category from MIME type and dispatch to the correct processor.
    Returns a list of PageImage objects for downstream OCR and analysis.
    """
    mime = mime_type.lower()

    if mime == "application/pdf":
        from app.core.processors.pdf_processor import extract_pages
        pages = extract_pages(file_bytes, max_pages=settings.MAX_PAGES)

    elif mime.startswith("image/"):
        from app.core.processors.image_processor import PageImage as PI
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        w, h = img.size
        jpeg = resize_for_vlm(file_bytes)
        pages = [PI(page_num=1, image_bytes=jpeg, width=w, height=h, source_type="image")]

    elif mime.startswith("video/"):
        from app.core.processors.video_processor import extract_frames
        pages = extract_frames(
            file_bytes,
            max_seconds=settings.VIDEO_MAX_SECONDS,
            fps=1,
        )[:settings.MAX_PAGES]

    else:
        raise ValueError(f"Unsupported MIME type: {mime_type}")

    # Ensure all page images are VLM-safe size
    resized = []
    for p in pages:
        p.image_bytes = resize_for_vlm(p.image_bytes)
        resized.append(p)
    return resized
