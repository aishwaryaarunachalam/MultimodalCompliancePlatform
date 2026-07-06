import { useState, useEffect, useCallback } from 'react';
import { getFindings } from '../services/api';
import type { Finding } from '../types';

export function useFindings(params?: {
  document_id?: string;
  status?: string;
  severity?: string;
  finding_type?: string;
  limit?: number;
}) {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loading, setLoading]   = useState(true);

  const fetch = useCallback(async () => {
    setLoading(true);
    try { setFindings(await getFindings({ limit: 100, ...params })); }
    finally { setLoading(false); }
  }, [JSON.stringify(params)]);

  useEffect(() => { fetch(); }, [fetch]);

  const updateLocal = (id: string, status: string) => {
    setFindings(prev => prev.map(f => f.id === id ? { ...f, status: status as any } : f));
  };

  return { findings, loading, refetch: fetch, updateLocal };
}
