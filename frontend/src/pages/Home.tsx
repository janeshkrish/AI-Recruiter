import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import {
  Zap, Users, Database, Briefcase, TrendingUp, Activity, FileSearch,
  Brain, Shield, Target, Layers, GitBranch, Search, ArrowRight, Sparkles,
  Network
} from 'lucide-react';

const API = 'http://127.0.0.1:8000';

function AnimatedCounter({ target, suffix = '' }: { target: number; suffix?: string }) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (target <= 0) return;
    const duration = 1500;
    const steps = 40;
    const increment = target / steps;
    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        setCount(target);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, duration / steps);
    return () => clearInterval(timer);
  }, [target]);
  return <>{count.toLocaleString()}{suffix}</>;
}

const agents = [
  { icon: Target, name: 'Technical Fit', desc: 'Skill Transfer Graph + Semantic Match', color: 'from-blue-500 to-cyan-400' },
  { icon: TrendingUp, name: 'Career Intelligence', desc: 'Promotion velocity & trajectory', color: 'from-emerald-500 to-teal-400' },
  { icon: Shield, name: 'Behavioral Intel', desc: '23 Redrob behavioral signals', color: 'from-amber-500 to-orange-400' },
  { icon: Brain, name: 'Potential Engine', desc: 'Learning velocity & growth', color: 'from-purple-500 to-violet-400' },
  { icon: Layers, name: 'Anti-Pattern Detection', desc: 'Consulting-only, title-hopping', color: 'from-rose-500 to-pink-400' },
];

const pipelineStages = [
  { label: 'Full Dataset', count: '100K', color: 'bg-slate-600' },
  { label: 'FAISS Retrieval', count: '500', color: 'bg-blue-500' },
  { label: 'Multi-Agent Jury', count: '200', color: 'bg-purple-500' },
  { label: 'Final Ranking', count: 'Top 100', color: 'bg-emerald-500' },
];

