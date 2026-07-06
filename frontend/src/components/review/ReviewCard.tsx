import { useState } from 'react';
import { CheckCircle, XCircle, AlertTriangle, Scissors } from 'lucide-react';
import { useReviews } from '../../hooks/useReviews';
import type { Finding } from '../../types';

const SEV_COLOR: Record<string, string> = {
  critical: 'border-red-400',
  high:     'border-orange-400',
  medium:   'border-yellow-400',
  low:      'border-blue-300',
};

interface Props {
  finding: Finding;
  reviewerName: string;
  onReviewed: (id: string, newStatus: string) => void;
}

const DECISIONS = [
  { key: 'approve',  label: 'Approve',  icon: <CheckCircle  size={13} />, cls: 'bg-red-50 text-red-600 hover:bg-red-100' },
  { key: 'dismiss',  label: 'Dismiss',  icon: <XCircle      size={13} />, cls: 'bg-gray-100 text-gray-500 hover:bg-gray-200' },
  { key: 'escalate', label: 'Escalate', icon: <AlertTriangle size={13} />, cls: 'bg-orange-50 text-orange-600 hover:bg-orange-100' },
  { key: 'redact',   label: 'Redact',   icon: <Scissors     size={13} />, cls: 'bg-purple-50 text-purple-600 hover:bg-purple-100' },
];

const DECISION_STATUS: Record<string, string> = {
  approve: 'approved', dismiss: 'dismissed', escalate: 'escalated', redact: 'redacted',
};

export default function ReviewCard({ finding, reviewerName, onReviewed }: Props) {
  const { submit, submitting } = useReviews();
  const [notes, setNotes] = useState('');
  const [done, setDone]   = useState(false);

  async function handle(decision: string) {
    if (!reviewerName.trim()) return alert('Please enter your name/email above.');
    const result = await submit({ finding_id: finding.id, reviewer_id: reviewerName, decision, notes });
    if (result) { setDone(true); onReviewed(finding.id, DECISION_STATUS[decision]); }
  }

  if (done) return null;

  return (
    <div className={`bg-white rounded-xl border border-gray-200 border-l-4 ${SEV_COLOR[finding.severity] ?? ''} shadow-sm overflow-hidden`}>
      <div className="px-5 py-4">
        <div className="flex items-start justify-between gap-2 mb-2">
          <div>
            <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded font-medium mr-2 uppercase">
              {finding.finding_type === 'pii' ? 'PII' : 'Policy'}
            </span>
            <span className="font-medium text-gray-800">{finding.category}</span>
          </div>
          <span className={`text-xs px-2 py-0.5 rounded-full font-semibold shrink-0
            ${finding.severity === 'critical' ? 'bg-red-100 text-red-700' :
              finding.severity === 'high'     ? 'bg-orange-100 text-orange-700' :
              finding.severity === 'medium'   ? 'bg-yellow-100 text-yellow-700' :
                                               'bg-blue-100 text-blue-700'}`}>
            {finding.severity}
          </span>
        </div>

        {finding.evidence_text && (
          <p className="text-sm bg-gray-50 border border-gray-100 rounded-lg px-3 py-2 text-gray-700 font-mono text-xs mb-2">
            {finding.evidence_text}
          </p>
        )}

        {finding.explanation && (
          <p className="text-xs text-gray-500 mb-3">{finding.explanation}</p>
        )}

        <textarea
          value={notes}
          onChange={e => setNotes(e.target.value)}
          placeholder="Optional notes…"
          rows={2}
          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-xs text-gray-600 resize-none focus:outline-none focus:ring-1 focus:ring-blue-400 mb-3"
        />

        <div className="flex gap-2 flex-wrap">
          {DECISIONS.map(d => (
            <button
              key={d.key}
              onClick={() => handle(d.key)}
              disabled={submitting}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium transition disabled:opacity-50 ${d.cls}`}
            >
              {d.icon} {d.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
