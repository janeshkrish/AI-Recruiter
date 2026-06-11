import { useState } from 'react';
import { Sparkles, BrainCircuit, MessageSquare, TrendingUp } from 'lucide-react';
import axios from 'axios';
import type { Candidate } from '../App';
import { motion } from 'framer-motion';

export default function InsightsPanel({ candidates }: { candidates: Candidate[] }) {
  const [copilotQuery, setCopilotQuery] = useState('');
  const [copilotResponse, setCopilotResponse] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // Compute live insights
  const hiddenGem = candidates.find(c => c.potential_score > 85 && c.experience_match < 60);
  const highestProb = [...candidates].sort((a,b) => b.location_match - a.location_match)[0];
  const techBeast = [...candidates].sort((a,b) => b.skill_match - a.skill_match)[0];

  const askCopilot = async (q: string) => {
    setIsTyping(true);
    setCopilotQuery(q);
    try {
      const res = await axios.post('http://127.0.0.1:8000/api/copilot', {
        question: q,
        candidates: candidates.slice(0, 5) // Send top 5 for context
      });
      setCopilotResponse(res.data.answer);
    } catch (e) {
      setCopilotResponse("My backend connection seems to be down.");
    }
    setIsTyping(false);
    setCopilotQuery('');
  };

  return (
    <div className="space-y-4 sticky top-4">
      {/* Dynamic Insights */}
      <div className="glass-panel p-5">
        <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2"><Sparkles size={16} className="text-indigo-400"/> Live Insights</h3>
        
        <div className="space-y-3">
          {hiddenGem && (
            <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg">
              <div className="text-[10px] uppercase tracking-wider text-amber-500/70 font-bold mb-1 flex items-center gap-1"><TrendingUp size={10}/> Hidden Gem</div>
              <div className="text-sm text-amber-200">Candidate <b>{hiddenGem.candidate_id}</b> has massive potential ({hiddenGem.potential_score.toFixed(0)}) despite low experience match.</div>
            </div>
          )}

          {highestProb && (
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
              <div className="text-[10px] uppercase tracking-wider text-emerald-500/70 font-bold mb-1">Highest Hiring Probability</div>
              <div className="text-sm text-emerald-200">Candidate <b>{highestProb.candidate_id}</b> is highly responsive and geographically aligned.</div>
            </div>
          )}

          {techBeast && (
            <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
              <div className="text-[10px] uppercase tracking-wider text-blue-500/70 font-bold mb-1">Technical Beast</div>
              <div className="text-sm text-blue-200">Candidate <b>{techBeast.candidate_id}</b> dominates the technical requirements ({techBeast.skill_match.toFixed(0)}% match).</div>
            </div>
          )}
        </div>
      </div>

      {/* Recruiter Copilot */}
      <div className="glass-panel overflow-hidden flex flex-col h-[400px]">
        <div className="p-4 border-b border-white/5 bg-white/5 flex items-center gap-2">
          <BrainCircuit size={16} className="text-purple-400" />
          <span className="text-sm font-semibold text-white">Recruiter Copilot</span>
        </div>
        
        <div className="flex-1 p-4 overflow-y-auto space-y-4 text-sm">
          <div className="bg-white/5 p-3 rounded-lg rounded-tl-none border border-white/10 text-slate-300">
            I've analyzed the current candidate ranking based on your weights. Ask me anything about the results.
          </div>
          
          {copilotResponse && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="bg-indigo-500/10 p-3 rounded-lg rounded-tr-none border border-indigo-500/20 text-indigo-200">
              {copilotResponse}
            </motion.div>
          )}
          
          {isTyping && <div className="text-xs text-slate-500 animate-pulse">Copilot is analyzing...</div>}
        </div>

        <div className="p-3 border-t border-white/5">
          <div className="flex flex-wrap gap-2 mb-3">
            <button onClick={() => askCopilot("Why is candidate 1 ranked highest?")} className="text-[10px] px-2 py-1 bg-white/5 rounded border border-white/10 hover:bg-white/10 text-slate-400">Why rank #1?</button>
            <button onClick={() => askCopilot("Compare the top 2 candidates")} className="text-[10px] px-2 py-1 bg-white/5 rounded border border-white/10 hover:bg-white/10 text-slate-400">Compare top 2</button>
            <button onClick={() => askCopilot("Are there any hidden gems?")} className="text-[10px] px-2 py-1 bg-white/5 rounded border border-white/10 hover:bg-white/10 text-slate-400">Find gems</button>
          </div>
          <div className="relative">
            <input 
              type="text" 
              value={copilotQuery}
              onChange={e => setCopilotQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && askCopilot(copilotQuery)}
              placeholder="Ask a question..." 
              className="w-full bg-[#0B0E14] border border-white/10 rounded-lg pl-3 pr-10 py-2 text-sm focus:outline-none focus:border-indigo-500 text-white"
            />
            <button onClick={() => askCopilot(copilotQuery)} className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-indigo-400">
              <MessageSquare size={14} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
