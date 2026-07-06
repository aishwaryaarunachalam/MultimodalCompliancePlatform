from typing import List
import fitz  # PyMuPDF
from app.core.processors.image_processor import PageImage, _to_jpeg
from PIL import Image
import io


def extract_pages(file_bytes: bytes, max_pages: int = 10) -> List[PageImage]:
    """
    Render each PDF page to a JPEG image at 150 DPI.
    Returns up to max_pages PageImage objects.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages: List[PageImage] = []
    total = min(len(doc), max_pages)

    for i in range(total):
        page = doc[i]
        # Render at 150 DPI (2× default for better OCR quality)
        mat = fitz.Matrix(150 / 72, 150 / 72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        jpeg = _to_jpeg(img, quality=85)
        pages.append(PageImage(
            page_num=i + 1,
            image_bytes=jpeg,
            width=pix.width,
            height=pix.height,
            source_type="pdf",
        ))

    doc.close()
    return pages
