import { motion } from 'framer-motion';

export default function WhatIfPanel({ weights, onChange }: { weights: any, onChange: (w: any) => void }) {
  const sliders = [
    { key: 'skill_match', label: 'Technical Depth (Skill Graph)' },
    { key: 'experience_match', label: 'Career Momentum' },
    { key: 'semantic_similarity', label: 'Learning Potential / Domain Match' },
    { key: 'education_match', label: 'Education Requirement' }
  ];

  return (
    <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="glass-panel p-5 mb-4 overflow-hidden">
      <div className="text-sm font-semibold text-white mb-4">What-If Analysis Engine</div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">
        {sliders.map(s => (
          <div key={s.key} className="flex flex-col gap-2">
            <div className="flex justify-between text-xs text-slate-400">
              <span>{s.label}</span>
              <span className="font-mono text-indigo-400">{weights[s.key].toFixed(1)}x</span>
            </div>
            <input 
              type="range" min="0" max="3" step="0.1" 
              value={weights[s.key]} 
              onChange={(e) => onChange({...weights, [s.key]: parseFloat(e.target.value)})}
              className="w-full accent-indigo-500 h-1 bg-white/10 rounded-lg appearance-none cursor-pointer"
            />
          </div>
        ))}
      </div>
    </motion.div>
  );
}
