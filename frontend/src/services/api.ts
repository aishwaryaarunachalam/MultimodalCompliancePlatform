import axios from 'axios';
import type {
  Document, DocumentPage, DocumentStatus,
  Finding, Review, Policy, DashboardStats
} from '../types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1',
  timeout: 60_000,
  headers: import.meta.env.VITE_API_KEY
    ? { 'X-API-Key': import.meta.env.VITE_API_KEY }
    : {},
});

// Retry once on 503 (Render cold start)
api.interceptors.response.use(
  r => r,
  async err => {
    if (err.response?.status === 503 && !err.config._retry) {
      err.config._retry = true;
      await new Promise(r => setTimeout(r, 3000));
      return api(err.config);
    }
    return Promise.reject(err);
  }
);

// ── Upload ────────────────────────────────────────────────────────────────────
export const uploadFile = (file: File, onProgress?: (pct: number) => void) => {
  const form = new FormData();
  form.append('file', file);
  return api.post<{ doc_id: string; status: string; file_type: string }>(
    '/upload',
    form,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: e => {
        if (onProgress && e.total) onProgress(Math.round(e.loaded / e.total * 100));
      },
    }
  ).then(r => r.data);
};

// ── Documents ─────────────────────────────────────────────────────────────────
export const getDocuments = (params?: { status?: string; risk_level?: string; file_type?: string; limit?: number }) =>
  api.get<Document[]>('/documents', { params }).then(r => r.data);

export const getDocument = (id: string) =>
  api.get<Document>(`/documents/${id}`).then(r => r.data);

export const getDocumentStatus = (id: string) =>
  api.get<DocumentStatus>(`/documents/${id}/status`).then(r => r.data);

export const getDocumentPages = (id: string) =>
  api.get<DocumentPage[]>(`/documents/${id}/pages`).then(r => r.data);

export const deleteDocument = (id: string) =>
  api.delete(`/documents/${id}`);

// ── Findings ──────────────────────────────────────────────────────────────────
export const getFindings = (params?: {
  document_id?: string; status?: string; severity?: string;
  finding_type?: string; limit?: number; offset?: number;
}) => api.get<Finding[]>('/findings', { params }).then(r => r.data);

export const getFinding = (id: string) =>
  api.get<Finding>(`/findings/${id}`).then(r => r.data);

// ── Reviews ───────────────────────────────────────────────────────────────────
export const submitReview = (body: {
  finding_id: string; reviewer_id: string; decision: string; notes?: string;
}) => api.post<Review>('/reviews', body).then(r => r.data);

export const getReviews = (document_id: string) =>
  api.get<Review[]>('/reviews', { params: { document_id } }).then(r => r.data);

// ── Policies ──────────────────────────────────────────────────────────────────
export const getPolicies    = (active_only = false) =>
  api.get<Policy[]>('/policies', { params: { active_only } }).then(r => r.data);

export const createPolicy   = (body: Partial<Policy>) =>
  api.post<Policy>('/policies', body).then(r => r.data);

export const updatePolicy   = (id: string, body: Partial<Policy>) =>
  api.put<Policy>(`/policies/${id}`, body).then(r => r.data);

export const deletePolicy   = (id: string) =>
  api.delete(`/policies/${id}`);

// ── Analytics ─────────────────────────────────────────────────────────────────
export const getDashboard = (days = 7) =>
  api.get<DashboardStats>('/analytics/dashboard', { params: { days } }).then(r => r.data);

export default api;
