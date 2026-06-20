import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import TopNav from './components/TopNav';
import Home from './pages/Home';
import CandidatesExplorer from './pages/CandidatesExplorer';
import AnalyzeJD from './pages/AnalyzeJD';
import PipelineAnalytics from './pages/PipelineAnalytics';
import AnalysisLoading from './pages/AnalysisLoading';
const queryClient = new QueryClient();

export interface Candidate {
  candidate_id: string;
  score: number;
  skill_match: number;
  experience_match: number;
  semantic_similarity: number;
  location_match: number;
  potential_score: number;
  behavioral_score: number;
  transferable_matches: number;
  reasoning: string;
  behavioral_insights: string[];
  anti_pattern_flags: string[];
  anti_pattern_penalty: number;
  candidate_details: any;
}

export interface ParsedJD {
  skills: string[];
  years_experience: number;
  location: string;
  require_degree: boolean;
  hidden_traits: string[];
  anti_patterns: string[];
}

export interface PipelineStats {
  total_indexed: number;
  retrieved: number;
  scored: number;
  returned: number;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>

        <div className="relative flex flex-col min-h-screen w-full bg-[#09090B] text-slate-100 overflow-hidden font-sans">

          {/* Premium Background */}
          <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">

            {/* Purple Glow */}
            <div className="absolute top-[-200px] left-[15%] w-[700px] h-[700px] rounded-full bg-violet-600/15 blur-[180px]" />

            {/* Cyan Glow */}
            <div className="absolute bottom-[-200px] right-[10%] w-[600px] h-[600px] rounded-full bg-cyan-500/10 blur-[180px]" />

            {/* Pink Glow */}
            <div className="absolute top-[40%] right-[30%] w-[400px] h-[400px] rounded-full bg-fuchsia-500/10 blur-[160px]" />

            {/* Grid */}
            <div className="absolute inset-0 bg-grid opacity-30" />

            {/* Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/20" />

          </div>

          {/* Navigation */}
          <div className="relative z-20">
            <TopNav />
          </div>

          {/* Main Content */}
          <main className="relative z-10 flex-1">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/candidates" element={<CandidatesExplorer />} />
              <Route path="/analyze" element={<AnalyzeJD />} />
              <Route path="/pipeline" element={<PipelineAnalytics />} />
              <Route path="/analysis-loading" element={<AnalysisLoading />} />
            </Routes>
          </main>
      

        </div>

      </BrowserRouter>
    </QueryClientProvider>
  );
}