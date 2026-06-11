import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Users, Search, Activity, Zap } from 'lucide-react';
import CommandCenter from './components/CommandCenter';
import JobUnderstandingPanel from './components/JobUnderstandingPanel';
import CandidateExplorer from './components/CandidateExplorer';
import CandidateProfileModal from './components/CandidateProfileModal';
import axios from 'axios';

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

function App() {
  const [activeTab, setActiveTab] = useState<'command' | 'explorer'>('command');
  const [jdText, setJdText] = useState('');
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [serverStatus, setServerStatus] = useState<'online' | 'offline'>('offline');

  useEffect(() => {
    // Health check
    axios.get('http://127.0.0.1:8000/api/health')
      .then(() => setServerStatus('online'))
      .catch(() => setServerStatus('offline'));
  }, []);

  const handleUnleashJury = async () => {
    if (!jdText) return;
    setIsEvaluating(true);
    try {
      const res = await axios.post('http://127.0.0.1:8000/api/rank', { job_description: jdText });
      setCandidates(res.data.ranked_candidates);
      setActiveTab('explorer');
    } catch (error) {
      console.error("Evaluation failed", error);
      alert("Evaluation failed. Please check the backend server.");
    } finally {
      setIsEvaluating(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-[#0B0E14] text-slate-200">
      
      {/* SIDEBAR */}
      <div className="w-64 border-r border-[#2A3140] bg-[#151A22] flex flex-col p-4">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center">
            <Brain size={20} className="text-white" />
          </div>
          <h1 className="font-bold text-lg text-white">Redrob AI</h1>
        </div>

        <div className="mb-6">
          <div className="text-xs uppercase text-slate-500 font-semibold tracking-wider mb-2">Platform Status</div>
          <div className="flex items-center gap-2 text-sm">
            <span className={`w-2 h-2 rounded-full ${serverStatus === 'online' ? 'bg-emerald-400 shadow-[0_0_8px_#34d399]' : 'bg-red-500'}`}></span>
            {serverStatus === 'online' ? 'Brain Engine Online' : 'Offline'}
          </div>
        </div>

        <nav className="flex-1 space-y-2">
          <button 
            onClick={() => setActiveTab('command')}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md transition-colors text-sm font-medium
              ${activeTab === 'command' ? 'bg-[#2A3140] text-white' : 'text-slate-400 hover:text-white hover:bg-[#2A3140]/50'}`}
          >
            <Activity size={18} /> Command Center
          </button>
          <button 
            onClick={() => setActiveTab('explorer')}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md transition-colors text-sm font-medium
              ${activeTab === 'explorer' ? 'bg-[#2A3140] text-white' : 'text-slate-400 hover:text-white hover:bg-[#2A3140]/50'}`}
          >
            <Users size={18} /> Candidate Explorer
          </button>
        </nav>

        <div className="pt-4 border-t border-[#2A3140]">
          <div className="text-xs uppercase text-slate-500 font-semibold tracking-wider mb-3">Active Engines</div>
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-xs text-slate-300">
              <Zap size={14} className="text-amber-400" /> Technical (Skill Graph)
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-300">
              <Zap size={14} className="text-indigo-400" /> Career (Velocity)
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-300">
              <Zap size={14} className="text-emerald-400" /> Potential (Learning)
            </div>
          </div>
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="flex-1 overflow-y-auto">
        <header className="h-16 border-b border-[#2A3140] flex items-center justify-between px-8 bg-[#151A22]/80 backdrop-blur-md sticky top-0 z-10">
          <h2 className="text-lg font-medium text-white">
            {activeTab === 'command' ? 'Intelligence Command Center' : 'Candidate Explorer'}
          </h2>
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
              <input 
                type="text" 
                placeholder="Search candidates, skills..." 
                className="bg-[#0B0E14] border border-[#2A3140] rounded-full pl-9 pr-4 py-1.5 text-sm focus:outline-none focus:border-indigo-500 w-64 transition-colors"
              />
            </div>
          </div>
        </header>

        <main className="p-8">
          <AnimatePresence mode="wait">
            {activeTab === 'command' && (
              <motion.div
                key="command"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
              >
                <CommandCenter 
                  jdText={jdText} 
                  setJdText={setJdText} 
                  onUnleash={handleUnleashJury}
                  isEvaluating={isEvaluating}
                  totalCandidates={100000}
                />
                {jdText && !isEvaluating && <JobUnderstandingPanel />}
              </motion.div>
            )}

            {activeTab === 'explorer' && (
              <motion.div
                key="explorer"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className="h-full"
              >
                <CandidateExplorer 
                  candidates={candidates} 
                  onSelect={setSelectedCandidate} 
                  isEvaluating={isEvaluating}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>

      <AnimatePresence>
        {selectedCandidate && (
          <CandidateProfileModal 
            candidate={selectedCandidate} 
            onClose={() => setSelectedCandidate(null)} 
          />
        )}
      </AnimatePresence>
      
    </div>
  );
}

export default App;
