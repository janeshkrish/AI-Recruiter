import { useState, useMemo } from 'react';
import type { Candidate } from '../App';
import { Sparkles } from 'lucide-react';
import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, ResponsiveContainer, Tooltip as RechartsTooltip, Cell } from 'recharts';

interface Props {
  candidates: Candidate[];
  onSelect: (c: Candidate) => void;
}

export default function TalentUniverse({ candidates, onSelect }: Props) {
  const [hoveredNode, setHoveredNode] = useState<any>(null);

  // Transform candidates for ScatterPlot
  // X-Axis: Experience Match
  // Y-Axis: Skill Match
  // Z-Axis (Size): Potential Score
  // Color: Hiring Probability (Score)
  const data = useMemo(() => {
    return candidates.map(c => ({
      x: c.experience_match,
      y: c.skill_match,
      z: c.potential_score,
      score: c.score,
      candidate: c
    }));
  }, [candidates]);

  const getColor = (score: number) => {
    if (score >= 90) return '#10B981'; // Emerald
    if (score >= 80) return '#3B82F6'; // Blue
    if (score >= 70) return '#8B5CF6'; // Purple
    return '#F59E0B'; // Amber
  };

  return (
    <div className="h-full w-full flex flex-col">
      <div className="flex items-center justify-between mb-4 glass-panel p-4">
        <div className="flex items-center gap-3 text-lg font-semibold">
          <Sparkles className="text-indigo-400" />
          <span>Talent Universe</span>
        </div>
        <div className="flex gap-4">
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <div className="w-3 h-3 rounded-full bg-[#10B981]"></div> &gt;90% Match
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <div className="w-3 h-3 rounded-full bg-[#3B82F6]"></div> &gt;80% Match
          </div>
        </div>
      </div>

      <div className="flex-1 glass-panel p-6 relative">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <XAxis type="number" dataKey="x" name="Experience Momentum" domain={[0, 100]} hide />
            <YAxis type="number" dataKey="y" name="Technical Capability" domain={[0, 100]} hide />
            <ZAxis type="number" dataKey="z" range={[50, 400]} name="Potential" />
            
            <RechartsTooltip 
              cursor={{ strokeDasharray: '3 3', stroke: 'rgba(255,255,255,0.1)' }}
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="glass-panel p-4 text-sm border-white/10 shadow-2xl shadow-black/50">
                      <div className="font-bold text-white mb-2">{data.candidate.candidate_id}</div>
                      <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                        <span className="text-slate-400">Jury Score:</span>
                        <span className="text-emerald-400 font-bold">{data.score.toFixed(1)}</span>
                        <span className="text-slate-400">Potential:</span>
                        <span className="text-amber-400 font-bold">{data.z.toFixed(1)}</span>
                        <span className="text-slate-400">Momentum:</span>
                        <span className="text-white">{data.x.toFixed(1)}</span>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />
            
            <Scatter 
              name="Candidates" 
              data={data} 
              onClick={(e: any) => {
                if(e && e.candidate) onSelect(e.candidate);
              }}
              onMouseEnter={(e: any) => setHoveredNode(e)}
              onMouseLeave={() => setHoveredNode(null)}
              className="cursor-pointer"
            >
              {data.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={getColor(entry.score)} 
                  fillOpacity={hoveredNode && hoveredNode.candidate.candidate_id !== entry.candidate.candidate_id ? 0.2 : 0.8}
                  stroke={getColor(entry.score)}
                  strokeWidth={hoveredNode?.candidate.candidate_id === entry.candidate.candidate_id ? 3 : 0}
                  className="transition-all duration-300"
                />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
        
        {/* Overlay Labels */}
        <div className="absolute left-4 bottom-1/2 -rotate-90 text-xs tracking-[0.2em] uppercase text-slate-500 font-bold opacity-50">
          Technical Capability →
        </div>
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-xs tracking-[0.2em] uppercase text-slate-500 font-bold opacity-50">
          Experience Momentum →
        </div>
      </div>
    </div>
  );
}
