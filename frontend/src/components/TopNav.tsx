import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Brain, BarChart3, Users, FileSearch, Workflow } from 'lucide-react';

const navLinks = [
  { path: '/', label: 'Dashboard', icon: BarChart3 },
  { path: '/analyze', label: 'Analyze JD', icon: FileSearch },
  { path: '/candidates', label: 'Candidates', icon: Users },
  { path: '/pipeline', label: 'Pipeline', icon: Workflow },
];

export default function TopNav() {
  const location = useLocation();

  return (
    <header className="h-16 glass-strong flex items-center px-6 shrink-0 z-30 sticky top-0">
      {/* Logo */}
      <Link to="/" className="flex items-center gap-3 mr-10 group">
        <div className="relative">
          <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20 group-hover:shadow-blue-500/40 transition-shadow">
            <Brain size={18} className="text-white" />
          </div>
          <div className="absolute -inset-1 bg-gradient-to-br from-blue-500/20 to-indigo-600/20 rounded-xl blur-sm opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
        <div className="flex flex-col">
          <span className="font-bold text-white tracking-tight text-sm leading-tight">
            AI Recruiter
          </span>
          <span className="text-[10px] text-blue-400 font-medium tracking-widest uppercase">
            Intelligence
          </span>
        </div>
      </Link>

      {/* Navigation */}
      <nav className="flex gap-1 flex-1">
        {navLinks.map(({ path, label, icon: Icon }) => {
          const isActive = location.pathname === path;
          return (
            <Link
              key={path}
              to={path}
              className={`relative flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'text-white bg-white/[0.08]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
              }`}
            >
              <Icon size={16} className={isActive ? 'text-blue-400' : ''} />
              {label}
              {isActive && (
                <div className="absolute bottom-0 left-3 right-3 h-[2px] bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Right Section */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs text-slate-400 font-medium">Engine Active</span>
        </div>
        <div className="w-px h-6 bg-white/10" />
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-slate-700 to-slate-800 border border-white/10 flex items-center justify-center text-xs font-bold text-slate-300">
          JK
        </div>
      </div>
    </header>
  );
}
