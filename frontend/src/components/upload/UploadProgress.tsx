import { useDocumentStatus } from '../../hooks/useDocuments';
import { Loader, CheckCircle, XCircle, ShieldAlert } from 'lucide-react';

interface Props { docId: string; onDone?: () => void; }

export default function UploadProgress({ docId, onDone }: Props) {
  const status = useDocumentStatus(docId);

  if (!status) return (
    <div className="flex items-center gap-2 text-sm text-gray-500 mt-6 justify-center">
      <Loader size={16} className="animate-spin" /> Initialising analysis…
    </div>
  );

  const pct = status.total_pages
    ? Math.round((status.processed_pages / status.total_pages) * 100)
    : 0;

  return (
    <div className="max-w-md mx-auto mt-8 bg-white rounded-2xl border border-gray-200 shadow-sm p-6 space-y-4">
      <div className="flex items-center gap-3">
        {status.status === 'processing' && <Loader size={18} className="animate-spin text-blue-500" />}
        {status.status === 'completed'  && <CheckCircle size={18} className="text-green-500" />}
        {status.status === 'failed'     && <XCircle size={18} className="text-red-500" />}
        <span className="font-medium text-gray-700 capitalize">{status.status}</span>
      </div>

      {status.status === 'processing' && (
        <>
          <p className="text-xs text-gray-500">
            {status.job_status === 'processing'
              ? `Analyzing page ${status.processed_pages ?? 0} of ${status.total_pages ?? '?'}…`
              : 'Queued for analysis…'}
          </p>
          <div className="w-full bg-gray-100 rounded-full h-2">
            <div className="bg-blue-500 h-2 rounded-full transition-all" style={{ width: `${pct}%` }} />
          </div>
        </>
      )}

      {status.status === 'completed' && (
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm">
            <ShieldAlert size={14} className="text-orange-400" />
            <span className="text-gray-600">{status.pii_count} PII instances · {status.violation_count} policy violations</span>
          </div>
          <div className={`inline-flex items-center gap-1 text-xs px-3 py-1 rounded-full font-medium
            ${status.risk_level === 'critical' ? 'bg-red-100 text-red-700' :
              status.risk_level === 'high'     ? 'bg-orange-100 text-orange-700' :
              status.risk_level === 'medium'   ? 'bg-yellow-100 text-yellow-700' :
              status.risk_level === 'low'      ? 'bg-blue-100 text-blue-700' :
                                                 'bg-green-100 text-green-700'}`}>
            Risk: {status.risk_level}
          </div>
          {onDone && (
            <button onClick={onDone} className="mt-2 w-full bg-blue-600 text-white py-2 rounded-lg text-sm hover:bg-blue-700 transition">
              View Results
            </button>
          )}
        </div>
      )}
    </div>
  );
}
