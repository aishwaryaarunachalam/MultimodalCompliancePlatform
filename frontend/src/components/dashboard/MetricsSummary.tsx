import { useEffect, useState } from 'react';
import { getDashboard } from '../../services/api';
import type { DashboardStats } from '../../types';
import { FileText, ShieldAlert, AlertTriangle, Clock } from 'lucide-react';

function KpiCard({ label, value, icon, color }: { label: string; value: string; icon: React.ReactNode; color: string }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 flex items-center gap-4">
      <div className={`p-3 rounded-lg ${color}`}>{icon}</div>
      <div>
        <p className="text-2xl font-bold text-gray-800">{value}</p>
        <p className="text-xs text-gray-500">{label}</p>
      </div>
    </div>
  );
}

export default function MetricsSummary() {
  const [data, setData]   = useState<DashboardStats | null>(null);
  const [days, setDays]   = useState(7);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getDashboard(days).then(setData).finally(() => setLoading(false));
  }, [days]);

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-gray-700">Overview</h2>
        <select value={days} onChange={e => setDays(+e.target.value)}
          className="text-xs border border-gray-300 rounded px-2 py-1">
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <div key={i} className="bg-white rounded-xl border h-20 animate-pulse" />)}
        </div>
      ) : data ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard label={`Docs processed (${days}d)`} value={String(data.total_documents)}
            icon={<FileText size={20} className="text-blue-600" />} color="bg-blue-50" />
          <KpiCard label="PII instances found" value={String(data.total_pii)}
            icon={<ShieldAlert size={20} className="text-red-500" />} color="bg-red-50" />
          <KpiCard label="Policy violations" value={String(data.total_violations)}
            icon={<AlertTriangle size={20} className="text-orange-500" />} color="bg-orange-50" />
          <KpiCard label="Severity breakdown" value={`${data.severity_breakdown?.critical ?? 0} critical`}
            icon={<Clock size={20} className="text-purple-500" />} color="bg-purple-50" />
        </div>
      ) : null}
    </div>
  );
}
