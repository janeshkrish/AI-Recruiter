import { Link, useLocation } from 'react-router-dom';
import {
  Brain,
  BarChart3,
  Users,
  FileSearch,
  Workflow,
} from 'lucide-react';

const navLinks = [
  { path: '/', label: 'Dashboard', icon: BarChart3 },
  { path: '/analyze', label: 'Analyze JD', icon: FileSearch },
  { path: '/candidates', label: 'Candidates', icon: Users },
  { path: '/pipeline', label: 'Pipeline', icon: Workflow },
];

export default function TopNav() {
  const location = useLocation();

  return (
    <header className="sticky top-0 z-50 h-20 border-b border-white/5 backdrop-blur-xl bg-[#09090B]/80">

      <div className="max-w-7xl mx-auto px-6 h-full flex items-center">

        {/* Logo */}
        <Link
          to="/"
          className="flex items-center gap-3 mr-10 group shrink-0"
        >
          <div className="relative">

            <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-violet-500 via-fuchsia-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-violet-500/20 group-hover:scale-105 transition-all duration-300">
              <Brain size={20} className="text-white" />
            </div>

            <div className="absolute -inset-2 bg-violet-500/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          </div>

          <div className="flex flex-col">
            <span className="font-black text-white text-base tracking-tight">
              TalentOS
            </span>

            <span className="text-[10px] uppercase tracking-[0.3em] text-violet-400 font-semibold">
              AI RECRUITING
            </span>
          </div>
        </Link>

        {/* Navigation */}
        <nav className="hidden md:flex items-center gap-2">

          {navLinks.map(({ path, label, icon: Icon }) => {
            const isActive = location.pathname === path;

            return (
              <Link
                key={path}
                to={path}
                className={`relative flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-300
                ${
                  isActive
                    ? 'bg-white/10 text-white'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
              >
                <Icon
                  size={16}
                  className={
                    isActive
                      ? 'text-violet-400'
                      : 'text-slate-500'
                  }
                />

                {label}

                {isActive && (
                  <span className="absolute bottom-0 left-3 right-3 h-[2px] rounded-full bg-gradient-to-r from-violet-500 to-cyan-400" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Spacer */}
        <div className="flex-1" />

        {/* Live Badge */}
        <div className="hidden md:flex items-center gap-2 px-3 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 mr-4">

          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />

          <span className="text-xs font-medium text-emerald-300">
            Live
          </span>
        </div>

        {/* Profile */}
        <button className="w-11 h-11 rounded-2xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white font-bold shadow-lg shadow-violet-500/20 hover:scale-105 transition-all duration-300">
          shri
        </button>

      </div>
    </header>
  );
}