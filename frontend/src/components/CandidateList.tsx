import { motion } from 'framer-motion';
import type { Candidate } from '../App';
import { Target, Activity } from 'lucide-react';

interface Props {
  candidates: Candidate[];
  selectedId?: string;
  onSelect: (c: Candidate) => void;
}

export default function CandidateList({ candidates, selectedId, onSelect }: Props) {
  return (
    <div className="flex-1 overflow-y-auto">
      <div className="sticky top-0 bg-slate-50 border-b border-slate-200 px-4 py-3 z-10 flex justify-between items-center text-xs font-semibold text-slate-500 uppercase tracking-wider">
        <span>Candidate Pipeline</span>
        <span>{candidates.length} Found</span>
      </div>

      <div className="p-3 space-y-2">
        {candidates.map((c) => {
          const isSelected = c.candidate_id === selectedId;
          const prob = ((c.location_match + c.score) / 2).toFixed(0);

          return (
            <motion.div
              key={c.candidate_id}
              onClick={() => onSelect(c)}
              className={`p-3 rounded-xl border transition-all cursor-pointer flex flex-col gap-2 ${
                isSelected 
                  ? 'bg-blue-50 border-blue-200 shadow-sm ring-1 ring-blue-500/20' 
                  : 'bg-white border-slate-200 hover:border-slate-300 hover:shadow-sm'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm shrink-0 ${
                  isSelected ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-600'
                }`}>
                  {c.candidate_details?.profile?.anonymized_name?.charAt(0) || 'C'}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-slate-900 truncate text-sm">
                    {c.candidate_details?.profile?.anonymized_name || c.candidate_id}
                  </div>
                  <div className="text-xs text-slate-500 truncate">
                    {c.candidate_details?.profile?.current_title || 'Software Engineer'}
                  </div>
                </div>
                <div className="text-right shrink-0">
                  <div className={`font-bold ${isSelected ? 'text-blue-700' : 'text-slate-700'}`}>
                    {c.score.toFixed(1)}
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between mt-1 text-xs">
                <div className="flex gap-2">
                  <span className="flex items-center gap-1 text-emerald-600 font-medium bg-emerald-50 px-1.5 py-0.5 rounded">
                    <Target size={10} /> {prob}%
                  </span>
                  <span className="flex items-center gap-1 text-amber-600 font-medium bg-amber-50 px-1.5 py-0.5 rounded">
                    <Activity size={10} /> {c.potential_score.toFixed(0)}
                  </span>
                </div>
                <div className="text-slate-400">
                  {c.experience_match > 80 ? 'Sr' : 'Mid'}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
