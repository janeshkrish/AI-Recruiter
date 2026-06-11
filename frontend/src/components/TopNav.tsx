import React from 'react';
import { Link, useLocation } from 'react-router-dom';

export default function TopNav() {
  const location = useLocation();

  const getLinkClass = (path: string) => {
    return `font-medium text-sm px-3 py-2 rounded-md transition-colors ${
      location.pathname === path 
        ? "text-blue-600 bg-blue-50" 
        : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
    }`;
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center px-6 shrink-0 z-20 shadow-sm sticky top-0">
      <Link to="/" className="flex items-center gap-2 mr-8">
        <div className="w-8 h-8 bg-blue-600 rounded-md flex items-center justify-center font-bold text-white shadow-sm">
          AI
        </div>
        <span className="font-bold text-slate-800 tracking-tight">Recruiter<span className="text-blue-600">Pro</span></span>
      </Link>

      <nav className="flex gap-1 flex-1">
        <Link to="/" className={getLinkClass('/')}>Dashboard</Link>
        <Link to="/candidates" className={getLinkClass('/candidates')}>All Candidates</Link>
        <Link to="/analyze" className={getLinkClass('/analyze')}>Analyze JD</Link>
      </nav>

      <div className="flex items-center gap-4">
        <div className="text-sm text-slate-500 font-medium">Workspace Admin</div>
        <div className="w-8 h-8 rounded-full bg-slate-200 border border-slate-300"></div>
      </div>
    </header>
  );
}
