import { SlidersHorizontal, Diamond, TrendingUp } from 'lucide-react';
import type { Candidate } from '../App';

interface Props {
  candidates: Candidate[];
  weights: any;
  onWeightChange: (newWeights: any) => void;
}

export default function InsightsSidebar({
  candidates,
  weights,
  onWeightChange,
}: Props) {
  const handleSliderChange = (
    e: React.ChangeEvent<HTMLInputElement>,
    key: string
  ) => {
    onWeightChange({
      ...weights,
      [key]: parseFloat(e.target.value),
    });
  };

  const highestPotential = [...candidates].sort(
    (a, b) => b.potential_score - a.potential_score
  )[0];

  const hiddenGem = [...candidates].sort(
    (a, b) =>
      b.potential_score -
      b.experience_match -
      (a.potential_score - a.experience_match)
  )[0];

  return (
    <div className="glass-card p-6 space-y-8">

      {/* What If Analysis */}
      <div>

        <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2 uppercase tracking-wide">
          <SlidersHorizontal
            size={16}
            className="text-violet-400"
          />
          What-If Analysis
        </h3>

        <p className="text-xs text-slate-400 mb-6">
          Adjust ranking weights and instantly
          recompute candidate ordering.
        </p>

        <div className="space-y-5">

          {/* Technical Depth */}
          <div>

            <div className="flex justify-between text-xs font-medium text-slate-300 mb-2">
              <span>Technical Depth</span>

              <span className="text-violet-400">
                {weights.skill_match.toFixed(1)}x
              </span>
            </div>

            <input
              type="range"
              min="0"
              max="3"
              step="0.1"
              value={weights.skill_match}
              onChange={(e) =>
                handleSliderChange(e, 'skill_match')
              }
              className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-violet-500"
            />

          </div>

          {/* Experience */}
          <div>

            <div className="flex justify-between text-xs font-medium text-slate-300 mb-2">
              <span>Experience & Seniority</span>

              <span className="text-violet-400">
                {weights.experience_match.toFixed(1)}x
              </span>
            </div>

            <input
              type="range"
              min="0"
              max="3"
              step="0.1"
              value={weights.experience_match}
              onChange={(e) =>
                handleSliderChange(
                  e,
                  'experience_match'
                )
              }
              className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-violet-500"
            />

          </div>

          {/* Domain Similarity */}
          <div>

            <div className="flex justify-between text-xs font-medium text-slate-300 mb-2">
              <span>Domain Similarity</span>

              <span className="text-violet-400">
                {weights.semantic_similarity.toFixed(
                  1
                )}x
              </span>
            </div>

            <input
              type="range"
              min="0"
              max="3"
              step="0.1"
              value={weights.semantic_similarity}
              onChange={(e) =>
                handleSliderChange(
                  e,
                  'semantic_similarity'
                )
              }
              className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-violet-500"
            />

          </div>

        </div>
      </div>

      <hr className="border-white/10" />

      {/* Batch Insights */}
      <div>

        <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2 uppercase tracking-wide">
          <TrendingUp
            size={16}
            className="text-cyan-400"
          />
          Batch Insights
        </h3>

        <div className="space-y-4">

          {/* Hidden Gem */}
          <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-4">

            <div className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest mb-2 flex items-center gap-1">
              <Diamond size={12} />
              Hidden Gem
            </div>

            <div className="font-semibold text-white text-sm truncate">
              {hiddenGem?.candidate_details?.profile
                ?.anonymized_name ||
                hiddenGem?.candidate_id}
            </div>

            <div className="text-xs text-slate-400 mt-2">
              High potential with strong transferability
              despite lower experience alignment.
            </div>

          </div>

          {/* Highest Ceiling */}
          <div className="bg-violet-500/10 border border-violet-500/20 rounded-2xl p-4">

            <div className="text-[10px] font-bold text-violet-400 uppercase tracking-widest mb-2 flex items-center gap-1">
              <TrendingUp size={12} />
              Highest Ceiling
            </div>

            <div className="font-semibold text-white text-sm truncate">
              {highestPotential?.candidate_details
                ?.profile?.anonymized_name ||
                highestPotential?.candidate_id}
            </div>

            <div className="text-xs text-slate-400 mt-2">
              Top learning velocity and long-term
              growth trajectory.
            </div>

          </div>

        </div>
      </div>

    </div>
  );
}