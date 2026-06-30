import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import {
  Zap, Users, Database, Briefcase, TrendingUp, Activity, FileSearch,
  Brain, Shield, Target, Layers, GitBranch, Search, ArrowRight, Sparkles,
  Network, Gem, CheckCircle2
} from 'lucide-react';
import { API_BASE_URL } from '../lib/api';

const API = API_BASE_URL;

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
  { icon: Target, name: 'Technical Fit', desc: 'Skill Transfer Graph + Semantic Match', color: 'from-[#b15c3e] to-[#d99c66]' },
  { icon: TrendingUp, name: 'Career Intelligence', desc: 'Promotion velocity & trajectory', color: 'from-[#0f766e] to-[#55a197]' },
  { icon: Shield, name: 'Behavioral Intel', desc: '23 Redrob behavioral signals', color: 'from-[#7257a3] to-[#9a85c4]' },
  { icon: Brain, name: 'Potential Engine', desc: 'Learning velocity & growth', color: 'from-[#d28d4e] to-[#e4b36b]' },
  { icon: Layers, name: 'Anti-Pattern Detection', desc: 'Consulting-only, title-hopping', color: 'from-[#1f1714] to-[#5f4a41]' },
];

const pipelineStages = [
  { label: 'Full Dataset', count: '100K', color: 'bg-[#b15c3e]' },
  { label: 'FAISS Retrieval', count: '500', color: 'bg-[#0f766e]' },
  { label: 'Multi-Agent Jury', count: '200', color: 'bg-[#7257a3]' },
  { label: 'Final Ranking', count: 'Top 100', color: 'bg-[#1f1714]' },
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
          
         <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-[#b15c3e]/12 bg-[#fff9f2] text-[#8a5a45] text-sm font-medium mb-8 shadow-[0_10px_24px_rgba(177,92,62,0.08)]">
  <Sparkles size={16} className="text-[#b15c3e]" />
  AI Recruiting Intelligence Platform
</div>

<h1 className="text-4xl md:text-6xl lg:text-7xl font-black tracking-tight leading-[1.05] mb-6">
  <span className="text-[var(--color-text-primary)]">
    Find Exceptional Talent
  </span>

  <br />

  <span className="gradient-text-blue">
    Faster Than Ever
  </span>
</h1>

          <p className="text-lg md:text-xl text-[var(--color-text-secondary)] max-w-3xl mx-auto mb-10 leading-relaxed">
            Not keyword matching. Real intelligence. A 5-agent jury evaluates candidates across
            technical fit, career trajectory, behavioral signals, learning potential, and career trajectory to uncover top talent.
          </p>

          <div className="flex items-center justify-center gap-4">
            <Link
              to="/analyze"
              className="group relative px-8 py-3.5 bg-gradient-to-r from-[#b15c3e] via-[#ca7d4d] to-[#df9f61] hover:scale-105 text-[#fff9f4] rounded-xl font-semibold shadow-lg shadow-[#b15c3e]/25 transition-all flex items-center gap-2"
            >
              <Zap size={18} />
              Analyze Job Description
              <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/candidates"
              className="px-8 py-3.5 glass hover:bg-[var(--color-button-soft-hover)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] rounded-xl font-semibold transition-all flex items-center gap-2"
            >
              <Users size={18} />
              Browse Dataset
            </Link>
          </div>
        </motion.div>

        {/* ─── Stats ─── */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-20">
          {[
            { icon: Database, label: 'Total Applicants', value: stats?.total_applicants || 0, color: 'text-[#b15c3e]' },
            { icon: Layers, label: 'FAISS Indexed', value: stats?.indexed_candidates || 0, color: 'text-[#0f766e]' },
            { icon: Briefcase, label: 'Companies', value: stats?.total_companies || 0, color: 'text-[#7257a3]' },
            { icon: Activity, label: 'Avg Experience', value: stats?.average_experience || 0, color: 'text-[#d28d4e]', suffix: ' yrs' },
            { icon: Network, label: 'Skill Graph', value: 120, color: 'text-[var(--color-text-secondary)]', suffix: ' edges' },
            { icon: Gem, label: 'Hidden Gems', value: stats?.hidden_gems_found || 0, color: 'text-[var(--color-text-primary)]' },
          ].map(({ icon: Icon, label, value, color, suffix }, i) => (
            <motion.div
              key={i}
            className="glass-card p-6 text-center group card-hover"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08, duration: 0.4 }}
            >
              <div className={`${color} mb-3 flex justify-center`}>
                <Icon size={26} />
              </div>
              <div className="text-2xl font-bold text-[var(--color-text-primary)] mb-1">
                <AnimatedCounter target={typeof value === 'number' ? value : 0} suffix={suffix || ''} />
              </div>
              <div className="text-xs text-[var(--color-text-tertiary)] font-medium">{label}</div>
            </motion.div>
          ))}
        </div>

        <div className="grid lg:grid-cols-3 gap-6 mb-20">

  <div className="glass-card p-6">
            <h3 className="text-lg font-bold text-[var(--color-text-primary)] mb-4">
      Candidate Funnel
    </h3>

    <div className="space-y-4">

      <div>
        <div className="flex justify-between text-sm">
          <span>Applicants</span>
          <span>100K</span>
        </div>

        <div className="progress-bar mt-2">
          <div
            className="progress-bar-fill bg-[#b15c3e]"
            style={{ width: '100%' }}
          />
        </div>
      </div>

      <div>
        <div className="flex justify-between text-sm">
          <span>Shortlisted</span>
          <span>500</span>
        </div>

        <div className="progress-bar mt-2">
          <div
            className="progress-bar-fill bg-[#0f766e]"
            style={{ width: '35%' }}
          />
        </div>
      </div>

    </div>
  </div>

  <div className="glass-card p-6">
    <h3 className="text-lg font-bold text-[var(--color-text-primary)] mb-4">
      Top Skills
    </h3>

    <div className="flex flex-wrap gap-2">
      {['React','Node.js','Python','AWS','Docker','ML'].map(skill => (
        <span
          key={skill}
          className="px-3 py-1 rounded-full bg-[var(--color-pill-bg)] border border-[var(--color-pill-border)] text-[var(--color-pill-text)] text-xs"
        >
          {skill}
        </span>
      ))}
    </div>
  </div>

  <div className="glass-card p-6">
    <h3 className="text-lg font-bold text-[var(--color-text-primary)] mb-4">
      Recent Activity
    </h3>

      <div className="space-y-3 text-sm text-[var(--color-text-secondary)]">
      <div className="flex items-center gap-2"><CheckCircle2 size={14} className="text-[#0f766e]" /> JD Uploaded</div>
      <div className="flex items-center gap-2"><CheckCircle2 size={14} className="text-[#0f766e]" /> 500 Candidates Ranked</div>
      <div className="flex items-center gap-2"><CheckCircle2 size={14} className="text-[#0f766e]" /> Hidden Gem Found</div>
      <div className="flex items-center gap-2"><CheckCircle2 size={14} className="text-[#0f766e]" /> Agent Consensus 95%</div>
    </div>
  </div>

</div>


        {/* ─── Pipeline Funnel ─── */}
        <motion.div
          className="mb-20"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          <h2 className="text-2xl font-bold text-[var(--color-text-primary)] mb-2 text-center">4-Stage Intelligence Pipeline</h2>
          <p className="text-[var(--color-text-tertiary)] text-center mb-8 text-sm">From 100K candidates to a curated shortlist</p>

          <div className="flex items-center justify-center gap-2 max-w-4xl mx-auto">
            {pipelineStages.map((stage, i) => (
              <React.Fragment key={i}>
                <motion.div
                  className="glass-card p-5 flex-1 text-center card-hover"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.4 + i * 0.15 }}
                >
                  <div className={`w-3 h-3 ${stage.color} rounded-full mx-auto mb-3`} />
                  <div className="text-2xl font-black text-[var(--color-text-primary)] mb-1">{stage.count}</div>
                  <div className="text-xs text-[var(--color-text-tertiary)] font-medium">{stage.label}</div>
                </motion.div>
                {i < pipelineStages.length - 1 && (
                  <div className="text-[#b69281] shrink-0">
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
          <h2 className="text-2xl font-bold text-[var(--color-text-primary)] mb-2 text-center">5-Agent Jury Architecture</h2>
          <p className="text-[var(--color-text-tertiary)] text-center mb-8 text-sm">Each candidate is evaluated independently by 5 specialized agents to identify the highest-potential candidates.</p>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {agents.map((agent, i) => (
              <motion.div
                key={i}
                className="glass-card p-5 text-center group cursor-default card-hover"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 + i * 0.1 }}
                whileHover={{ y: -4 }}
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${agent.color} flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:scale-110 transition-transform`}>
                  <agent.icon size={22} className="text-[#fff9f4]" />
                </div>
                <h3 className="text-sm font-bold text-[var(--color-text-primary)] mb-1">{agent.name}</h3>
                <p className="text-xs text-[var(--color-text-tertiary)] leading-relaxed">{agent.desc}</p>
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
          <h2 className="text-2xl font-bold text-[var(--color-text-primary)] mb-6 text-center">Get Started</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl mx-auto">
            <ActionCard
              to="/analyze"
              icon={<FileSearch />}
              title="Analyze New JD"
              desc="Paste a job description, get ranked candidates instantly"
              gradient="from-white/8 to-white/0"
              border="hover:border-white/20"
            />
            <ActionCard
              to="/candidates"
              icon={<Search />}
              title="Explore Dataset"
              desc="Browse and filter the full candidate database"
              gradient="from-zinc-200/10 to-transparent"
              border="hover:border-white/20"
            />
            <ActionCard
              to="/pipeline"
              icon={<GitBranch />}
              title="Pipeline Analytics"
              desc="Score distributions, agent agreement, pipeline stats"
              gradient="from-zinc-400/10 to-transparent"
              border="hover:border-white/20"
            />
          </div>
        </motion.div>

        {/* ─── Footer ─── */}
        <div className="text-center text-xs text-[var(--color-text-tertiary)] pb-8">
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
      <div className="text-[var(--color-text-secondary)] group-hover:text-[var(--color-accent-blue)] transition-colors">
        {icon}
      </div>
      <div>
        <h4 className="font-semibold text-[var(--color-text-primary)] group-hover:text-[var(--color-accent-blue)] transition-colors text-sm">{title}</h4>
        <p className="text-xs text-[var(--color-text-tertiary)] mt-1 leading-relaxed">{desc}</p>
      </div>
    </Link>
  );
}
