import { ShieldCheck, Menu } from 'lucide-react';
import { useAppStore } from '../../store/appStore';

export default function Navbar() {
  const { toggleSidebar } = useAppStore();
  return (
    <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-3 shrink-0 shadow-sm">
      <button onClick={toggleSidebar} className="text-gray-400 hover:text-gray-700 transition">
        <Menu size={20} />
      </button>
      <ShieldCheck size={22} className="text-blue-600" />
      <span className="font-semibold text-gray-800 text-lg tracking-tight">
        Compliance Intelligence
      </span>
      <span className="ml-auto text-xs text-gray-400">Multimodal PII & Policy Platform</span>
    </header>
  );
}
