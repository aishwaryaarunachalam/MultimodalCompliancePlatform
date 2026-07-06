import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Upload, FileText, ClipboardList, ShieldCheck } from 'lucide-react';
import { useAppStore } from '../../store/appStore';

const link = ({ isActive }: { isActive: boolean }) =>
  `flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition ${
    isActive ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-100'
  }`;

export default function Sidebar() {
  const { sidebarOpen } = useAppStore();
  if (!sidebarOpen) return null;

  return (
    <aside className="w-52 bg-white border-r border-gray-200 flex flex-col shrink-0 overflow-y-auto">
      <nav className="p-3 space-y-1">
        <NavLink to="/"          className={link} end><LayoutDashboard size={15} /> Dashboard</NavLink>
        <NavLink to="/upload"    className={link}><Upload       size={15} /> Upload</NavLink>
        <NavLink to="/documents" className={link}><FileText     size={15} /> Documents</NavLink>
        <NavLink to="/review"    className={link}><ClipboardList size={15} /> Review Queue</NavLink>
        <NavLink to="/policies"  className={link}><ShieldCheck  size={15} /> Policies</NavLink>
      </nav>
    </aside>
  );
}
