import { motion } from 'framer-motion';
import { useState } from 'react';
import type { Candidate } from '../App';
import { Target, Activity, AlertTriangle } from 'lucide-react';

interface Props {
  candidates: Candidate[];
  selectedId?: string;
  onSelect: (c: Candidate) => void;
}

export default function CandidateList({ candidates, selectedId, onSelect }: Props) {
  const [currentPage, setCurrentPage] = useState(1);

const candidatesPerPage = 6;

const totalPages = Math.ceil(
  candidates.length / candidatesPerPage
);

const startIndex =
  (currentPage - 1) * candidatesPerPage;

const currentCandidates =
  candidates.slice(
    startIndex,
    startIndex + candidatesPerPage
  );
  return (
    <div className="flex-1 overflow-y-auto">
      <div className="sticky top-0 glass-strong border-b border-white/[0.06] px-4 py-3 z-10 flex justify-between items-center text-xs font-semibold text-slate-500 uppercase tracking-wider">
        <span>Ranked Candidates</span>
        <span className="text-blue-400">{candidates.length} Found</span>
      </div>

      <div className="p-3 space-y-1.5">
        {currentCandidates.map((c, index) => {
          const actualIndex =
    startIndex + index;
          const isSelected = c.candidate_id === selectedId;
          const hasFlags = c.anti_pattern_flags && c.anti_pattern_flags.length > 0;
          const rankBadge = actualIndex < 3;

          return (
            <motion.div
              key={c.candidate_id}
              onClick={() => onSelect(c)}
              className={`p-3 rounded-xl border transition-all cursor-pointer flex flex-col gap-2 ${
                isSelected
                  ? 'bg-blue-500/10 border-blue-500/30 shadow-lg shadow-blue-500/5'
                  : 'bg-white/[0.02] border-white/[0.04] hover:border-white/[0.08] hover:bg-white/[0.04]'
              }`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: actualIndex * 0.03, duration: 0.3 }}
            >
              <div className="flex items-center gap-3">
                {/* Rank Badge or Avatar */}
                <div className="relative">
                  {rankBadge ? (
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center font-black text-sm shrink-0 ${
                      actualIndex === 0 ? 'rank-gold' : actualIndex === 1 ? 'rank-silver' : 'rank-bronze'
                    }`}>
                      #{actualIndex + 1}
                    </div>
                  ) : (
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm shrink-0 ${
                      isSelected ? 'bg-blue-600 text-white' : 'bg-white/[0.06] text-slate-400'
                    }`}>
                      {c.candidate_details?.profile?.anonymized_name?.charAt(0) || 'C'}
                    </div>
                  )}
                  {hasFlags && (
                    <div className="absolute -top-0.5 -right-0.5 w-3.5 h-3.5 bg-rose-500 rounded-full flex items-center justify-center">
                      <AlertTriangle size={8} className="text-white" />
                    </div>
                  )}
                </div>

                {/* Name & Title */}
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-white truncate text-sm">
                    {c.candidate_details?.profile?.anonymized_name || c.candidate_id}
                  </div>
                  <div className="text-xs text-slate-500 truncate">
                    {c.candidate_details?.profile?.current_title || 'Software Engineer'}
                  </div>
                </div>

                {/* Score */}
                <div className="text-right shrink-0">
                  <div className={`text-lg font-black ${
                    c.score >= 80 ? 'gradient-text-emerald' :
                    c.score >= 60 ? 'gradient-text-amber' :
                    'text-slate-400'
                  }`}>
                    {c.score.toFixed(1)}
                  </div>
                </div>
              </div>

              {/* Score Breakdown Bar */}
              <div className="flex gap-1 h-1 rounded-full overflow-hidden bg-white/[0.04]">
                <div
                  className="h-full bg-blue-500/60 rounded-full transition-all duration-700"
                  style={{ width: `${Math.min(c.skill_match, 100)}%` }}
                />
              </div>
              <div className="sticky bottom-0 bg-[#09090B] border-t border-white/5 p-3 flex items-center justify-between">

  <button
    onClick={() =>
      setCurrentPage((p) =>
        Math.max(1, p - 1)
      )
    }
    disabled={currentPage === 1}
    className="px-3 py-1.5 rounded-lg bg-white/5 text-xs text-white disabled:opacity-40"
  >
    ← Prev
  </button>

  <div className="text-xs text-slate-400">
    Page {currentPage} of {totalPages}
  </div>

  <button
    onClick={() =>
      setCurrentPage((p) =>
        Math.min(totalPages, p + 1)
      )
    }
    disabled={currentPage === totalPages}
    className="px-3 py-1.5 rounded-lg bg-white/5 text-xs text-white disabled:opacity-40"
  >
    Next →
  </button>

</div>

              {/* Mini Metrics */}
              <div className="flex items-center justify-between text-[10px]">
                <div className="flex gap-2">
                  <span className="flex items-center gap-1 text-emerald-400 font-medium px-1.5 py-0.5 rounded bg-emerald-500/10">
                    <Target size={9} /> {c.skill_match.toFixed(0)}%
                  </span>
                  <span className="flex items-center gap-1 text-amber-400 font-medium px-1.5 py-0.5 rounded bg-amber-500/10">
                    <Activity size={9} /> {c.potential_score.toFixed(0)}
                  </span>
                  {c.transferable_matches > 0 && (
                    <span className="text-purple-400 font-medium px-1.5 py-0.5 rounded bg-purple-500/10">
                      +{c.transferable_matches} transfer
                    </span>
                  )}
                </div>
                <div className="text-slate-600">
                  {c.candidate_details?.profile?.years_of_experience || 0}y
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
