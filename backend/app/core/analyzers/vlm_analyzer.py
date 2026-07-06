import asyncio
import base64
import json
import re
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings

# Module-level Gemini client (lazy init)
_gemini_model = None


def _get_model():
    global _gemini_model
    if _gemini_model is None:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)
    return _gemini_model


def _image_part(image_bytes: bytes) -> Dict:
    """Build a Gemini inline_data image part."""
    import google.generativeai as genai
    return {
        "inline_data": {
            "mime_type": "image/jpeg",
            "data": base64.b64encode(image_bytes).decode(),
        }
    }


def _parse_json_response(raw: str) -> List[Dict[str, Any]]:
    """Strip markdown fences and parse JSON array from VLM output."""
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        result = json.loads(text)
        return result if isinstance(result, list) else []
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return []


class VLMAnalyzer:

    PII_PROMPT = """You are a PII detection expert. Analyze the provided text and image for personally identifiable information.

For each PII instance found, return a JSON array:
[{{
  "pii_type": "<type: name|email|phone|ssn|credit_card|address|passport|medical_record|date_of_birth|ip_address|bank_account|tax_id|vehicle_id|biometric|other>",
  "evidence": "<exact text containing the PII>",
  "severity": "<low|medium|high|critical>",
  "confidence": <float 0.0-1.0>,
  "explanation": "<why this is PII and what risk it poses>"
}}]

Severity guide:
  critical = direct identity theft risk (SSN, full CC number, passport number)
  high     = significant re-identification risk (name + address together, full DOB)
  medium   = moderate risk (email alone, phone alone)
  low      = minimal risk alone (first name only, partial date)

Pre-identified regex candidates: {candidates}
Extracted text: {text}

Return ONLY the JSON array. Return [] if no PII found."""

    POLICY_PROMPT = """You are a compliance officer reviewing content against company policies.

Active policies:
{policies}

Analyze the text and image below for policy violations.

For each violation found, return a JSON array:
[{{
  "policy_id": "<uuid>",
  "policy_name": "<name>",
  "severity": "<low|medium|high|critical>",
  "confidence": <float 0.0-1.0>,
  "violated_text": "<exact excerpt that violates the policy>",
  "explanation": "<why this violates the policy and recommended action>"
}}]

Extracted text: {text}

Return ONLY the JSON array. Return [] if no violations found."""

    OCR_PROMPT = "Extract all text from this image exactly as it appears. Return only the raw text, no commentary."

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=30))
    async def _call_gemini(self, parts: list) -> str:
        """Async Gemini call with retry."""
        model = _get_model()
        # Run in thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: model.generate_content(parts))
        return response.text

    async def analyze_for_pii(
        self,
        image_bytes: bytes,
        text: str,
        regex_candidates: List[Dict],
    ) -> List[Dict[str, Any]]:
        """Run PII analysis on a page. Returns list of PII finding dicts."""
        if not settings.GEMINI_API_KEY:
            return []
        try:
            prompt = self.PII_PROMPT.format(
                candidates=json.dumps(regex_candidates),
                text=text[:4000],  # context window safety
            )
            parts = [_image_part(image_bytes), prompt]
            raw = await self._call_gemini(parts)
            await asyncio.sleep(settings.VLM_RATE_LIMIT_SLEEP)
            return _parse_json_response(raw)
        except Exception:
            return []

    async def analyze_for_policies(
        self,
        image_bytes: bytes,
        text: str,
        policies: List[Dict],
    ) -> List[Dict[str, Any]]:
        """Run policy violation analysis. Returns list of violation dicts."""
        if not settings.GEMINI_API_KEY or not policies:
            return []
        try:
            policy_str = json.dumps([
                {"id": str(p["id"]), "name": p["name"], "rules": p["rules"]}
                for p in policies
            ], indent=2)
            prompt = self.POLICY_PROMPT.format(policies=policy_str, text=text[:4000])
            parts = [_image_part(image_bytes), prompt]
            raw = await self._call_gemini(parts)
            await asyncio.sleep(settings.VLM_RATE_LIMIT_SLEEP)
            return _parse_json_response(raw)
        except Exception:
            return []

    async def ocr_fallback(self, image_bytes: bytes) -> str:
        """Use Gemini Vision as OCR when Tesseract confidence is too low."""
        if not settings.GEMINI_API_KEY:
            return ""
        try:
            parts = [_image_part(image_bytes), self.OCR_PROMPT]
            raw = await self._call_gemini(parts)
            await asyncio.sleep(settings.VLM_RATE_LIMIT_SLEEP)
            return raw.strip()
        except Exception:
            return ""
