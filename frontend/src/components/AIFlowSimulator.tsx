import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  FileText,
  Code,
  Network,
  Brain,
  Cpu,
  Sparkles
} from 'lucide-react';

const STAGES = [
  {
    id: 'role',
    title: 'Role Intelligence',
    description: 'Understands job requirements and role expectations.',
    icon: FileText,
    color: '#8B5CF6'
  },
  {
    id: 'tech',
    title: 'Technical Match',
    description: 'Evaluates skills, technologies, and experience.',
    icon: Code,
    color: '#06B6D4'
  },
  {
    id: 'career',
    title: 'Career Growth',
    description: 'Analyzes progression, promotions, and trajectory.',
    icon: Network,
    color: '#10B981'
  },
  {
    id: 'behavior',
    title: 'Behavioral Signals',
    description: 'Measures collaboration and professional indicators.',
    icon: Brain,
    color: '#F59E0B'
  },
  {
    id: 'potential',
    title: 'Potential Engine',
    description: 'Predicts adaptability and future performance.',
    icon: Cpu,
    color: '#EC4899'
  }
];

export default function AIFlowSimulator() {
  const [activeStage, setActiveStage] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setActiveStage(prev => {
        if (prev < STAGES.length - 1) {
          return prev + 1;
        }
        return 0;
      });
    }, 1500);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="w-full max-w-6xl mx-auto py-16">

      {/* Header */}
      <div className="text-center mb-14">

        <motion.div
          animate={{ rotate: 360 }}
          transition={{
            repeat: Infinity,
            duration: 10,
            ease: 'linear'
          }}
          className="w-20 h-20 rounded-full bg-gradient-to-r from-violet-500 via-fuchsia-500 to-cyan-500 p-[2px] mx-auto mb-8"
        >
          <div className="w-full h-full bg-[#09090B] rounded-full flex items-center justify-center">
            <Sparkles
              className="text-white"
              size={28}
            />
          </div>
        </motion.div>

        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-sm font-medium mb-6">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          AI Agents Processing Candidates
        </div>

        <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
          AI Evaluation Framework
        </h2>

        <p className="text-slate-400 text-lg max-w-2xl mx-auto">
          Five specialized AI systems collaborate to identify
          high-potential candidates across technical expertise,
          behavioral signals, career growth, and future potential.
        </p>
      </div>

      {/* Agent Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5">

        {STAGES.map((stage, index) => {
          const isActive = index === activeStage;
          const isCompleted = index < activeStage;

          return (
            <motion.div
              key={stage.id}
              whileHover={{
                y: -8,
                scale: 1.02
              }}
              animate={{
                opacity: isActive || isCompleted ? 1 : 0.45,
                scale: isActive ? 1.05 : 1
              }}
              transition={{
                duration: 0.3
              }}
              className="glass-card p-6 text-center relative overflow-hidden"
            >

              {/* Glow */}
              {isActive && (
                <div
                  className="absolute inset-0 opacity-20 blur-3xl"
                  style={{
                    background: stage.color
                  }}
                />
              )}

              {/* Icon */}
              <div
                className="w-16 h-16 rounded-2xl mx-auto mb-5 flex items-center justify-center relative z-10"
                style={{
                  background: `${stage.color}20`,
                  border: `1px solid ${stage.color}40`
                }}
              >
                <stage.icon
                  size={28}
                  color={stage.color}
                />
              </div>

              {/* Title */}
              <h3 className="text-white font-semibold mb-2 relative z-10">
                {stage.title}
              </h3>

              {/* Description */}
              <p className="text-slate-500 text-xs leading-relaxed relative z-10">
                {stage.description}
              </p>

              {/* Progress Bar */}
              <div className="mt-5 h-1.5 rounded-full bg-white/5 overflow-hidden relative z-10">

                <motion.div
                  className="h-full rounded-full"
                  style={{
                    background: stage.color
                  }}
                  initial={{ width: 0 }}
                  animate={{
                    width:
                      isCompleted
                        ? '100%'
                        : isActive
                        ? '100%'
                        : '0%'
                  }}
                  transition={{
                    duration: 0.8
                  }}
                />
              </div>

              {/* Status */}
              <div className="mt-3 text-xs font-medium relative z-10">
                {isCompleted ? (
                  <span className="text-emerald-400">
                    Completed
                  </span>
                ) : isActive ? (
                  <span style={{ color: stage.color }}>
                    Processing...
                  </span>
                ) : (
                  <span className="text-slate-500">
                    Waiting
                  </span>
                )}
              </div>

            </motion.div>
          );
        })}
      </div>

    </div>
  );
}