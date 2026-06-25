import { motion } from 'framer-motion';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Candidate } from '../App';
import { Target, Activity, AlertTriangle, ChevronLeft, ChevronRight, ExternalLink } from 'lucide-react';

interface Props {
  candidates: Candidate[];
  selectedId?: string;
  onSelect: (c: Candidate) => void;
}

export default function CandidateList({ candidates, selectedId, onSelect }: Props) {
  const [currentPage, setCurrentPage] = useState(1);
  const navigate = useNavigate();

  const candidatesPerPage = 6;
  const totalPages = Math.ceil(candidates.length / candidatesPerPage);
  const startIndex = (currentPage - 1) * candidatesPerPage;
  const currentCandidates = candidates.slice(startIndex, startIndex + candidatesPerPage);

  return (
    <div className="flex-1 min-h-0 flex flex-col overflow-hidden">
      <div className="sticky top-0 glass-strong border-b border-[var(--color-border-subtle)] px-4 py-3 z-10 flex justify-between items-center text-xs font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider shrink-0">
        <span>Ranked Candidates</span>
        <span className="text-[var(--color-text-primary)]">{candidates.length} Found</span>
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto p-3 space-y-1.5 overscroll-contain">
        {currentCandidates.map((c, index) => {
          const actualIndex = startIndex + index;
          const isSelected = c.candidate_id === selectedId;
          const hasFlags = c.anti_pattern_flags && c.anti_pattern_flags.length > 0;
          const rankBadge = actualIndex < 3;

          return (
            <motion.div
              key={c.candidate_id}
              onClick={() => onSelect(c)}
              className={`p-3 rounded-xl border transition-all cursor-pointer flex flex-col gap-2 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-black/8 ${
                isSelected
                  ? 'bg-[var(--color-surface-pressed)] border-[var(--color-border-focus)] shadow-lg shadow-black/6'
                  : 'bg-[var(--color-bg-elevated)] border-[var(--color-border-subtle)] hover:border-[var(--color-border-focus)] hover:bg-[var(--color-surface-soft)]'
              }`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.03, duration: 0.3 }}
            >
              <div className="flex items-center gap-3">
                <div className="relative">
                  {rankBadge ? (
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center font-black text-sm shrink-0 ring-2 ring-offset-1 ring-offset-[var(--color-bg-base)] ${
                      actualIndex === 0 ? 'rank-gold ring-[var(--color-border-focus)]' : actualIndex === 1 ? 'rank-silver ring-[var(--color-border-subtle)]' : 'rank-bronze ring-[var(--color-border-subtle)]'
                    }`}>
                      #{actualIndex + 1}
                    </div>
                  ) : (
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm shrink-0 ${
                      isSelected ? 'bg-[var(--color-avatar-bg)] text-[var(--color-avatar-text)]' : 'bg-[var(--color-surface-pressed)] text-[var(--color-text-tertiary)]'
                    }`}>
                      {c.candidate_details?.profile?.anonymized_name?.charAt(0) || 'C'}
                    </div>
                  )}
                  {hasFlags && (
                    <div className="absolute -top-0.5 -right-0.5 w-3.5 h-3.5 bg-rose-500 rounded-full flex items-center justify-center">
                      <AlertTriangle size={8} className="text-[var(--color-button-solid-text)]" />
                    </div>
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/candidate/${c.candidate_id}`, { state: { candidate: c, returnTo: '/analyze' } });
                    }}
                    className="font-semibold text-[var(--color-text-primary)] truncate text-sm hover:text-[var(--color-accent-blue)] transition-colors text-left block"
                  >
                    {c.candidate_details?.profile?.anonymized_name || c.candidate_id}
                  </button>
                  <div className="text-xs text-[var(--color-text-tertiary)] truncate">
                    {c.candidate_details?.profile?.current_title || 'Software Engineer'}
                  </div>
                </div>

                <div className="text-right shrink-0">
                  <div className={`text-lg font-black ${
                    c.score >= 80 ? 'gradient-text-emerald' :
                    c.score >= 60 ? 'gradient-text-amber' :
                    'text-[var(--color-text-tertiary)]'
                  }`}>
                    {c.score.toFixed(1)}
                  </div>
                </div>
              </div>

              <div className="flex gap-1 h-1 rounded-full overflow-hidden bg-[var(--color-surface-pressed)]">
                <div
                  className="h-full bg-[var(--color-accent-blue)] rounded-full transition-all duration-700"
                  style={{ width: `${Math.min(c.skill_match, 100)}%` }}
                />
              </div>

              <div className="flex items-center justify-between gap-3 text-[10px]">
                <div className="flex gap-2">
                  <span className="flex items-center gap-1 text-[var(--color-text-primary)] font-medium px-1.5 py-0.5 rounded bg-[var(--color-surface-pressed)]">
                    <Target size={9} /> {c.skill_match.toFixed(0)}%
                  </span>
                  <span className="flex items-center gap-1 text-[var(--color-text-secondary)] font-medium px-1.5 py-0.5 rounded bg-[var(--color-surface-pressed)]">
                    <Activity size={9} /> {c.potential_score.toFixed(0)}
                  </span>
                  {c.transferable_matches > 0 && (
                    <span className="text-[var(--color-text-secondary)] font-medium px-1.5 py-0.5 rounded bg-[var(--color-surface-pressed)]">
                      +{c.transferable_matches} transfer
                    </span>
                  )}
                </div>
                <div className="text-[var(--color-text-tertiary)]">
                  {c.candidate_details?.profile?.years_of_experience || 0}y
                </div>
              </div>

              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  navigate(`/candidate/${c.candidate_id}`, { state: { candidate: c, returnTo: '/analyze' } });
                }}
                className="inline-flex items-center gap-1.5 self-start rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-button-solid)] text-[var(--color-button-solid-text)] px-2.5 py-1 text-[11px] font-medium transition-colors hover:bg-[var(--color-button-solid-hover)]"
              >
                <ExternalLink size={11} />
                View Candidate
              </button>
            </motion.div>
          );
        })}
      </div>

      {totalPages > 1 && (
        <div className="shrink-0 bg-[var(--color-bg-elevated)] border-t border-[var(--color-border-subtle)] px-4 py-3 flex items-center justify-between">
          <button
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="p-2 rounded-lg bg-[var(--color-surface-pressed)] hover:bg-[var(--color-button-soft-hover)] text-[var(--color-text-tertiary)] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft size={14} />
          </button>

          <div className="text-xs text-[var(--color-text-secondary)] font-medium">
            Page {currentPage} of {totalPages}
          </div>

          <button
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className="p-2 rounded-lg bg-[var(--color-surface-pressed)] hover:bg-[var(--color-button-soft-hover)] text-[var(--color-text-tertiary)] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronRight size={14} />
          </button>
        </div>
      )}
    </div>
  );
}
