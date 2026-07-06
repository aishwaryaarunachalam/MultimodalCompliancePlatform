import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useDocument } from '../../hooks/useDocuments';
import { useFindings } from '../../hooks/useFindings';
import UploadProgress from '../upload/UploadProgress';
import FindingPanel from '../review/FindingPanel';
import type { Finding, DocumentPage } from '../../types';
import { ShieldAlert, Eye } from 'lucide-react';

const SEV_COLOR: Record<string, string> = {
  critical: 'border-l-red-500',
  high:     'border-l-orange-400',
  medium:   'border-l-yellow-400',
  low:      'border-l-blue-300',
};

function FindingRow({ f, onClick }: { f: Finding; onClick: () => void }) {
  return (
    <div
      onClick={onClick}
      className={`px-4 py-3 border-l-4 ${SEV_COLOR[f.severity] ?? 'border-l-gray-200'} cursor-pointer hover:bg-gray-50 transition`}
    >
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-semibold text-gray-500 uppercase mr-2">{f.finding_type === 'pii' ? 'PII' : 'POLICY'}</span>
          <span className="text-sm font-medium text-gray-800">{f.category}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium
            ${f.status === 'pending'    ? 'bg-yellow-50 text-yellow-600' :
              f.status === 'approved'   ? 'bg-red-50 text-red-600' :
              f.status === 'dismissed'  ? 'bg-gray-100 text-gray-400 line-through' :
              f.status === 'escalated'  ? 'bg-orange-50 text-orange-600' :
                                          'bg-purple-50 text-purple-600'}`}>
            {f.status}
          </span>
          <Eye size={13} className="text-gray-400" />
        </div>
      </div>
      {f.evidence_text && (
        <p className="text-xs text-gray-400 mt-0.5 truncate">{f.evidence_text}</p>
      )}
    </div>
  );
}

export default function DocumentDetail() {
  const { id } = useParams<{ id: string }>();
  const { doc, pages, loading } = useDocument(id ?? null);
  const { findings, refetch: refetchFindings } = useFindings({ document_id: id });
  const [selectedPage, setSelectedPage] = useState<DocumentPage | null>(null);
  const [activeFinding, setActiveFinding] = useState<Finding | null>(null);

  if (loading || !doc) return <div className="p-8 text-sm text-gray-400">Loading…</div>;

  if (doc.status === 'processing' || doc.status === 'uploaded') {
    return (
      <div className="p-8">
        <h1 className="text-xl font-semibold text-gray-800 mb-4">{doc.original_name}</h1>
        <UploadProgress docId={doc.id} />
      </div>
    );
  }

  const pageFIndings = selectedPage
    ? findings.filter(f => f.page_id === selectedPage.id)
    : findings;

  return (
    <div className="flex h-full overflow-hidden">
      {/* Page thumbnail strip */}
      {pages.length > 0 && (
        <aside className="w-36 bg-gray-50 border-r border-gray-200 overflow-y-auto p-2 space-y-2 shrink-0">
          <p className="text-xs text-gray-400 font-semibold px-1 mb-2">Pages</p>
          {pages.map(p => (
            <button key={p.id} onClick={() => setSelectedPage(p)}
              className={`w-full rounded-lg overflow-hidden border-2 transition
                ${selectedPage?.id === p.id ? 'border-blue-500' : 'border-transparent hover:border-gray-300'}`}>
              {p.image_url
                ? <img src={p.image_url} alt={`Page ${p.page_num}`} className="w-full object-cover" />
                : <div className="h-20 bg-gray-200 flex items-center justify-center text-xs text-gray-400">p.{p.page_num}</div>}
            </button>
          ))}
        </aside>
      )}

      {/* Main panel */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-5 py-3 flex items-center gap-3 shrink-0">
          <h1 className="font-semibold text-gray-800 truncate">{doc.original_name}</h1>
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ml-auto
            ${doc.risk_level === 'critical' ? 'bg-red-100 text-red-700' :
              doc.risk_level === 'high'     ? 'bg-orange-100 text-orange-700' :
              doc.risk_level === 'medium'   ? 'bg-yellow-100 text-yellow-700' :
                                             'bg-green-100 text-green-700'}`}>
            {doc.risk_level} risk
          </span>
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <ShieldAlert size={13} className="text-orange-400" />
            {doc.pii_count} PII · {doc.violation_count} violations
          </div>
        </div>

        {/* Findings list */}
        <div className="flex-1 overflow-y-auto divide-y divide-gray-100">
          {pageFIndings.length === 0
            ? <p className="text-center text-sm text-gray-400 py-12">No findings{selectedPage ? ' on this page' : ''}.</p>
            : pageFIndings.map(f => (
                <FindingRow key={f.id} f={f} onClick={() => setActiveFinding(f)} />
              ))}
        </div>
      </div>

      {/* Finding panel modal */}
      {activeFinding && (
        <FindingPanel
          finding={activeFinding}
          page={pages.find(p => p.id === activeFinding.page_id)}
          onClose={() => setActiveFinding(null)}
          onReviewed={() => { setActiveFinding(null); refetchFindings(); }}
        />
      )}
    </div>
  );
}
