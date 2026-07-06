import { useState } from 'react';
import { useFindings } from '../../hooks/useFindings';
import { useAppStore } from '../../store/appStore';
import ReviewCard from './ReviewCard';
import type { Severity } from '../../types';

const SEVERITY_ORDER: Record<Severity, number> = { critical: 4, high: 3, medium: 2, low: 1 };

export default function ReviewQueue() {
  const { reviewerName, setReviewerName } = useAppStore();
  const [typeFilter, setTypeFilter] = useState('');
  const { findings, loading, refetch, updateLocal } = useFindings({
    status: 'pending',
    finding_type: typeFilter || undefined,
    limit: 100,
  });

  const sorted = [...findings].sort(
    (a, b) => (SEVERITY_ORDER[b.severity as Severity] ?? 0) - (SEVERITY_ORDER[a.severity as Severity] ?? 0)
  );

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold text-gray-800">
          Review Queue <span className="text-sm text-gray-400 font-normal">({findings.length} pending)</span>
        </h1>
        <div className="flex gap-2">
          <select value={typeFilter} onChange={e => setTypeFilter(e.target.value)}
            className="text-sm border border-gray-300 rounded-lg px-2 py-1.5">
            <option value="">All types</option>
            <option value="pii">PII only</option>
            <option value="policy_violation">Policy only</option>
          </select>
        </div>
      </div>

      {/* Reviewer name */}
      <div className="mb-5">
        <label className="block text-xs font-medium text-gray-500 mb-1">Your Name / Email</label>
        <input
          value={reviewerName}
          onChange={e => setReviewerName(e.target.value)}
          placeholder="alice@company.com"
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-64 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
      </div>

      {loading ? <p className="text-sm text-gray-400">Loading…</p> : (
        <div className="space-y-3">
          {sorted.map(f => (
            <ReviewCard
              key={f.id}
              finding={f}
              reviewerName={reviewerName}
              onReviewed={(id, status) => { updateLocal(id, status); }}
            />
          ))}
          {sorted.length === 0 && (
            <div className="text-center py-12 text-gray-400 text-sm bg-white rounded-xl border border-gray-200">
              🎉 No pending findings. All clear!
            </div>
          )}
        </div>
      )}
    </div>
  );
}
