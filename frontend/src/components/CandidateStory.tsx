import { motion } from 'framer-motion';
import { X, Sparkles, TrendingUp, Cpu, GitMerge } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer } from 'recharts';
import type { Candidate } from '../App';

interface Props {
  candidate: Candidate;
  onClose: () => void;
}

export default function CandidateStory({ candidate, onClose }: Props) {
  const radarData = [
    { subject: 'Leadership', A: Math.min(100, candidate.experience_match * 1.1) },
    { subject: 'Execution', A: candidate.skill_match },
    { subject: 'Product Sense', A: Math.min(100, candidate.transferable_matches * 30 + 50) },
    { subject: 'Learning Velocity', A: candidate.potential_score },
    { subject: 'Communication', A: candidate.location_match },
    { subject: 'Technical Depth', A: candidate.semantic_similarity },
  ];

  const reasons = candidate.reasoning.split(';').filter(r => r.trim());
  const history = candidate.candidate_details?.career_history || [];
  const isHiddenGem = candidate.potential_score > 85 && candidate.experience_match < 60;

  return (
    <motion.div 
      initial={{ opacity: 0, x: '100%' }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: '100%' }}
      transition={{ type: "spring", bounce: 0, duration: 0.4 }}
      className="fixed inset-y-0 right-0 w-full md:w-[600px] glass-panel bg-[#030712]/90 border-l border-white/10 z-[60] overflow-y-auto"
    >
      {/* Sticky Header */}
      <div className="sticky top-0 z-10 glass-panel border-b border-white/10 p-6 flex justify-between items-start rounded-none">
        <div>
          <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400 mb-2">
            {candidate.candidate_details?.profile?.anonymized_name || candidate.candidate_id}
          </h2>
          <div className="flex gap-3">
            <span className="px-3 py-1 rounded-full text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              Jury Score: {candidate.score.toFixed(1)}
            </span>
            <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              Hiring Prob: {((candidate.score + candidate.location_match)/2).toFixed(0)}%
            </span>
          </div>
        </div>
        <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-colors text-slate-400 hover:text-white">
          <X size={24} />
        </button>
      </div>

      <div className="p-8 space-y-12">
        
        {/* Hidden Gem Alert */}
        {isHiddenGem && (
          <motion.div 
            initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
            className="p-6 rounded-2xl bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-500/30 relative overflow-hidden group"
          >
            <div className="absolute top-0 right-0 w-full h-full bg-amber-500/10 blur-3xl rounded-full animate-pulse"></div>
            <div className="relative z-10">
              <div className="flex items-center gap-2 text-amber-400 font-bold mb-2">
                <Sparkles /> AI Discovered a Hidden Gem
              </div>
              <p className="text-amber-200/80 text-sm">
                This candidate has lower traditional experience but exhibits an extreme Learning Velocity curve. They are highly likely to outperform their peers in a fast-paced environment.
              </p>
            </div>
          </motion.div>
        )}

        {/* AI Reasoning Story */}
        <section>
          <h3 className="text-sm font-bold text-slate-400 uppercase tracking-[0.2em] mb-6 flex items-center gap-3">
            <Cpu size={16} /> Jury Verdict
          </h3>
          <div className="space-y-4">
            {reasons.map((r, i) => (
              <motion.div 
                initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }}
                key={i} 
                className="p-4 rounded-xl bg-white/5 border border-white/5 text-slate-300 leading-relaxed text-sm"
              >
                {r.trim()}
              </motion.div>
            ))}
          </div>
        </section>

        {/* Career DNA Helix (Radar) */}
        <section>
          <h3 className="text-sm font-bold text-slate-400 uppercase tracking-[0.2em] mb-6 flex items-center gap-3">
            <TrendingUp size={16} /> Career DNA
          </h3>
          <div className="h-80 glass-panel rounded-2xl p-4 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-b from-indigo-500/5 to-purple-500/5"></div>
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="65%" data={radarData}>
                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#94A3B8', fontSize: 11 }} />
                <Radar name="DNA" dataKey="A" stroke="#8B5CF6" strokeWidth={3} fill="#8B5CF6" fillOpacity={0.4} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* Skill Evolution River */}
        <section>
          <h3 className="text-sm font-bold text-slate-400 uppercase tracking-[0.2em] mb-6 flex items-center gap-3">
            <GitMerge size={16} /> Skill Evolution River
          </h3>
          <div className="relative pl-6 space-y-8 before:absolute before:inset-y-0 before:left-[11px] before:w-0.5 before:bg-gradient-to-b before:from-emerald-500 before:via-indigo-500 before:to-purple-500">
            {history.map((job: any, i: number) => (
              <motion.div 
                initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.15 }}
                key={i} 
                className="relative"
              >
                <div className="absolute -left-[30px] top-1.5 w-3 h-3 bg-[#030712] border-2 border-indigo-400 rounded-full shadow-[0_0_10px_#818CF8]"></div>
                <div className="glass-panel p-5 rounded-xl border border-white/5">
                  <div className="text-emerald-400 font-bold mb-1">{job.title}</div>
                  <div className="text-xs text-slate-500 mb-4">{job.company} • {job.start_date} - {job.end_date || 'Present'}</div>
                  <div className="text-sm text-slate-300 line-clamp-3">{job.description}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </section>

      </div>
    </motion.div>
  );
}
