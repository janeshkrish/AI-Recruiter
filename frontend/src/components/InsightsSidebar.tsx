import { SlidersHorizontal, Diamond, TrendingUp } from 'lucide-react';
import type { Candidate } from '../App';

interface Props {
  candidates: Candidate[];
  weights: any;
  onWeightChange: (newWeights: any) => void;
}

export default function InsightsSidebar({ candidates, weights, onWeightChange }: Props) {
  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>, key: string) => {
    onWeightChange({
      ...weights,
      [key]: parseFloat(e.target.value)
    });
  };

  const highestPotential = [...candidates].sort((a, b) => b.potential_score - a.potential_score)[0];
  const hiddenGem = [...candidates].sort((a, b) => (b.potential_score - b.experience_match) - (a.potential_score - a.experience_match))[0];

  return (
    <div className="space-y-8">
      
      <div>
        <h3 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2 uppercase tracking-wide">
          <SlidersHorizontal size={16} className="text-blue-500" /> What-If Analysis
        </h3>
        <p className="text-xs text-slate-500 mb-6">Adjust the algorithmic weights. Rankings will recompute instantly across the dataset.</p>
        
        <div className="space-y-5">
          <div>
            <div className="flex justify-between text-xs font-medium text-slate-700 mb-2">
              <span>Technical Depth</span>
              <span className="text-blue-600">{weights.skill_match.toFixed(1)}x</span>
            </div>
            <input 
              type="range" min="0" max="3" step="0.1" 
              value={weights.skill_match} 
              onChange={(e) => handleSliderChange(e, 'skill_match')}
              className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs font-medium text-slate-700 mb-2">
              <span>Experience & Seniority</span>
              <span className="text-blue-600">{weights.experience_match.toFixed(1)}x</span>
            </div>
            <input 
              type="range" min="0" max="3" step="0.1" 
              value={weights.experience_match} 
              onChange={(e) => handleSliderChange(e, 'experience_match')}
              className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs font-medium text-slate-700 mb-2">
              <span>Domain Similarity</span>
              <span className="text-blue-600">{weights.semantic_similarity.toFixed(1)}x</span>
            </div>
            <input 
              type="range" min="0" max="3" step="0.1" 
              value={weights.semantic_similarity} 
              onChange={(e) => handleSliderChange(e, 'semantic_similarity')}
              className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
          </div>
        </div>
      </div>

      <hr className="border-slate-200" />

      <div>
        <h3 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2 uppercase tracking-wide">
          <TrendingUp size={16} className="text-emerald-500" /> Batch Insights
        </h3>

        <div className="space-y-4">
          <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-4">
            <div className="text-[10px] font-bold text-emerald-600 uppercase tracking-widest mb-1 flex items-center gap-1"><Diamond size={12}/> Hidden Gem</div>
            <div className="font-semibold text-slate-900 text-sm truncate">{hiddenGem?.candidate_details?.profile?.anonymized_name || hiddenGem?.candidate_id}</div>
            <div className="text-xs text-slate-600 mt-1">High potential, lower absolute experience. Evaluated well on transferability.</div>
          </div>

          <div className="bg-purple-50 border border-purple-100 rounded-xl p-4">
            <div className="text-[10px] font-bold text-purple-600 uppercase tracking-widest mb-1 flex items-center gap-1"><TrendingUp size={12}/> Highest Ceiling</div>
            <div className="font-semibold text-slate-900 text-sm truncate">{highestPotential?.candidate_details?.profile?.anonymized_name || highestPotential?.candidate_id}</div>
            <div className="text-xs text-slate-600 mt-1">Top learning velocity percentile based on career trajectory.</div>
          </div>
        </div>
      </div>

    </div>
  );
}
