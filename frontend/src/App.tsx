import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import TopNav from './components/TopNav';
import Home from './pages/Home';
import CandidatesExplorer from './pages/CandidatesExplorer';
import AnalyzeJD from './pages/AnalyzeJD';

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="flex flex-col h-screen w-screen bg-[#FAFAFA] text-[#0F172A] overflow-hidden font-sans">
          <TopNav />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/candidates" element={<CandidatesExplorer />} />
            <Route path="/analyze" element={<AnalyzeJD />} />
          </Routes>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
