import { useState, useCallback } from 'react';
import { submitReview, getReviews } from '../services/api';
import type { Review } from '../types';

export function useReviews() {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError]           = useState<string | null>(null);

  const submit = useCallback(async (body: {
    finding_id: string;
    reviewer_id: string;
    decision: string;
    notes?: string;
  }): Promise<Review | null> => {
    setSubmitting(true);
    setError(null);
    try {
      return await submitReview(body);
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? 'Failed to submit review.');
      return null;
    } finally {
      setSubmitting(false);
    }
  }, []);

  return { submit, submitting, error };
}

export function useDocumentReviews(documentId: string | null) {
  const [reviews, setReviews]   = useState<Review[]>([]);
  const [loading, setLoading]   = useState(false);

  const fetch = useCallback(async () => {
    if (!documentId) return;
    setLoading(true);
    try { setReviews(await getReviews(documentId)); }
    finally { setLoading(false); }
  }, [documentId]);

  return { reviews, loading, fetch };
}
