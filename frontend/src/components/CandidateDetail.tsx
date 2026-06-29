import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronDown, Network, Briefcase, CheckCircle, AlertTriangle,
  Target, Shield, Activity, MapPin, Award, Circle, BadgeCheck, TriangleAlert, ExternalLink
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
  const scoreBreakdown = candidate.score_breakdown && Object.keys(candidate.score_breakdown).length > 0
    ? [
        { name: 'Production ML', value: candidate.score_breakdown.production_ml_experience || 0, color: '#0f766e' },
        { name: 'Retrieval/Ranking', value: candidate.score_breakdown.retrieval_ranking_experience || 0, color: '#b15c3e' },
        { name: 'Vector DBs', value: candidate.score_breakdown.vector_databases || 0, color: '#7257a3' },
        { name: 'Python', value: candidate.score_breakdown.python_engineering || 0, color: '#c48733' },
        { name: 'Evaluation', value: candidate.score_breakdown.evaluation_frameworks || 0, color: '#b44f5d' },
      ]
    : [
        { name: 'Technical', value: candidate.skill_match, color: '#0f766e' },
        { name: 'Career', value: candidate.experience_match, color: '#b15c3e' },
        { name: 'Behavioral', value: candidate.behavioral_score || 50, color: '#7257a3' },
        { name: 'Potential', value: candidate.potential_score, color: '#c48733' },
        { name: 'Semantic', value: candidate.semantic_similarity, color: '#b44f5d' },
      ];

  const hasFlags = candidate.anti_pattern_flags && candidate.anti_pattern_flags.length > 0;
  const topEvidence = candidate.top_matching_evidence || [];
  const missingRequirements = candidate.missing_requirements || [];

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
        <div className="absolute -top-24 -right-24 w-48 h-48 bg-[var(--color-accent-blue-light)] rounded-full mix-blend-multiply filter blur-[80px] opacity-100 pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-48 h-48 bg-[var(--color-accent-emerald-light)] rounded-full mix-blend-multiply filter blur-[80px] opacity-100 pointer-events-none" />

        <div className="flex flex-col gap-4 mb-6 relative z-10 lg:flex-row lg:justify-between lg:items-start">
          <div className="flex gap-5 items-center">
            <div className="w-16 h-16 rounded-2xl bg-[var(--color-avatar-bg)] shadow-lg shadow-black/12 flex items-center justify-center text-2xl font-black text-[var(--color-avatar-text)]">
              {profile.anonymized_name?.charAt(0) || 'C'}
            </div>
            <div>
              <button
                type="button"
                onClick={() =>
                  navigate(`/candidate/${candidate.candidate_id}`, {
                    state: { candidate, returnTo: '/analyze' },
                  })
                }
                className="text-left text-2xl font-bold text-[var(--color-text-primary)] tracking-tight hover:text-[var(--color-text-secondary)] transition-colors"
              >
                {profile.anonymized_name || candidate.candidate_id}
              </button>
              <p className="text-[var(--color-text-secondary)] font-medium mt-0.5 text-sm">
                {profile.current_title || 'Engineer'}
              </p>
              <div className="flex items-center gap-4 mt-2 text-xs text-[var(--color-text-tertiary)]">
                <span className="flex items-center gap-1"><Briefcase size={12} /> {profile.years_of_experience || 0}y exp</span>
                <span className="flex items-center gap-1"><MapPin size={12} /> {profile.location || 'N/A'}</span>
                {profile.current_company && (
                  <span className="flex items-center gap-1"><Award size={12} /> {profile.current_company}</span>
                )}
              </div>
            </div>
          </div>

          <div className="flex flex-col items-start gap-3 lg:items-end">
            {/* Score Display */}
            <div className="flex gap-4 glass p-4 rounded-2xl">
              <div className="text-center px-3 border-r border-[var(--color-border-subtle)]">
                <div className="text-3xl font-black gradient-text-emerald">{candidate.score.toFixed(1)}</div>
                <div className="text-[9px] font-bold text-[var(--color-text-tertiary)] uppercase tracking-widest mt-1">Score</div>
              </div>
              <div className="text-center px-3 border-r border-[var(--color-border-subtle)]">
                <div className="text-3xl font-black gradient-text-amber">{candidate.potential_score.toFixed(0)}</div>
                <div className="text-[9px] font-bold text-[var(--color-text-tertiary)] uppercase tracking-widest mt-1">Potential</div>
              </div>
              <div className="text-center pl-3">
                <div className="text-3xl font-black gradient-text-blue">{(candidate.behavioral_score || 50).toFixed(0)}</div>
                <div className="text-[9px] font-bold text-[var(--color-text-tertiary)] uppercase tracking-widest mt-1">Behavioral</div>
              </div>
            </div>

            <button
              type="button"
              onClick={() =>
                navigate(`/candidate/${candidate.candidate_id}`, {
                  state: { candidate, returnTo: '/analyze' },
                })
              }
              className="inline-flex items-center gap-2 rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-button-solid)] px-3 py-2 text-sm font-medium text-[var(--color-button-solid-text)] transition-colors hover:bg-[var(--color-button-solid-hover)]"
            >
              <ExternalLink size={14} />
              View Candidate Info
            </button>
          </div>
        </div>

        {/* Top Skills */}
        <div className="relative z-10">
          <div className="text-[10px] font-bold text-[var(--color-text-tertiary)] uppercase tracking-widest mb-3">Core Competencies</div>
          <div className="flex flex-wrap gap-1.5">
            {skills.slice(0, 8).map((s: any, idx: number) => (
              <span key={idx} className="px-2.5 py-1 bg-[var(--color-pill-bg)] border border-[var(--color-pill-border)] rounded-lg text-xs font-medium text-[var(--color-pill-text)] hover:border-[var(--color-border-focus)] transition-colors">
                {s.name || s}
              </span>
            ))}
            {candidate.transferable_matches > 0 && (
              <span className="px-2.5 py-1 bg-[var(--color-button-solid)] text-[var(--color-button-solid-text)] rounded-lg text-xs font-bold">
                +{candidate.transferable_matches} Transferable
              </span>
            )}
          </div>
        </div>
      </motion.div>

      <motion.div
        className="glass-card p-6 border-l-2 border-l-[var(--color-accent-blue)]"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
      >
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div>
            <h3 className="text-sm font-bold text-[var(--color-text-primary)] mb-3 flex items-center gap-2">
              <Target size={16} className="text-[var(--color-accent-blue)]" />
              Role Fit Reasoning
            </h3>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
              {candidate.reasoning}
            </p>
          </div>
          <div className="flex shrink-0 flex-wrap gap-2 md:justify-end">
            {candidate.rank && (
              <span className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-[var(--color-pill-bg)] text-[var(--color-pill-text)] border border-[var(--color-pill-border)]">
                Rank #{candidate.rank}
              </span>
            )}
            {candidate.hiring_recommendation && (
              <span className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                {candidate.hiring_recommendation}
              </span>
            )}
          </div>
        </div>
      </motion.div>

      {/* ─── Strengths + Risks First ─── */}
      <div className="grid grid-cols-2 gap-6">
        {/* Strengths */}
        <motion.div
          className="glass-card p-6 border-l-2 border-l-emerald-500"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h3 className="text-sm font-bold text-[var(--color-text-primary)] mb-4 flex items-center gap-2">
            <CheckCircle size={16} className="text-[var(--color-accent-emerald)]" /> Why Matched & Strengths
          </h3>
          <div className="space-y-2.5">
            {candidate.reasoning.split(';').filter(r => !r.trim().startsWith('⚠')).map((r, i) => (
              <div key={i} className="text-xs text-[var(--color-text-secondary)] flex items-start gap-2 leading-relaxed">
                <BadgeCheck size={12} className="text-[var(--color-accent-emerald)] mt-0.5 shrink-0" />
                {r.replace(/^⚠\s*/, '').trim()}
              </div>
            ))}
            {topEvidence.map((evidence, i) => (
              <div key={`top-evidence-${i}`} className="text-xs text-[var(--color-text-secondary)] flex items-start gap-2 leading-relaxed">
                <BadgeCheck size={12} className="text-[var(--color-accent-emerald)] mt-0.5 shrink-0" />
                {evidence}
              </div>
            ))}
            {candidate.production_evidence?.slice(0, 2).map((evidence, i) => (
              <div key={`production-${i}`} className="text-xs text-[var(--color-text-secondary)] flex items-start gap-2 leading-relaxed">
                <BadgeCheck size={12} className="text-[var(--color-accent-emerald)] mt-0.5 shrink-0" />
                {evidence}
              </div>
            ))}
          </div>
        </motion.div>

        {/* Risks */}
        <motion.div
          className="glass-card p-6 border-l-2 border-l-rose-500"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h3 className="text-sm font-bold text-[var(--color-text-primary)] mb-4 flex items-center gap-2">
            <AlertTriangle size={16} className="text-rose-400" /> Gaps & Risks
          </h3>
          <div className="space-y-2.5">
            {hasFlags ? (
              candidate.anti_pattern_flags.map((flag, i) => (
                <div key={i} className="text-xs text-rose-400 flex items-start gap-2 px-3 py-2 rounded-lg bg-rose-500/10 border border-rose-500/20">
                  <AlertTriangle size={12} className="mt-0.5 shrink-0" />
                  {flag.replace(/^⚠\s*/, '')}
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
              <div className="text-xs text-[var(--color-text-tertiary)] italic">No major risk factors detected. Solid baseline match.</div>
            )}
            {missingRequirements.slice(0, 3).map((gap, i) => (
              <div key={`gap-${i}`} className="text-xs text-[var(--color-text-secondary)] flex items-start gap-2 px-3 py-2 rounded-lg bg-[var(--color-surface-pressed)] border border-[var(--color-border-subtle)]">
                <AlertTriangle size={12} className="mt-0.5 shrink-0 text-amber-400" />
                {gap}
              </div>
            ))}

            {candidate.anti_pattern_penalty < 1.0 && (
              <div className="mt-3 pt-3 border-t border-[var(--color-border-subtle)]">
                <div className="text-[10px] text-[var(--color-text-tertiary)] uppercase tracking-wider mb-1">Anti-Pattern Penalty</div>
                <div className="text-sm font-bold text-rose-400">×{candidate.anti_pattern_penalty.toFixed(2)} multiplier applied</div>
              </div>
            )}
          </div>

          <div className="mt-4 pt-4 border-t border-[var(--color-border-subtle)]">
            <h4 className="text-[10px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider mb-2">Recruiter Recommendation</h4>
            <div className={`text-sm font-medium flex items-center gap-2 ${
              candidate.score > 80 ? 'text-[var(--color-text-primary)]' : candidate.potential_score > 70 ? 'text-[var(--color-text-secondary)]' : 'text-[var(--color-text-tertiary)]'
            }`}>
              {candidate.score > 80 ? <BadgeCheck size={14} className="shrink-0" /> :
               candidate.potential_score > 70 ? <Target size={14} className="shrink-0" /> :
               <Circle size={14} className="shrink-0" />}
              {candidate.hiring_recommendation ? `${candidate.hiring_recommendation}. Proceed with recruiter screen.` :
               candidate.score > 80 ? 'Strong Hire. Interview immediately.' :
               candidate.potential_score > 70 ? 'High Potential. Evaluate for growth.' :
               'Standard Fit. Proceed with screen.'}
            </div>
          </div>
        </motion.div>
      </div>

      {/* ─── Radar Chart + Score Breakdown ─── */}
      <div className="grid grid-cols-2 gap-6">
        <motion.div
          className="glass-card p-6"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h3 className="text-sm font-bold text-[var(--color-text-primary)] mb-4 flex items-center gap-2">
            <Target size={16} className="text-[var(--color-accent-blue)]" /> Multi-Agent Score Radar
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="rgba(120,120,120,0.16)" />
              <PolarAngleAxis dataKey="dimension" tick={{ fill: 'var(--color-text-tertiary)', fontSize: 11 }} />
              <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
              <Radar
                name="Score"
                dataKey="value"
                stroke="var(--color-accent-blue)"
                fill="var(--color-accent-blue)"
                fillOpacity={0.1}
                strokeWidth={2}
              />
            </RadarChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div
          className="glass-card p-6"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
        >
          <h3 className="text-sm font-bold text-[var(--color-text-primary)] mb-4 flex items-center gap-2">
            <Activity size={16} className="text-[var(--color-accent-emerald)]" /> Dimension Breakdown
          </h3>
          <div className="space-y-3">
            {scoreBreakdown.map((item, i) => (
              <div key={i}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-[var(--color-text-secondary)] font-medium">{item.name}</span>
                  <span className="text-[var(--color-text-primary)] font-bold">{item.value.toFixed(1)}%</span>
                </div>
                <div className="progress-bar">
                  <motion.div
                    className="progress-bar-fill"
                    style={{ backgroundColor: item.color }}
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(item.value, 100)}%` }}
                    transition={{ delay: 0.6 + i * 0.1, duration: 0.8, ease: 'easeOut' }}
                  />
                </div>
              </div>
            ))}
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
          <h3 className="text-sm font-bold text-[var(--color-text-primary)] mb-4 flex items-center gap-2">
            <Shield size={16} className="text-[var(--color-accent-purple)]" /> Behavioral Intelligence (Redrob Signals)
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
                      : 'bg-[var(--color-surface-pressed)] text-[var(--color-text-primary)] border border-[var(--color-border-subtle)]'
                  } flex items-center gap-2`}
                >
                  {isWarning ? <TriangleAlert size={12} className="shrink-0" /> : <BadgeCheck size={12} className="shrink-0" />}
                  <span>{insight.replace(/^⚠\s*/, '')}</span>
                </div>
              );
            })}
          </div>

          {/* Signal Meters */}
          {redrob && (
            <div className="grid grid-cols-4 gap-4 mt-4 pt-4 border-t border-[var(--color-border-subtle)]">
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
            className="w-full p-4 flex items-center justify-between bg-[var(--color-surface-soft)] hover:bg-[var(--color-surface-pressed)] transition-colors"
          >
            <span className="font-semibold text-[var(--color-text-primary)] flex items-center gap-2 text-sm">
              <Briefcase size={16} className="text-[var(--color-text-tertiary)]" /> Career Timeline ({history.length} roles)
            </span>
            <motion.div
              animate={{ rotate: careerOpen ? 180 : 0 }}
              transition={{ duration: 0.3 }}
            >
              <ChevronDown size={16} className="text-[var(--color-text-tertiary)]" />
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
                <div className="p-6 border-t border-[var(--color-border-subtle)]">
                  <div className="relative pl-6 space-y-6 before:absolute before:inset-y-0 before:left-[11px] before:w-px before:bg-[var(--color-border-subtle)]">
                    {history.map((job: any, i: number) => (
                      <div key={i} className="relative">
                        <div className={`absolute -left-[30px] top-1.5 w-3 h-3 rounded-full border-2 ${
                          job.is_current ? 'bg-[var(--color-accent-blue)] border-[var(--color-accent-blue)]' : 'bg-[var(--color-bg-elevated)] border-[var(--color-border-subtle)]'
                        }`} />
                        <div className="font-semibold text-[var(--color-text-primary)] text-sm">{job.title}</div>
                        <div className="text-xs text-[var(--color-accent-blue)] font-medium mb-1">
                          {job.company} {job.is_current ? '(Current)' : ''} • {job.duration_months || 0} months
                        </div>
                        <div className="text-xs text-[var(--color-text-tertiary)] mb-2">
                          {job.start_date} – {job.end_date || 'Present'}
                        </div>
                        {job.description && (
                          <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed line-clamp-3">{job.description}</p>
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
            className="w-full p-4 flex items-center justify-between bg-[var(--color-surface-soft)] hover:bg-[var(--color-surface-pressed)] transition-colors"
          >
            <span className="font-semibold text-[var(--color-text-primary)] flex items-center gap-2 text-sm">
              <Network size={16} className="text-[var(--color-text-tertiary)]" /> All Skills ({skills.length})
            </span>
            <motion.div
              animate={{ rotate: skillsOpen ? 180 : 0 }}
              transition={{ duration: 0.3 }}
            >
              <ChevronDown size={16} className="text-[var(--color-text-tertiary)]" />
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
                <div className="p-6 border-t border-[var(--color-border-subtle)]">
                  <div className="flex flex-wrap gap-2">
                    {skills.map((s: any, i: number) => {
                      const prof = (s.proficiency || 'intermediate').toLowerCase();
                      const color = prof === 'expert' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                                   prof === 'advanced' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                                   prof === 'intermediate' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                                   'bg-[var(--color-pill-bg)] text-[var(--color-text-tertiary)] border-[var(--color-pill-border)]';
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
      <div className="text-[10px] text-[var(--color-text-tertiary)] mb-1 font-medium">{label}</div>
      <div className="flex items-center gap-2">
        <div className="flex-1 progress-bar">
          <div className={`progress-bar-fill ${color}`} style={{ width: `${pct}%` }} />
        </div>
        <span className="text-xs font-bold text-[var(--color-text-secondary)]">{value.toFixed(0)}</span>
      </div>
    </div>
  );
}
