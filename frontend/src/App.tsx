import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/layout/Navbar';
import Sidebar from './components/layout/Sidebar';
import MetricsSummary from './components/dashboard/MetricsSummary';
import ViolationChart from './components/dashboard/ViolationChart';
import DropZone from './components/upload/DropZone';
import DocumentList from './components/documents/DocumentList';
import DocumentDetail from './components/documents/DocumentDetail';
import ReviewQueue from './components/review/ReviewQueue';
import PolicyList from './components/policies/PolicyList';
import PolicyEditor from './components/policies/PolicyEditor';

function Dashboard() {
  return (
    <div className="p-6 space-y-6">
      <MetricsSummary />
      <ViolationChart />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex flex-col h-screen overflow-hidden">
        <Navbar />
        <div className="flex flex-1 overflow-hidden">
          <Sidebar />
          <main className="flex-1 overflow-y-auto">
            <Routes>
              <Route path="/"                     element={<Dashboard />} />
              <Route path="/upload"               element={<DropZone />} />
              <Route path="/documents"            element={<DocumentList />} />
              <Route path="/documents/:id"        element={<DocumentDetail />} />
              <Route path="/review"               element={<ReviewQueue />} />
              <Route path="/policies"             element={<PolicyList />} />
              <Route path="/policies/new"         element={<PolicyEditor />} />
              <Route path="/policies/:id/edit"    element={<PolicyEditor />} />
              <Route path="*"                     element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}
