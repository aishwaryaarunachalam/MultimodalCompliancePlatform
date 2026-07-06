import re
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class PolicyFinding:
    policy_id: str
    policy_name: str
    severity: str
    confidence: float
    violated_text: str
    explanation: str


class PolicyChecker:

    def _run_keyword_check(
        self,
        text: str,
        policies: List[Dict],
    ) -> List[Dict[str, Any]]:
        """
        Fast keyword/regex pre-filter.
        Returns candidate matches for VLM confirmation.
        """
        candidates = []
        text_lower = text.lower()

        for policy in policies:
            for rule in policy.get("rules", []):
                rule_type = rule.get("type", "")
                value = rule.get("value", "")
                severity = rule.get("severity", "medium")

                if rule_type == "keyword":
                    if value.lower() in text_lower:
                        # Find actual excerpt
                        idx = text_lower.find(value.lower())
                        excerpt = text[max(0, idx - 30): idx + len(value) + 30]
                        candidates.append({
                            "policy_id":    str(policy["id"]),
                            "policy_name":  policy["name"],
                            "rule_type":    "keyword",
                            "violated_text": excerpt,
                            "severity":     severity,
                        })

                elif rule_type == "regex":
                    try:
                        pattern = re.compile(value, re.IGNORECASE)
                        for match in pattern.finditer(text):
                            candidates.append({
                                "policy_id":    str(policy["id"]),
                                "policy_name":  policy["name"],
                                "rule_type":    "regex",
                                "violated_text": match.group(),
                                "severity":     severity,
                            })
                    except re.error:
                        pass

        return candidates

    async def run_full(
        self,
        image_bytes: bytes,
        text: str,
        policies: List[Dict],
        vlm,
    ) -> List[PolicyFinding]:
        """
        Two-stage policy check:
        1. Keyword/regex pre-filter (fast)
        2. VLM semantic analysis (catches nuanced violations)
        """
        if not policies:
            return []

        keyword_candidates = self._run_keyword_check(text, policies)

        # Always run VLM for semantic rules and visual content
        vlm_findings = await vlm.analyze_for_policies(image_bytes, text, policies)

        results: List[PolicyFinding] = []
        seen = set()

        for f in vlm_findings:
            key = (f.get("policy_id", ""), (f.get("violated_text", "") or "")[:80])
            if key not in seen:
                seen.add(key)
                results.append(PolicyFinding(
                    policy_id=f.get("policy_id", ""),
                    policy_name=f.get("policy_name", ""),
                    severity=f.get("severity", "medium"),
                    confidence=float(f.get("confidence", 0.7)),
                    violated_text=f.get("violated_text", ""),
                    explanation=f.get("explanation", ""),
                ))

        # Add keyword-only candidates not caught by VLM
        vlm_texts = {f.violated_text for f in results}
        for c in keyword_candidates:
            if c["violated_text"] not in vlm_texts:
                key = (c["policy_id"], c["violated_text"][:80])
                if key not in seen:
                    seen.add(key)
                    results.append(PolicyFinding(
                        policy_id=c["policy_id"],
                        policy_name=c["policy_name"],
                        severity=c["severity"],
                        confidence=0.75,
                        violated_text=c["violated_text"],
                        explanation=f"Matched {c['rule_type']} rule in policy '{c['policy_name']}'.",
                    ))

        return results
