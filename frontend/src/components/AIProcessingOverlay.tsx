import { motion, AnimatePresence } from 'framer-motion';
import {
  FileText, Brain, Target, Shield, Sparkles,
  CheckCircle, Loader2
} from 'lucide-react';

const pipelineSteps = [
  { label: 'Parsing JD', desc: 'Extracting skills, traits, anti-patterns', icon: FileText, pct: 20 },
  { label: 'Generating Embeddings', desc: 'Encoding JD into vector space', icon: Brain, pct: 40 },
  { label: 'FAISS Retrieval', desc: 'Semantic search across candidates', icon: Target, pct: 60 },
  { label: 'Multi-Agent Jury', desc: '5-agent scoring & reasoning', icon: Shield, pct: 80 },
  { label: 'Final Ranking', desc: 'Weighted synthesis & ranking', icon: Sparkles, pct: 100 },
];

interface AIProcessingOverlayProps {
  isVisible: boolean;
  currentStep: number;
  totalCandidates?: number;
  isComplete: boolean;
}

// Floating particle component
function Particle({ delay, x, y, size }: { delay: number; x: number; y: number; size: number }) {
  return (
    <motion.div
      className="absolute rounded-full bg-violet-500/30"
      style={{ width: size, height: size, left: `${x}%`, top: `${y}%` }}
      initial={{ opacity: 0, scale: 0 }}
      animate={{
        opacity: [0, 0.6, 0],
        scale: [0, 1.2, 0],
        y: [0, -80, -160],
      }}
      transition={{
        duration: 4,
        delay,
        repeat: Infinity,
        ease: 'easeOut',
      }}
    />
  );
}

