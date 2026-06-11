import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, BrainCircuit, Target, Users } from 'lucide-react';

interface Props {
  jdText: string;
  setJdText: (val: string) => void;
  onRun: () => void;
}

// Animated Counter Hook
function useCounter(end: number, duration: number = 2000) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTime: number | null = null;
    const animate = (time: number) => {
      if (!startTime) startTime = time;
      const progress = Math.min((time - startTime) / duration, 1);
      
      // Easing function outQuart
      const ease = 1 - Math.pow(1 - progress, 4);
      setCount(Math.floor(ease * end));
      
      if (progress < 1) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  }, [end, duration]);

  return count;
}

export default function HeroSection({ jdText, setJdText, onRun }: Props) {
  const candidatesCount = useCounter(100000);
  const confidence = useCounter(95);
  const gems = useCounter(87);

  return (
    <div className="flex flex-col items-center max-w-4xl mx-auto text-center mt-12">
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="mb-6 inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-sm font-medium"
      >
        <Sparkles size={14} className="animate-pulse" />
        Intelligence Engine v2.0 Online
      </motion.div>

      <motion.h1 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="text-5xl md:text-7xl font-bold tracking-tight mb-6"
      >
        Find the <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">impossible</span> hires.
      </motion.h1>

      <motion.p 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="text-lg text-slate-400 max-w-2xl mx-auto mb-16"
      >
        Redrob OS doesn't just search keywords. We simulate 4 distinct AI Recruiter Agents to analyze career momentum, skill transferability, and hidden potential across the universe of talent.
      </motion.p>

      {/* Animated Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full mb-16">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="glass-panel p-6 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 blur-3xl rounded-full group-hover:bg-blue-500/20 transition-all duration-700"></div>
          <Users size={24} className="text-blue-400 mb-4" />
          <div className="text-4xl font-bold text-white mb-1">{candidatesCount.toLocaleString()}+</div>
          <div className="text-sm text-slate-400 font-medium">Talent Universe Evaluated</div>
        </motion.div>
        
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="glass-panel p-6 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 blur-3xl rounded-full group-hover:bg-emerald-500/20 transition-all duration-700"></div>
          <Target size={24} className="text-emerald-400 mb-4" />
          <div className="text-4xl font-bold text-white mb-1">{confidence}%</div>
          <div className="text-sm text-slate-400 font-medium">Prediction Confidence</div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }} className="glass-panel p-6 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/10 blur-3xl rounded-full group-hover:bg-amber-500/20 transition-all duration-700"></div>
          <BrainCircuit size={24} className="text-amber-400 mb-4" />
          <div className="text-4xl font-bold text-white mb-1">{gems}%</div>
          <div className="text-sm text-slate-400 font-medium">Hidden Talent Discovered</div>
        </motion.div>
      </div>

      {/* Input Section */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }} 
        animate={{ opacity: 1, scale: 1 }} 
        transition={{ delay: 0.7 }}
        className="w-full glass-panel p-2 flex flex-col md:flex-row items-center gap-2"
      >
        <div className="flex-1 w-full pl-4">
          <textarea 
            value={jdText}
            onChange={e => setJdText(e.target.value)}
            placeholder="Describe the role or paste a JD. E.g. 'I need a Senior ML Engineer who is comfortable in startups...'"
            className="w-full bg-transparent border-none focus:ring-0 text-white placeholder-slate-500 resize-none h-14 pt-4 outline-none"
          />
        </div>
        <button 
          onClick={onRun}
          disabled={!jdText}
          className="w-full md:w-auto h-14 px-8 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-semibold flex items-center justify-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(99,102,241,0.4)]"
        >
          <Sparkles size={18} /> Let AI Find Them
        </button>
      </motion.div>

    </div>
  );
}
