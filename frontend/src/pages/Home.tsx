import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Search, Users, Database, Briefcase, Zap, TrendingUp, Activity, FileText } from 'lucide-react';

export default function Home() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/stats')
      .then(res => setStats(res.data))
      .catch(console.error);
  }, []);

  return (
    <div className="flex-1 overflow-y-auto bg-[#FAFAFA] text-slate-800">
      {/* Hero Section */}
      <div className="max-w-6xl mx-auto px-6 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-extrabold tracking-tight text-slate-900 mb-6 leading-tight">
            AI Recruiter <span className="text-blue-600">Intelligence Platform</span>
          </h1>
          <p className="text-xl text-slate-500 max-w-3xl mx-auto mb-10 leading-relaxed">
            Analyze job descriptions, discover talent, identify hidden gems, and rank candidates using recruiter-grade AI reasoning.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link to="/analyze" className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium shadow-sm transition-colors flex items-center gap-2">
              <Zap size={18} /> Analyze Job Description
            </Link>
            <Link to="/candidates" className="px-6 py-3 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded-lg font-medium shadow-sm transition-colors flex items-center gap-2">
              <Users size={18} /> Browse Candidates
            </Link>
          </div>
        </div>

        {/* Statistics Section */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-slate-800 mb-6">Dataset Insights</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <StatCard icon={<Database className="text-blue-500" />} title="Total Applicants" value={stats?.total_applicants?.toLocaleString() || "..."} />
            <StatCard icon={<Briefcase className="text-purple-500" />} title="Total Skills" value={stats?.total_skills?.toLocaleString() || "..."} />
            <StatCard icon={<TrendingUp className="text-emerald-500" />} title="Total Domains" value={stats?.total_domains?.toLocaleString() || "..."} />
            <StatCard icon={<Activity className="text-rose-500" />} title="Total Companies" value={stats?.total_companies?.toLocaleString() || "..."} />
            <StatCard icon={<Users className="text-amber-500" />} title="Average Experience" value={stats ? `${stats.average_experience} yrs` : "..."} />
            <StatCard icon={<Zap className="text-indigo-500" />} title="Hidden Gems Found" value={stats?.hidden_gems_found?.toLocaleString() || "..."} />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-slate-800 mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <ActionCard to="/analyze" icon={<FileText />} title="Analyze New JD" desc="Paste a JD to find candidates" />
            <ActionCard to="/candidates" icon={<Search />} title="Search Dataset" desc="Advanced boolean search" />
            <ActionCard to="/candidates" icon={<Users />} title="Compare Candidates" desc="Direct side-by-side battle" />
            <ActionCard to="/" icon={<Zap />} title="Recruiter Copilot" desc="Chat with your AI assistant" />
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, title, value }: { icon: React.ReactNode, title: string, value: string | number }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center gap-4 mb-4">
        <div className="p-3 bg-slate-50 rounded-lg">
          {icon}
        </div>
        <h3 className="text-slate-500 font-medium">{title}</h3>
      </div>
      <div className="text-3xl font-bold text-slate-900">{value}</div>
    </div>
  );
}

function ActionCard({ to, icon, title, desc }: { to: string, icon: React.ReactNode, title: string, desc: string }) {
  return (
    <Link to={to} className="group bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:border-blue-400 hover:shadow-md transition-all flex flex-col items-start gap-3">
      <div className="text-slate-400 group-hover:text-blue-500 transition-colors">
        {icon}
      </div>
      <div>
        <h4 className="font-semibold text-slate-800 group-hover:text-blue-600 transition-colors">{title}</h4>
        <p className="text-sm text-slate-500 mt-1">{desc}</p>
      </div>
    </Link>
  );
}
