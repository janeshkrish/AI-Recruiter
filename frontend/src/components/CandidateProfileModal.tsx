import React, { useState } from 'react';
import { X, Briefcase, GraduationCap, MapPin, Award, CheckCircle, Brain, Target, Shield, Heart } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

interface Props {
  candidateId: string;
  onClose: () => void;
}

const fetchCandidate = async (id: string) => {
  const res = await axios.get(`http://127.0.0.1:8000/api/candidates/${id}`);
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
      <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-8 shadow-2xl flex flex-col items-center">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4"></div>
          <p className="text-slate-600 font-medium">Loading candidate profile...</p>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex justify-end z-50" onClick={onClose}>
      <div 
        className="w-[800px] max-w-[90vw] h-full bg-white shadow-2xl flex flex-col transform transition-transform animate-slide-in"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-6 border-b border-slate-200 bg-slate-50 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-xl">
              {data.profile?.anonymized_name?.charAt(0) || "U"}
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-800">{data.profile?.anonymized_name || "Unknown"}</h2>
              <div className="text-sm text-slate-500">{data.profile?.headline}</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex bg-slate-200 p-1 rounded-lg">
              <button 
                onClick={() => setView('summary')}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${view === 'summary' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}
              >
                Summary
              </button>
              <button 
                onClick={() => setView('full')}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${view === 'full' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}
              >
                Full Raw Dataset
              </button>
            </div>
            <button onClick={onClose} className="p-2 text-slate-400 hover:bg-slate-200 rounded-full transition-colors">
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-8">
          {view === 'summary' ? (
            <div className="space-y-8 animate-fade-in">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <MetricCard icon={<Target />} title="Match Score" value="88%" color="text-emerald-600" bg="bg-emerald-50" />
                <MetricCard icon={<Brain />} title="Potential" value="95%" color="text-purple-600" bg="bg-purple-50" />
                <MetricCard icon={<CheckCircle />} title="Hiring Prob" value="High" color="text-blue-600" bg="bg-blue-50" />
                <MetricCard icon={<Heart />} title="Behavioral" value="Top 10%" color="text-rose-600" bg="bg-rose-50" />
              </div>

              <div>
                <h3 className="text-lg font-bold text-slate-800 mb-3 border-b border-slate-100 pb-2">AI Recruiter Summary</h3>
                <p className="text-slate-600 leading-relaxed bg-blue-50/50 p-4 rounded-xl border border-blue-100">
                  {data.profile?.summary || "No summary provided in dataset. This candidate shows strong indicators in technical capabilities based on their parsed skills."}
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-lg font-bold text-slate-800 mb-3 border-b border-slate-100 pb-2 flex items-center gap-2">
                    <Briefcase size={18} className="text-slate-400" /> Current Status
                  </h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between"><span className="text-slate-500">Role:</span> <span className="font-medium text-slate-800">{data.profile?.current_title || "N/A"}</span></div>
                    <div className="flex justify-between"><span className="text-slate-500">Company:</span> <span className="font-medium text-slate-800">{data.profile?.current_company || "N/A"}</span></div>
                    <div className="flex justify-between"><span className="text-slate-500">Experience:</span> <span className="font-medium text-slate-800">{data.profile?.years_of_experience || 0} years</span></div>
                    <div className="flex justify-between"><span className="text-slate-500">Location:</span> <span className="font-medium text-slate-800">{data.profile?.location || "N/A"}</span></div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-bold text-slate-800 mb-3 border-b border-slate-100 pb-2 flex items-center gap-2">
                    <Award size={18} className="text-slate-400" /> Top Skills
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {data.skills?.slice(0, 8).map((skill: any, i: number) => (
                      <span key={i} className="px-3 py-1 bg-slate-100 text-slate-700 rounded-full text-xs font-medium border border-slate-200">
                        {skill.name || skill}
                      </span>
                    ))}
                    {(data.skills?.length || 0) > 8 && (
                      <span className="px-3 py-1 bg-slate-50 text-slate-500 rounded-full text-xs font-medium border border-slate-200">
                        +{(data.skills?.length || 0) - 8} more
                      </span>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="flex justify-center mt-8">
                 <button onClick={() => setView('full')} className="px-6 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors">
                    View Full Dataset Profile
                 </button>
              </div>
            </div>
          ) : (
            <div className="animate-fade-in space-y-8 pb-8">
              {/* Professional Profile */}
              <section>
                <h3 className="text-lg font-bold text-slate-800 mb-4 pb-2 border-b border-slate-200">Professional Profile</h3>
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
                  <h3 className="text-lg font-bold text-slate-800 mb-4 pb-2 border-b border-slate-200">Career History</h3>
                  <div className="space-y-6">
                    {data.career_history.map((job: any, i: number) => (
                      <div key={i} className="bg-slate-50 p-4 rounded-lg border border-slate-100">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h4 className="font-semibold text-slate-800">{job.title}</h4>
                            <div className="text-blue-600 font-medium text-sm">{job.company} {job.is_current ? '(Current)' : ''}</div>
                          </div>
                          <div className="text-sm text-slate-500 font-mono">
                            {job.start_date} - {job.end_date || 'Present'} ({job.duration_months} mos)
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-xs text-slate-500 mb-3">
                          <div>Industry: {job.industry || 'N/A'}</div>
                          <div>Company Size: {job.company_size || 'N/A'}</div>
                        </div>
                        {job.description && (
                          <p className="text-sm text-slate-600 whitespace-pre-wrap leading-relaxed">{job.description}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* Education */}
              {data.education?.length > 0 && (
                <section>
                  <h3 className="text-lg font-bold text-slate-800 mb-4 pb-2 border-b border-slate-200">Education</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {data.education.map((edu: any, i: number) => (
                      <div key={i} className="bg-slate-50 p-4 rounded-lg border border-slate-100 flex flex-col gap-1">
                        <h4 className="font-semibold text-slate-800">{edu.institution} <span className="text-xs px-2 py-0.5 bg-slate-200 text-slate-600 rounded-full font-normal">{edu.tier}</span></h4>
                        <div className="text-sm text-slate-600">{edu.degree} in {edu.field_of_study}</div>
                        <div className="text-xs text-slate-500">{edu.start_year} - {edu.end_year} • Grade: {edu.grade || 'N/A'}</div>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* Comprehensive Skills */}
              <section>
                <h3 className="text-lg font-bold text-slate-800 mb-4 pb-2 border-b border-slate-200">Comprehensive Skills</h3>
                <div className="flex flex-wrap gap-2">
                  {data.skills?.map((skill: any, i: number) => (
                    <div key={i} className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 text-blue-700 border border-blue-100 rounded-lg text-sm">
                      <span className="font-medium">{skill.name || skill}</span>
                      {skill.proficiency && (
                        <span className="text-xs text-blue-500 capitalize px-1.5 py-0.5 bg-blue-100 rounded-md">{skill.proficiency}</span>
                      )}
                      {skill.duration_months > 0 && (
                        <span className="text-xs text-slate-500">{Math.round(skill.duration_months/12)}y</span>
                      )}
                    </div>
                  ))}
                </div>
              </section>

              {/* Platform Signals */}
              {data.redrob_signals && (
                <section>
                  <h3 className="text-lg font-bold text-slate-800 mb-4 pb-2 border-b border-slate-200">Platform & Activity Signals</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-y-4 gap-x-6 text-sm bg-slate-50 p-6 rounded-xl border border-slate-200">
                    <DetailItem label="Completeness" value={`${(data.redrob_signals.profile_completeness_score * 100).toFixed(0)}%`} />
                    <DetailItem label="Open to Work" value={data.redrob_signals.open_to_work_flag ? 'Yes' : 'No'} />
                    <DetailItem label="Preferred Mode" value={data.redrob_signals.preferred_work_mode} className="capitalize" />
                    <DetailItem label="Willing to Relocate" value={data.redrob_signals.willing_to_relocate ? 'Yes' : 'No'} />
                    <DetailItem label="Notice Period" value={`${data.redrob_signals.notice_period_days} days`} />
                    <DetailItem label="Salary Range (LPA)" value={data.redrob_signals.expected_salary_range_inr_lpa ? `${data.redrob_signals.expected_salary_range_inr_lpa.min} - ${data.redrob_signals.expected_salary_range_inr_lpa.max} LPA` : 'N/A'} />
                    <DetailItem label="Verified Email" value={data.redrob_signals.verified_email ? 'Yes' : 'No'} />
                    <DetailItem label="LinkedIn Connected" value={data.redrob_signals.linkedin_connected ? 'Yes' : 'No'} />
                    <DetailItem label="GitHub Activity" value={data.redrob_signals.github_activity_score > 0 ? `${data.redrob_signals.github_activity_score}` : 'N/A'} />
                    <DetailItem label="Connections" value={data.redrob_signals.connection_count} />
                    <DetailItem label="Endorsements" value={data.redrob_signals.endorsements_received} />
                    <DetailItem label="Applications (30d)" value={data.redrob_signals.applications_submitted_30d} />
                  </div>
                </section>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function DetailItem({ label, value, colSpan = 1, className = "" }: { label: string, value: any, colSpan?: number, className?: string }) {
  if (!value) return null;
  return (
    <div className={`col-span-${colSpan} flex flex-col gap-1`}>
      <span className="text-xs text-slate-500 font-medium uppercase tracking-wider">{label}</span>
      <span className={`text-slate-800 ${className}`}>{value}</span>
    </div>
  );
}

function MetricCard({ icon, title, value, color, bg }: { icon: React.ReactNode, title: string, value: string, color: string, bg: string }) {
  return (
    <div className="border border-slate-200 rounded-xl p-4 flex flex-col items-center justify-center text-center">
      <div className={`${bg} ${color} p-2 rounded-full mb-3`}>
        {icon}
      </div>
      <div className="text-sm text-slate-500 mb-1">{title}</div>
      <div className="text-xl font-bold text-slate-800">{value}</div>
    </div>
  );
}
