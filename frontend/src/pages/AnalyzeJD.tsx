import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import {
  Loader2, Zap, FileText, CheckCircle, Brain, Target, AlertTriangle,
  Sparkles, ChevronRight, Clock, GitBranch, Shield, Clipboard
} from 'lucide-react';
import type { Candidate, ParsedJD, PipelineStats } from '../App';
import CandidateList from '../components/CandidateList';
import CandidateDetail from '../components/CandidateDetail';

const API = 'http://127.0.0.1:8000';

const SAMPLE_JD = `Job Description: Senior AI Engineer — Founding Team
Company: Redrob AI (Series A AI-native talent intelligence platform)
Location: Pune/Noida, India (Hybrid — flexible cadence) | Open to relocation candidates from Tier-1 Indian cities
Employment Type: Full-time
Experience Required: 5–9 years

We need someone who is simultaneously comfortable with: Deep technical depth in modern ML systems — embeddings, retrieval, ranking, LLMs, fine-tuning. Scrappy product-engineering attitude — willing to ship a working ranker in a week.

Things you absolutely need:
- Production experience with embeddings-based retrieval systems (sentence-transformers, OpenAI embeddings, BGE, E5)
- Production experience with vector databases (Pinecone, Weaviate, Qdrant, Milvus, FAISS)
- Strong Python
- Hands-on experience designing evaluation frameworks for ranking systems — NDCG, MRR, MAP, A/B test interpretation

Things we'd like: LLM fine-tuning experience (LoRA, QLoRA, PEFT), Learning-to-rank models (XGBoost-based)

Things we do NOT want: Title-chasers, Framework enthusiasts, People who have only worked at consulting firms (TCS, Infosys, Wipro, Accenture, Cognizant, Capgemini) in their entire career.`;

const pipelineSteps = [
  { label: 'Parsing JD', desc: 'Extracting skills, traits, anti-patterns', icon: FileText },
  { label: 'Generating Embeddings', desc: 'Encoding JD into vector space', icon: Brain },
  { label: 'FAISS Retrieval', desc: 'Semantic search across candidates', icon: Target },
  { label: 'Multi-Agent Jury', desc: '5-agent scoring & reasoning', icon: Shield },
  { label: 'Final Ranking', desc: 'Weighted synthesis & ranking', icon: Sparkles },
];

