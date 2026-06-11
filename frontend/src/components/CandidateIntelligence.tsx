import { motion } from 'framer-motion';
import { X, Network, Briefcase, ChevronRight } from 'lucide-react';
import type { Candidate } from '../App';
import SkillGraph from './SkillGraph';

interface Props {
  candidate: Candidate;
  onClose: () => void;
}

export default function CandidateIntelligence({ candidate, onClose }: Props) {
  const history = candidate.candidate_details?.career_history || [];
  const skills = candidate.candidate_details?.normalized_skills || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 bg-[#030712]/80 backdrop-blur-sm" onClick={onClose} />
      
      <motion.div 
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        className="relative w-full max-w-6xl h-[85vh] glass-panel bg-[#0B0E14] border border-white/10 shadow-2xl rounded-2xl flex flex-col overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10 bg-white/5">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-indigo-500/20 border border-indigo-500/50 flex items-center justify-center text-xl font-bold text-indigo-200">
              {candidate.candidate_details?.profile?.anonymized_name?.charAt(0) || 'C'}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">{candidate.candidate_details?.profile?.anonymized_name || candidate.candidate_id}</h2>
              <div className="text-slate-400 text-sm">{candidate.candidate_details?.profile?.current_title || 'Engineer'}</div>
            </div>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="text-right">
              <div className="text-2xl font-bold text-emerald-400">{((candidate.location_match + candidate.score)/2).toFixed(0)}%</div>
              <div className="text-[10px] uppercase tracking-wider text-slate-500">Hiring Prob</div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-amber-400">{candidate.potential_score.toFixed(1)}</div>
              <div className="text-[10px] uppercase tracking-wider text-slate-500">Potential</div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-indigo-400">{candidate.score.toFixed(1)}</div>
              <div className="text-[10px] uppercase tracking-wider text-slate-500">Match</div>
            </div>
            <button onClick={onClose} className="p-2 ml-4 bg-white/5 hover:bg-white/10 rounded-full transition-colors text-slate-400 hover:text-white">
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 flex flex-col md:flex-row gap-6">
          
          <div className="flex-1 space-y-6">
            <section className="glass-panel p-5">
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4 flex items-center gap-2"><Network size={16} className="text-indigo-400"/> Interactive Skill Graph</h3>
              {skills.length > 0 ? (
                <SkillGraph skills={skills} />
              ) : (
                <div className="h-64 flex items-center justify-center text-slate-500">No structured skills found in payload.</div>
              )}
            </section>

            <section className="glass-panel p-5">
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">AI Recruiter Reasoning</h3>
              <div className="p-4 bg-white/5 border border-white/5 rounded-xl text-slate-300 text-sm leading-relaxed">
                {candidate.reasoning.split(';').map((r, i) => (
                  <div key={i} className="mb-2 flex items-start gap-2">
                    <ChevronRight size={16} className="text-indigo-400 mt-0.5 shrink-0" /> {r.trim()}
                  </div>
                ))}
              </div>
            </section>
          </div>

          <div className="w-[400px] space-y-6">
            <section className="glass-panel p-5 h-full">
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-6 flex items-center gap-2"><Briefcase size={16} className="text-emerald-400"/> Career Journey Timeline</h3>
              <div className="relative pl-6 space-y-8 before:absolute before:inset-y-0 before:left-[11px] before:w-[2px] before:bg-white/10">
                {history.map((job: any, i: number) => (
                  <div key={i} className="relative">
                    <div className="absolute -left-[30px] top-1.5 w-3 h-3 bg-emerald-400 rounded-full ring-4 ring-[#0B0E14]"></div>
                    <div className="text-white font-bold mb-0.5">{job.title}</div>
                    <div className="text-xs text-slate-400 mb-2">{job.company} • {job.start_date} - {job.end_date || 'Present'}</div>
                    <div className="text-sm text-slate-300 leading-relaxed">{job.description}</div>
                  </div>
                ))}
              </div>
            </section>
          </div>

        </div>
      </motion.div>
    </div>
  );
}
