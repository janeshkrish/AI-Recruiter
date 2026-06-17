import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import axios from 'axios';
import {
  ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
} from 'recharts';
import {
  Brain, Target, Shield, TrendingUp, Layers, Zap, GitBranch, Network,
  Database, Activity, Sparkles, Award
} from 'lucide-react';

const API = 'http://127.0.0.1:8000';

const fetchAnalytics = async () => {
  const res = await axios.get(`${API}/api/pipeline/analytics`);
  return res.data;
};

const agentIcons: Record<string, any> = {
  agent_a: Target,
  agent_b: TrendingUp,
  agent_c: Shield,
  agent_d: Brain,
  agent_e: Layers,
};

const agentColors = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#F43F5E'];
const pieColors = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#06B6D4'];

export default function PipelineAnalytics() {
  const { data, isLoading } = useQuery({
    queryKey: ['pipeline-analytics'],
    queryFn: fetchAnalytics,
  });

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center relative z-10">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-slate-500 text-sm">Loading pipeline analytics...</span>
        </div>
      </div>
    );
  }

  const weights = data?.weights || {};
  const weightsData = Object.entries(weights).map(([key, value]) => ({
    name: key.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
    value: (value as number) * 100,
  }));

  return (
    <div className="flex-1 overflow-y-auto relative z-10">
      <div className="max-w-6xl mx-auto px-6 py-10">
        {/* Header */}
        <motion.div
          className="mb-10"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass text-xs font-medium text-purple-400 mb-4">
            <GitBranch size={14} />
            System Architecture
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Pipeline Analytics</h1>
          <p className="text-slate-500 text-sm">System configuration, agent weights, and architecture overview</p>
        </motion.div>

        {/* Infrastructure Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
          {[
            { icon: Database, color: 'text-blue-400', value: data?.vector_store?.total_indexed?.toLocaleString() || '0', label: 'FAISS Indexed' },
            { icon: Activity, color: 'text-emerald-400', value: data?.vector_store?.dimension || '0', label: 'Embedding Dimension' },
            { icon: Network, color: 'text-amber-400', value: data?.skill_graph?.total_edges || '0', label: 'Skill Graph Edges' },
            { icon: Sparkles, color: 'text-purple-400', value: data?.skill_graph?.total_skills || '0', label: 'Skill Nodes' },
          ].map(({ icon: Icon, color, value, label }, i) => (
            <motion.div
              key={i}
              className="glass-card p-5 text-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
            >
              <Icon size={22} className={`${color} mx-auto mb-3`} />
              <div className="text-2xl font-black text-white">{value}</div>
              <div className="text-xs text-slate-500 mt-1">{label}</div>
            </motion.div>
          ))}
        </div>

        {/* Agents + Weights */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
          {/* 5-Agent Architecture */}
          <motion.div
            className="glass-card p-6"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <h2 className="text-sm font-bold text-white mb-6 flex items-center gap-2">
              <Brain size={16} className="text-blue-400" /> 5-Agent Jury Architecture
            </h2>
            <div className="space-y-3">
              {(data?.agents || []).map((agent: any, i: number) => {
                const Icon = agentIcons[agent.id] || Zap;
                return (
                  <motion.div
                    key={agent.id}
                    className="flex items-center gap-4 p-3 rounded-xl bg-white/[0.02] border border-white/[0.04] hover:border-white/[0.08] transition-colors"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + i * 0.08 }}
                  >
                    <div
                      className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
                      style={{ backgroundColor: `${agentColors[i]}15`, color: agentColors[i] }}
                    >
                      <Icon size={18} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold text-white">{agent.name}</div>
                      <div className="text-xs text-slate-500 truncate">{agent.description}</div>
                    </div>
                    <div
                      className="px-2.5 py-1 rounded-lg text-xs font-bold"
                      style={{ backgroundColor: `${agentColors[i]}15`, color: agentColors[i] }}
                    >
                      Agent {String.fromCharCode(65 + i)}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>

          {/* Scoring Weights */}
          <motion.div
            className="glass-card p-6"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <h2 className="text-sm font-bold text-white mb-6 flex items-center gap-2">
              <Award size={16} className="text-amber-400" /> Scoring Weights Configuration
            </h2>

            {/* Radar View */}
            <ResponsiveContainer width="100%" height={200}>
              <RadarChart data={weightsData}>
                <PolarGrid stroke="rgba(255,255,255,0.06)" />
                <PolarAngleAxis dataKey="name" tick={{ fill: '#94A3B8', fontSize: 10 }} />
                <PolarRadiusAxis angle={90} domain={[0, 50]} tick={false} axisLine={false} />
                <Radar dataKey="value" stroke="#8B5CF6" fill="#8B5CF6" fillOpacity={0.2} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>

            {/* Weight Bars */}
            <div className="mt-4 space-y-2.5">
              {weightsData.map((w, i) => (
                <div key={i}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400 font-medium">{w.name}</span>
                    <span className="text-white font-bold">{w.value.toFixed(0)}%</span>
                  </div>
                  <div className="progress-bar">
                    <motion.div
                      className="progress-bar-fill"
                      style={{ backgroundColor: pieColors[i % pieColors.length] }}
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(w.value * 2, 100)}%` }}
                      transition={{ delay: 0.6 + i * 0.1, duration: 0.8 }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Formula Display */}
        <motion.div
          className="glass-card p-6 mb-10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          <h2 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
            <Zap size={16} className="text-emerald-400" /> Final Score Formula
          </h2>
          <div className="font-mono text-sm text-slate-300 bg-white/[0.02] p-4 rounded-xl border border-white/[0.06] leading-loose">
            <span className="text-emerald-400">final_score</span> = (
            <span className="text-blue-400">{((weights.skill_match || 0.4) * 100).toFixed(0)}%</span> × technical +{' '}
            <span className="text-emerald-400">{((weights.experience_match || 0.25) * 100).toFixed(0)}%</span> × career +{' '}
            <span className="text-amber-400">10%</span> × behavioral +{' '}
            <span className="text-purple-400">{((weights.semantic_similarity || 0.2) * 100).toFixed(0)}%</span> × potential +{' '}
            <span className="text-cyan-400">{((weights.education_match || 0.1) * 100).toFixed(0)}%</span> × education
            ) × <span className="text-rose-400">anti_pattern_penalty</span>
          </div>
        </motion.div>

        {/* Architecture Key Differentiators */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
        >
          <DiffCard
            title="Skill Transfer Graph"
            desc="Unlike keyword matching, our graph of 120+ edges understands that PyTorch transfers to TensorFlow, and FAISS transfers to Pinecone. Candidates get partial credit for adjacent skills."
            color="blue"
          />
          <DiffCard
            title="23-Signal Behavioral Engine"
            desc="Response rate, GitHub activity, notice period, open-to-work status, interview completion — all 23 Redrob signals factor into ranking."
            color="amber"
          />
          <DiffCard
            title="Anti-Pattern Detection"
            desc="The JD explicitly warns against consulting-only careers, title-hoppers, and keyword-stuffers. Our Agent E detects these patterns and applies appropriate penalties."
            color="rose"
          />
        </motion.div>

        <div className="text-center text-xs text-slate-600 pb-8">
          AI Recruiter Intelligence Platform • Built for the India Runs Data & AI Challenge
        </div>
      </div>
    </div>
  );
}

function DiffCard({ title, desc, color }: { title: string; desc: string; color: string }) {
  const colorMap: Record<string, string> = {
    blue: 'border-l-blue-500 from-blue-500/5',
    amber: 'border-l-amber-500 from-amber-500/5',
    rose: 'border-l-rose-500 from-rose-500/5',
  };
  return (
    <div className={`glass-card p-5 border-l-2 ${colorMap[color]} bg-gradient-to-r to-transparent`}>
      <h3 className="text-sm font-bold text-white mb-2">{title}</h3>
      <p className="text-xs text-slate-500 leading-relaxed">{desc}</p>
    </div>
  );
}
