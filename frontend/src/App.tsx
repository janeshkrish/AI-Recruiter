import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import TopNav from './components/TopNav';
import Home from './pages/Home';
import CandidatesExplorer from './pages/CandidatesExplorer';
import AnalyzeJD from './pages/AnalyzeJD';
import PipelineAnalytics from './pages/PipelineAnalytics';
import CandidateProfilePage from './pages/CandidateProfilePage';

const queryClient = new QueryClient();
const THEME_STORAGE_KEY = 'talentos-theme';
type ThemeMode = 'light' | 'dark';

export interface Candidate {
  candidate_id: string;
  rank?: number;
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
  overall_score?: number;
  hiring_recommendation?: string;
  top_matching_evidence?: string[];
  missing_requirements?: string[];
  risk_factors?: string[];
  production_evidence?: string[];
  behavioral_evidence?: string[];
  jd_alignment_score?: number;
  score_breakdown?: Record<string, number>;
  scoring_weights?: Record<string, number>;
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
  const [theme, setTheme] = useState<ThemeMode>(() => {
    const savedTheme = window.localStorage.getItem(THEME_STORAGE_KEY) as ThemeMode | null;
    if (savedTheme === 'light' || savedTheme === 'dark') return savedTheme;

    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    document.body.setAttribute('data-theme', theme);
    window.localStorage.setItem(THEME_STORAGE_KEY, theme);
  }, [theme]);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="relative flex flex-col min-h-screen w-full overflow-hidden font-sans bg-[var(--color-bg-base)] text-[var(--color-text-primary)]">
          <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
            <div className="absolute top-[-160px] left-[8%] w-[680px] h-[680px] rounded-full bg-[var(--color-bg-elevated)] blur-[170px]" />
            <div className="absolute bottom-[-180px] right-[10%] w-[560px] h-[560px] rounded-full bg-[var(--color-accent-blue-light)] blur-[180px]" />
            <div className="absolute top-[30%] right-[24%] w-[420px] h-[420px] rounded-full bg-[var(--color-accent-emerald-light)] blur-[160px]" />
            <div className="absolute inset-0 bg-grid opacity-50" />
            <div className="absolute inset-0 bg-gradient-to-b from-white/20 via-transparent to-[var(--color-accent-blue-light)]" />
          </div>

          <div className="relative z-20 shrink-0">
            <TopNav
              theme={theme}
              onToggleTheme={() => setTheme((currentTheme) => (currentTheme === 'light' ? 'dark' : 'light'))}
            />
          </div>

          <main className="relative z-10 flex flex-1 min-h-0 flex-col overflow-hidden">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/candidates" element={<CandidatesExplorer />} />
              <Route path="/analyze" element={<AnalyzeJD />} />
              <Route path="/pipeline" element={<PipelineAnalytics />} />
              <Route path="/candidate/:candidateId" element={<CandidateProfilePage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