export default function AnalyzeJD() {
  const [jdText, setJdText] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [parsedJD, setParsedJD] = useState<ParsedJD | null>(null);
  const [pipelineStats, setPipelineStats] = useState<PipelineStats | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleAnalyze = async () => {
    if (!jdText.trim()) return;
    setIsSearching(true);
    setCandidates([]);
    setSelectedCandidate(null);
    setParsedJD(null);

    // Animate pipeline steps
    for (let i = 0; i < pipelineSteps.length; i++) {
      setCurrentStep(i);
      await new Promise(r => setTimeout(r, i === 3 ? 600 : 400));
    }

    try {
      const res = await axios.post(`${API}/api/rank`, {
        job_description: jdText,
      });
      setCandidates(res.data.ranked_candidates);
      setParsedJD(res.data.parsed_jd);
      setPipelineStats(res.data.pipeline_stats);
      if (res.data.ranked_candidates.length > 0) {
        setSelectedCandidate(res.data.ranked_candidates[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsSearching(false);
      setCurrentStep(-1);
    }
  };

  const fillSample = () => {
    setJdText(SAMPLE_JD);
    if (textareaRef.current) textareaRef.current.focus();
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden relative z-10">
      {/* Top: JD Input */}
      <AnimatePresence mode="wait">
        {candidates.length === 0 ? (
          <motion.div
            key="input"
            className="flex-1 flex flex-col items-center justify-center px-6 py-12"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <div className="w-full max-w-3xl">
              <div className="text-center mb-8">
                <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass text-xs font-medium text-blue-400 mb-4">
                  <FileText size={14} />
                  Intelligent JD Analysis
                </div>
                <h1 className="text-3xl font-bold text-white mb-2">Paste Your Job Description</h1>
                <p className="text-slate-500 text-sm">
                  Our 5-agent jury will parse requirements, search semantically, and rank candidates
                </p>
              </div>

              <div className="glass-card p-1 mb-4">
                <textarea
                  ref={textareaRef}
                  className="w-full h-48 p-5 bg-transparent text-slate-200 rounded-xl resize-y focus:outline-none placeholder:text-slate-600 font-mono text-sm leading-relaxed"
                  placeholder="Paste your full job description here...&#10;&#10;The AI will extract: required skills, experience level, location, hidden traits, and anti-patterns from the text."
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                />
              </div>

              <div className="flex items-center justify-between">
                <button
                  onClick={fillSample}
                  className="flex items-center gap-2 text-xs text-slate-500 hover:text-blue-400 transition-colors"
                >
                  <Clipboard size={14} />
                  Load sample JD (Senior AI Engineer)
                </button>
                <button
                  onClick={handleAnalyze}
                  disabled={isSearching || !jdText.trim()}
                  className="px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl font-semibold shadow-lg shadow-blue-500/25 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSearching ? <Loader2 size={18} className="animate-spin" /> : <Zap size={18} />}
                  Analyze & Rank
                </button>
              </div>

              {/* Pipeline Progress */}
              <AnimatePresence>
                {isSearching && (
                  <motion.div
                    className="mt-8 glass-card p-6"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                  >
                    <div className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-4">
                      Pipeline Progress
                    </div>
                    <div className="space-y-3">
                      {pipelineSteps.map((step, i) => {
                        const Icon = step.icon;
                        const isActive = i === currentStep;
                        const isDone = i < currentStep;
                        return (
                          <motion.div
                            key={i}
                            className={`flex items-center gap-3 p-3 rounded-lg transition-all ${
                              isActive ? 'bg-blue-500/10 border border-blue-500/20' :
                              isDone ? 'bg-emerald-500/5' : 'opacity-40'
                            }`}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: isActive || isDone ? 1 : 0.4, x: 0 }}
                            transition={{ delay: i * 0.1 }}
                          >
                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                              isDone ? 'bg-emerald-500/20 text-emerald-400' :
                              isActive ? 'bg-blue-500/20 text-blue-400' :
                              'bg-white/5 text-slate-600'
                            }`}>
                              {isDone ? <CheckCircle size={16} /> : isActive ? <Loader2 size={16} className="animate-spin" /> : <Icon size={16} />}
                            </div>
                            <div>
                              <div className={`text-sm font-medium ${isDone ? 'text-emerald-400' : isActive ? 'text-white' : 'text-slate-600'}`}>
                                {step.label}
                              </div>
                              <div className="text-xs text-slate-600">{step.desc}</div>
                            </div>
                          </motion.div>
                        );
                      })}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        ) : (
          /* Results View */
          <motion.div
            key="results"
            className="flex-1 flex overflow-hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {/* Left: Parsed JD + Candidate List */}
            <div className="w-[380px] border-r border-white/[0.06] flex flex-col shrink-0">
              {/* Parsed JD Summary */}
              {parsedJD && (
                <div className="p-4 border-b border-white/[0.06]">
                  <div className="flex items-center justify-between mb-3">
                    <div className="text-xs font-semibold text-slate-400 uppercase tracking-widest">Parsed JD</div>
                    <button
                      onClick={() => { setCandidates([]); setSelectedCandidate(null); setParsedJD(null); }}
                      className="text-xs text-blue-400 hover:text-blue-300 font-medium"
                    >
                      New Analysis
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-1.5 mb-2">
                    {parsedJD.skills.slice(0, 8).map((s, i) => (
                      <span key={i} className="px-2 py-0.5 text-[10px] font-medium rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20">
                        {s}
                      </span>
                    ))}
                    {parsedJD.skills.length > 8 && (
                      <span className="px-2 py-0.5 text-[10px] font-medium rounded-md bg-white/5 text-slate-500">
                        +{parsedJD.skills.length - 8} more
                      </span>
                    )}
                  </div>
                  <div className="flex gap-3 text-[10px] text-slate-500">
                    <span className="flex items-center gap-1"><Clock size={10} /> {parsedJD.years_experience}y exp</span>
                    <span className="flex items-center gap-1"><Target size={10} /> {parsedJD.location}</span>
                    {parsedJD.hidden_traits.length > 0 && (
                      <span className="flex items-center gap-1"><Brain size={10} /> {parsedJD.hidden_traits.length} traits</span>
                    )}
                  </div>
                  {parsedJD.anti_patterns.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {parsedJD.anti_patterns.map((p, i) => (
                        <span key={i} className="px-2 py-0.5 text-[10px] font-medium rounded-md bg-rose-500/10 text-rose-400 border border-rose-500/20">
                          ⚠ {p}
                        </span>
                      ))}
                    </div>
                  )}
                  {pipelineStats && (
                    <div className="mt-3 flex gap-2 text-[10px]">
                      <span className="px-2 py-0.5 rounded bg-white/5 text-slate-500">
                        Indexed: {pipelineStats.total_indexed.toLocaleString()}
                      </span>
                      <span className="px-2 py-0.5 rounded bg-white/5 text-slate-500">
                        Retrieved: {pipelineStats.retrieved}
                      </span>
                      <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400">
                        Ranked: {pipelineStats.returned}
                      </span>
                    </div>
                  )}
                </div>
              )}

              {/* Candidate List */}
              <CandidateList
                candidates={candidates}
                selectedId={selectedCandidate?.candidate_id}
                onSelect={setSelectedCandidate}
              />
            </div>

            {/* Right: Candidate Detail */}
            <div className="flex-1 overflow-y-auto">
              {selectedCandidate && (
                <CandidateDetail key={selectedCandidate.candidate_id} candidate={selectedCandidate} />
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
