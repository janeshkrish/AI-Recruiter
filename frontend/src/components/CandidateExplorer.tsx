import { useState } from 'react';
import { Filter, ArrowUpRight, TrendingUp, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import type { Candidate } from '../App';

interface Props {
  candidates: Candidate[];
  onSelect: (c: Candidate) => void;
  isEvaluating: boolean;
}

export default function CandidateExplorer({ candidates, onSelect, isEvaluating }: Props) {
  const [minScore, setMinScore] = useState(0);

  if (isEvaluating) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-slate-400">
        <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 2, ease: "linear" }} className="mb-4 text-indigo-500">
          <Zap size={48} />
        </motion.div>
        <p>Jury is evaluating the 100K talent pool...</p>
      </div>
    );
  }

  if (!candidates.length) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-slate-500">
        <p>Awaiting commands. Enter a JD to unleash the jury.</p>
      </div>
    );
  }

  const filtered = candidates.filter(c => c.score >= minScore);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between bg-[#151A22] p-4 rounded-xl border border-[#2A3140]">
        <div className="flex items-center gap-4">
          <Filter size={18} className="text-slate-400" />
          <span className="text-sm font-medium">Minimum Jury Score: {minScore}%</span>
          <input 
            type="range" 
            min="0" max="100" 
            value={minScore} 
            onChange={(e) => setMinScore(Number(e.target.value))}
            className="w-48 accent-indigo-500"
          />
        </div>
        <div className="text-sm text-slate-400">
          Showing <span className="text-white font-bold">{filtered.length}</span> top candidates
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {filtered.map((c, i) => (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.05 }}
            key={c.candidate_id}
            onClick={() => onSelect(c)}
            className="bg-[#151A22] border border-[#2A3140] rounded-xl p-5 cursor-pointer hover:border-indigo-500 hover:shadow-[0_0_15px_rgba(79,70,229,0.2)] transition-all group relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/10 blur-2xl rounded-full translate-x-1/2 -translate-y-1/2 group-hover:bg-indigo-500/20 transition-all"></div>
            
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="font-bold text-lg text-white mb-1">{c.candidate_id}</h3>
                <div className="flex gap-2 text-xs font-medium">
                  {c.potential_score > 80 && (
                    <span className="bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2 py-0.5 rounded flex items-center gap-1">
                      <TrendingUp size={12}/> High Potential
                    </span>
                  )}
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-br from-indigo-400 to-cyan-400">
                  {c.score.toFixed(1)}
                </div>
                <div className="text-[10px] text-slate-500 uppercase tracking-wider">Jury Score</div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-y-3 gap-x-2 text-sm mb-4">
              <div>
                <div className="text-xs text-slate-500 mb-1">Tech Match</div>
                <div className="font-semibold">{c.skill_match.toFixed(1)}%</div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-1">Momentum</div>
                <div className="font-semibold text-emerald-400">{c.experience_match.toFixed(1)}%</div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-1">Transferable</div>
                <div className="font-semibold text-indigo-400">{c.transferable_matches} Skills</div>
              </div>
            </div>

            <button className="w-full py-2 bg-[#2A3140]/50 hover:bg-[#2A3140] text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-2 group-hover:text-indigo-400">
              Deep Dive <ArrowUpRight size={16} />
            </button>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
