import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronDown, Network, Briefcase, CheckCircle, AlertTriangle,
  ExternalLink, Target, Shield, Activity, MapPin, Award
} from 'lucide-react';
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ResponsiveContainer
} from 'recharts';
import type { Candidate } from '../App';

interface Props {
  candidate: Candidate;
}

export default function CandidateDetail({ candidate }: Props) {
  // Independent accordion states — both can be open simultaneously
  const [careerOpen, setCareerOpen] = useState(false);
  const [skillsOpen, setSkillsOpen] = useState(false);
  const navigate = useNavigate();

  const history = candidate.candidate_details?.career_history || [];
  const skills = candidate.candidate_details?.skills || [];
  const profile = candidate.candidate_details?.profile || {};
  const redrob = candidate.candidate_details?.redrob_signals || {};

  // Radar chart data
  const radarData = [
    { dimension: 'Technical', value: Math.min(candidate.skill_match, 100), fullMark: 100 },
    { dimension: 'Career', value: Math.min(candidate.experience_match, 100), fullMark: 100 },
    { dimension: 'Behavioral', value: Math.min(candidate.behavioral_score || 50, 100), fullMark: 100 },
    { dimension: 'Potential', value: Math.min(candidate.potential_score, 100), fullMark: 100 },
    { dimension: 'Semantic', value: Math.min(candidate.semantic_similarity, 100), fullMark: 100 },
  ];

  // Score bar data
  const scoreBreakdown = [
    { name: 'Technical', value: candidate.skill_match, color: '#3B82F6' },
    { name: 'Career', value: candidate.experience_match, color: '#10B981' },
    { name: 'Behavioral', value: candidate.behavioral_score || 50, color: '#F59E0B' },
    { name: 'Potential', value: candidate.potential_score, color: '#8B5CF6' },
    { name: 'Semantic', value: candidate.semantic_similarity, color: '#06B6D4' },
  ];

  const hasFlags = candidate.anti_pattern_flags && candidate.anti_pattern_flags.length > 0;

  return (
    <div className="max-w-4xl mx-auto p-8 space-y-6">

      {/* ─── Header Card ─── */}
      <motion.div
        className="glass-card p-6 relative overflow-hidden"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Background glows */}
        <div className="absolute -top-24 -right-24 w-48 h-48 bg-blue-500 rounded-full mix-blend-screen filter blur-[80px] opacity-10 pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-48 h-48 bg-purple-500 rounded-full mix-blend-screen filter blur-[80px] opacity-10 pointer-events-none" />

        <div className="flex justify-between items-start mb-6 relative z-10">
          <div className="flex gap-5 items-center">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg shadow-blue-500/20 flex items-center justify-center text-2xl font-black text-white">
              {profile.anonymized_name?.charAt(0) || 'C'}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">
                {profile.anonymized_name || candidate.candidate_id}
              </h2>
              <p className="text-blue-400 font-medium mt-0.5 text-sm">
                {profile.current_title || 'Engineer'}
              </p>
              <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
                <span className="flex items-center gap-1"><Briefcase size={12} /> {profile.years_of_experience || 0}y exp</span>
                <span className="flex items-center gap-1"><MapPin size={12} /> {profile.location || 'N/A'}</span>
                {profile.current_company && (
                  <span className="flex items-center gap-1"><Award size={12} /> {profile.current_company}</span>
                )}
              </div>
            </div>
          </div>

          {/* Score Display */}
          <div className="flex gap-4 glass p-4 rounded-2xl">
            <div className="text-center px-3 border-r border-white/10">
              <div className="text-3xl font-black gradient-text-emerald">{candidate.score.toFixed(1)}</div>
              <div className="text-[9px] font-bold text-slate-500 uppercase tracking-widest mt-1">Score</div>
            </div>
            <div className="text-center px-3 border-r border-white/10">
              <div className="text-3xl font-black gradient-text-amber">{candidate.potential_score.toFixed(0)}</div>
              <div className="text-[9px] font-bold text-slate-500 uppercase tracking-widest mt-1">Potential</div>
            </div>
            <div className="text-center pl-3">
              <div className="text-3xl font-black gradient-text-blue">{(candidate.behavioral_score || 50).toFixed(0)}</div>
              <div className="text-[9px] font-bold text-slate-500 uppercase tracking-widest mt-1">Behavioral</div>
            </div>
          </div>
        </div>

        {/* View Full Profile button — navigates to /candidate/:id */}
        <div className="mb-4 flex justify-end relative z-10">
          <button
            onClick={() =>
              navigate(`/candidate/${candidate.candidate_id}`, {
                state: { candidate },
              })
            }
            className="px-5 py-2 bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 text-white rounded-xl shadow-lg shadow-violet-500/20 transition-all flex items-center gap-2 font-medium text-sm border border-violet-500/20"
          >
            <ExternalLink size={14} /> View Full Profile
          </button>
        </div>

        {/* Top Skills */}
        <div className="relative z-10">
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">Core Competencies</div>
          <div className="flex flex-wrap gap-1.5">
            {skills.slice(0, 8).map((s: any, idx: number) => (
              <span key={idx} className="px-2.5 py-1 bg-white/[0.04] border border-white/[0.08] rounded-lg text-xs font-medium text-slate-300 hover:border-blue-500/30 transition-colors">
                {s.name || s}
              </span>
            ))}
            {candidate.transferable_matches > 0 && (
              <span className="px-2.5 py-1 bg-purple-500/10 border border-purple-500/20 rounded-lg text-xs font-bold text-purple-400">
                +{candidate.transferable_matches} Transferable
              </span>
            )}
          </div>
        </div>
      </motion.div>

      {/* ─── Radar Chart + Score Breakdown ─── */}
      <div className="grid grid-cols-2 gap-6">
        <motion.div
          className="glass-card p-6"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
            <Target size={16} className="text-blue-400" /> Multi-Agent Score Radar
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="rgba(255,255,255,0.06)" />
              <PolarAngleAxis dataKey="dimension" tick={{ fill: '#94A3B8', fontSize: 11 }} />
              <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
              <Radar
                name="Score"
                dataKey="value"
                stroke="#3B82F6"
                fill="#3B82F6"
                fillOpacity={0.15}
                strokeWidth={2}
              />
            </RadarChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div
          className="glass-card p-6"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
            <Activity size={16} className="text-emerald-400" /> Dimension Breakdown
          </h3>
          <div className="space-y-3">
            {scoreBreakdown.map((item, i) => (
              <div key={i}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400 font-medium">{item.name}</span>
                  <span className="text-white font-bold">{item.value.toFixed(1)}%</span>
                </div>
                <div className="progress-bar">
                  <motion.div
                    className="progress-bar-fill"
                    style={{ backgroundColor: item.color }}
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(item.value, 100)}%` }}
                    transition={{ delay: 0.4 + i * 0.1, duration: 0.8, ease: 'easeOut' }}
                  />
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* ─── Reasoning + Risk Cards ─── */}
      <div className="grid grid-cols-2 gap-6">
        {/* Strengths */}
        <motion.div
          className="glass-card p-6 border-l-2 border-l-emerald-500"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
            <CheckCircle size={16} className="text-emerald-400" /> Why Matched & Strengths
          </h3>
          <div className="space-y-2.5">
            {candidate.reasoning.split(';').filter(r => !r.trim().startsWith('⚠')).map((r, i) => (
              <div key={i} className="text-xs text-slate-400 flex items-start gap-2 leading-relaxed">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                {r.trim()}
              </div>
            ))}
          </div>
        </motion.div>

        {/* Risks */}
        <motion.div
          className="glass-card p-6 border-l-2 border-l-rose-500"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
            <AlertTriangle size={16} className="text-rose-400" /> Risk Factors
          </h3>
          <div className="space-y-2.5">
            {hasFlags ? (
              candidate.anti_pattern_flags.map((flag, i) => (
                <div key={i} className="text-xs text-rose-400 flex items-start gap-2 px-3 py-2 rounded-lg bg-rose-500/10 border border-rose-500/20">
                  <AlertTriangle size={12} className="mt-0.5 shrink-0" />
                  {flag}
                </div>
              ))
            ) : candidate.experience_match < 60 ? (
              <div className="text-xs text-amber-400 px-3 py-2 rounded-lg bg-amber-500/10 border border-amber-500/20">
                Lower experience level compared to JD requirements
              </div>
            ) : candidate.skill_match < 50 ? (
              <div className="text-xs text-rose-400 px-3 py-2 rounded-lg bg-rose-500/10 border border-rose-500/20">
                Missing primary technical requirements; relying on transferability
              </div>
            ) : (
              <div className="text-xs text-slate-500 italic">No major risk factors detected. Solid baseline match.</div>
            )}

            {candidate.anti_pattern_penalty < 1.0 && (
              <div className="mt-3 pt-3 border-t border-white/[0.06]">
                <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Anti-Pattern Penalty</div>
                <div className="text-sm font-bold text-rose-400">×{candidate.anti_pattern_penalty.toFixed(2)} multiplier applied</div>
              </div>
            )}
          </div>

          <div className="mt-4 pt-4 border-t border-white/[0.06]">
            <h4 className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-2">Recruiter Recommendation</h4>
            <div className={`text-sm font-medium ${
              candidate.score > 80 ? 'text-emerald-400' : candidate.potential_score > 70 ? 'text-amber-400' : 'text-slate-400'
            }`}>
              {candidate.score > 80 ? '🟢 Strong Buy. Interview immediately.' :
               candidate.potential_score > 70 ? '🟡 High Potential. Evaluate for growth.' :
               '⚪ Standard Fit. Proceed with screen.'}
            </div>
          </div>
        </motion.div>
      </div>

      {/* ─── Behavioral Intelligence Panel ─── */}
      {candidate.behavioral_insights && candidate.behavioral_insights.length > 0 && (
        <motion.div
          className="glass-card p-6"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
            <Shield size={16} className="text-amber-400" /> Behavioral Intelligence (Redrob Signals)
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {candidate.behavioral_insights.map((insight, i) => {
              const isWarning = insight.startsWith('⚠');
              return (
                <div
                  key={i}
                  className={`px-3 py-2 rounded-lg text-xs font-medium ${
                    isWarning
                      ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  }`}
                >
                  {insight}
                </div>
              );
            })}
          </div>

          {/* Signal Meters */}
          {redrob && (
            <div className="grid grid-cols-4 gap-4 mt-4 pt-4 border-t border-white/[0.06]">
              <SignalMeter label="Response Rate" value={redrob.recruiter_response_rate * 100} />
              <SignalMeter label="Completeness" value={redrob.profile_completeness_score * 100} />
              <SignalMeter label="Interview Rate" value={redrob.interview_completion_rate * 100} />
              <SignalMeter label="GitHub" value={Math.max(0, redrob.github_activity_score)} max={100} />
            </div>
          )}
        </motion.div>
      )}

      {/* ─── Expandable Sections (INDEPENDENT — both can be open) ─── */}
      <div className="space-y-3 pt-2">
        {/* Career Timeline */}
        <div className="glass-card overflow-hidden">
          <button
            onClick={() => setCareerOpen(prev => !prev)}
            className="w-full p-4 flex items-center justify-between bg-white/[0.02] hover:bg-white/[0.04] transition-colors"
          >
            <span className="font-semibold text-white flex items-center gap-2 text-sm">
              <Briefcase size={16} className="text-slate-400" /> Career Timeline ({history.length} roles)
            </span>
            <motion.div
              animate={{ rotate: careerOpen ? 180 : 0 }}
              transition={{ duration: 0.3 }}
            >
              <ChevronDown size={16} className="text-slate-400" />
            </motion.div>
          </button>
          <AnimatePresence>
            {careerOpen && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="overflow-hidden"
              >
                <div className="p-6 border-t border-white/[0.06]">
                  <div className="relative pl-6 space-y-6 before:absolute before:inset-y-0 before:left-[11px] before:w-px before:bg-white/10">
                    {history.map((job: any, i: number) => (
                      <div key={i} className="relative">
                        <div className={`absolute -left-[30px] top-1.5 w-3 h-3 rounded-full border-2 ${
                          job.is_current ? 'bg-blue-500 border-blue-400' : 'bg-white/10 border-white/20'
                        }`} />
                        <div className="font-semibold text-white text-sm">{job.title}</div>
                        <div className="text-xs text-blue-400 font-medium mb-1">
                          {job.company} {job.is_current ? '(Current)' : ''} • {job.duration_months || 0} months
                        </div>
                        <div className="text-xs text-slate-500 mb-2">
                          {job.start_date} – {job.end_date || 'Present'}
                        </div>
                        {job.description && (
                          <p className="text-xs text-slate-400 leading-relaxed line-clamp-3">{job.description}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Skills Detail */}
        <div className="glass-card overflow-hidden">
          <button
            onClick={() => setSkillsOpen(prev => !prev)}
            className="w-full p-4 flex items-center justify-between bg-white/[0.02] hover:bg-white/[0.04] transition-colors"
          >
            <span className="font-semibold text-white flex items-center gap-2 text-sm">
              <Network size={16} className="text-slate-400" /> All Skills ({skills.length})
            </span>
            <motion.div
              animate={{ rotate: skillsOpen ? 180 : 0 }}
              transition={{ duration: 0.3 }}
            >
              <ChevronDown size={16} className="text-slate-400" />
            </motion.div>
          </button>
          <AnimatePresence>
            {skillsOpen && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="overflow-hidden"
              >
                <div className="p-6 border-t border-white/[0.06]">
                  <div className="flex flex-wrap gap-2">
                    {skills.map((s: any, i: number) => {
                      const prof = (s.proficiency || 'intermediate').toLowerCase();
                      const color = prof === 'expert' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                                   prof === 'advanced' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                                   prof === 'intermediate' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                                   'bg-white/5 text-slate-500 border-white/10';
                      return (
                        <span key={i} className={`px-2.5 py-1 text-xs font-medium rounded-lg border ${color} flex items-center gap-1.5`}>
                          {s.name || s}
                          {s.proficiency && <span className="text-[9px] opacity-60 capitalize">{s.proficiency}</span>}
                        </span>
                      );
                    })}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

function SignalMeter({ label, value, max = 100 }: { label: string; value: number; max?: number }) {
  const pct = Math.min((value / max) * 100, 100);
  const color = pct >= 70 ? 'bg-emerald-500' : pct >= 40 ? 'bg-amber-500' : 'bg-rose-500';
  return (
    <div>
      <div className="text-[10px] text-slate-500 mb-1 font-medium">{label}</div>
      <div className="flex items-center gap-2">
        <div className="flex-1 progress-bar">
          <div className={`progress-bar-fill ${color}`} style={{ width: `${pct}%` }} />
        </div>
        <span className="text-xs font-bold text-slate-300">{value.toFixed(0)}</span>
      </div>
    </div>
  );
}
