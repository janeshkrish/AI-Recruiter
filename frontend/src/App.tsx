import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import TopNav from './components/TopNav';
import Home from './pages/Home';
import CandidatesExplorer from './pages/CandidatesExplorer';
import AnalyzeJD from './pages/AnalyzeJD';
import PipelineAnalytics from './pages/PipelineAnalytics';

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
        <div className="flex flex-col h-screen w-screen bg-[#050810] text-slate-100 overflow-hidden font-sans">
          {/* Animated background */}
          <div className="fixed inset-0 bg-grid bg-gradient-radial pointer-events-none z-0" />
          
          <TopNav />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/candidates" element={<CandidatesExplorer />} />
            <Route path="/analyze" element={<AnalyzeJD />} />
            <Route path="/pipeline" element={<PipelineAnalytics />} />
          </Routes>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
