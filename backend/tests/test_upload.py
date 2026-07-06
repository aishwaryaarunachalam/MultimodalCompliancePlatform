import io
import pytest
from PIL import Image
from unittest.mock import patch, MagicMock, AsyncMock


def _make_pdf_bytes() -> bytes:
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "SSN: 123-45-6789. Contact admin@corp.com")
    b = doc.tobytes()
    doc.close()
    return b


def _make_image_bytes() -> bytes:
    img = Image.new("RGB", (400, 200), color="white")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.mark.asyncio
async def test_upload_unsupported_type(client):
    r = await client.post(
        "/api/v1/upload",
        files={"file": ("test.xyz", b"fake content", "application/octet-stream")},
    )
    assert r.status_code == 415


@pytest.mark.asyncio
async def test_upload_too_large(client):
    big = b"x" * (25 * 1024 * 1024)
    r = await client.post(
        "/api/v1/upload",
        files={"file": ("big.pdf", big, "application/pdf")},
    )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_get_nonexistent_document(client):
    import uuid
    r = await client.get(f"/api/v1/documents/{uuid.uuid4()}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_health_endpoint(client):
    with patch("app.api.routes.health.get_redis") as mock_redis_dep:
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_redis_dep.return_value = mock_redis
        r = await client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_policy_crud(client, sample_policy_payload):
    r = await client.post("/api/v1/policies", json=sample_policy_payload)
    assert r.status_code == 201
    policy_id = r.json()["id"]

    r2 = await client.get(f"/api/v1/policies/{policy_id}")
    assert r2.status_code == 200
    assert r2.json()["name"] == sample_policy_payload["name"]

    r3 = await client.put(f"/api/v1/policies/{policy_id}", json={"is_active": False})
    assert r3.status_code == 200
    assert r3.json()["is_active"] is False

    r4 = await client.delete(f"/api/v1/policies/{policy_id}")
    assert r4.status_code == 204


@pytest.mark.asyncio
async def test_review_invalid_decision(client):
    import uuid
    r = await client.post("/api/v1/reviews", json={
        "finding_id":  str(uuid.uuid4()),
        "reviewer_id": "alice@corp.com",
        "decision":    "invalid_decision",
    })
    assert r.status_code == 422