export default function Home() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    axios.get(`${API}/api/stats`).then(res => setStats(res.data)).catch(() => {});
  }, []);

  return (
    <div className="flex-1 overflow-y-auto relative z-10">
      <div className="max-w-6xl mx-auto px-6 py-12">

        {/* ─── Hero ─── */}
        <motion.div
          className="text-center mb-20"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass text-xs font-medium text-blue-400 mb-6">
            <Sparkles size={14} />
            Multi-Agent Recruitment Intelligence
          </div>

          <h1 className="text-5xl md:text-7xl font-black tracking-tight leading-[1.1] mb-6">
            <span className="text-white">Hire Smarter with</span>
            <br />
            <span className="gradient-text-blue">AI-Powered</span>{' '}
            <span className="text-white">Ranking</span>
          </h1>

          <p className="text-lg md:text-xl text-slate-400 max-w-3xl mx-auto mb-10 leading-relaxed">
            Not keyword matching. Real intelligence. A 5-agent jury evaluates candidates across
            technical fit, career trajectory, behavioral signals, learning potential, and anti-patterns.
          </p>

          <div className="flex items-center justify-center gap-4">
            <Link
              to="/analyze"
              className="group relative px-8 py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl font-semibold shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 transition-all flex items-center gap-2"
            >
              <Zap size={18} />
              Analyze Job Description
              <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/candidates"
              className="px-8 py-3.5 glass hover:bg-white/[0.06] text-slate-300 hover:text-white rounded-xl font-semibold transition-all flex items-center gap-2"
            >
              <Users size={18} />
              Browse Dataset
            </Link>
          </div>
        </motion.div>

        {/* ─── Stats ─── */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-20">
          {[
            { icon: Database, label: 'Total Applicants', value: stats?.total_applicants || 0, color: 'text-blue-400' },
            { icon: Layers, label: 'FAISS Indexed', value: stats?.indexed_candidates || 0, color: 'text-indigo-400' },
            { icon: Briefcase, label: 'Companies', value: stats?.total_companies || 0, color: 'text-purple-400' },
            { icon: Activity, label: 'Avg Experience', value: stats?.average_experience || 0, color: 'text-emerald-400', suffix: ' yrs' },
            { icon: Network, label: 'Skill Graph', value: 120, color: 'text-amber-400', suffix: ' edges' },
            { icon: Sparkles, label: 'Hidden Gems', value: stats?.hidden_gems_found || 0, color: 'text-rose-400' },
          ].map(({ icon: Icon, label, value, color, suffix }, i) => (
            <motion.div
              key={i}
              className="glass-card p-5 text-center group"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08, duration: 0.4 }}
            >
              <div className={`${color} mb-3 flex justify-center`}>
                <Icon size={22} />
              </div>
              <div className="text-2xl font-bold text-white mb-1">
                <AnimatedCounter target={typeof value === 'number' ? value : 0} suffix={suffix || ''} />
              </div>
              <div className="text-xs text-slate-500 font-medium">{label}</div>
            </motion.div>
          ))}
        </div>

        {/* ─── Pipeline Funnel ─── */}
        <motion.div
          className="mb-20"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          <h2 className="text-2xl font-bold text-white mb-2 text-center">4-Stage Intelligence Pipeline</h2>
          <p className="text-slate-500 text-center mb-8 text-sm">From 100K candidates to a curated shortlist</p>

          <div className="flex items-center justify-center gap-2 max-w-4xl mx-auto">
            {pipelineStages.map((stage, i) => (
              <React.Fragment key={i}>
                <motion.div
                  className="glass-card p-5 flex-1 text-center"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.4 + i * 0.15 }}
                >
                  <div className={`w-3 h-3 ${stage.color} rounded-full mx-auto mb-3`} />
                  <div className="text-2xl font-black text-white mb-1">{stage.count}</div>
                  <div className="text-xs text-slate-500 font-medium">{stage.label}</div>
                </motion.div>
                {i < pipelineStages.length - 1 && (
                  <div className="text-slate-600 shrink-0">
                    <ArrowRight size={20} />
                  </div>
                )}
              </React.Fragment>
            ))}
          </div>
        </motion.div>

        {/* ─── 5-Agent Architecture ─── */}
        <motion.div
          className="mb-20"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.6 }}
        >
          <h2 className="text-2xl font-bold text-white mb-2 text-center">5-Agent Jury Architecture</h2>
          <p className="text-slate-500 text-center mb-8 text-sm">Each candidate is evaluated independently by 5 specialized agents</p>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {agents.map((agent, i) => (
              <motion.div
                key={i}
                className="glass-card p-5 text-center group cursor-default"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 + i * 0.1 }}
                whileHover={{ y: -4 }}
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${agent.color} flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:scale-110 transition-transform`}>
                  <agent.icon size={22} className="text-white" />
                </div>
                <h3 className="text-sm font-bold text-white mb-1">{agent.name}</h3>
                <p className="text-xs text-slate-500 leading-relaxed">{agent.desc}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* ─── Quick Actions ─── */}
        <motion.div
          className="mb-16"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7, duration: 0.6 }}
        >
          <h2 className="text-2xl font-bold text-white mb-6 text-center">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl mx-auto">
            <ActionCard
              to="/analyze"
              icon={<FileSearch />}
              title="Analyze New JD"
              desc="Paste a job description, get ranked candidates instantly"
              gradient="from-blue-500/10 to-indigo-500/10"
              border="hover:border-blue-500/30"
            />
            <ActionCard
              to="/candidates"
              icon={<Search />}
              title="Explore Dataset"
              desc="Browse and filter the full candidate database"
              gradient="from-emerald-500/10 to-teal-500/10"
              border="hover:border-emerald-500/30"
            />
            <ActionCard
              to="/pipeline"
              icon={<GitBranch />}
              title="Pipeline Analytics"
              desc="Score distributions, agent agreement, pipeline stats"
              gradient="from-purple-500/10 to-violet-500/10"
              border="hover:border-purple-500/30"
            />
          </div>
        </motion.div>

        {/* ─── Footer ─── */}
        <div className="text-center text-xs text-slate-600 pb-8">
          AI Recruiter Intelligence Platform • Multi-Agent Architecture • Skill Transfer Graph
        </div>
      </div>
    </div>
  );
}

function ActionCard({ to, icon, title, desc, gradient, border }: {
  to: string; icon: React.ReactNode; title: string; desc: string; gradient: string; border: string;
}) {
  return (
    <Link
      to={to}
      className={`glass-card p-6 group bg-gradient-to-br ${gradient} ${border} flex flex-col gap-3`}
    >
      <div className="text-slate-400 group-hover:text-white transition-colors">
        {icon}
      </div>
      <div>
        <h4 className="font-semibold text-white group-hover:text-blue-300 transition-colors text-sm">{title}</h4>
        <p className="text-xs text-slate-500 mt-1 leading-relaxed">{desc}</p>
      </div>
    </Link>
  );
}
