# Architecture — Multimodal Compliance Platform

## System Diagram

```
React (Vercel)  ──REST──►  FastAPI (Render)  ──►  PostgreSQL (Neon)
                                  │
                                  ├──► Cloudflare R2  (file storage)
                                  │
                                  └──► Upstash Redis   (job status)
                                  │
                    ┌─────────────▼─────────────┐
                    │  Analysis Pipeline        │
                    │  (BackgroundTask)          │
                    └─────────────┬─────────────┘
                                  │
            ┌─────────────────────┼──────────────────────┐
            ▼                     ▼                      ▼
     PDF Processor          Image Processor       Video Processor
     PyMuPDF                PIL normalize         OpenCV 1fps
     → page images          → resize 2048px       → frame images
            └─────────────────────┴──────────────────────┘
                                  │ List[PageImage]
                                  ▼
                          OCR Layer (per page)
                          Tesseract → text + confidence
                          if conf < 0.6 → Gemini Vision OCR
                                  │
                                  ▼
                        VLM Analyzer (Gemini 1.5 Flash)
                        ┌─────────────────────────────┐
                        │ PII Prompt → JSON findings  │
                        │ Policy Prompt → violations  │
                        └─────────────────────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 ▼                                 ▼
          PII Detector                    Policy Checker
          regex pre-filter               keyword/regex filter
          + VLM confirmation             + semantic VLM analysis
                 └────────────────┬────────────────┘
                                  ▼
                    Findings → PostgreSQL
                    Document risk level computed
                    Job status cached in Redis
```

## Key Design Decisions

### No Heavy ML on Free Tier
Surya OCR (PyTorch, ~2 GB RAM) is disabled on Render. Instead:
- **Tesseract** (lightweight, apt-installable) for primary OCR
- **Gemini Vision** as OCR fallback when Tesseract confidence < 60%

### Rate Limit Compliance (Gemini Free: 15 RPM)
- Pages processed serially (not parallel)
- `asyncio.sleep(4.0)` between Gemini calls
- `tenacity` retry with exponential backoff on 429

### Two-Stage Detection
- Stage 1: Regex/keyword (zero API cost, milliseconds)
- Stage 2: VLM confirmation (eliminates false positives, adds explanations)
- Merged and deduplicated by (type, evidence)

### Reviewer Workflow
- Findings prioritised: critical → high → medium → low
- Decisions: approve / dismiss / escalate / redact
- All decisions stored as immutable Review records (full audit trail)
- Document risk level auto-recomputed after each decision
