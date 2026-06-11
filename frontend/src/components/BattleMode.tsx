import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { X, Swords, Zap } from 'lucide-react';
import axios from 'axios';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer } from 'recharts';
import type { Candidate } from '../App';

export default function BattleMode({ candidates, onClose }: { candidates: Candidate[], onClose: () => void }) {
  const [c1, setC1] = useState<Candidate | null>(candidates[0] || null);
  const [c2, setC2] = useState<Candidate | null>(candidates[1] || null);
  const [battleResult, setBattleResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (c1 && c2) {
      setLoading(true);
      axios.post('http://127.0.0.1:8000/api/battle', {
        candidate1_id: c1.candidate_id,
        candidate2_id: c2.candidate_id
      }).then(res => {
        setBattleResult(res.data);
      }).catch(err => {
        console.error(err);
      }).finally(() => {
        setLoading(false);
      });
    }
  }, [c1, c2]);

  const radarData = c1 && c2 ? [
    { subject: 'Technical', A: c1.skill_match, B: c2.skill_match },
    { subject: 'Career', A: c1.experience_match, B: c2.experience_match },
    { subject: 'Hiring Prob', A: (c1.score + c1.location_match)/2, B: (c2.score + c2.location_match)/2 },
    { subject: 'Potential', A: c1.potential_score, B: c2.potential_score },
    { subject: 'Match', A: c1.score, B: c2.score },
  ] : [];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-50 bg-[#030712]/95 backdrop-blur-3xl flex flex-col p-10 pointer-events-auto">
      <button onClick={onClose} className="absolute top-10 right-10 p-4 bg-white/5 hover:bg-white/10 rounded-full transition-colors text-slate-400 hover:text-white">
        <X size={32} />
      </button>

      <div className="text-center mb-10">
        <h2 className="text-4xl font-black text-white flex items-center justify-center gap-4">
          <Swords className="text-rose-500" size={40} /> Candidate Battle Mode
        </h2>
        <p className="text-slate-400 mt-2">Select two candidates to run the algorithmic comparison.</p>
      </div>

      <div className="flex-1 max-w-7xl mx-auto w-full grid grid-cols-3 gap-10">
        
        {/* Candidate 1 Selector */}
        <div className="flex flex-col gap-4">
          <select 
            value={c1?.candidate_id || ''} 
            onChange={(e) => setC1(candidates.find(c => c.candidate_id === e.target.value) || null)}
            className="w-full bg-indigo-500/10 border border-indigo-500/30 text-white p-4 rounded-2xl appearance-none focus:outline-none"
          >
            {candidates.map(c => <option key={c.candidate_id} value={c.candidate_id}>{c.candidate_details?.profile?.anonymized_name || c.candidate_id}</option>)}
          </select>
          {c1 && (
            <div className="flex-1 bg-white/5 border border-indigo-500/30 rounded-3xl p-8 shadow-[0_0_50px_rgba(99,102,241,0.1)]">
              <div className="text-3xl font-bold text-white mb-8 text-center">{c1.candidate_details?.profile?.anonymized_name || c1.candidate_id}</div>
              <div className="space-y-6">
                <div className="flex justify-between items-center"><span className="text-slate-400">Match Score</span><span className="text-2xl font-black text-indigo-400">{c1.score.toFixed(1)}</span></div>
                <div className="flex justify-between items-center"><span className="text-slate-400">Technical Depth</span><span className="text-xl font-bold text-white">{c1.skill_match.toFixed(1)}</span></div>
                <div className="flex justify-between items-center"><span className="text-slate-400">Potential</span><span className="text-xl font-bold text-white">{c1.potential_score.toFixed(1)}</span></div>
              </div>
            </div>
          )}
        </div>

        {/* The Arena (Radar Chart) */}
        <div className="flex flex-col items-center justify-center bg-white/5 border border-white/10 rounded-3xl p-8 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-b from-rose-500/5 to-indigo-500/5"></div>
          {loading ? (
            <div className="animate-pulse flex flex-col items-center gap-4 text-rose-400">
              <Zap size={48} className="animate-bounce" />
              <div className="font-bold tracking-widest uppercase">Simulating Matchup...</div>
            </div>
          ) : (
            <>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                    <PolarGrid stroke="rgba(255,255,255,0.1)" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#94A3B8', fontSize: 12 }} />
                    <Radar name="C1" dataKey="A" stroke="#818CF8" strokeWidth={3} fill="#818CF8" fillOpacity={0.3} />
                    <Radar name="C2" dataKey="B" stroke="#F43F5E" strokeWidth={3} fill="#F43F5E" fillOpacity={0.3} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>

              {battleResult && (
                <div className="mt-8 text-center">
                  <div className="text-xs uppercase tracking-widest text-slate-500 font-bold mb-2">Algorithm Prediction</div>
                  <div className="text-xl text-white font-bold mb-2">Winner: <span className="text-rose-400">{battleResult.winner === c1?.candidate_id ? (c1?.candidate_details?.profile?.anonymized_name || c1?.candidate_id) : (c2?.candidate_details?.profile?.anonymized_name || c2?.candidate_id)}</span></div>
                  <div className="text-sm text-slate-400 leading-relaxed max-w-sm mx-auto">{battleResult.reasoning}</div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Candidate 2 Selector */}
        <div className="flex flex-col gap-4">
          <select 
            value={c2?.candidate_id || ''} 
            onChange={(e) => setC2(candidates.find(c => c.candidate_id === e.target.value) || null)}
            className="w-full bg-rose-500/10 border border-rose-500/30 text-white p-4 rounded-2xl appearance-none focus:outline-none text-right"
          >
            {candidates.map(c => <option key={c.candidate_id} value={c.candidate_id}>{c.candidate_details?.profile?.anonymized_name || c.candidate_id}</option>)}
          </select>
          {c2 && (
            <div className="flex-1 bg-white/5 border border-rose-500/30 rounded-3xl p-8 shadow-[0_0_50px_rgba(244,63,94,0.1)]">
              <div className="text-3xl font-bold text-white mb-8 text-center">{c2.candidate_details?.profile?.anonymized_name || c2.candidate_id}</div>
              <div className="space-y-6">
                <div className="flex justify-between items-center"><span className="text-slate-400">Match Score</span><span className="text-2xl font-black text-rose-400">{c2.score.toFixed(1)}</span></div>
                <div className="flex justify-between items-center"><span className="text-slate-400">Technical Depth</span><span className="text-xl font-bold text-white">{c2.skill_match.toFixed(1)}</span></div>
                <div className="flex justify-between items-center"><span className="text-slate-400">Potential</span><span className="text-xl font-bold text-white">{c2.potential_score.toFixed(1)}</span></div>
              </div>
            </div>
          )}
        </div>

      </div>
    </motion.div>
  );
}
