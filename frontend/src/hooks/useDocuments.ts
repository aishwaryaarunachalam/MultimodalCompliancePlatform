import { useState, useEffect, useCallback, useRef } from 'react';
import { getDocuments, getDocument, getDocumentStatus, getDocumentPages, uploadFile, deleteDocument } from '../services/api';
import type { Document, DocumentPage } from '../types';

export function useDocuments(filters?: { status?: string; risk_level?: string; file_type?: string }) {
  const [docs, setDocs]       = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);

  const fetch = useCallback(async () => {
    setLoading(true);
    try { setDocs(await getDocuments({ ...filters, limit: 50 })); }
    finally { setLoading(false); }
  }, [JSON.stringify(filters)]);

  useEffect(() => { fetch(); }, [fetch]);

  const remove = async (id: string) => {
    await deleteDocument(id);
    setDocs(d => d.filter(x => x.id !== id));
  };

  return { docs, loading, refetch: fetch, remove };
}

export function useDocument(id: string | null) {
  const [doc, setDoc]         = useState<Document | null>(null);
  const [pages, setPages]     = useState<DocumentPage[]>([]);
  const [loading, setLoading] = useState(false);
  const pollRef               = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);

    const load = async () => {
      const d = await getDocument(id);
      setDoc(d);
      if (d.status === 'completed') {
        const p = await getDocumentPages(id);
        setPages(p);
      }
      setLoading(false);
    };
    load();

    // Poll while processing
    pollRef.current = setInterval(async () => {
      const d = await getDocument(id);
      setDoc(d);
      if (d.status === 'completed' || d.status === 'failed') {
        if (pollRef.current) clearInterval(pollRef.current);
        if (d.status === 'completed') {
          const p = await getDocumentPages(id);
          setPages(p);
        }
      }
    }, 3000);

    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [id]);

  return { doc, pages, loading };
}

export function useUpload() {
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [error, setError]       = useState<string | null>(null);
  const [result, setResult]     = useState<{ doc_id: string; file_type: string } | null>(null);

  const upload = async (file: File) => {
    setUploading(true);
    setError(null);
    setProgress(0);
    setResult(null);
    try {
      const res = await uploadFile(file, setProgress);
      setResult(res);
      return res;
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? 'Upload failed.');
      return null;
    } finally {
      setUploading(false);
    }
  };

  const reset = () => { setProgress(0); setError(null); setResult(null); };

  return { upload, uploading, progress, error, result, reset };
}

export function useDocumentStatus(docId: string | null) {
  const [status, setStatus] = useState<any>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!docId) return;
    const poll = async () => {
      try {
        const s = await getDocumentStatus(docId);
        setStatus(s);
        if (s.status === 'completed' || s.status === 'failed') {
          if (pollRef.current) clearInterval(pollRef.current);
        }
      } catch { /* ignore */ }
    };
    poll();
    pollRef.current = setInterval(poll, 3000);
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [docId]);

  return status;
}
