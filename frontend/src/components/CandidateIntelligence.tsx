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
        className="relative w-full max-w-7xl h-[88vh] glass-card border border-violet-500/10 shadow-[0_20px_80px_rgba(139,92,246,0.15)] rounded-3xl flex flex-col overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10 bg-gradient-to-r from-violet-500/5 via-transparent to-cyan-500/5">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-xl font-bold text-white shadow-lg shadow-violet-500/20">
              {candidate.candidate_details?.profile?.anonymized_name?.charAt(0) || 'C'}
            </div>
           <div>
  <h2 className="text-2xl font-bold text-white">
    {candidate.candidate_details?.profile?.anonymized_name ||
      candidate.candidate_id}
  </h2>

  <div className="text-slate-400 text-sm">
    {candidate.candidate_details?.profile?.current_title ||
      'Engineer'}
  </div>

  <div className="flex flex-wrap gap-2 mt-3">
    <span className="px-3 py-1 rounded-full bg-violet-500/10 text-violet-300 text-xs border border-violet-500/20">
      AI Ranked
    </span>

    <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-300 text-xs border border-emerald-500/20">
      Top Candidate
    </span>

    {candidate.potential_score > 80 && (
      <span className="px-3 py-1 rounded-full bg-amber-500/10 text-amber-300 text-xs border border-amber-500/20">
        High Potential
      </span>
    )}

    {candidate.skill_match > 85 && (
      <span className="px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-300 text-xs border border-cyan-500/20">
        Technical Expert
      </span>
    )}
  </div>
</div>
</div>
          
        <div className="flex items-center gap-3">

  <div className="bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-center min-w-[110px]">
    <div className="text-2xl font-bold text-emerald-400">
      {((candidate.location_match + candidate.score) / 2).toFixed(0)}%
    </div>
    <div className="text-[10px] uppercase tracking-wider text-slate-500">
      Hiring Prob
    </div>
  </div>

  <div className="bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-center min-w-[110px]">
    <div className="text-2xl font-bold text-amber-400">
      {candidate.potential_score.toFixed(1)}
    </div>
    <div className="text-[10px] uppercase tracking-wider text-slate-500">
      Potential
    </div>
  </div>

  <div className="bg-white/5 border border-white/10 rounded-2xl px-5 py-3 text-center min-w-[110px]">
    <div className="text-2xl font-bold text-violet-400">
      {candidate.score.toFixed(1)}
    </div>
    <div className="text-[10px] uppercase tracking-wider text-slate-500">
      Match
    </div>
  </div>

  <button
    onClick={onClose}
    className="p-3 ml-2 bg-white/5 hover:bg-white/10 rounded-xl transition-colors text-slate-400 hover:text-white"
  >
    <X size={20} />
  </button>
  </div>

</div>
        <div className="px-6 py-4 border-b border-white/5">
  <div className="glass-card p-4">
    <h3 className="text-white font-semibold mb-2">
      Executive Summary
    </h3>

    <p className="text-sm text-slate-300 leading-relaxed">
      Strong technical alignment with excellent growth potential.
      Candidate demonstrates relevant experience, transferable skills,
      and high interview readiness. Recommended for immediate recruiter review.
    </p>
  </div>
</div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 flex flex-col md:flex-row gap-6">
          
          <div className="flex-1 space-y-6">
            <section className="glass-card p-5">
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4 flex items-center gap-2"><Network size={16} className="text-violet-400"/> Interactive Skill Graph</h3>
              {skills.length > 0 ? (
                <SkillGraph skills={skills} />
              ) : (
                <div className="h-64 flex items-center justify-center text-slate-500">No structured skills found in payload.</div>
              )}
            </section>

            <section className="glass-card p-5">
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">AI Recruiter Reasoning</h3>
              <div className="p-4 bg-white/5 border border-white/5 rounded-xl text-slate-300 text-sm leading-relaxed">
                {candidate.reasoning.split(';').map((r, i) => (
                  <div key={i} className="mb-2 flex items-start gap-2">
                    <ChevronRight size={16} className="text-violet-400 mt-0.5 shrink-0" /> {r.trim()}
                  </div>
                ))}
              </div>
            </section>
          </div>

          <div className="w-[400px] space-y-6">
            <section className="glass-card p-5 h-full">
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
