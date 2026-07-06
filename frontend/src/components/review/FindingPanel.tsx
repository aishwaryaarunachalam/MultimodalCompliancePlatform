import { useState } from 'react';
import { X, CheckCircle, XCircle, AlertTriangle, Scissors } from 'lucide-react';
import { useReviews } from '../../hooks/useReviews';
import { useAppStore } from '../../store/appStore';
import type { Finding, DocumentPage } from '../../types';

interface Props {
  finding: Finding;
  page?: DocumentPage;
  onClose: () => void;
  onReviewed: () => void;
}

export default function FindingPanel({ finding, page, onClose, onReviewed }: Props) {
  const { reviewerName } = useAppStore();
  const { submit, submitting } = useReviews();
  const [notes, setNotes] = useState('');

  async function handle(decision: string) {
    if (!reviewerName.trim()) return alert('Set your name in Review Queue first.');
    const r = await submit({ finding_id: finding.id, reviewer_id: reviewerName, decision, notes });
    if (r) onReviewed();
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <div>
            <span className="text-xs font-semibold text-gray-400 uppercase mr-2">
              {finding.finding_type === 'pii' ? 'PII' : 'Policy Violation'}
            </span>
            <span className="font-semibold text-gray-800">{finding.category}</span>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700"><X size={18} /></button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          {/* Page image */}
          {page?.image_url && (
            <img src={page.image_url} alt={`Page ${page.page_num}`}
              className="w-full rounded-xl border border-gray-200 object-contain max-h-64" />
          )}

          {/* Severity + confidence */}
          <div className="flex gap-3">
            <span className={`text-xs px-2 py-0.5 rounded-full font-semibold
              ${finding.severity === 'critical' ? 'bg-red-100 text-red-700' :
                finding.severity === 'high'     ? 'bg-orange-100 text-orange-700' :
                finding.severity === 'medium'   ? 'bg-yellow-100 text-yellow-700' :
                                                 'bg-blue-100 text-blue-700'}`}>
              {finding.severity}
            </span>
            {finding.confidence != null && (
              <span className="text-xs text-gray-400">
                Confidence: {(finding.confidence * 100).toFixed(0)}%
              </span>
            )}
          </div>

          {/* Evidence */}
          {finding.evidence_text && (
            <div>
              <p className="text-xs font-semibold text-gray-500 mb-1">Evidence</p>
              <p className="bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-xs font-mono text-gray-700">
                {finding.evidence_text}
              </p>
            </div>
          )}

          {/* Explanation */}
          {finding.explanation && (
            <div>
              <p className="text-xs font-semibold text-gray-500 mb-1">Explanation</p>
              <p className="text-sm text-gray-600 leading-relaxed">{finding.explanation}</p>
            </div>
          )}

          {/* OCR text */}
          {page?.extracted_text && (
            <details className="border border-gray-100 rounded-lg">
              <summary className="px-3 py-2 text-xs text-gray-400 cursor-pointer">Page OCR text</summary>
              <pre className="px-3 py-2 text-xs text-gray-500 whitespace-pre-wrap max-h-40 overflow-y-auto">
                {page.extracted_text}
              </pre>
            </details>
          )}

          {/* Notes */}
          <textarea value={notes} onChange={e => setNotes(e.target.value)}
            placeholder="Optional reviewer notes…" rows={3}
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:ring-1 focus:ring-blue-400" />
        </div>

        {/* Actions */}
        <div className="border-t border-gray-100 px-5 py-4 flex gap-2 flex-wrap">
          {[
            { d: 'approve',  label: 'Approve',  icon: <CheckCircle size={13} />,  cls: 'bg-red-600 text-white hover:bg-red-700' },
            { d: 'dismiss',  label: 'Dismiss',  icon: <XCircle size={13} />,      cls: 'bg-gray-100 text-gray-600 hover:bg-gray-200' },
            { d: 'escalate', label: 'Escalate', icon: <AlertTriangle size={13} />, cls: 'bg-orange-500 text-white hover:bg-orange-600' },
            { d: 'redact',   label: 'Redact',   icon: <Scissors size={13} />,     cls: 'bg-purple-600 text-white hover:bg-purple-700' },
          ].map(({ d, label, icon, cls }) => (
            <button key={d} onClick={() => handle(d)} disabled={submitting}
              className={`flex items-center gap-1 px-4 py-2 rounded-lg text-sm font-medium transition disabled:opacity-50 ${cls}`}>
              {icon} {label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
