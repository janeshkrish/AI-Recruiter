import { motion } from 'framer-motion';
import { Target, Activity, Cpu } from 'lucide-react';
import type { Candidate } from '../App';

export default function CandidatePreviewCard({ candidate }: { candidate: Candidate }) {
  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.9, y: 20 }} 
      animate={{ opacity: 1, scale: 1, y: 0 }} 
      exit={{ opacity: 0, scale: 0.9, y: 20 }}
      className="absolute bottom-10 left-10 w-[400px] pointer-events-auto backdrop-blur-2xl bg-[#0B0E14]/80 border border-white/10 p-6 rounded-3xl shadow-[0_20px_50px_rgba(0,0,0,0.5)]"
    >
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-2xl font-bold text-white mb-1">{candidate.candidate_details?.profile?.anonymized_name || candidate.candidate_id}</h3>
          <p className="text-slate-400 text-sm">{candidate.candidate_details?.profile?.current_title || 'AI Engineer'}</p>
        </div>
        <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-indigo-500 to-emerald-400 flex items-center justify-center text-xl font-bold text-white shadow-lg">
          {candidate.score.toFixed(0)}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-white/5 p-3 rounded-2xl border border-white/5">
          <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase tracking-wider mb-1">
            <Target size={12} /> Hiring Prob
          </div>
          <div className="text-2xl font-black text-white">{((candidate.location_match + candidate.score)/2).toFixed(0)}%</div>
        </div>
        <div className="bg-white/5 p-3 rounded-2xl border border-white/5">
          <div className="flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-wider mb-1">
            <Activity size={12} /> Potential
          </div>
          <div className="text-2xl font-black text-white">{candidate.potential_score.toFixed(0)}</div>
        </div>
      </div>

      <div className="mb-4">
        <div className="text-xs text-slate-500 font-bold uppercase tracking-wider mb-2 flex items-center gap-2"><Cpu size={12}/> Top Skills</div>
        <div className="flex flex-wrap gap-2">
          {(candidate.candidate_details?.normalized_skills || []).slice(0, 4).map((s: any, idx: number) => (
            <span key={idx} className="px-3 py-1 bg-white/10 border border-white/10 rounded-lg text-xs text-slate-200">
              {s.name}
            </span>
          ))}
        </div>
      </div>
      
      <div className="text-sm text-slate-400 line-clamp-2">
        <strong className="text-white">AI Note:</strong> {candidate.reasoning.split(';')[0]}
      </div>

      <div className="mt-6 pt-4 border-t border-white/10 text-center text-xs text-slate-500 uppercase tracking-widest font-bold animate-pulse">
        Click Star for Deep Dive
      </div>
    </motion.div>
  );
}
