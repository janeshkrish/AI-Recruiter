import { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import {
  ArrowLeft, ChevronDown, ChevronRight,
  Briefcase, MapPin, Award, GraduationCap, Shield,
  Target, Activity, Network, CheckCircle, AlertTriangle,
  Star, TrendingUp, Zap
} from 'lucide-react';
import type { Candidate } from '../App';

const API = 'http://127.0.0.1:8000';

const fetchCandidate = async (id: string) => {
  const res = await axios.get(`${API}/api/candidates/${id}`);
  return res.data;
};

// Group skills by category
function groupSkills(skills: any[]): Record<string, any[]> {
  const groups: Record<string, any[]> = {};
  for (const skill of skills) {
    const category = skill.category || 'Other';
    if (!groups[category]) groups[category] = [];
    groups[category].push(skill);
  }
  return groups;
}

// Section reveal animation
const sectionVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0 },
};

export default function CandidateProfilePage() {
  const { candidateId } = useParams<{ candidateId: string }>();
  const navigate = useNavigate();
  const location = useLocation();

  // Candidate data might be passed from ranking results via location state
  const rankedCandidate: Candidate | undefined = location.state?.candidate;

  const [careerOpen, setCareerOpen] = useState(true);
  const [skillsOpen, setSkillsOpen] = useState(true);
  const [educationOpen, setEducationOpen] = useState(false);

  // Scroll to top on mount
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [candidateId]);

  const { data, isLoading } = useQuery({
    queryKey: ['candidate-profile', candidateId],
    queryFn: () => fetchCandidate(candidateId!),
    enabled: !!candidateId,
  });

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center relative z-10 min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-4 border-violet-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-slate-500 text-sm font-medium">Loading candidate profile...</span>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex-1 flex items-center justify-center relative z-10 min-h-[60vh]">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white mb-2">Candidate Not Found</h2>
          <p className="text-slate-500 mb-6">This candidate profile could not be loaded.</p>
          <button onClick={() => navigate(-1)} className="px-6 py-2.5 glass hover:bg-white/[0.06] text-white rounded-xl font-medium text-sm transition-all">
            Go Back
          </button>
        </div>
      </div>
    );
  }

  const profile = data.profile || {};
  const history = data.career_history || [];
  const skills = data.skills || [];
  const education = data.education || [];
  const redrob = data.redrob_signals || {};
  const groupedSkills = groupSkills(skills);

  return (
    <div className="flex-1 overflow-y-auto relative z-10">
      {/* ─── Hero Section ─── */}
      <div className="relative overflow-hidden">
        {/* Hero gradient background */}
        <div className="absolute inset-0 bg-gradient-to-b from-violet-600/10 via-fuchsia-500/5 to-transparent pointer-events-none" />
        <div className="absolute top-0 left-1/4 w-[500px] h-[300px] bg-violet-500/15 rounded-full blur-[100px] pointer-events-none" />
        <div className="absolute top-0 right-1/4 w-[400px] h-[300px] bg-cyan-500/10 rounded-full blur-[100px] pointer-events-none" />

        <div className="max-w-6xl mx-auto px-6 pt-6 pb-10 relative z-10">
          {/* Breadcrumb */}
          <motion.nav
            className="flex items-center gap-2 text-xs text-slate-500 mb-6"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Link to="/" className="hover:text-white transition-colors">Dashboard</Link>
            <ChevronRight size={12} />
            <Link to="/candidates" className="hover:text-white transition-colors">Candidates</Link>
            <ChevronRight size={12} />
            <span className="text-violet-400 font-medium">{profile.anonymized_name || candidateId}</span>
          </motion.nav>

          {/* Back button */}
          <motion.button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-6 group transition-colors"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            whileHover={{ x: -4 }}
          >
            <ArrowLeft size={16} className="group-hover:text-violet-400 transition-colors" />
            Back to Results
          </motion.button>

          {/* Hero content */}
          <motion.div
            className="flex flex-col lg:flex-row gap-8 items-start"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* Left: Avatar + Info */}
            <div className="flex gap-5 items-start flex-1">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-violet-500 via-fuchsia-500 to-cyan-500 shadow-lg shadow-violet-500/20 flex items-center justify-center text-3xl font-black text-white shrink-0">
                {profile.anonymized_name?.charAt(0) || 'C'}
              </div>
              <div>
                <h1 className="text-3xl font-black text-white tracking-tight mb-1">
                  {profile.anonymized_name || candidateId}
                </h1>
                <p className="text-lg text-violet-400 font-medium mb-3">
                  {profile.current_title || 'Professional'}
                </p>
                <div className="flex flex-wrap items-center gap-4 text-sm text-slate-400">
                  {profile.location && (
                    <span className="flex items-center gap-1.5">
                      <MapPin size={14} className="text-slate-600" />
                      {profile.location}{profile.country ? `, ${profile.country}` : ''}
                    </span>
                  )}
                  <span className="flex items-center gap-1.5">
                    <Briefcase size={14} className="text-slate-600" />
                    {profile.years_of_experience || 0} years experience
                  </span>
                  {profile.current_company && (
                    <span className="flex items-center gap-1.5">
                      <Award size={14} className="text-slate-600" />
                      {profile.current_company}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Right: Score panel (if ranked data available) */}
            {rankedCandidate && (
              <motion.div
                className="glass-card p-5 flex gap-5 shrink-0"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                <ScoreBadge
                  label="Match Score"
                  value={rankedCandidate.score.toFixed(1)}
                  gradient="gradient-text-emerald"
                />
                <div className="w-px bg-white/10" />
                <ScoreBadge
                  label="Behavioral"
                  value={(rankedCandidate.behavioral_score || 50).toFixed(0)}
                  gradient="gradient-text-amber"
                />
                <div className="w-px bg-white/10" />
                <ScoreBadge
                  label="Potential"
                  value={rankedCandidate.potential_score.toFixed(0)}
                  gradient="gradient-text-blue"
                />
                <div className="w-px bg-white/10" />
                <ScoreBadge
                  label="Transferable"
                  value={String(rankedCandidate.transferable_matches)}
                  gradient="gradient-text-purple"
                />
              </motion.div>
            )}
          </motion.div>
        </div>
      </div>

      {/* ─── Main Content ─── */}
      <div className="max-w-6xl mx-auto px-6 pb-16">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Main content */}
          <div className="lg:col-span-2 space-y-6">

            {/* Profile Summary */}
            <motion.div
              className="glass-card p-6"
              variants={sectionVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-50px' }}
              transition={{ duration: 0.5 }}
            >
              <h2 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                <Star size={16} className="text-amber-400" />
                Profile Summary
              </h2>
              <p className="text-sm text-slate-400 leading-relaxed">
                {profile.summary || profile.headline || 'No summary available for this candidate. Profile data is based on parsed career history and skills assessment.'}
              </p>
            </motion.div>

            {/* Career Timeline */}
            <motion.div
              className="glass-card overflow-hidden"
              variants={sectionVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-50px' }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              <button
                onClick={() => setCareerOpen((prev) => !prev)}
                className="w-full p-5 flex items-center justify-between bg-white/[0.02] hover:bg-white/[0.04] transition-colors"
              >
                <span className="font-semibold text-white flex items-center gap-2 text-sm">
                  <Briefcase size={16} className="text-slate-400" />
                  Career Timeline ({history.length} roles)
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
                      {history.length > 0 ? (
                        <div className="relative pl-6 space-y-6 before:absolute before:inset-y-0 before:left-[11px] before:w-px before:bg-white/10">
                          {history.map((job: any, i: number) => (
                            <motion.div
                              key={i}
                              className="relative"
                              initial={{ opacity: 0, x: -10 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: i * 0.05 }}
                            >
                              <div
                                className={`absolute -left-[30px] top-1.5 w-3 h-3 rounded-full border-2 ${
                                  job.is_current
                                    ? 'bg-violet-500 border-violet-400'
                                    : 'bg-white/10 border-white/20'
                                }`}
                              />
                              <div className="font-semibold text-white text-sm">{job.title}</div>
                              <div className="text-xs text-violet-400 font-medium mb-1">
                                {job.company} {job.is_current ? '(Current)' : ''} • {job.duration_months || 0} months
                              </div>
                              <div className="text-xs text-slate-600 mb-2">
                                {job.start_date} – {job.end_date || 'Present'}
                              </div>
                              {job.description && (
                                <p className="text-xs text-slate-400 leading-relaxed">{job.description}</p>
                              )}
                            </motion.div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-slate-500 italic">No career history available.</p>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Skills */}
            <motion.div
              className="glass-card overflow-hidden"
              variants={sectionVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-50px' }}
              transition={{ duration: 0.5, delay: 0.15 }}
            >
              <button
                onClick={() => setSkillsOpen((prev) => !prev)}
                className="w-full p-5 flex items-center justify-between bg-white/[0.02] hover:bg-white/[0.04] transition-colors"
              >
                <span className="font-semibold text-white flex items-center gap-2 text-sm">
                  <Network size={16} className="text-slate-400" />
                  Skills ({skills.length})
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
                    <div className="p-6 border-t border-white/[0.06] space-y-5">
                      {Object.entries(groupedSkills).map(([category, categorySkills]) => (
                        <div key={category}>
                          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">{category}</h4>
                          <div className="flex flex-wrap gap-2">
                            {categorySkills.map((s: any, i: number) => {
                              const prof = (s.proficiency || 'intermediate').toLowerCase();
                              const color =
                                prof === 'expert'
                                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                                  : prof === 'advanced'
                                  ? 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                                  : prof === 'intermediate'
                                  ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                                  : 'bg-white/5 text-slate-500 border-white/10';
                              return (
                                <span
                                  key={i}
                                  className={`px-2.5 py-1 text-xs font-medium rounded-lg border ${color} flex items-center gap-1.5`}
                                >
                                  {s.name || s}
                                  {s.proficiency && (
                                    <span className="text-[9px] opacity-60 capitalize">{s.proficiency}</span>
                                  )}
                                </span>
                              );
                            })}
                          </div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Match Analysis (only if ranked data available) */}
            {rankedCandidate && (
              <motion.div
                className="grid grid-cols-1 md:grid-cols-2 gap-6"
                variants={sectionVariants}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: '-50px' }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                {/* Strengths */}
                <div className="glass-card p-6 border-l-2 border-l-emerald-500">
                  <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                    <CheckCircle size={16} className="text-emerald-400" />
                    Strengths & Match
                  </h3>
                  <div className="space-y-2.5">
                    {rankedCandidate.reasoning
                      .split(';')
                      .filter((r) => !r.trim().startsWith('⚠'))
                      .map((r, i) => (
                        <div key={i} className="text-xs text-slate-400 flex items-start gap-2 leading-relaxed">
                          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                          {r.trim()}
                        </div>
                      ))}
                  </div>
                </div>

                {/* Gaps / Risks */}
                <div className="glass-card p-6 border-l-2 border-l-rose-500">
                  <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                    <AlertTriangle size={16} className="text-rose-400" />
                    Gaps & Risk Factors
                  </h3>
                  <div className="space-y-2.5">
                    {rankedCandidate.anti_pattern_flags && rankedCandidate.anti_pattern_flags.length > 0 ? (
                      rankedCandidate.anti_pattern_flags.map((flag, i) => (
                        <div key={i} className="text-xs text-rose-400 flex items-start gap-2 px-3 py-2 rounded-lg bg-rose-500/10 border border-rose-500/20">
                          <AlertTriangle size={12} className="mt-0.5 shrink-0" />
                          {flag}
                        </div>
                      ))
                    ) : (
                      <div className="text-xs text-slate-500 italic">No major risk factors detected.</div>
                    )}
                    {rankedCandidate.transferable_matches > 0 && (
                      <div className="mt-3 pt-3 border-t border-white/[0.06]">
                        <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Transferable Skills</div>
                        <div className="text-sm font-bold text-purple-400">
                          {rankedCandidate.transferable_matches} adjacent skills detected
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            )}

            {/* Education */}
            <motion.div
              className="glass-card overflow-hidden"
              variants={sectionVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-50px' }}
              transition={{ duration: 0.5, delay: 0.25 }}
            >
              <button
                onClick={() => setEducationOpen((prev) => !prev)}
                className="w-full p-5 flex items-center justify-between bg-white/[0.02] hover:bg-white/[0.04] transition-colors"
              >
                <span className="font-semibold text-white flex items-center gap-2 text-sm">
                  <GraduationCap size={16} className="text-slate-400" />
                  Education ({education.length})
                </span>
                <motion.div
                  animate={{ rotate: educationOpen ? 180 : 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <ChevronDown size={16} className="text-slate-400" />
                </motion.div>
              </button>
              <AnimatePresence>
                {educationOpen && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden"
                  >
                    <div className="p-6 border-t border-white/[0.06]">
                      {education.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {education.map((edu: any, i: number) => (
                            <motion.div
                              key={i}
                              className="glass p-4 rounded-xl flex flex-col gap-1"
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ delay: i * 0.05 }}
                            >
                              <h4 className="font-semibold text-white text-sm">
                                {edu.institution}{' '}
                                {edu.tier && (
                                  <span className="text-[10px] px-2 py-0.5 bg-blue-500/10 text-blue-400 rounded-full font-medium">
                                    {edu.tier}
                                  </span>
                                )}
                              </h4>
                              <div className="text-xs text-slate-400">
                                {edu.degree} in {edu.field_of_study}
                              </div>
                              <div className="text-[10px] text-slate-600">
                                {edu.start_year} - {edu.end_year} • Grade: {edu.grade || 'N/A'}
                              </div>
                            </motion.div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-slate-500 italic">No education data available.</p>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          </div>

          {/* Right Column: Sticky sidebar */}
          <div className="lg:col-span-1 space-y-6">
            <div className="lg:sticky lg:top-28">
              {/* Quick Stats */}
              <motion.div
                className="glass-card p-5 space-y-4 mb-6"
                variants={sectionVariants}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Activity size={16} className="text-cyan-400" />
                  Quick Overview
                </h3>
                <div className="space-y-3">
                  <QuickStat label="Experience" value={`${profile.years_of_experience || 0} years`} icon={<Briefcase size={14} />} />
                  <QuickStat label="Location" value={profile.location || 'N/A'} icon={<MapPin size={14} />} />
                  <QuickStat label="Industry" value={profile.current_industry || 'N/A'} icon={<TrendingUp size={14} />} />
                  <QuickStat label="Company" value={profile.current_company || 'N/A'} icon={<Award size={14} />} />
                  <QuickStat label="Company Size" value={profile.current_company_size || 'N/A'} icon={<Network size={14} />} />
                </div>
              </motion.div>

              {/* Platform Signals */}
              {redrob && Object.keys(redrob).length > 0 && (
                <motion.div
                  className="glass-card p-5 space-y-4"
                  variants={sectionVariants}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                >
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Shield size={16} className="text-amber-400" />
                    Platform Signals
                  </h3>
                  <div className="space-y-3">
                    <SignalBar label="Profile Completeness" value={(redrob.profile_completeness_score || 0) * 100} />
                    <SignalBar label="Response Rate" value={(redrob.recruiter_response_rate || 0) * 100} />
                    <SignalBar label="Interview Rate" value={(redrob.interview_completion_rate || 0) * 100} />
                    <SignalBar label="GitHub Activity" value={Math.max(0, redrob.github_activity_score || 0)} />
                  </div>
                  <div className="pt-3 border-t border-white/[0.06] space-y-2 text-xs">
                    <div className="flex justify-between text-slate-500">
                      <span>Open to Work</span>
                      <span className={redrob.open_to_work_flag ? 'text-emerald-400' : 'text-slate-600'}>
                        {redrob.open_to_work_flag ? 'Yes ✓' : 'No'}
                      </span>
                    </div>
                    <div className="flex justify-between text-slate-500">
                      <span>Willing to Relocate</span>
                      <span className={redrob.willing_to_relocate ? 'text-emerald-400' : 'text-slate-600'}>
                        {redrob.willing_to_relocate ? 'Yes ✓' : 'No'}
                      </span>
                    </div>
                    <div className="flex justify-between text-slate-500">
                      <span>Notice Period</span>
                      <span className="text-slate-300">{redrob.notice_period_days || 'N/A'} days</span>
                    </div>
                    <div className="flex justify-between text-slate-500">
                      <span>Work Mode</span>
                      <span className="text-slate-300">{redrob.preferred_work_mode || 'N/A'}</span>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Recruiter Recommendation */}
              {rankedCandidate && (
                <motion.div
                  className="glass-card p-5 mt-6"
                  variants={sectionVariants}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: 0.3 }}
                >
                  <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
                    <Zap size={16} className="text-violet-400" />
                    AI Recommendation
                  </h3>
                  <div
                    className={`text-sm font-medium p-3 rounded-xl ${
                      rankedCandidate.score > 80
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : rankedCandidate.potential_score > 70
                        ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        : 'bg-white/5 text-slate-400 border border-white/10'
                    }`}
                  >
                    {rankedCandidate.score > 80
                      ? '🟢 Strong Buy. Interview immediately.'
                      : rankedCandidate.potential_score > 70
                      ? '🟡 High Potential. Evaluate for growth.'
                      : '⚪ Standard Fit. Proceed with screen.'}
                  </div>
                </motion.div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ─── Sub-components ─── */

function ScoreBadge({ label, value, gradient }: { label: string; value: string; gradient: string }) {
  return (
    <div className="text-center px-2">
      <motion.div
        className={`text-3xl font-black ${gradient}`}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', stiffness: 200, damping: 15, delay: 0.3 }}
      >
        {value}
      </motion.div>
      <div className="text-[9px] font-bold text-slate-500 uppercase tracking-widest mt-1">{label}</div>
    </div>
  );
}

function QuickStat({ label, value, icon }: { label: string; value: string; icon: React.ReactNode }) {
  return (
    <div className="flex items-center gap-3">
      <div className="text-slate-600">{icon}</div>
      <div className="flex-1 min-w-0">
        <div className="text-[10px] text-slate-600 font-medium uppercase tracking-wider">{label}</div>
        <div className="text-sm text-white font-medium truncate">{value}</div>
      </div>
    </div>
  );
}

function SignalBar({ label, value }: { label: string; value: number }) {
  const pct = Math.min(value, 100);
  const color = pct >= 70 ? 'bg-emerald-500' : pct >= 40 ? 'bg-amber-500' : 'bg-rose-500';
  return (
    <div>
      <div className="flex justify-between text-[10px] mb-1">
        <span className="text-slate-500 font-medium">{label}</span>
        <span className="text-slate-300 font-bold">{pct.toFixed(0)}%</span>
      </div>
      <div className="progress-bar">
        <motion.div
          className={`progress-bar-fill ${color}`}
          initial={{ width: 0 }}
          whileInView={{ width: `${pct}%` }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
    </div>
  );
}
