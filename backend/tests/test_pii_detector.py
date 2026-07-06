import pytest
from app.core.analyzers.pii_detector import run_regex, PIIDetector


def test_regex_detects_email():
    text = "Contact us at john.doe@example.com for more info."
    candidates = run_regex(text)
    types = [c["pii_type"] for c in candidates]
    assert "email" in types
    evidences = [c["evidence"] for c in candidates]
    assert "john.doe@example.com" in evidences


def test_regex_detects_ssn():
    text = "SSN: 123-45-6789 is on file."
    candidates = run_regex(text)
    types = [c["pii_type"] for c in candidates]
    assert "ssn" in types


def test_regex_detects_phone():
    text = "Call us at (555) 123-4567 anytime."
    candidates = run_regex(text)
    types = [c["pii_type"] for c in candidates]
    assert "phone" in types


def test_regex_no_false_positive_on_clean_text():
    text = "The weather today is sunny and warm."
    candidates = run_regex(text)
    assert candidates == []


def test_regex_detects_multiple_types():
    text = "Email: bob@corp.com, SSN: 987-65-4321, Phone: 800-555-0199"
    candidates = run_regex(text)
    types = {c["pii_type"] for c in candidates}
    assert "email" in types
    assert "ssn" in types
    assert "phone" in types


def test_regex_deduplicates():
    text = "Email: test@test.com and again test@test.com"
    candidates = run_regex(text)
    emails = [c for c in candidates if c["pii_type"] == "email"]
    assert len(emails) == 1


@pytest.mark.asyncio
async def test_pii_detector_full_with_mock_vlm():
    from unittest.mock import AsyncMock, MagicMock
    mock_vlm = MagicMock()
    mock_vlm.analyze_for_pii = AsyncMock(return_value=[
        {
            "pii_type": "email",
            "evidence": "alice@company.com",
            "severity": "medium",
            "confidence": 0.95,
            "explanation": "A corporate email address found in the document.",
        }
    ])
    detector = PIIDetector()
    findings = await detector.run_full(
        image_bytes=b"fake_image",
        text="Contact alice@company.com for details.",
        vlm=mock_vlm,
    )
    assert len(findings) >= 1
    assert any(f.pii_type == "email" for f in findings)
    assert any(f.evidence == "alice@company.com" for f in findings)
