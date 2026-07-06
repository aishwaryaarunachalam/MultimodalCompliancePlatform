import { useState, useEffect, useCallback } from 'react';
import { getPolicies, createPolicy, updatePolicy, deletePolicy } from '../services/api';
import type { Policy } from '../types';

export function usePolicies(activeOnly = false) {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [loading, setLoading]   = useState(true);

  const fetch = useCallback(async () => {
    setLoading(true);
    try { setPolicies(await getPolicies(activeOnly)); }
    finally { setLoading(false); }
  }, [activeOnly]);

  useEffect(() => { fetch(); }, [fetch]);

  const add = async (body: Partial<Policy>) => {
    const created = await createPolicy(body);
    setPolicies(prev => [...prev, created]);
    return created;
  };

  const update = async (id: string, body: Partial<Policy>) => {
    const updated = await updatePolicy(id, body);
    setPolicies(prev => prev.map(p => p.id === id ? updated : p));
    return updated;
  };

  const remove = async (id: string) => {
    await deletePolicy(id);
    setPolicies(prev => prev.filter(p => p.id !== id));
  };

  const toggle = async (p: Policy) => update(p.id, { is_active: !p.is_active });

  return { policies, loading, refetch: fetch, add, update, remove, toggle };
}
