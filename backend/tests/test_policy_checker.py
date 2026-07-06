import pytest
from unittest.mock import AsyncMock, MagicMock
from app.core.analyzers.policy_checker import PolicyChecker


DEMO_POLICIES = [
    {
        "id": "policy-001",
        "name": "Competitor Mention Ban",
        "rules": [
            {"type": "keyword", "value": "CompetitorCo", "severity": "medium", "description": "Competitor name"},
            {"type": "regex",   "value": r"\b100%\s+effective\b", "severity": "high", "description": "Absolute efficacy claim"},
        ],
    },
    {
        "id": "policy-002",
        "name": "Hate Speech Prohibition",
        "rules": [
            {"type": "semantic", "value": "Content implying racial or ethnic superiority", "severity": "critical"}
        ],
    },
]


def test_keyword_match_found():
    checker = PolicyChecker()
    candidates = checker._run_keyword_check("We are better than CompetitorCo in every way.", DEMO_POLICIES)
    assert any(c["policy_id"] == "policy-001" for c in candidates)


def test_keyword_no_match():
    checker = PolicyChecker()
    candidates = checker._run_keyword_check("We offer excellent quality products.", DEMO_POLICIES)
    assert candidates == []


def test_regex_match_found():
    checker = PolicyChecker()
    candidates = checker._run_keyword_check("Our product is 100% effective for everyone.", DEMO_POLICIES)
    assert any(c["policy_id"] == "policy-001" for c in candidates)


@pytest.mark.asyncio
async def test_policy_checker_full_with_mock_vlm():
    mock_vlm = MagicMock()
    mock_vlm.analyze_for_policies = AsyncMock(return_value=[
        {
            "policy_id":     "policy-002",
            "policy_name":   "Hate Speech Prohibition",
            "severity":      "critical",
            "confidence":    0.92,
            "violated_text": "some inflammatory text",
            "explanation":   "Content implies ethnic superiority.",
        }
    ])
    checker = PolicyChecker()
    findings = await checker.run_full(
        image_bytes=b"fake",
        text="Some inflammatory text here.",
        policies=DEMO_POLICIES,
        vlm=mock_vlm,
    )
    assert len(findings) >= 1
    assert any(f.policy_id == "policy-002" for f in findings)
    assert any(f.severity == "critical" for f in findings)


@pytest.mark.asyncio
async def test_policy_checker_empty_policies():
    mock_vlm = MagicMock()
    checker = PolicyChecker()
    findings = await checker.run_full(b"fake", "text", [], mock_vlm)
    assert findings == []
