import io
import pytest
from PIL import Image
from app.core.processors.image_processor import normalize_for_ocr, resize_for_vlm, PageImage, _to_jpeg


def _make_test_image(w: int = 200, h: int = 100, color: str = "white") -> bytes:
    img = Image.new("RGB", (w, h), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_normalize_for_ocr_returns_bytes():
    img_bytes = _make_test_image()
    result = normalize_for_ocr(img_bytes)
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_resize_for_vlm_reduces_large_image():
    large = _make_test_image(w=4000, h=3000)
    result = resize_for_vlm(large, max_side=2048)
    img = Image.open(io.BytesIO(result))
    assert max(img.size) <= 2048


def test_resize_for_vlm_leaves_small_image():
    small = _make_test_image(w=800, h=600)
    result = resize_for_vlm(small, max_side=2048)
    img = Image.open(io.BytesIO(result))
    assert img.size == (800, 600)


def test_pdf_processor_returns_page_images():
    """Basic test: ensure pdf_processor returns PageImage objects for a valid PDF."""
    try:
        import fitz
    except ImportError:
        pytest.skip("PyMuPDF not installed")

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Hello compliance world")
    pdf_bytes = doc.tobytes()
    doc.close()

    from app.core.processors.pdf_processor import extract_pages
    pages = extract_pages(pdf_bytes, max_pages=5)
    assert len(pages) == 1
    assert pages[0].page_num == 1
    assert pages[0].source_type == "pdf"
    assert len(pages[0].image_bytes) > 0
