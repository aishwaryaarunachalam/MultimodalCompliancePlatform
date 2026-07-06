import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePolicies } from '../../hooks/usePolicies';
import { Plus, Trash2, Edit2, ToggleLeft, ToggleRight } from 'lucide-react';

export default function PolicyList() {
  const navigate = useNavigate();
  const { policies, loading, remove, toggle } = usePolicies();

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold text-gray-800">Policies</h1>
        <button onClick={() => navigate('/policies/new')}
          className="flex items-center gap-1 bg-blue-600 text-white px-3 py-2 rounded-lg text-sm hover:bg-blue-700 transition">
          <Plus size={14} /> New Policy
        </button>
      </div>

      {loading ? <p className="text-sm text-gray-400">Loading…</p> : (
        <div className="space-y-3">
          {policies.map(p => (
            <div key={p.id} className={`bg-white rounded-xl border shadow-sm overflow-hidden transition
              ${p.is_active ? 'border-gray-200' : 'border-gray-100 opacity-60'}`}>
              <div className="px-5 py-4 flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-800">{p.name}</p>
                  {p.description && <p className="text-xs text-gray-400 mt-0.5">{p.description}</p>}
                  <div className="flex flex-wrap gap-1 mt-2">
                    {(p.rules ?? []).map((r, i) => (
                      <span key={i} className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded font-mono">
                        {r.type}:{r.severity}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <button onClick={() => toggle(p)} className="text-gray-400 hover:text-blue-600 transition">
                    {p.is_active ? <ToggleRight size={20} className="text-blue-500" /> : <ToggleLeft size={20} />}
                  </button>
                  <button onClick={() => navigate(`/policies/${p.id}/edit`)} className="text-gray-400 hover:text-blue-600 transition">
                    <Edit2 size={15} />
                  </button>
                  <button onClick={() => remove(p.id)} className="text-gray-300 hover:text-red-400 transition">
                    <Trash2 size={15} />
                  </button>
                </div>
              </div>
            </div>
          ))}
          {policies.length === 0 && (
            <p className="text-center text-sm text-gray-400 py-12">No policies yet. Create one to start detecting violations.</p>
          )}
        </div>
      )}
    </div>
  );
}
