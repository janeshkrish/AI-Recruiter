import { useState } from 'react';
import axios from 'axios';
import { AnimatePresence } from 'framer-motion';

import TopNav from './components/TopNav';
import CandidateList from './components/CandidateList';
import CandidateDetail from './components/CandidateDetail';
import InsightsSidebar from './components/InsightsSidebar';
import CopilotDock from './components/CopilotDock';

export interface Candidate {
  candidate_id: string;
  score: number;
  skill_match: number;
  experience_match: number;
  semantic_similarity: number;
  location_match: number;
  potential_score: number;
  transferable_matches: number;
  reasoning: string;
  candidate_details?: any;
}

export default function App() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const [weights, setWeights] = useState({
    skill_match: 1.0,
    experience_match: 1.0,
    semantic_similarity: 1.0,
    education_match: 0.2
  });

  const [jdText, setJdText] = useState('');

  const handleSearch = async (currentWeights = weights) => {
    if (!jdText) return;
    setIsSearching(true);
    try {
      const res = await axios.post('http://127.0.0.1:8000/api/rank', { 
        job_description: jdText,
        custom_weights: currentWeights
      });
      setCandidates(res.data.ranked_candidates);
      setHasSearched(true);
      // Auto-select first candidate
      if (res.data.ranked_candidates.length > 0) {
        setSelectedCandidate(res.data.ranked_candidates[0]);
      }
    } catch (err) {
      console.error(err);
      alert("Backend connection failed.");
    } finally {
      setIsSearching(false);
    }
  };

  const handleWeightChange = (newWeights: any) => {
    setWeights(newWeights);
    handleSearch(newWeights);
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-[#FAFAFA] text-[#0F172A] overflow-hidden font-sans">
      <TopNav jdText={jdText} setJdText={setJdText} onSearch={() => handleSearch()} isSearching={isSearching} />

      <main className="flex-1 flex overflow-hidden">
        {!hasSearched ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
            <h1 className="text-3xl font-bold text-slate-800 mb-4">Recruiter Intelligence Workspace</h1>
            <p className="text-slate-500 max-w-lg">Enter a job description or query in the top search bar to instantly analyze the dataset and discover the optimal candidates.</p>
          </div>
        ) : (
          <>
            {/* Left Pane: List */}
            <div className="w-[350px] border-r border-slate-200 bg-white flex flex-col z-10 shadow-[2px_0_10px_rgba(0,0,0,0.02)]">
              <CandidateList 
                candidates={candidates} 
                selectedId={selectedCandidate?.candidate_id} 
                onSelect={setSelectedCandidate} 
              />
            </div>

            {/* Center Pane: Detail */}
            <div className="flex-1 bg-[#FAFAFA] overflow-y-auto relative">
              <AnimatePresence mode="wait">
                {selectedCandidate && (
                  <CandidateDetail key={selectedCandidate.candidate_id} candidate={selectedCandidate} />
                )}
              </AnimatePresence>
            </div>

            {/* Right Pane: Insights */}
            <div className="w-[320px] border-l border-slate-200 bg-white p-6 overflow-y-auto hidden xl:block z-10 shadow-[-2px_0_10px_rgba(0,0,0,0.02)]">
              <InsightsSidebar 
                candidates={candidates} 
                weights={weights} 
                onWeightChange={handleWeightChange}
              />
            </div>
          </>
        )}
      </main>

      {/* Persistent Copilot */}
      {hasSearched && <CopilotDock candidates={candidates} />}
    </div>
  );
}
