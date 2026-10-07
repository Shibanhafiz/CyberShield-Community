import { Suspense, lazy, useEffect, useState } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import BottomNav from './components/BottomNav';
import Footer from './components/Footer';
import LoadingState from './components/LoadingState';
import Navbar from './components/Navbar';
import About from './pages/About';
import Analyze from './pages/Analyze';
import Awareness from './pages/Awareness';
import Home from './pages/Home';
import Impact from './pages/Impact';
import Learn from './pages/Learn';
import NotFound from './pages/NotFound';
import Privacy from './pages/Privacy';
import Quiz from './pages/Quiz';
import Report from './pages/Report';
import Scenario from './pages/Scenario';
import AdminLayout from './pages/admin/AdminLayout';
import Audit from './pages/admin/Audit';
import AwarenessAdmin from './pages/admin/AwarenessAdmin';
import Dashboard from './pages/admin/Dashboard';
import Exports from './pages/admin/Exports';
import FeedbackAdmin from './pages/admin/FeedbackAdmin';
import Login from './pages/admin/Login';
import ReportDetail from './pages/admin/ReportDetail';
import Reports from './pages/admin/Reports';
import { getHealth } from './api';

/* Chart-heavy routes load on demand so the first screen stays light
   on mobile networks. Test files import pages directly — unaffected. */
const Community = lazy(() => import('./pages/Community'));
const Analytics = lazy(() => import('./pages/admin/Analytics'));

function LazyPage({ children }) {
  return (
    <Suspense
      fallback={(
        <div className="mx-auto w-full max-w-[1200px] px-4 sm:px-6">
          <LoadingState label="Loading…" />
        </div>
      )}
    >
      {children}
    </Suspense>
  );
}

export default function App() {
  const [backendStatus, setBackendStatus] = useState('unknown');

  useEffect(() => {
    let mounted = true;
    getHealth()
      .then(() => { if (mounted) setBackendStatus('online'); })
      .catch(() => { if (mounted) setBackendStatus('offline'); });
    return () => { mounted = false; };
  }, []);

  return (
    <BrowserRouter>
      <div className="flex min-h-screen flex-col bg-paper text-ink">
        <Navbar backendStatus={backendStatus} />
        <main className="flex-1 pb-24 pt-6 md:py-10">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/analyze" element={<Analyze />} />
            <Route path="/analyze/url" element={<Analyze initialTab="url" />} />
            <Route path="/about" element={<About />} />
            <Route path="/community" element={<LazyPage><Community /></LazyPage>} />
            <Route path="/learn" element={<Learn />} />
            <Route path="/learn/scenario/:id" element={<Scenario />} />
            <Route path="/quiz" element={<Quiz />} />
            <Route path="/awareness" element={<Awareness />} />
            <Route path="/impact" element={<Impact />} />
            <Route path="/report" element={<Report />} />
            <Route path="/privacy" element={<Privacy />} />
            <Route path="/admin/login" element={<Login />} />
            <Route path="/admin" element={<AdminLayout />}>
              <Route index element={<Dashboard />} />
              <Route path="reports" element={<Reports />} />
              <Route path="reports/:id" element={<ReportDetail />} />
              <Route path="analytics" element={<LazyPage><Analytics /></LazyPage>} />
              <Route path="awareness" element={<AwarenessAdmin />} />
              <Route path="feedback" element={<FeedbackAdmin />} />
              <Route path="exports" element={<Exports />} />
              <Route path="audit" element={<Audit />} />
            </Route>
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
        <Footer />
        <BottomNav />
      </div>
    </BrowserRouter>
  );
}
