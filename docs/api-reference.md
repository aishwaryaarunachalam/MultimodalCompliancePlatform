# API Reference — Multimodal Compliance Platform

Base URL: `http://localhost:8000/api/v1`

Set `X-API-Key` header if `API_KEY` env var is configured.

---

## GET /health
Liveness probe. Returns DB + Redis status.
```json
{ "status": "ok", "db": "ok", "redis": "ok" }
```

---

## POST /upload
Upload a file for analysis. Multipart form-data.

| Field | Type | Description |
|---|---|---|
| `file` | File | PDF, image, or video (max 20 MB) |

**Response 200**
```json
{ "doc_id": "uuid", "status": "uploaded", "file_type": "pdf", "size_mb": 1.4 }
```
**Errors:** `400` (too large) · `415` (unsupported type)

---

## Documents — `/documents`

| Method | Path | Description |
|---|---|---|
| GET | /documents | List documents (filter: status, risk_level, file_type) |
| GET | /documents/{id} | Get document detail |
| GET | /documents/{id}/status | Poll processing status |
| GET | /documents/{id}/pages | Get extracted pages with presigned image URLs |
| DELETE | /documents/{id} | Delete document + R2 objects |

**Status response:**
```json
{
  "document_id": "uuid",
  "status": "processing",
  "job_status": "processing",
  "total_pages": 5,
  "processed_pages": 2,
  "risk_level": "high",
  "pii_count": 3,
  "violation_count": 1
}
```

---

## Findings — `/findings`

| Method | Path | Description |
|---|---|---|
| GET | /findings | List findings (filter: document_id, status, severity, finding_type) |
| GET | /findings/{id} | Get single finding |

**Finding object:**
```json
{
  "id": "uuid",
  "document_id": "uuid",
  "page_id": "uuid",
  "finding_type": "pii",
  "category": "email",
  "severity": "medium",
  "confidence": 0.92,
  "evidence_text": "john.doe@example.com",
  "explanation": "Corporate email address found; medium re-identification risk.",
  "bounding_box": null,
  "status": "pending",
  "created_at": "2024-01-01T12:00:00"
}
```

---

## Reviews — `/reviews`

### POST /reviews
Submit a reviewer decision.

```json
{
  "finding_id":  "uuid",
  "reviewer_id": "alice@company.com",
  "decision":    "approve",
  "notes":       "Confirmed PII in HR document."
}
```

Valid decisions: `approve` · `dismiss` · `escalate` · `redact`

**Response 201:** Review object

### GET /reviews?document_id={uuid}
Audit trail for a document. Returns list of Review objects.

---

## Policies — `/policies`

| Method | Path | Description |
|---|---|---|
| POST | /policies | Create policy |
| GET | /policies?active_only=true | List policies |
| GET | /policies/{id} | Get policy |
| PUT | /policies/{id} | Update policy / toggle active |
| DELETE | /policies/{id} | Delete policy |

**Policy body:**
```json
{
  "name": "No Competitor Mentions",
  "description": "Block competitor brand references",
  "rules": [
    { "type": "keyword",  "value": "CompetitorCo", "severity": "medium" },
    { "type": "regex",    "value": "\\bCompetitor\\s*Co\\.?\\b", "severity": "medium" },
    { "type": "semantic", "value": "References to competing products or brands", "severity": "low" }
  ],
  "is_active": true
}
```

Rule types: `keyword` · `regex` · `semantic`
Severity values: `low` · `medium` · `high` · `critical`

---

## Analytics — `/analytics`

### GET /analytics/dashboard?days=7

```json
{
  "period_days": 7,
  "total_documents": 42,
  "total_pii": 187,
  "total_violations": 23,
  "severity_breakdown": {
    "critical": 5,
    "high": 18,
    "medium": 112,
    "low": 75
  },
  "top_pii_categories": [
    { "category": "email",  "count": 94 },
    { "category": "phone",  "count": 42 },
    { "category": "ssn",    "count": 8  }
  ]
}
```
