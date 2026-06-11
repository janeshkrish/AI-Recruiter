import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Sparkles, SlidersHorizontal, Activity } from 'lucide-react';
import axios from 'axios';
import CandidateGrid from './components/CandidateGrid';
import InsightsPanel from './components/InsightsPanel';
import CandidateIntelligence from './components/CandidateIntelligence';
import WhatIfPanel from './components/WhatIfPanel';

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
  
  const [jdText, setJdText] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [showWhatIf, setShowWhatIf] = useState(false);

  const [weights, setWeights] = useState({
    skill_match: 1.0,
    experience_match: 1.0,
    semantic_similarity: 1.0,
    education_match: 0.2
  });

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
    } catch (err) {
      console.error(err);
      alert("AI Brain offline.");
    } finally {
      setIsSearching(false);
    }
  };

  const handleWeightChange = (newWeights: any) => {
    setWeights(newWeights);
    handleSearch(newWeights); // Real-time what-if recalculation
  };

  return (
    <>
      <div className="aurora-bg">
        <div className="aurora-blob blob-1"></div>
        <div className="aurora-blob blob-2"></div>
      </div>

      <div className="relative min-h-screen text-slate-200 font-sans selection:bg-indigo-500/30 flex flex-col">
        
        {/* Header / Search Area */}
        <header className={`transition-all duration-700 ease-in-out flex flex-col items-center justify-center ${hasSearched ? 'pt-8 pb-4' : 'h-screen'}`}>
          {!hasSearched && (
            <motion.h1 initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="text-4xl md:text-5xl font-semibold mb-8 tracking-tight text-white flex items-center gap-4">
              <Sparkles className="text-indigo-400" size={32} /> Redrob Intelligence
            </motion.h1>
          )}

          <motion.div layout className={`w-full px-6 transition-all duration-700 ${hasSearched ? 'max-w-4xl' : 'max-w-2xl'}`}>
            <div className="relative group">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl blur opacity-30 group-hover:opacity-60 transition duration-500"></div>
              <div className="relative flex items-center bg-[#0B0E14]/90 backdrop-blur-xl border border-white/10 rounded-2xl p-2 shadow-2xl">
                <Search className="text-slate-400 ml-3" size={20} />
                <input 
                  autoFocus
                  type="text" 
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Find senior AI engineers with startup experience..." 
                  className="w-full bg-transparent p-3 text-lg focus:outline-none text-white placeholder-slate-500"
                />
                <button 
                  onClick={() => handleSearch()}
                  disabled={isSearching || !jdText}
                  className="px-6 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl font-medium transition-colors disabled:opacity-50"
                >
                  {isSearching ? <Activity className="animate-spin" size={20} /> : 'Search'}
                </button>
              </div>
            </div>
          </motion.div>
        </header>

        {/* Workspace Area */}
        <AnimatePresence>
          {hasSearched && (
            <motion.main 
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} 
              className="flex-1 w-full max-w-[1600px] mx-auto px-6 pb-12 flex gap-6"
            >
              {/* Left/Center: Candidate Grid */}
              <div className="flex-1 space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-white">Talent Discovery</h2>
                  <button 
                    onClick={() => setShowWhatIf(!showWhatIf)}
                    className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm border transition-colors ${showWhatIf ? 'bg-indigo-500/20 border-indigo-500 text-indigo-300' : 'bg-white/5 border-white/10 text-slate-300 hover:text-white'}`}
                  >
                    <SlidersHorizontal size={16} /> What-If Simulator
                  </button>
                </div>
                
                {showWhatIf && (
                  <WhatIfPanel weights={weights} onChange={handleWeightChange} />
                )}

                <CandidateGrid candidates={candidates} onSelect={setSelectedCandidate} />
              </div>

              {/* Right Panel: Live Insights */}
              <div className="w-[380px] hidden xl:block">
                <InsightsPanel candidates={candidates} />
              </div>
            </motion.main>
          )}
        </AnimatePresence>

        {/* Intelligence View Modal */}
        <AnimatePresence>
          {selectedCandidate && (
            <CandidateIntelligence candidate={selectedCandidate} onClose={() => setSelectedCandidate(null)} />
          )}
        </AnimatePresence>

      </div>
    </>
  );
}
