import { motion } from 'framer-motion';
import { X, CheckCircle2, AlertTriangle, Lightbulb, GitCommit } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip } from 'recharts';
import type { Candidate } from '../App';

interface Props {
  candidate: Candidate;
  onClose: () => void;
}

export default function CandidateProfileModal({ candidate, onClose }: Props) {
  // Mocking the Career DNA based on Jury Scores
  const radarData = [
    { subject: 'Technical', A: candidate.skill_match, fullMark: 100 },
    { subject: 'Momentum', A: candidate.experience_match, fullMark: 100 },
    { subject: 'Potential', A: candidate.potential_score, fullMark: 100 },
    { subject: 'Reliability', A: candidate.location_match, fullMark: 100 },
    { subject: 'Transferability', A: Math.min(100, candidate.transferable_matches * 30 + 50), fullMark: 100 },
    { subject: 'Semantic', A: candidate.semantic_similarity, fullMark: 100 },
  ];

  // AI Explanation parsed from reasonings
  const reasons = candidate.reasoning.split(';').filter(r => r.trim());

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-8">
      <motion.div 
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
        className="absolute inset-0 bg-[#0B0E14]/80 backdrop-blur-sm"
        onClick={onClose}
      />
      
      <motion.div 
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        className="relative w-full max-w-5xl bg-[#151A22] border border-[#2A3140] shadow-2xl rounded-2xl flex flex-col max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-[#2A3140] bg-[#1A202C]">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h2 className="text-2xl font-bold text-white">{candidate.candidate_details?.profile?.anonymized_name || candidate.candidate_id}</h2>
              <span className="px-3 py-1 bg-indigo-500/20 text-indigo-400 font-bold rounded-full text-sm border border-indigo-500/30">
                Score: {candidate.score.toFixed(1)}
              </span>
            </div>
            <div className="text-slate-400 text-sm">
              {candidate.candidate_details?.profile?.current_title || 'Software Engineer'} • {candidate.candidate_details?.profile?.years_of_experience || 5} Years Experience
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-[#2A3140] rounded-full transition-colors text-slate-400 hover:text-white">
            <X size={24} />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Left Column: AI Reasoning */}
            <div className="lg:col-span-2 space-y-6">
              
              {/* AI Jury Verdict */}
              <div className="bg-[#1A202C] border border-[#2A3140] rounded-xl p-5">
                <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
                  <BrainCircuit size={16} className="text-indigo-400" /> AI Jury Explanation
                </h3>
                <div className="space-y-3">
                  {reasons.map((r, i) => {
                    let Icon = CheckCircle2;
                    let color = "text-emerald-400";
                    let bg = "bg-emerald-400/10 border-emerald-400/20";
                    if (r.toLowerCase().includes('penalty') || r.toLowerCase().includes('missing')) {
                      Icon = AlertTriangle;
                      color = "text-amber-400";
                      bg = "bg-amber-400/10 border-amber-400/20";
                    }
                    if (r.toLowerCase().includes('potential') || r.toLowerCase().includes('velocity')) {
                      Icon = Lightbulb;
                      color = "text-indigo-400";
                      bg = "bg-indigo-400/10 border-indigo-400/20";
                    }
                    return (
                      <div key={i} className={`flex items-start gap-3 p-3 rounded-lg border ${bg}`}>
                        <Icon size={18} className={`mt-0.5 ${color} shrink-0`} />
                        <p className="text-sm text-slate-300 leading-relaxed">{r.trim()}</p>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Career Timeline */}
              <div className="bg-[#1A202C] border border-[#2A3140] rounded-xl p-5">
                <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
                  <GitCommit size={16} className="text-indigo-400" /> Skill Evolution Timeline
                </h3>
                <div className="relative pl-4 border-l border-[#2A3140] space-y-6 mt-4">
                  {(candidate.candidate_details?.career_history || []).slice(0, 4).map((job: any, i: number) => (
                    <div key={i} className="relative">
                      <div className="absolute -left-[21px] top-1 w-2.5 h-2.5 bg-indigo-500 rounded-full ring-4 ring-[#1A202C]"></div>
                      <div className="text-sm font-medium text-white">{job.title}</div>
                      <div className="text-xs text-slate-400 mb-2">{job.company} • {job.start_date} to {job.end_date || 'Present'}</div>
                      <p className="text-xs text-slate-300 line-clamp-2">{job.description}</p>
                    </div>
                  ))}
                </div>
              </div>

            </div>

            {/* Right Column: Visualizations */}
            <div className="space-y-6">
              
              {/* Career DNA Radar */}
              <div className="bg-[#1A202C] border border-[#2A3140] rounded-xl p-5 h-72 flex flex-col">
                <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-2 text-center">Career DNA</h3>
                <div className="flex-1 -ml-4 -mt-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                      <PolarGrid stroke="#2A3140" />
                      <PolarAngleAxis dataKey="subject" tick={{ fill: '#94A3B8', fontSize: 10 }} />
                      <Radar name="Candidate" dataKey="A" stroke="#6366F1" fill="#6366F1" fillOpacity={0.3} />
                      <Tooltip contentStyle={{ backgroundColor: '#151A22', borderColor: '#2A3140', color: '#fff' }} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Hiring Probability */}
              <div className="bg-[#1A202C] border border-[#2A3140] rounded-xl p-5 text-center">
                <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">Hiring Probability</h3>
                <div className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-b from-emerald-300 to-emerald-600 mb-2">
                  {((candidate.location_match + candidate.score) / 2).toFixed(0)}%
                </div>
                <p className="text-xs text-slate-400">Probability recruiter would interview based on Redrob signals and match logic.</p>
              </div>

            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

// Ensure the BrainCircuit icon is available or we use an alternative 
function BrainCircuit(props: any) {
  return <Lightbulb {...props} />;
}
