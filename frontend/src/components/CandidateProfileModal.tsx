import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { X, Briefcase, MapPin, Activity, Target, Star } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

interface Props {
  candidateId: string;
  onClose: () => void;
}

const API = 'http://127.0.0.1:8000';

const fetchCandidate = async (id: string) => {
  const res = await axios.get(`${API}/api/candidates/${id}`);
  return res.data;
};

export default function CandidateProfileModal({ candidateId, onClose }: Props) {
  const [view, setView] = useState<'summary' | 'full'>('summary');

  const { data, isLoading } = useQuery({
    queryKey: ['candidate', candidateId],
    queryFn: () => fetchCandidate(candidateId),
  });

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
        <div className="glass-card p-8 flex flex-col items-center">
          <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4" />
          <p className="text-slate-400 font-medium text-sm">Loading candidate profile...</p>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex justify-end z-50" onClick={onClose}>
      <motion.div
        className="w-[800px] max-w-[90vw] h-full bg-[#0A0E1A] border-l border-white/[0.06] shadow-2xl flex flex-col"
        onClick={(e) => e.stopPropagation()}
        initial={{ x: 100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: 100, opacity: 0 }}
        transition={{ type: 'spring', damping: 30, stiffness: 300 }}
      >
        {/* Header */}
        <div className="p-6 border-b border-white/[0.06] glass-strong flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 text-white flex items-center justify-center font-bold text-xl shadow-lg shadow-blue-500/20">
              {data.profile?.anonymized_name?.charAt(0) || "U"}
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">{data.profile?.anonymized_name || "Unknown"}</h2>
              <div className="text-xs text-slate-500">{data.profile?.headline}</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex bg-white/[0.04] p-1 rounded-lg">
              <button
                onClick={() => setView('summary')}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${view === 'summary' ? 'bg-white/10 text-white' : 'text-slate-500 hover:text-slate-300'}`}
              >
                Summary
              </button>
              <button
                onClick={() => setView('full')}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${view === 'full' ? 'bg-white/10 text-white' : 'text-slate-500 hover:text-slate-300'}`}
              >
                Full Data
              </button>
            </div>
            <button onClick={onClose} className="p-2 text-slate-500 hover:bg-white/[0.06] rounded-lg transition-colors">
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-8">
          {view === 'summary' ? (
            <div className="space-y-6 animate-fade-in">
              {/* Quick Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <MetricCard icon={<Target size={18} />} title="Experience" value={`${data.profile?.years_of_experience || 0}y`} color="text-blue-400" bg="bg-blue-500/10" />
                <MetricCard icon={<MapPin size={18} />} title="Location" value={data.profile?.location || 'N/A'} color="text-emerald-400" bg="bg-emerald-500/10" />
                <MetricCard icon={<Briefcase size={18} />} title="Company" value={data.profile?.current_company || 'N/A'} color="text-purple-400" bg="bg-purple-500/10" />
                <MetricCard icon={<Activity size={18} />} title="Industry" value={data.profile?.current_industry || 'N/A'} color="text-amber-400" bg="bg-amber-500/10" />
              </div>

              {/* Summary */}
              <div>
                <h3 className="text-sm font-bold text-white mb-3">Profile Summary</h3>
                <p className="text-sm text-slate-400 leading-relaxed glass-card p-4">
                  {data.profile?.summary || "No summary provided. This candidate's profile is based on parsed career data and skills."}
                </p>
              </div>

              {/* Top Skills */}
              <div>
                <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
                  <Star size={14} className="text-amber-400" /> Skills
                </h3>
                <div className="flex flex-wrap gap-2">
                  {data.skills?.slice(0, 12).map((skill: any, i: number) => {
                    const prof = (skill.proficiency || '').toLowerCase();
                    const color = prof === 'expert' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                                 prof === 'advanced' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                                 'bg-white/5 text-slate-400 border-white/10';
                    return (
                      <span key={i} className={`px-2.5 py-1 rounded-lg text-xs font-medium border ${color}`}>
                        {skill.name || skill}
                      </span>
                    );
                  })}
                  {(data.skills?.length || 0) > 12 && (
                    <span className="px-2.5 py-1 bg-white/5 text-slate-600 rounded-lg text-xs font-medium border border-white/10">
                      +{(data.skills?.length || 0) - 12} more
                    </span>
                  )}
                </div>
              </div>

              <div className="flex justify-center mt-6">
                <button onClick={() => setView('full')} className="px-6 py-2 bg-gradient-to-r from-slate-700 to-slate-800 text-white rounded-xl hover:from-slate-600 hover:to-slate-700 transition-all text-sm font-medium border border-white/10">
                  View Full Dataset Profile
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-8 pb-8 animate-fade-in">
              {/* Professional Profile */}
              <section>
                <h3 className="text-sm font-bold text-white mb-4 pb-2 border-b border-white/[0.06]">Professional Profile</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-y-4 gap-x-6 text-sm">
                  <DetailItem label="Headline" value={data.profile?.headline} />
                  <DetailItem label="Summary" value={data.profile?.summary} colSpan={2} />
                  <DetailItem label="Location" value={`${data.profile?.location}, ${data.profile?.country}`} />
                  <DetailItem label="Current Title" value={data.profile?.current_title} />
                  <DetailItem label="Current Company" value={data.profile?.current_company} />
                  <DetailItem label="Industry" value={data.profile?.current_industry} />
                  <DetailItem label="Company Size" value={data.profile?.current_company_size} />
                  <DetailItem label="Years Experience" value={`${data.profile?.years_of_experience || 0} years`} />
                </div>
              </section>

              {/* Career History */}
              {data.career_history?.length > 0 && (
                <section>
                  <h3 className="text-sm font-bold text-white mb-4 pb-2 border-b border-white/[0.06]">Career History</h3>
                  <div className="space-y-4">
                    {data.career_history.map((job: any, i: number) => (
                      <div key={i} className="glass-card p-4">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h4 className="font-semibold text-white text-sm">{job.title}</h4>
                            <div className="text-blue-400 font-medium text-xs">{job.company} {job.is_current ? '(Current)' : ''}</div>
                          </div>
                          <div className="text-xs text-slate-500 font-mono">
                            {job.start_date} - {job.end_date || 'Present'} ({job.duration_months} mos)
                          </div>
                        </div>
                        {job.description && (
                          <p className="text-xs text-slate-400 leading-relaxed">{job.description}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* Education */}
              {data.education?.length > 0 && (
                <section>
                  <h3 className="text-sm font-bold text-white mb-4 pb-2 border-b border-white/[0.06]">Education</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {data.education.map((edu: any, i: number) => (
                      <div key={i} className="glass-card p-4 flex flex-col gap-1">
                        <h4 className="font-semibold text-white text-sm">
                          {edu.institution}{' '}
                          <span className="text-[10px] px-2 py-0.5 bg-blue-500/10 text-blue-400 rounded-full font-medium">{edu.tier}</span>
                        </h4>
                        <div className="text-xs text-slate-400">{edu.degree} in {edu.field_of_study}</div>
                        <div className="text-[10px] text-slate-600">{edu.start_year} - {edu.end_year} • Grade: {edu.grade || 'N/A'}</div>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* Platform Signals */}
              {data.redrob_signals && (
                <section>
                  <h3 className="text-sm font-bold text-white mb-4 pb-2 border-b border-white/[0.06]">Platform & Activity Signals</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-y-4 gap-x-6 text-sm glass-card p-6">
                    <DetailItem label="Completeness" value={`${(data.redrob_signals.profile_completeness_score * 100).toFixed(0)}%`} />
                    <DetailItem label="Open to Work" value={data.redrob_signals.open_to_work_flag ? 'Available' : 'No'} />
                    <DetailItem label="Preferred Mode" value={data.redrob_signals.preferred_work_mode} />
                    <DetailItem label="Relocate" value={data.redrob_signals.willing_to_relocate ? 'Open' : 'No'} />
                    <DetailItem label="Notice Period" value={`${data.redrob_signals.notice_period_days} days`} />
                    <DetailItem label="Response Rate" value={`${(data.redrob_signals.recruiter_response_rate * 100).toFixed(0)}%`} />
                    <DetailItem label="GitHub" value={data.redrob_signals.github_activity_score > 0 ? `${data.redrob_signals.github_activity_score}` : 'N/A'} />
                    <DetailItem label="Connections" value={data.redrob_signals.connection_count} />
                    <DetailItem label="Endorsements" value={data.redrob_signals.endorsements_received} />
                  </div>
                </section>
              )}
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
}

function DetailItem({ label, value, colSpan = 1 }: { label: string; value: any; colSpan?: number }) {
  if (!value) return null;
  return (
    <div className={`col-span-${colSpan} flex flex-col gap-1`}>
      <span className="text-[10px] text-slate-600 font-medium uppercase tracking-wider">{label}</span>
      <span className="text-slate-300 text-sm">{value}</span>
    </div>
  );
}

function MetricCard({ icon, title, value, color, bg }: { icon: React.ReactNode; title: string; value: string; color: string; bg: string }) {
  return (
    <div className="glass-card p-4 flex flex-col items-center justify-center text-center">
      <div className={`${bg} ${color} p-2 rounded-lg mb-2`}>
        {icon}
      </div>
      <div className="text-[10px] text-slate-500 mb-1">{title}</div>
      <div className="text-sm font-bold text-white truncate max-w-full">{value}</div>
    </div>
  );
}
