"""
CLI tool: run the full analysis pipeline on a local file without cloud storage.
Useful for development and debugging without R2 credentials.

Usage:
    cd backend
    python ../scripts/test_pipeline.py --file ../sample.pdf --output results.json
    python ../scripts/test_pipeline.py --file ../photo.jpg
"""
import argparse
import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


async def run(file_path: str, output_path: str):
    import magic
    from app.config import settings
    from app.core.processors.file_router import route_file
    from app.core.ocr.ocr_router import extract_text
    from app.core.analyzers.vlm_analyzer import VLMAnalyzer
    from app.core.analyzers.pii_detector import PIIDetector
    from app.core.analyzers.policy_checker import PolicyChecker

    file_bytes = Path(file_path).read_bytes()
    mime_type  = magic.from_buffer(file_bytes, mime=True)

    print(f"File:      {file_path}")
    print(f"MIME:      {mime_type}")
    print(f"Size:      {len(file_bytes) / 1024:.1f} KB")
    print(f"OCR:       {settings.OCR_ENGINE}")
    print(f"Gemini:    {'configured' if settings.GEMINI_API_KEY else 'NOT SET — PII/policy analysis will be skipped'}")
    print()

    pages = route_file(mime_type, file_bytes)
    print(f"Extracted {len(pages)} page(s)/frame(s).")

    vlm = VLMAnalyzer()
    pii_detector    = PIIDetector()
    policy_checker  = PolicyChecker()

    # Demo policies for standalone test
    demo_policies = [
        {
            "id": "demo-001",
            "name": "PII Policy",
            "rules": [
                {"type": "keyword", "value": "social security", "severity": "critical"},
                {"type": "regex",   "value": r"\d{3}-\d{2}-\d{4}", "severity": "critical"},
            ],
        }
    ]

    results = []

    for page in pages:
        print(f"  Analyzing page {page.page_num}…")

        text, ocr_conf, ocr_engine = await extract_text(page.image_bytes, vlm)
        print(f"    OCR ({ocr_engine}): {len(text)} chars, confidence {ocr_conf:.2f}")

        pii_findings   = await pii_detector.run_full(page.image_bytes, text, vlm)
        policy_findings = await policy_checker.run_full(page.image_bytes, text, demo_policies, vlm)

        print(f"    PII findings:    {len(pii_findings)}")
        print(f"    Policy findings: {len(policy_findings)}")

        results.append({
            "page_num":        page.page_num,
            "ocr_engine":      ocr_engine,
            "ocr_confidence":  ocr_conf,
            "text_length":     len(text),
            "pii_findings":    [
                {"type": f.pii_type, "evidence": f.evidence, "severity": f.severity, "confidence": f.confidence}
                for f in pii_findings
            ],
            "policy_findings": [
                {"policy": f.policy_name, "text": f.violated_text, "severity": f.severity}
                for f in policy_findings
            ],
        })

    # Summary
    total_pii    = sum(len(r["pii_findings"])    for r in results)
    total_policy = sum(len(r["policy_findings"]) for r in results)
    print(f"\nSummary: {total_pii} PII instances, {total_policy} policy violations across {len(pages)} page(s).")

    if output_path:
        Path(output_path).write_text(json.dumps(results, indent=2, ensure_ascii=False))
        print(f"Results written to {output_path}")
    else:
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the analysis pipeline on a local file.")
    parser.add_argument("--file",   required=True, help="Path to PDF, image, or video file")
    parser.add_argument("--output", default="",    help="Optional JSON output path")
    args = parser.parse_args()
    asyncio.run(run(args.file, args.output))
