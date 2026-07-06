import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class PIIFinding:
    pii_type: str
    evidence: str
    severity: str
    confidence: float
    explanation: str


# Compiled regex patterns for 15 PII categories
PATTERNS: Dict[str, re.Pattern] = {
    "email":          re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
    "phone":          re.compile(r"\b(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "ssn":            re.compile(r"\b\d{3}[-\s]\d{2}[-\s]\d{4}\b"),
    "credit_card":    re.compile(r"\b(?:4\d{12}(?:\d{3})?|5[1-5]\d{14}|3[47]\d{13}|6(?:011|5\d{2})\d{12})\b"),
    "ip_address":     re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "date_of_birth":  re.compile(r"\b(?:DOB|Date of Birth|Born)[:\s]+\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}\b", re.IGNORECASE),
    "passport":       re.compile(r"\b[A-Z]{1,2}\d{6,9}\b"),
    "bank_account":   re.compile(r"\b\d{8,17}\b(?=.*(?:account|acct|bank))", re.IGNORECASE),
    "tax_id":         re.compile(r"\b\d{2}[-\s]\d{7}\b"),
    "medical_record": re.compile(r"\b(?:MRN|Medical Record)[:\s#]+[A-Z0-9\-]+\b", re.IGNORECASE),
    "vehicle_id":     re.compile(r"\b[A-Z]{1,3}[-\s]?\d{1,4}[-\s]?[A-Z]{0,3}\d{0,4}\b"),
    "zip_code":       re.compile(r"\b\d{5}(?:-\d{4})?\b"),
    "iban":           re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}(?:[A-Z0-9]?){0,16}\b"),
    "url":            re.compile(r"https?://[^\s]+"),
}

SEVERITY_MAP = {
    "ssn":            "critical",
    "credit_card":    "critical",
    "passport":       "critical",
    "medical_record": "high",
    "bank_account":   "high",
    "tax_id":         "high",
    "date_of_birth":  "high",
    "email":          "medium",
    "phone":          "medium",
    "iban":           "high",
    "ip_address":     "low",
    "zip_code":       "low",
    "vehicle_id":     "low",
    "url":            "low",
}


def run_regex(text: str) -> List[Dict[str, Any]]:
    """Fast regex pre-filter. Returns candidate dicts for VLM confirmation."""
    candidates = []
    for pii_type, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            candidates.append({
                "pii_type":  pii_type,
                "evidence":  match.group(),
                "severity":  SEVERITY_MAP.get(pii_type, "medium"),
                "start":     match.start(),
                "end":       match.end(),
            })
    # Deduplicate by (type, evidence)
    seen = set()
    unique = []
    for c in candidates:
        key = (c["pii_type"], c["evidence"])
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique


class PIIDetector:

    async def run_full(
        self,
        image_bytes: bytes,
        text: str,
        vlm,
    ) -> List[PIIFinding]:
        """
        Two-stage PII detection:
        1. Regex pre-filter (fast, zero API cost)
        2. VLM confirmation + additional visual PII detection
        Merges and deduplicates results.
        """
        regex_candidates = run_regex(text)
        vlm_findings = await vlm.analyze_for_pii(image_bytes, text, regex_candidates)

        results: List[PIIFinding] = []
        seen = set()

        for f in vlm_findings:
            key = (f.get("pii_type", "other"), (f.get("evidence", "") or "")[:80])
            if key not in seen:
                seen.add(key)
                results.append(PIIFinding(
                    pii_type=f.get("pii_type", "other"),
                    evidence=f.get("evidence", ""),
                    severity=f.get("severity", "medium"),
                    confidence=float(f.get("confidence", 0.7)),
                    explanation=f.get("explanation", ""),
                ))

        # Add regex-only candidates not caught by VLM (with lower confidence)
        vlm_evidences = {f.evidence for f in results}
        for c in regex_candidates:
            if c["evidence"] not in vlm_evidences:
                key = (c["pii_type"], c["evidence"][:80])
                if key not in seen:
                    seen.add(key)
                    results.append(PIIFinding(
                        pii_type=c["pii_type"],
                        evidence=c["evidence"],
                        severity=c["severity"],
                        confidence=0.6,
                        explanation=f"Detected by regex pattern for {c['pii_type']}.",
                    ))

        return results
