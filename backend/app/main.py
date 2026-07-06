from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db.session import init_db
from app.api.routes import health, upload, documents, findings, reviews, policies, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Multimodal Compliance Platform",
    description="PII and policy violation detection for PDFs, images, and video.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional API key middleware — only active when API_KEY is configured
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    if settings.API_KEY and request.url.path not in ("/api/v1/health", "/docs", "/openapi.json"):
        key = request.headers.get("X-API-Key", "")
        if key != settings.API_KEY:
            return JSONResponse(status_code=401, content={"detail": "Invalid or missing API key"})
    return await call_next(request)

PREFIX = "/api/v1"
app.include_router(health.router,     prefix=PREFIX,                  tags=["health"])
app.include_router(upload.router,     prefix=f"{PREFIX}/upload",      tags=["upload"])
app.include_router(documents.router,  prefix=f"{PREFIX}/documents",   tags=["documents"])
app.include_router(findings.router,   prefix=f"{PREFIX}/findings",    tags=["findings"])
app.include_router(reviews.router,    prefix=f"{PREFIX}/reviews",     tags=["reviews"])
app.include_router(policies.router,   prefix=f"{PREFIX}/policies",    tags=["policies"])
app.include_router(analytics.router,  prefix=f"{PREFIX}/analytics",   tags=["analytics"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc)})
