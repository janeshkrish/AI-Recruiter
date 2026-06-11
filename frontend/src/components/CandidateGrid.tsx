import { motion } from 'framer-motion';
import { Network } from 'lucide-react';
import type { Candidate } from '../App';

interface Props {
  candidates: Candidate[];
  onSelect: (c: Candidate) => void;
}

export default function CandidateGrid({ candidates, onSelect }: Props) {
  if (candidates.length === 0) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 auto-rows-max">
      {candidates.map((c, i) => (
        <motion.div
          key={c.candidate_id}
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
          onClick={() => onSelect(c)}
          className="glass-panel p-5 cursor-pointer hover:border-indigo-500/50 hover:bg-white/5 transition-all group relative overflow-hidden flex flex-col"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/5 blur-3xl rounded-full group-hover:bg-indigo-500/10 transition-all"></div>
          
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-slate-700 to-slate-900 border border-white/10 flex items-center justify-center font-bold text-sm">
                {c.candidate_details?.profile?.anonymized_name?.charAt(0) || 'C'}
              </div>
              <div>
                <div className="font-bold text-white text-sm">
                  {c.candidate_details?.profile?.anonymized_name || c.candidate_id}
                </div>
                <div className="text-xs text-slate-400">
                  {c.candidate_details?.profile?.current_title || 'Software Engineer'}
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-lg font-black text-transparent bg-clip-text bg-gradient-to-br from-indigo-400 to-cyan-400">
                {c.score.toFixed(1)}
              </div>
            </div>
          </div>

          <div className="space-y-3 flex-1">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Hiring Probability</span>
              <span className="font-medium text-emerald-400">{((c.location_match + c.score)/2).toFixed(0)}%</span>
            </div>
            
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Potential Score</span>
              <span className="font-medium text-amber-400">{c.potential_score.toFixed(1)}</span>
            </div>

            <div className="pt-3 border-t border-white/5">
              <div className="text-xs text-slate-500 mb-2 flex items-center gap-1"><Network size={12}/> Top Skills</div>
              <div className="flex flex-wrap gap-1.5">
                {(c.candidate_details?.normalized_skills || []).slice(0, 3).map((s: any, idx: number) => (
                  <span key={idx} className="px-2 py-0.5 bg-white/5 border border-white/5 rounded text-[10px] text-slate-300">
                    {s.name}
                  </span>
                ))}
                {c.transferable_matches > 0 && (
                  <span className="px-2 py-0.5 bg-indigo-500/10 border border-indigo-500/20 rounded text-[10px] text-indigo-300 font-medium">
                    +{c.transferable_matches} Transferable
                  </span>
                )}
              </div>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
