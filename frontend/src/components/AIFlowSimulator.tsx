import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FileText, Code, Network, Brain, Cpu, Sparkles } from 'lucide-react';

const STAGES = [
  { id: 'role', title: 'Role Understanding Agent', icon: FileText, color: '#3B82F6' },
  { id: 'tech', title: 'Technical Fit Agent', icon: Code, color: '#10B981' },
  { id: 'career', title: 'Career Trajectory Agent', icon: Network, color: '#F59E0B' },
  { id: 'behavior', title: 'Behavioral Agent', icon: Brain, color: '#EC4899' },
  { id: 'potential', title: 'Learning Potential Agent', icon: Cpu, color: '#8B5CF6' },
];

export default function AIFlowSimulator() {
  const [activeStage, setActiveStage] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setActiveStage(prev => {
        if (prev < STAGES.length - 1) return prev + 1;
        return prev;
      });
    }, 800); // Progress through stages
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex flex-col items-center max-w-3xl w-full">
      <div className="text-center mb-16">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 8, ease: "linear" }}
          className="w-16 h-16 rounded-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 p-[2px] mx-auto mb-6"
        >
          <div className="w-full h-full bg-[#030712] rounded-full flex items-center justify-center">
            <Sparkles className="text-white" size={24} />
          </div>
        </motion.div>
        <h2 className="text-2xl font-bold mb-2">Simulating Recruiter Jury</h2>
        <p className="text-slate-400">Evaluating 100K candidates against 5 dimensions.</p>
      </div>

      <div className="relative w-full">
        {/* Connection Line */}
        <div className="absolute top-1/2 left-0 w-full h-1 bg-white/10 -translate-y-1/2 rounded-full overflow-hidden">
          <motion.div 
            className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-emerald-500"
            initial={{ width: '0%' }}
            animate={{ width: `${((activeStage) / (STAGES.length - 1)) * 100}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>

        {/* Nodes */}
        <div className="relative flex justify-between w-full">
          {STAGES.map((stage, i) => {
            const isActive = i === activeStage;
            const isPast = i < activeStage;
            
            return (
              <div key={stage.id} className="flex flex-col items-center">
                <motion.div 
                  initial={{ scale: 0.8, opacity: 0.5 }}
                  animate={{ 
                    scale: isActive ? 1.2 : 1, 
                    opacity: isActive || isPast ? 1 : 0.3,
                    boxShadow: isActive ? `0 0 30px ${stage.color}80` : 'none',
                    borderColor: isActive || isPast ? stage.color : 'rgba(255,255,255,0.1)'
                  }}
                  className="w-12 h-12 rounded-full bg-[#151A22] border-2 flex items-center justify-center z-10 transition-colors duration-300"
                  style={{ backgroundColor: isPast ? stage.color : '#151A22' }}
                >
                  <stage.icon size={20} color={isPast ? '#fff' : (isActive ? stage.color : '#64748B')} />
                </motion.div>
                
                <motion.div 
                  animate={{ opacity: isActive ? 1 : 0.4 }}
                  className="absolute top-16 text-center w-24 -ml-6"
                >
                  <span className="text-[10px] font-medium uppercase tracking-wider block" style={{ color: isActive ? stage.color : '#64748B' }}>
                    {stage.title}
                  </span>
                </motion.div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