export default function AIProcessingOverlay({
  isVisible,
  currentStep,
  totalCandidates = 0,
  isComplete,
}: AIProcessingOverlayProps) {
  const progressPct = isComplete
    ? 100
    : currentStep >= 0
    ? pipelineSteps[Math.min(currentStep, pipelineSteps.length - 1)].pct
    : 0;

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className="fixed inset-0 z-[100] flex items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.4 }}
        >
          {/* Dark backdrop with blur */}
          <div className="absolute inset-0 bg-[#09090B]/90 backdrop-blur-2xl" />

          {/* Animated gradient glow orbs */}
          <motion.div
            className="absolute w-[600px] h-[600px] rounded-full bg-violet-600/20 blur-[120px]"
            animate={{
              x: [0, 60, -30, 0],
              y: [0, -40, 30, 0],
              scale: [1, 1.15, 0.95, 1],
            }}
            transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
            style={{ top: '10%', left: '20%' }}
          />
          <motion.div
            className="absolute w-[500px] h-[500px] rounded-full bg-cyan-500/15 blur-[120px]"
            animate={{
              x: [0, -50, 40, 0],
              y: [0, 50, -30, 0],
              scale: [1, 0.9, 1.1, 1],
            }}
            transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }}
            style={{ bottom: '10%', right: '15%' }}
          />
          <motion.div
            className="absolute w-[400px] h-[400px] rounded-full bg-fuchsia-500/10 blur-[100px]"
            animate={{
              x: [0, 30, -50, 0],
              y: [0, -60, 20, 0],
            }}
            transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut' }}
            style={{ top: '40%', right: '30%' }}
          />

          {/* Floating particles */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            {Array.from({ length: 20 }).map((_, i) => (
              <Particle
                key={i}
                delay={i * 0.5}
                x={10 + (i * 37) % 80}
                y={20 + (i * 53) % 60}
                size={2 + (i % 4) * 2}
              />
            ))}
          </div>

          {/* Central content */}
          <motion.div
            className="relative z-10 w-full max-w-xl mx-4"
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          >
            <AnimatePresence mode="wait">
              {!isComplete ? (
                <motion.div
                  key="processing"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.3 }}
                >
                  {/* AI Brain animation */}
                  <div className="flex justify-center mb-8">
                    <div className="relative w-24 h-24">
                      {/* Outer ring */}
                      <motion.div
                        className="absolute inset-0 rounded-full border-2 border-violet-500/30"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
                      />
                      {/* Middle ring */}
                      <motion.div
                        className="absolute inset-2 rounded-full border-2 border-cyan-500/30"
                        animate={{ rotate: -360 }}
                        transition={{ duration: 6, repeat: Infinity, ease: 'linear' }}
                      />
                      {/* Inner ring */}
                      <motion.div
                        className="absolute inset-4 rounded-full border-2 border-fuchsia-500/30"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
                      />
                      {/* Center brain */}
                      <div className="absolute inset-0 flex items-center justify-center">
                        <motion.div
                          animate={{ scale: [1, 1.1, 1] }}
                          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                        >
                          <Brain size={32} className="text-violet-400" />
                        </motion.div>
                      </div>
                      {/* Glow behind brain */}
                      <div className="absolute inset-0 flex items-center justify-center">
                        <motion.div
                          className="w-12 h-12 rounded-full bg-violet-500/20 blur-xl"
                          animate={{ scale: [1, 1.5, 1], opacity: [0.3, 0.6, 0.3] }}
                          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Title */}
                  <div className="text-center mb-8">
                    <h2 className="text-2xl font-bold text-white mb-2">AI Analysis in Progress</h2>
                    <p className="text-sm text-slate-500">Multi-agent intelligence pipeline is evaluating candidates</p>
                  </div>

                  {/* Glass panel with pipeline stages */}
                  <div className="glass-card p-6 border border-violet-500/10">
                    <div className="space-y-3 mb-6">
                      {pipelineSteps.map((step, i) => {
                        const Icon = step.icon;
                        const isActive = i === currentStep;
                        const isDone = i < currentStep;

                        return (
                          <motion.div
                            key={i}
                            className={`flex items-center gap-3 p-3 rounded-xl transition-all ${
                              isActive
                                ? 'bg-violet-500/10 border border-violet-500/20'
                                : isDone
                                ? 'bg-emerald-500/5 border border-emerald-500/10'
                                : 'bg-white/[0.02] border border-transparent opacity-40'
                            }`}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{
                              opacity: isActive || isDone ? 1 : 0.4,
                              x: 0,
                            }}
                            transition={{ delay: i * 0.1, duration: 0.3 }}
                          >
                            {/* Step icon */}
                            <div
                              className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                                isDone
                                  ? 'bg-emerald-500/20 text-emerald-400'
                                  : isActive
                                  ? 'bg-violet-500/20 text-violet-400'
                                  : 'bg-white/5 text-slate-600'
                              }`}
                            >
                              {isDone ? (
                                <motion.div
                                  initial={{ scale: 0, rotate: -90 }}
                                  animate={{ scale: 1, rotate: 0 }}
                                  transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                                >
                                  <CheckCircle size={18} />
                                </motion.div>
                              ) : isActive ? (
                                <motion.div
                                  animate={{ scale: [1, 1.15, 1] }}
                                  transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
                                >
                                  <Loader2 size={18} className="animate-spin" />
                                </motion.div>
                              ) : (
                                <Icon size={18} />
                              )}
                            </div>

                            {/* Step text */}
                            <div className="flex-1 min-w-0">
                              <div
                                className={`text-sm font-semibold ${
                                  isDone
                                    ? 'text-emerald-400'
                                    : isActive
                                    ? 'text-white'
                                    : 'text-slate-600'
                                }`}
                              >
                                {step.label}
                              </div>
                              <div className="text-xs text-slate-600">{step.desc}</div>
                            </div>

                            {/* Status indicator */}
                            <div className="shrink-0">
                              {isDone && (
                                <span className="text-[10px] font-semibold text-emerald-400 uppercase">Done</span>
                              )}
                              {isActive && (
                                <motion.span
                                  className="text-[10px] font-semibold text-violet-400 uppercase"
                                  animate={{ opacity: [1, 0.4, 1] }}
                                  transition={{ duration: 1.5, repeat: Infinity }}
                                >
                                  Running
                                </motion.span>
                              )}
                            </div>
                          </motion.div>
                        );
                      })}
                    </div>

                    {/* Progress bar */}
                    <div className="mb-3">
                      <div className="flex justify-between text-xs mb-2">
                        <span className="text-slate-500 font-medium">Pipeline Progress</span>
                        <motion.span
                          className="text-violet-400 font-bold"
                          key={progressPct}
                          initial={{ scale: 1.3 }}
                          animate={{ scale: 1 }}
                        >
                          {progressPct}%
                        </motion.span>
                      </div>
                      <div className="h-2 rounded-full bg-white/[0.06] overflow-hidden">
                        <motion.div
                          className="h-full rounded-full bg-gradient-to-r from-violet-500 via-fuchsia-500 to-cyan-500"
                          initial={{ width: 0 }}
                          animate={{ width: `${progressPct}%` }}
                          transition={{ duration: 0.8, ease: 'easeOut' }}
                        />
                      </div>
                    </div>

                    {/* Estimated time */}
                    <div className="text-center text-[10px] text-slate-600">
                      Analyzing your job description with 5 specialized AI agents...
                    </div>
                  </div>
                </motion.div>
              ) : (
                /* ─── Completion Screen ─── */
                <motion.div
                  key="complete"
                  className="text-center"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                >
                  {/* Animated checkmark */}
                  <motion.div
                    className="mx-auto w-24 h-24 rounded-full bg-emerald-500/20 flex items-center justify-center mb-6 relative"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: 'spring', stiffness: 200, damping: 15, delay: 0.1 }}
                  >
                    <motion.div
                      initial={{ scale: 0, rotate: -180 }}
                      animate={{ scale: 1, rotate: 0 }}
                      transition={{ type: 'spring', stiffness: 200, damping: 15, delay: 0.3 }}
                    >
                      <CheckCircle size={48} className="text-emerald-400" />
                    </motion.div>
                    {/* Success glow */}
                    <motion.div
                      className="absolute inset-0 rounded-full bg-emerald-500/20 blur-xl"
                      initial={{ scale: 0 }}
                      animate={{ scale: [1, 1.5, 1.2] }}
                      transition={{ duration: 1, delay: 0.4 }}
                    />
                  </motion.div>

                  <motion.h2
                    className="text-3xl font-black text-white mb-3"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                  >
                    Analysis Complete
                  </motion.h2>

                  <motion.p
                    className="text-lg text-emerald-400 font-semibold mb-2"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 }}
                  >
                    {totalCandidates} Candidates Ranked Successfully
                  </motion.p>

                  <motion.p
                    className="text-sm text-slate-500"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.8 }}
                  >
                    Transitioning to results...
                  </motion.p>

                  {/* Animated loading dots */}
                  <motion.div
                    className="flex justify-center gap-1.5 mt-4"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.9 }}
                  >
                    {[0, 1, 2].map(i => (
                      <motion.div
                        key={i}
                        className="w-2 h-2 rounded-full bg-emerald-400"
                        animate={{ opacity: [0.3, 1, 0.3], scale: [0.8, 1.2, 0.8] }}
                        transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
                      />
                    ))}
                  </motion.div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
