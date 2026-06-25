import { Link, useLocation } from 'react-router-dom';
import {
  Brain,
  BarChart3,
  Users,
  FileSearch,
  Workflow,
  Moon,
  Sun,
} from 'lucide-react';

const navLinks = [
  { path: '/', label: 'Dashboard', icon: BarChart3 },
  { path: '/analyze', label: 'Analyze JD', icon: FileSearch },
  { path: '/candidates', label: 'Candidates', icon: Users },
  { path: '/pipeline', label: 'Pipeline', icon: Workflow },
];

interface TopNavProps {
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
}

export default function TopNav({ theme, onToggleTheme }: TopNavProps) {
  const location = useLocation();

  return (
    <header className="sticky top-0 z-50 h-20 border-b border-[var(--color-border-subtle)] backdrop-blur-xl bg-[color-mix(in_srgb,var(--color-bg-elevated)_88%,transparent)] shadow-[0_16px_36px_var(--color-shadow-soft)]">

      <div className="max-w-7xl mx-auto px-6 h-full flex items-center">

        {/* Logo */}
        <Link
          to="/"
          className="flex items-center gap-3 mr-10 group shrink-0"
        >
          <div className="relative">

            <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-[#b15c3e] to-[#d58f55] flex items-center justify-center shadow-lg shadow-[#b15c3e]/20 group-hover:scale-105 transition-all duration-300">
              <Brain size={20} className="text-[#fffaf5]" />
            </div>

            <div className="absolute -inset-2 bg-[#d58f55]/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          </div>

          <div className="flex flex-col">
            <span className="font-black text-[var(--color-text-primary)] text-base tracking-tight">
              TalentOS
            </span>

            <span className="text-[10px] uppercase tracking-[0.3em] text-[var(--color-text-tertiary)] font-semibold">
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
                    ? 'bg-[var(--color-button-solid)] text-[var(--color-button-solid-text)] border border-transparent shadow-[0_10px_24px_var(--color-shadow-soft)]'
                    : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface-pressed)]'
                }`}
              >
                <Icon
                  size={16}
                  className={
                    isActive
                      ? 'text-[var(--color-button-solid-text)]'
                      : 'text-[var(--color-text-tertiary)]'
                  }
                />

                {label}

                {isActive && (
                  <span className="absolute bottom-0 left-3 right-3 h-[2px] rounded-full bg-[var(--color-accent-amber)]" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Spacer */}
        <div className="flex-1" />

        {/* Live Badge */}
        <div className="hidden md:flex items-center gap-2 px-3 py-2 rounded-full bg-[var(--color-button-soft)] text-[var(--color-text-primary)] border border-[var(--color-border-subtle)] mr-3 shadow-[0_10px_24px_var(--color-shadow-soft)]">

          <div className="w-2 h-2 rounded-full bg-[#0f766e] animate-pulse" />

          <span className="text-xs font-medium text-[var(--color-text-primary)]">
            Live
          </span>
        </div>

        <button
          type="button"
          onClick={onToggleTheme}
          className="inline-flex items-center gap-2 rounded-full border border-[var(--color-border-subtle)] bg-[var(--color-button-soft)] px-3 py-2 text-xs font-medium text-[var(--color-button-soft-text)] shadow-[0_10px_24px_var(--color-shadow-soft)] transition-colors hover:bg-[var(--color-button-soft-hover)]"
          aria-label="Toggle dark mode"
          title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
        >
          {theme === 'light' ? <Moon size={14} /> : <Sun size={14} />}
          <span className="hidden sm:inline">{theme === 'light' ? 'Dark Mode' : 'Light Mode'}</span>
        </button>

      </div>
    </header>
  );
}
