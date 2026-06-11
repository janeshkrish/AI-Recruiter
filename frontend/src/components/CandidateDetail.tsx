import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, Network, Briefcase, CheckCircle, AlertTriangle, ExternalLink } from 'lucide-react';
import type { Candidate } from '../App';
import SkillGraph from './SkillGraph';
import CandidateProfileModal from './CandidateProfileModal';

interface Props {
  candidate: Candidate;
}

export default function CandidateDetail({ candidate }: Props) {
  const [expandedSection, setExpandedSection] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);

  const toggleSection = (section: string) => {
    setExpandedSection(prev => prev === section ? null : section);
  };

  const prob = ((candidate.location_match + candidate.score) / 2).toFixed(0);
  const history = candidate.candidate_details?.career_history || [];
  const skills = candidate.candidate_details?.normalized_skills || [];

  return (
    <div className="max-w-4xl mx-auto p-8 space-y-6">
      
      {/* Top Header Card */}
      <div className="bg-gradient-to-br from-white to-slate-50 border border-slate-200 rounded-2xl p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)] relative overflow-hidden">
        {/* Subtle background glow */}
        <div className="absolute -top-24 -right-24 w-48 h-48 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-10 pointer-events-none"></div>
        <div className="absolute -bottom-24 -left-24 w-48 h-48 bg-emerald-400 rounded-full mix-blend-multiply filter blur-3xl opacity-10 pointer-events-none"></div>

        <div className="flex justify-between items-start mb-6 relative z-10">
          <div className="flex gap-5 items-center">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg shadow-blue-500/20 flex items-center justify-center text-3xl font-black text-white">
              {candidate.candidate_details?.profile?.anonymized_name?.charAt(0) || 'C'}
            </div>
            <div>
              <h2 className="text-3xl font-bold text-slate-900 tracking-tight">{candidate.candidate_details?.profile?.anonymized_name || candidate.candidate_id}</h2>
              <p className="text-blue-600 font-semibold mt-1">{candidate.candidate_details?.profile?.current_title || 'AI Engineer'}</p>
              <div className="flex items-center gap-2 mt-2 text-sm text-slate-500">
                <Briefcase size={14}/> {candidate.candidate_details?.profile?.years_of_experience || 0} years exp
              </div>
            </div>
          </div>
          <div className="flex gap-6 bg-white/60 backdrop-blur-md border border-slate-100 p-4 rounded-2xl shadow-sm">
            <div className="text-center px-4 border-r border-slate-200">
              <div className="text-3xl font-black bg-clip-text text-transparent bg-gradient-to-r from-emerald-500 to-teal-400">{prob}%</div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">Hiring Prob</div>
            </div>
            <div className="text-center px-4 border-r border-slate-200">
              <div className="text-3xl font-black bg-clip-text text-transparent bg-gradient-to-r from-amber-400 to-orange-500">{candidate.potential_score.toFixed(0)}</div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">Potential</div>
            </div>
            <div className="text-center pl-4">
              <div className="text-3xl font-black bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-500">{candidate.score.toFixed(1)}</div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">Match Score</div>
            </div>
          </div>
        </div>
        
        <div className="mb-6 flex justify-end relative z-10">
           <button 
             onClick={() => setShowModal(true)}
             className="px-5 py-2.5 bg-slate-900 hover:bg-black text-white rounded-xl shadow-md hover:shadow-xl transition-all flex items-center gap-2 font-semibold text-sm"
           >
             <ExternalLink size={16} /> View Full Profile
           </button>
        </div>

        {/* Top Skills Quick View */}
        <div className="mb-2 relative z-10">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Core Competencies</div>
          <div className="flex flex-wrap gap-2">
            {skills.slice(0, 6).map((s: any, idx: number) => (
              <span key={idx} className="px-3 py-1.5 bg-white border border-slate-200 shadow-sm rounded-lg text-xs font-semibold text-slate-700 hover:border-blue-300 transition-colors cursor-default">
                {s.name}
              </span>
            ))}
            {candidate.transferable_matches > 0 && (
              <span className="px-3 py-1.5 bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg text-xs font-bold text-purple-700 shadow-sm">
                +{candidate.transferable_matches} Transferable
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Intelligence Readout (No Scrolling Required) */}
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white border-l-4 border-l-emerald-400 border-y border-r border-y-slate-200 border-r-slate-200 rounded-2xl p-6 shadow-sm">
          <h3 className="text-base font-bold text-slate-900 mb-5 flex items-center gap-2">
            <CheckCircle size={18} className="text-emerald-500" /> Why Matched & Strengths
          </h3>
          <div className="space-y-3">
            {candidate.reasoning.split(';').map((r, i) => (
              <div key={i} className="text-sm text-slate-600 flex items-start gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                {r.trim()}
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white border-l-4 border-l-rose-400 border-y border-r border-y-slate-200 border-r-slate-200 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900 mb-5 flex items-center gap-2">
              <AlertTriangle size={18} className="text-rose-500" /> Risk Factors & Weaknesses
            </h3>
            <div className="text-sm text-slate-600">
              {candidate.experience_match < 60 ? (
                <span className="text-amber-700 bg-amber-50 px-2 py-1 rounded inline-block">Lower absolute experience level compared to JD</span>
              ) : candidate.skill_match < 50 ? (
                <span className="text-rose-700 bg-rose-50 px-2 py-1 rounded inline-block">Missing primary technical requirements; relying heavily on transferability</span>
              ) : (
                <span className="text-slate-500 italic">No major algorithmic risk factors detected. Solid baseline match.</span>
              )}
            </div>
          </div>
          
          <div className="mt-6 pt-4 border-t border-slate-100">
            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Recruiter Recommendation</h4>
            <div className="text-sm font-medium text-slate-800">
              {candidate.score > 85 ? 'Strong Buy. Interview immediately.' : candidate.potential_score > 80 ? 'High Potential. Evaluate for growth role.' : 'Standard Fit. Proceed with technical screen.'}
            </div>
          </div>
        </div>
      </div>

      {/* Expandable Sections (View More) */}
      <div className="space-y-4 pt-4">
        
        {/* Career Timeline Expand */}
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          <button onClick={() => toggleSection('career')} className="w-full p-4 flex items-center justify-between bg-slate-50 hover:bg-slate-100 transition-colors">
            <span className="font-semibold text-slate-800 flex items-center gap-2"><Briefcase size={16} className="text-slate-400"/> Career Timeline</span>
            {expandedSection === 'career' ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          <AnimatePresence>
            {expandedSection === 'career' && (
              <motion.div initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }} className="overflow-hidden">
                <div className="p-6 border-t border-slate-200">
                  <div className="relative pl-6 space-y-8 before:absolute before:inset-y-0 before:left-[11px] before:w-px before:bg-slate-200">
                    {history.map((job: any, i: number) => (
                      <div key={i} className="relative">
                        <div className="absolute -left-[30px] top-1.5 w-3 h-3 bg-white border-2 border-slate-400 rounded-full"></div>
                        <div className="font-semibold text-slate-900">{job.title}</div>
                        <div className="text-xs text-slate-500 font-medium mb-2">{job.company} • {job.start_date} - {job.end_date || 'Present'}</div>
                        <div className="text-sm text-slate-600 leading-relaxed">{job.description}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Skill Graph Expand */}
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          <button onClick={() => toggleSection('skills')} className="w-full p-4 flex items-center justify-between bg-slate-50 hover:bg-slate-100 transition-colors">
            <span className="font-semibold text-slate-800 flex items-center gap-2"><Network size={16} className="text-slate-400"/> Skill Evolution Graph</span>
            {expandedSection === 'skills' ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          <AnimatePresence>
            {expandedSection === 'skills' && (
              <motion.div initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }} className="overflow-hidden">
                <div className="p-6 border-t border-slate-200 h-[400px]">
                  {skills.length > 0 ? (
                    <SkillGraph skills={skills} />
                  ) : (
                    <div className="flex h-full items-center justify-center text-slate-400">No structured skills available</div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

      </div>

      {showModal && (
        <CandidateProfileModal 
          candidateId={candidate.candidate_id} 
          onClose={() => setShowModal(false)} 
        />
      )}
    </div>
  );
}
