import { Search, Loader2 } from 'lucide-react';

interface Props {
  jdText: string;
  setJdText: (text: string) => void;
  onSearch: () => void;
  isSearching: boolean;
}

export default function TopNav({ jdText, setJdText, onSearch, isSearching }: Props) {
  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shrink-0 z-20">
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 bg-blue-600 rounded-md flex items-center justify-center font-bold text-white shadow-sm">
          R
        </div>
        <span className="font-semibold text-slate-800 tracking-tight">Redrob Intelligence</span>
      </div>

      <div className="flex-1 max-w-2xl mx-12">
        <div className="relative flex items-center bg-slate-50 border border-slate-200 rounded-lg overflow-hidden focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500 transition-shadow">
          <Search className="text-slate-400 ml-3" size={16} />
          <input
            type="text"
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && onSearch()}
            placeholder="e.g. Senior Machine Learning Engineer with MLOps experience..."
            className="w-full bg-transparent p-2 text-sm text-slate-800 placeholder-slate-400 focus:outline-none"
          />
          <button 
            onClick={onSearch}
            disabled={isSearching || !jdText}
            className="h-full px-4 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 transition-colors disabled:bg-slate-300 flex items-center gap-2"
          >
            {isSearching ? <Loader2 size={16} className="animate-spin" /> : 'Analyze'}
          </button>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="w-8 h-8 rounded-full bg-slate-200 border border-slate-300"></div>
      </div>
    </header>
  );
}
