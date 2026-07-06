import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { usePolicies } from '../../hooks/usePolicies';
import { Plus, Trash2 } from 'lucide-react';
import type { PolicyRule } from '../../types';

const BLANK_RULE: PolicyRule = { type: 'keyword', value: '', severity: 'medium', description: '' };

export default function PolicyEditor() {
  const { id } = useParams<{ id?: string }>();
  const navigate = useNavigate();
  const { policies, add, update } = usePolicies();

  const existing = id && id !== 'new' ? policies.find(p => p.id === id) : null;

  const [name, setName]           = useState(existing?.name ?? '');
  const [desc, setDesc]           = useState(existing?.description ?? '');
  const [rules, setRules]         = useState<PolicyRule[]>(existing?.rules ?? [{ ...BLANK_RULE }]);
  const [saving, setSaving]       = useState(false);
  const [error, setError]         = useState('');

  useEffect(() => {
    if (existing) { setName(existing.name); setDesc(existing.description ?? ''); setRules(existing.rules ?? []); }
  }, [existing?.id]);

  function addRule() { setRules(r => [...r, { ...BLANK_RULE }]); }
  function removeRule(i: number) { setRules(r => r.filter((_, idx) => idx !== i)); }
  function updateRule(i: number, field: keyof PolicyRule, value: string) {
    setRules(r => r.map((rule, idx) => idx === i ? { ...rule, [field]: value } : rule));
  }

  async function save() {
    if (!name.trim()) { setError('Name is required.'); return; }
    setSaving(true);
    setError('');
    try {
      const payload = { name, description: desc, rules, is_active: true };
      if (existing) { await update(existing.id, payload); }
      else           { await add(payload); }
      navigate('/policies');
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? 'Save failed.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-xl font-semibold text-gray-800 mb-6">{existing ? 'Edit Policy' : 'New Policy'}</h1>

      <div className="space-y-4 bg-white rounded-xl border border-gray-200 shadow-sm p-5 mb-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
          <input value={name} onChange={e => setName(e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea value={desc} onChange={e => setDesc(e.target.value)} rows={2}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 mb-5">
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm font-semibold text-gray-700">Rules</p>
          <button onClick={addRule} className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800">
            <Plus size={13} /> Add Rule
          </button>
        </div>
        <div className="space-y-3">
          {rules.map((rule, i) => (
            <div key={i} className="flex gap-2 items-start p-3 bg-gray-50 rounded-lg border border-gray-100">
              <select value={rule.type} onChange={e => updateRule(i, 'type', e.target.value)}
                className="border border-gray-300 rounded px-2 py-1.5 text-xs">
                <option value="keyword">Keyword</option>
                <option value="regex">Regex</option>
                <option value="semantic">Semantic</option>
              </select>
              <input value={rule.value} onChange={e => updateRule(i, 'value', e.target.value)}
                placeholder={rule.type === 'semantic' ? 'Describe what to detect…' : 'value'}
                className="flex-1 border border-gray-300 rounded px-2 py-1.5 text-xs" />
              <select value={rule.severity} onChange={e => updateRule(i, 'severity', e.target.value)}
                className="border border-gray-300 rounded px-2 py-1.5 text-xs">
                {['low','medium','high','critical'].map(s => <option key={s}>{s}</option>)}
              </select>
              <button onClick={() => removeRule(i)} className="text-gray-300 hover:text-red-400 transition mt-1">
                <Trash2 size={13} />
              </button>
            </div>
          ))}
          {rules.length === 0 && <p className="text-xs text-gray-400 text-center py-4">No rules yet.</p>}
        </div>
      </div>

      {error && <p className="text-sm text-red-500 mb-3">{error}</p>}

      <div className="flex gap-3">
        <button onClick={save} disabled={saving}
          className="bg-blue-600 text-white px-5 py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 transition">
          {saving ? 'Saving…' : 'Save Policy'}
        </button>
        <button onClick={() => navigate('/policies')}
          className="bg-gray-100 text-gray-600 px-5 py-2 rounded-lg text-sm hover:bg-gray-200 transition">
          Cancel
        </button>
      </div>
    </div>
  );
}
