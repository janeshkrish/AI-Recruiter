import { useState } from 'react';
import { Filter, ArrowUpRight, TrendingUp, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import type { Candidate } from '../App';

interface Props {
  candidates: Candidate[];
  onSelect: (c: Candidate) => void;
  isEvaluating: boolean;
}

export default function CandidateExplorer({
  candidates,
  onSelect,
  isEvaluating,
}: Props) {
  const [minScore, setMinScore] = useState(0);

  if (isEvaluating) {
    return (
      <div className="flex flex-col items-center justify-center h-80">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{
            repeat: Infinity,
            duration: 2,
            ease: 'linear',
          }}
          className="mb-6 text-violet-400"
        >
          <Zap size={56} />
        </motion.div>

        <h3 className="text-xl font-bold text-white mb-2">
          AI Agents Evaluating Talent
        </h3>

        <p className="text-slate-400">
          Ranking candidates across the talent universe...
        </p>
      </div>
    );
  }

  if (!candidates.length) {
    return (
      <div className="flex items-center justify-center h-80 text-slate-500">
        Awaiting Job Description Analysis...
      </div>
    );
  }

  const filtered = candidates.filter(
    (c) => c.score >= minScore
  );

  return (
    <div className="space-y-6">

      {/* Filter */}
      <div className="glass-card p-5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">

          <div className="flex items-center gap-3">
            <Filter
              size={18}
              className="text-violet-400"
            />

            <div>
              <div className="font-semibold text-white">
                Candidate Filter
              </div>

              <div className="text-xs text-slate-500">
                Minimum Score: {minScore}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <input
              type="range"
              min="0"
              max="100"
              value={minScore}
              onChange={(e) =>
                setMinScore(Number(e.target.value))
              }
              className="w-48 accent-violet-500"
            />

            <span className="text-sm text-slate-400">
              {filtered.length} Results
            </span>
          </div>

        </div>
      </div>

      {/* Candidate Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">

        {filtered.map((c, i) => (
          <motion.div
            key={c.candidate_id}
            initial={{
              opacity: 0,
              y: 20,
            }}
            animate={{
              opacity: 1,
              y: 0,
            }}
            transition={{
              delay: i * 0.05,
            }}
            whileHover={{
              y: -6,
            }}
            onClick={() => onSelect(c)}
            className="glass-card p-6 cursor-pointer group relative overflow-hidden"
          >

            {/* Glow */}
            <div className="absolute top-0 right-0 w-40 h-40 bg-violet-500/10 blur-3xl rounded-full opacity-0 group-hover:opacity-100 transition-all" />

            {/* Header */}
            <div className="flex justify-between items-start mb-5">

              <div>
                <h3 className="font-bold text-lg text-white">
                  {c.candidate_id}
                </h3>

                {c.potential_score > 80 && (
                  <div className="mt-2 inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-amber-500/10 text-amber-400 border border-amber-500/20">
                    <TrendingUp size={12} />
                    High Potential
                  </div>
                )}
              </div>

              <div className="text-right">
                <div className="text-4xl font-black gradient-text-blue">
                  {c.score.toFixed(0)}
                </div>

                <div className="text-[10px] uppercase tracking-wider text-slate-500">
                  AI Score
                </div>
              </div>

            </div>

            {/* Metrics */}
            <div className="space-y-4">

              <MetricBar
                label="Technical Match"
                value={c.skill_match}
                color="bg-cyan-500"
              />

              <MetricBar
                label="Experience Match"
                value={c.experience_match}
                color="bg-emerald-500"
              />

              <MetricBar
                label="Potential"
                value={c.potential_score}
                color="bg-violet-500"
              />

            </div>

            {/* Footer */}
            <div className="mt-6 flex justify-between items-center">

              <span className="text-xs text-slate-500">
                {c.transferable_matches} transferable skills
              </span>

              <span className="flex items-center gap-1 text-violet-400 text-sm font-medium">
                View Details
                <ArrowUpRight size={14} />
              </span>

            </div>

          </motion.div>
        ))}

      </div>
    </div>
  );
}

function MetricBar({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-slate-400">
          {label}
        </span>

        <span className="text-white">
          {value.toFixed(0)}%
        </span>
      </div>

      <div className="h-2 bg-white/5 rounded-full overflow-hidden">
        <div
          className={`h-full ${color}`}
          style={{
            width: `${Math.min(value, 100)}%`,
          }}
        />
      </div>
    </div>
  );
}