import { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell,
  PieChart, Pie, Legend,
} from 'recharts';
import { getDashboard } from '../../services/api';
import type { DashboardStats } from '../../types';

const SEV_COLORS: Record<string, string> = {
  critical: '#ef4444',
  high:     '#f97316',
  medium:   '#eab308',
  low:      '#3b82f6',
};

export default function ViolationChart() {
  const [data, setData] = useState<DashboardStats | null>(null);

  useEffect(() => { getDashboard(30).then(setData).catch(() => {}); }, []);

  if (!data) return null;

  const sevData = Object.entries(data.severity_breakdown ?? {}).map(([k, v]) => ({ name: k, count: v }));
  const piiData = (data.top_pii_categories ?? []).slice(0, 6).map(d => ({ name: d.category, value: d.count }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Severity breakdown bar chart */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">Findings by Severity (30d)</h3>
        {sevData.length > 0 ? (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={sevData} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {sevData.map((entry, i) => (
                  <Cell key={i} fill={SEV_COLORS[entry.name] ?? '#6b7280'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : <p className="text-sm text-gray-400 text-center py-8">No findings yet.</p>}
      </div>

      {/* Top PII categories pie chart */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">Top PII Categories (30d)</h3>
        {piiData.length > 0 ? (
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={piiData}
                dataKey="value"
                nameKey="name"
                cx="50%" cy="50%"
                outerRadius={80}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                labelLine={false}
              >
                {piiData.map((_, i) => (
                  <Cell key={i} fill={['#3b82f6','#8b5cf6','#ec4899','#f97316','#22c55e','#06b6d4'][i % 6]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        ) : <p className="text-sm text-gray-400 text-center py-8">No PII found yet.</p>}
      </div>
    </div>
  );
}
