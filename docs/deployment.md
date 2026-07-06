# Deployment Guide — Zero Cost

## Prerequisites
- GitHub account (to push the repo)
- Google account (Gemini API key — free)
- Cloudflare account (R2 storage — free tier)

---

## Step 1 — Cloudflare R2 (File Storage)

1. Sign up at **cloudflare.com** → Dashboard → R2 Object Storage
2. Create bucket: `multimodal-compliance`
3. Settings → CORS Policy → add:
```json
[
  {
    "AllowedOrigins": ["https://your-app.vercel.app", "http://localhost:5173"],
    "AllowedMethods": ["GET", "PUT", "DELETE"],
    "AllowedHeaders": ["*"]
  }
]
```
4. Create R2 API Token (permission: Object Read & Write on your bucket)
5. Note: `Account ID`, `Access Key ID`, `Secret Access Key`, `Endpoint URL`

**Free tier:** 10 GB storage · 10M Class A ops · 100M Class B ops · No egress fees

---

## Step 2 — Upstash Redis (Job Status Cache)

1. Sign up at **upstash.com** (GitHub OAuth)
2. Create database → select region near Render deployment (US East)
3. Copy `REDIS_URL` — format: `rediss://default:<token>@<host>:6380`

**Free tier:** 10,000 commands/day · 256 MB

---

## Step 3 — Neon PostgreSQL

1. Sign up at **neon.tech** (GitHub OAuth)
2. Create project: `multimodal-compliance`
3. Copy connection string → convert to asyncpg format:
   `postgresql+asyncpg://user:pass@ep-xxx.neon.tech/neondb?sslmode=require`

**Free tier:** 0.5 GB · 1 compute unit · Auto-suspend

---

## Step 4 — Google Gemini API Key

1. Go to **aistudio.google.com**
2. Create API Key (no credit card required)
3. Set `GEMINI_MODEL=gemini-1.5-flash` (free tier model)

**Free tier:** 15 RPM · 1M tokens/day

---

## Step 5 — Backend on Render.com

1. Sign up at **render.com** (GitHub OAuth)
2. New → Web Service → connect your GitHub repo
3. Settings:
   - **Root directory:** `backend`
   - **Build command:** `apt-get install -y tesseract-ocr tesseract-ocr-eng libmagic1 libgl1 libglib2.0-0 && pip install -r requirements.txt`
   - **Start command:** `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add all environment variables from `.env.example`
5. Note your service URL: `https://your-service.onrender.com`

### render.yaml (alternative — add to repo root)
```yaml
services:
  - type: web
    name: multimodal-compliance-backend
    runtime: python
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
    nativeBuildCommand: apt-get install -y tesseract-ocr tesseract-ocr-eng libmagic1 libgl1 libglib2.0-0
```

**Free tier:** 512 MB RAM · Shared CPU · 750 hrs/mo · Spins down after 15 min idle

---

## Step 6 — Frontend on Vercel

1. Sign up at **vercel.com** (GitHub OAuth)
2. New Project → import repo → Framework: **Vite**
3. Root directory: `frontend`
4. Environment variables:
   - `VITE_API_URL` = `https://your-service.onrender.com/api/v1`
   - `VITE_API_KEY` = (your API_KEY if set)
5. Deploy → auto-deploys on every push to `main`

---

## Step 7 — Keep-Warm Ping (Prevent Cold Start)

1. Sign up at **uptimerobot.com** (free)
2. New Monitor → HTTP(s)
3. URL: `https://your-service.onrender.com/api/v1/health`
4. Interval: **5 minutes**

This keeps Render awake during demos.

---

## Step 8 — Seed Default Policies

After deployment, run once:
```bash
DATABASE_URL="your-neon-url" python scripts/seed_policies.py
```

Or trigger via the UI by creating policies manually.

---

## Cost Summary

| Service | Provider | Limit | Cost |
|---|---|---|---|
| PostgreSQL | Neon.tech | 0.5 GB | $0 |
| Backend | Render.com | 750 hrs/mo | $0 |
| Frontend | Vercel | Unlimited | $0 |
| File storage | Cloudflare R2 | 10 GB | $0 |
| Job cache | Upstash Redis | 10k cmd/day | $0 |
| VLM | Google Gemini | 1M tok/day | $0 |
| Keep-warm | UptimeRobot | 50 monitors | $0 |
| **Total** | | | **$0/month** |

---

## Common Issues

**Tesseract not found on Render**
Add to build command: `apt-get install -y tesseract-ocr tesseract-ocr-eng`

**python-magic error: libmagic not found**
Add to build command: `apt-get install -y libmagic1`

**OpenCV import error**
Ensure `opencv-python-headless` (not `opencv-python`) is in requirements.txt

**Gemini 429 Too Many Requests**
Increase `VLM_RATE_LIMIT_SLEEP` env var to `5.0` or higher

**Neon connection timeout**
Add `?sslmode=require&connect_timeout=10` to `DATABASE_URL`

**R2 upload fails**
Verify `R2_ENDPOINT_URL` format: `https://<account_id>.r2.cloudflarestorage.com`
