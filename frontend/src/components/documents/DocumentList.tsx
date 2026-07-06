import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Trash2, FileText, Image, Video, RefreshCw } from 'lucide-react';
import { useDocuments } from '../../hooks/useDocuments';
import type { Document, RiskLevel } from '../../types';

const RISK_STYLES: Record<RiskLevel, string> = {
  critical: 'bg-red-100 text-red-700',
  high:     'bg-orange-100 text-orange-700',
  medium:   'bg-yellow-100 text-yellow-700',
  low:      'bg-blue-100 text-blue-700',
  none:     'bg-green-100 text-green-700',
};

const STATUS_STYLES: Record<string, string> = {
  completed:  'bg-green-50 text-green-600',
  processing: 'bg-blue-50 text-blue-600',
  uploaded:   'bg-gray-50 text-gray-500',
  failed:     'bg-red-50 text-red-500',
};

function TypeIcon({ type }: { type: string }) {
  if (type === 'image') return <Image size={14} className="text-green-400" />;
  if (type === 'video') return <Video size={14} className="text-purple-400" />;
  return <FileText size={14} className="text-blue-400" />;
}

export default function DocumentList() {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState('');
  const [riskFilter, setRiskFilter]     = useState('');
  const { docs, loading, refetch, remove } = useDocuments({
    status:     statusFilter || undefined,
    risk_level: riskFilter   || undefined,
  });

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold text-gray-800">Documents</h1>
        <div className="flex items-center gap-2">
          <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)}
            className="text-sm border border-gray-300 rounded-lg px-2 py-1.5">
            <option value="">All statuses</option>
            {['uploaded','processing','completed','failed'].map(s => <option key={s}>{s}</option>)}
          </select>
          <select value={riskFilter} onChange={e => setRiskFilter(e.target.value)}
            className="text-sm border border-gray-300 rounded-lg px-2 py-1.5">
            <option value="">All risk levels</option>
            {['none','low','medium','high','critical'].map(r => <option key={r}>{r}</option>)}
          </select>
          <button onClick={refetch} className="text-gray-400 hover:text-blue-600 transition">
            <RefreshCw size={16} />
          </button>
        </div>
      </div>

      {loading ? <p className="text-sm text-gray-400">Loading…</p> : (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                {['File','Type','Status','Risk','PII','Violations','Uploaded'].map(h => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">{h}</th>
                ))}
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {docs.map(doc => (
                <tr key={doc.id} className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => navigate(`/documents/${doc.id}`)}>
                  <td className="px-4 py-3 font-medium text-gray-800 truncate max-w-xs">{doc.original_name}</td>
                  <td className="px-4 py-3"><TypeIcon type={doc.file_type} /></td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_STYLES[doc.status] ?? ''}`}>
                      {doc.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${RISK_STYLES[doc.risk_level]}`}>
                      {doc.risk_level}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-600">{doc.pii_count}</td>
                  <td className="px-4 py-3 text-gray-600">{doc.violation_count}</td>
                  <td className="px-4 py-3 text-gray-400 text-xs">{new Date(doc.uploaded_at).toLocaleDateString()}</td>
                  <td className="px-4 py-3">
                    <button onClick={e => { e.stopPropagation(); remove(doc.id); }}
                      className="text-gray-300 hover:text-red-400 transition">
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
              {docs.length === 0 && (
                <tr><td colSpan={8} className="text-center py-12 text-gray-400 text-sm">No documents yet.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
