import { motion } from 'framer-motion';
import { X, Network, Briefcase, TrendingUp } from 'lucide-react';
import type { Candidate } from '../App';
import SkillGraph from './SkillGraph';

interface Props {
  candidate: Candidate;
  onClose: () => void;
}

export default function CandidateNetflixProfile({ candidate, onClose }: Props) {
  const history = candidate.candidate_details?.career_history || [];
  const skills = candidate.candidate_details?.normalized_skills || [];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 50 }} 
      animate={{ opacity: 1, y: 0 }} 
      exit={{ opacity: 0, y: 50 }}
      transition={{ type: "spring", bounce: 0, duration: 0.5 }}
      className="fixed inset-0 z-50 bg-[#030712] overflow-y-auto pointer-events-auto"
    >
      {/* Hero Banner */}
      <div className="relative h-[60vh] w-full bg-gradient-to-b from-indigo-900/40 to-[#030712] flex items-end p-16">
        <button onClick={onClose} className="absolute top-10 right-10 p-4 bg-white/5 hover:bg-white/10 rounded-full transition-colors text-slate-400 hover:text-white border border-white/10 backdrop-blur-md">
          <X size={32} />
        </button>

        <div className="max-w-7xl mx-auto w-full flex items-end justify-between">
          <div>
            <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="text-7xl font-black text-white tracking-tight mb-4 drop-shadow-2xl">
              {candidate.candidate_details?.profile?.anonymized_name || candidate.candidate_id}
            </motion.h1>
            <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="text-3xl text-slate-300 font-medium">
              {candidate.candidate_details?.profile?.current_title || 'Software Engineer'}
            </motion.p>
          </div>
          
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.4 }} className="flex gap-6">
            <div className="text-center">
              <div className="text-4xl font-black text-emerald-400 drop-shadow-[0_0_20px_rgba(16,185,129,0.5)]">{((candidate.location_match + candidate.score)/2).toFixed(0)}%</div>
              <div className="text-xs uppercase tracking-widest text-emerald-400/70 font-bold mt-2">Hiring Prob</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-black text-amber-400 drop-shadow-[0_0_20px_rgba(245,158,11,0.5)]">{candidate.potential_score.toFixed(0)}</div>
              <div className="text-xs uppercase tracking-widest text-amber-400/70 font-bold mt-2">Potential</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-black text-white drop-shadow-[0_0_20px_rgba(255,255,255,0.5)]">{candidate.score.toFixed(0)}</div>
              <div className="text-xs uppercase tracking-widest text-white/70 font-bold mt-2">Match Score</div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Content Stream */}
      <div className="max-w-7xl mx-auto w-full p-16 -mt-10">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-16">
          
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-16">
            
            {/* AI Explanation Engine */}
            <motion.section initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3"><TrendingUp className="text-indigo-400"/> AI Reasoning Engine</h2>
              <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-3xl p-8 shadow-2xl">
                <div className="space-y-4">
                  {candidate.reasoning.split(';').map((r, i) => (
                    <div key={i} className="text-lg text-slate-300 leading-relaxed pl-6 relative before:absolute before:left-0 before:top-2 before:w-2 before:h-2 before:bg-indigo-500 before:rounded-full">
                      {r.trim()}
                    </div>
                  ))}
                </div>
              </div>
            </motion.section>

            {/* Career Timeline */}
            <motion.section initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
              <h2 className="text-2xl font-bold text-white mb-8 flex items-center gap-3"><Briefcase className="text-emerald-400"/> Career Timeline</h2>
              <div className="relative pl-10 space-y-12 before:absolute before:inset-y-0 before:left-[19px] before:w-1 before:bg-gradient-to-b before:from-emerald-500 before:via-indigo-500 before:to-purple-500">
                {history.map((job: any, i: number) => (
                  <motion.div initial={{ x: -20, opacity: 0 }} whileInView={{ x: 0, opacity: 1 }} viewport={{ once: true, margin: "-100px" }} key={i} className="relative">
                    <div className="absolute -left-[45px] top-2 w-5 h-5 bg-[#030712] rounded-full ring-4 ring-emerald-500"></div>
                    <div className="backdrop-blur-md bg-white/5 border border-white/10 p-8 rounded-3xl hover:bg-white/10 transition-colors">
                      <div className="text-2xl font-bold text-white mb-2">{job.title}</div>
                      <div className="text-indigo-400 font-medium tracking-wide mb-6">{job.company} • {job.start_date} - {job.end_date || 'Present'}</div>
                      <div className="text-slate-300 leading-relaxed text-lg">{job.description}</div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.section>
          </div>

          {/* Sidebar */}
          <div className="space-y-12">
            
            {/* Skill Evolution (Graph) */}
            <motion.section initial={{ opacity: 0, x: 20 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}>
              <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-3"><Network className="text-blue-400"/> Skill Evolution</h2>
              {skills.length > 0 ? (
                <div className="h-[400px] rounded-3xl overflow-hidden border border-white/10">
                  <SkillGraph skills={skills} />
                </div>
              ) : (
                <div className="h-[400px] flex items-center justify-center border border-white/10 rounded-3xl bg-white/5 text-slate-500">
                  No structured skills available.
                </div>
              )}
            </motion.section>

            {/* Profile Summary */}
            <motion.section initial={{ opacity: 0, x: 20 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} className="backdrop-blur-md bg-white/5 border border-white/10 rounded-3xl p-8">
              <h3 className="text-sm uppercase tracking-widest text-slate-500 font-bold mb-4">Executive Summary</h3>
              <p className="text-slate-300 leading-relaxed">
                {candidate.candidate_details?.profile?.summary || "No executive summary provided."}
              </p>
            </motion.section>

          </div>

        </div>
      </div>
    </motion.div>
  );
}
