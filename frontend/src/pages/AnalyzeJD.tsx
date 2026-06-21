import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import {
  Loader2, Zap, FileText, Brain, Target,
  Sparkles, Clock, Shield, Clipboard
} from 'lucide-react';
import type { Candidate, ParsedJD, PipelineStats } from '../App';
import CandidateList from '../components/CandidateList';
import CandidateDetail from '../components/CandidateDetail';
import AIProcessingOverlay from '../components/AIProcessingOverlay';

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

export default function AnalyzeJD() {
  const [jdText, setJdText] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [parsedJD, setParsedJD] = useState<ParsedJD | null>(null);
  const [pipelineStats, setPipelineStats] = useState<PipelineStats | null>(null);
  const [showOverlay, setShowOverlay] = useState(false);
  const [overlayComplete, setOverlayComplete] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  const handleAnalyze = async () => {
    if (!jdText.trim()) return;
    setIsSearching(true);
    setCandidates([]);
    setSelectedCandidate(null);
    setParsedJD(null);
    setShowOverlay(true);
    setOverlayComplete(false);

    // Animate pipeline steps
    for (let i = 0; i < 5; i++) {
      setCurrentStep(i);
      await new Promise(r => setTimeout(r, i === 3 ? 600 : 400));
    }

    try {
      const res = await axios.post(`${API}/api/rank`, {
        job_description: jdText,
      });

      // Show completion state
      setOverlayComplete(true);
      setCandidates(res.data.ranked_candidates);
      setParsedJD(res.data.parsed_jd);
      setPipelineStats(res.data.pipeline_stats);
      if (res.data.ranked_candidates.length > 0) {
        setSelectedCandidate(res.data.ranked_candidates[0]);
      }

      // Auto-dismiss overlay after success screen shows
      await new Promise(r => setTimeout(r, 2200));
      setShowOverlay(false);
      setOverlayComplete(false);

      // Smooth scroll to results after a short delay
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 300);
    } catch (err) {
      console.error(err);
      setShowOverlay(false);
      setOverlayComplete(false);
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
      {/* Fullscreen AI Processing Overlay */}
      <AIProcessingOverlay
        isVisible={showOverlay}
        currentStep={currentStep}
        totalCandidates={candidates.length}
        isComplete={overlayComplete}
      />

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
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-300 text-sm font-medium mb-6">
   AI Recruiting Intelligence
</div>

<h1 className="text-5xl font-black tracking-tight text-white mb-4">
  Analyze Any Job Description
</h1>

<p className="text-slate-400 text-lg max-w-2xl mx-auto">
  Extract skills, evaluate requirements, and discover the
  best candidates using a multi-agent AI evaluation system.
</p>
                <p className="text-slate-500 text-sm">
                  Our 5-agent jury will parse requirements, search semantically, and rank candidates
                </p>
              </div>
              <div className="grid md:grid-cols-3 gap-4 mb-8">

  <div className="glass-card p-4 text-center">
    <Brain className="mx-auto mb-2 text-violet-400" />
    <div className="font-semibold">5 AI Agents</div>
    <div className="text-xs text-slate-500">
      Multi-dimensional evaluation
    </div>
  </div>

  <div className="glass-card p-4 text-center">
    <Target className="mx-auto mb-2 text-cyan-400" />
    <div className="font-semibold">Semantic Search</div>
    <div className="text-xs text-slate-500">
      Beyond keyword matching
    </div>
  </div>

  <div className="glass-card p-4 text-center">
    <Sparkles className="mx-auto mb-2 text-emerald-400" />
    <div className="font-semibold">Hidden Talent</div>
    <div className="text-xs text-slate-500">
      Discover overlooked candidates
    </div>
  </div>

</div>

             <div className="glass-card p-2 mb-6 border border-violet-500/10">
                <textarea
                  ref={textareaRef}
                  className="
w-full
h-64
p-6
bg-transparent
text-slate-200
rounded-2xl
resize-none
focus:outline-none
placeholder:text-slate-600
font-mono
text-sm
leading-relaxed
"
                  placeholder={"Paste your full job description here...\n\nThe AI will extract: required skills, experience level, location, hidden traits, and anti-patterns from the text."}
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
                  className="px-8 py-3 bg-gradient-to-r from-violet-600 via-fuchsia-600 to-cyan-500 hover:from-violet-500 hover:to-cyan-500 text-white rounded-xl font-semibold shadow-lg shadow-violet-500/25 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSearching ? <Loader2 size={18} className="animate-spin" /> : <Zap size={18} />}
                  Analyze & Rank
                </button>
              </div>
            </div>
          </motion.div>
        ) : (
          /* Results View */
          <motion.div
            key="results"
            ref={resultsRef}
            className="flex-1 flex overflow-hidden"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* Left: Parsed JD + Candidate List */}
            <div className="w-[350px] border-r border-white/[0.06] flex flex-col shrink-0">
              {/* Parsed JD Summary */}
              {parsedJD && (
                <div className="p-4 border-b border-white/[0.06]">
                  <div className="flex items-center justify-between mb-3">
                    <div className="text-xs font-semibold text-slate-400 uppercase tracking-widest">Parsed JD</div>
                    <button
                      onClick={() => { setCandidates([]); setSelectedCandidate(null); setParsedJD(null); }}
                      className="text-xs text-violet-400 hover:text-violet-300 font-medium"
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
