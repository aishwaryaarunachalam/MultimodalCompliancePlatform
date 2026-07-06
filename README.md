# Multimodal Compliance & Content Intelligence Platform

![Python](https://img.shields.io/badge/python-3.11-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green) ![React](https://img.shields.io/badge/React-18-61dafb) ![Gemini](https://img.shields.io/badge/Gemini-1.5--flash-orange)

A self-hostable compliance engine that analyzes PDFs, images, and short video clips for PII and policy violations using Vision-Language Models and OCR. Provides policy-aligned explanations and a full reviewer workflow. **$0/month to host.**

---

## Features

- **Multimodal ingestion** — PDF (per-page), images (PNG/JPG/WEBP), video clips (MP4 ≤ 60s)
- **Two-stage PII detection** — regex pre-filter + Gemini VLM confirmation (15 PII categories)
- **Configurable policy engine** — keyword, regex, and semantic (VLM-evaluated) rules
- **Reviewer workflow** — Approve / Dismiss / Escalate / Redact with full audit trail
- **Document risk scoring** — auto-computed from worst pending/approved finding
- **Analytics dashboard** — severity breakdown, PII category distribution, processing trends

---

## Quick Start (Docker)

```bash
git clone https://github.com/yourname/multimodal-compliance
cd multimodal-compliance
cp .env.example .env        # add GEMINI_API_KEY + R2 credentials
cd infra && docker compose -f docker-compose.lite.yml up -d
cd ../backend && pip install -r requirements.txt
alembic upgrade head
python ../scripts/seed_policies.py
```

Frontend: http://localhost:3000 · API docs: http://localhost:8000/docs

---

## Zero-Cost Deployment

| Service | Provider | Free Tier |
|---|---|---|
| PostgreSQL | Neon.tech | 0.5 GB |
| Backend | Render.com | 750 hrs/mo |
| Frontend | Vercel | Unlimited |
| File storage | Cloudflare R2 | 10 GB, no egress |
| Job cache | Upstash Redis | 10k cmd/day |
| VLM | Google Gemini | 1M tokens/day |

See [docs/deployment.md](docs/deployment.md) for full setup guide.

---

## Supported File Types

| Type | Formats | Limit |
|---|---|---|
| PDF | .pdf | 10 pages max |
| Image | .png .jpg .jpeg .webp .gif | 20 MB |
| Video | .mp4 .mov .webm | 60s / 50 MB |
