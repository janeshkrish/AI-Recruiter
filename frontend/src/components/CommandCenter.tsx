
import { motion } from 'framer-motion';
import { Sparkles, FileText, Database, Target } from 'lucide-react';

interface Props {
  jdText: string;
  setJdText: (val: string) => void;
  onUnleash: () => void;
  isEvaluating: boolean;
  totalCandidates: number;
}

export default function CommandCenter({ jdText, setJdText, onUnleash, isEvaluating, totalCandidates }: Props) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Talent Pool', value: totalCandidates.toLocaleString(), icon: Database, color: 'text-blue-400' },
          { label: 'Jury Agents', value: '4 Active', icon: Sparkles, color: 'text-indigo-400' },
          { label: 'Avg Match', value: '87.4%', icon: Target, color: 'text-emerald-400' },
          { label: 'Hidden Gems', value: '2,401', icon: Sparkles, color: 'text-amber-400' },
        ].map((stat, i) => (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            key={i} 
            className="bg-[#151A22] border border-[#2A3140] rounded-xl p-5 flex items-center gap-4 hover:border-[#3A4150] transition-colors shadow-lg shadow-black/20"
          >
            <div className={`p-3 rounded-lg bg-[#2A3140]/50 ${stat.color}`}>
              <stat.icon size={20} />
            </div>
            <div>
              <div className="text-2xl font-bold text-white">{stat.value}</div>
              <div className="text-xs text-slate-400 uppercase tracking-wider font-medium">{stat.label}</div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="bg-[#151A22] border border-[#2A3140] rounded-xl overflow-hidden shadow-xl shadow-black/20">
        <div className="bg-[#1A202C] px-6 py-4 border-b border-[#2A3140] flex items-center gap-2">
          <FileText size={18} className="text-indigo-400" />
          <h3 className="font-semibold text-white">Target Job Description</h3>
        </div>
        <div className="p-6">
          <textarea
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            placeholder="Paste Job Description here... e.g. Senior AI Engineer, 5+ years experience, must know PyTorch, strong product mindset..."
            className="w-full h-48 bg-[#0B0E14] border border-[#2A3140] rounded-lg p-4 text-sm text-slate-300 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all resize-none"
          />
          <div className="mt-4 flex justify-end">
            <button
              onClick={onUnleash}
              disabled={!jdText || isEvaluating}
              className={`relative overflow-hidden px-8 py-3 rounded-lg font-medium text-sm transition-all shadow-[0_0_20px_rgba(79,70,229,0.3)]
                ${(!jdText || isEvaluating) ? 'bg-slate-700 text-slate-400 cursor-not-allowed' : 'bg-indigo-600 text-white hover:bg-indigo-500 hover:-translate-y-0.5'}`}
            >
              {isEvaluating ? (
                <span className="flex items-center gap-2">
                  <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
                    <Sparkles size={16} />
                  </motion.div>
                  Jury is Evaluating...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <Sparkles size={16} /> Unleash the Jury
                </span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
