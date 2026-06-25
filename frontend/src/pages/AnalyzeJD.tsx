import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import {
  Loader2, Zap, FileText, Brain, Target,
  Sparkles, Clock, Clipboard, RotateCcw
} from 'lucide-react';
import type { Candidate, ParsedJD, PipelineStats } from '../App';
import CandidateList from '../components/CandidateList';
import CandidateDetail from '../components/CandidateDetail';
import AIProcessingOverlay from '../components/AIProcessingOverlay';

const API = 'http://127.0.0.1:8000';
const ANALYZE_RESULTS_STORAGE_KEY = 'analyze-jd-results';

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

  useEffect(() => {
    const savedResults = sessionStorage.getItem(ANALYZE_RESULTS_STORAGE_KEY);
    if (!savedResults) return;

    try {
      const parsed = JSON.parse(savedResults) as {
        candidates: Candidate[];
        parsedJD: ParsedJD | null;
        pipelineStats: PipelineStats | null;
        selectedCandidateId: string | null;
      };

      setCandidates(parsed.candidates ?? []);
      setParsedJD(parsed.parsedJD ?? null);
      setPipelineStats(parsed.pipelineStats ?? null);

      if (parsed.selectedCandidateId) {
        const restoredCandidate = parsed.candidates?.find(
          (candidate) => candidate.candidate_id === parsed.selectedCandidateId,
        );
        setSelectedCandidate(restoredCandidate ?? parsed.candidates?.[0] ?? null);
      } else {
        setSelectedCandidate(parsed.candidates?.[0] ?? null);
      }
    } catch (error) {
      console.error('Failed to restore Analyze JD results', error);
      sessionStorage.removeItem(ANALYZE_RESULTS_STORAGE_KEY);
    }
  }, []);

  useEffect(() => {
    if (candidates.length === 0) return;

    sessionStorage.setItem(
      ANALYZE_RESULTS_STORAGE_KEY,
      JSON.stringify({
        candidates,
        parsedJD,
        pipelineStats,
        selectedCandidateId: selectedCandidate?.candidate_id ?? null,
      }),
    );
  }, [candidates, parsedJD, pipelineStats, selectedCandidate]);

  const resetAnalysis = () => {
    setJdText('');
    setCandidates([]);
    setSelectedCandidate(null);
    setParsedJD(null);
    setPipelineStats(null);
    setCurrentStep(-1);
    setShowOverlay(false);
    setOverlayComplete(false);
    setIsSearching(false);
    sessionStorage.removeItem(ANALYZE_RESULTS_STORAGE_KEY);

    window.requestAnimationFrame(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      textareaRef.current?.focus();
    });
  };

  const handleAnalyze = async () => {
    if (!jdText.trim()) return;
    setIsSearching(true);
    resetAnalysis();
    setShowOverlay(true);
    setOverlayComplete(false);

    for (let i = 0; i < 5; i++) {
      setCurrentStep(i);
      await new Promise((r) => setTimeout(r, i === 3 ? 600 : 400));
    }

    try {
      const res = await axios.post(`${API}/api/rank`, {
        job_description: jdText,
      });

      setOverlayComplete(true);
      setCandidates(res.data.ranked_candidates);
      setParsedJD(res.data.parsed_jd);
      setPipelineStats(res.data.pipeline_stats);
      if (res.data.ranked_candidates.length > 0) {
        setSelectedCandidate(res.data.ranked_candidates[0]);
      }

      await new Promise((r) => setTimeout(r, 2200));
      setShowOverlay(false);
      setOverlayComplete(false);

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
    <div className="relative z-10 flex h-full min-h-0 w-full flex-col overflow-hidden">
      <AIProcessingOverlay
        isVisible={showOverlay}
        currentStep={currentStep}
        totalCandidates={candidates.length}
        isComplete={overlayComplete}
      />

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
                <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass text-xs font-medium text-[var(--color-text-secondary)] mb-4">
                  <FileText size={14} />
                  Intelligent JD Analysis
                </div>
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--color-button-soft)] border border-[var(--color-border-subtle)] text-[var(--color-button-soft-text)] text-sm font-medium mb-6 shadow-[0_8px_20px_var(--color-shadow-soft)]">
                  AI Recruiting Intelligence
                </div>

                <h1 className="text-5xl font-black tracking-tight text-[var(--color-text-primary)] mb-4">
                  Analyze Any Job Description
                </h1>

                <p className="text-[var(--color-text-secondary)] text-lg max-w-2xl mx-auto">
                  Extract skills, evaluate requirements, and discover the
                  best candidates using a multi-agent AI evaluation system.
                </p>
                <p className="text-[var(--color-text-tertiary)] text-sm">
                  Our 5-agent jury will parse requirements, search semantically, and rank candidates
                </p>
              </div>

              <div className="grid md:grid-cols-3 gap-4 mb-8">
                <div className="glass-card p-4 text-center">
                  <Brain className="mx-auto mb-2 text-[#8b72bd]" />
                  <div className="font-semibold text-[var(--color-text-primary)]">5 AI Agents</div>
                  <div className="text-xs text-[var(--color-text-tertiary)]">Multi-dimensional evaluation</div>
                </div>

                <div className="glass-card p-4 text-center">
                  <Target className="mx-auto mb-2 text-[#0f766e]" />
                  <div className="font-semibold text-[var(--color-text-primary)]">Semantic Search</div>
                  <div className="text-xs text-[var(--color-text-tertiary)]">Beyond keyword matching</div>
                </div>

                <div className="glass-card p-4 text-center">
                  <Sparkles className="mx-auto mb-2 text-[#b15c3e]" />
                  <div className="font-semibold text-[var(--color-text-primary)]">Hidden Talent</div>
                  <div className="text-xs text-[var(--color-text-tertiary)]">Discover overlooked candidates</div>
                </div>
              </div>

              <div className="glass-card p-2 mb-6 border border-[#b15c3e]/10">
                <textarea
                  ref={textareaRef}
                  className="w-full h-64 p-6 bg-transparent text-[var(--color-text-primary)] rounded-2xl resize-none focus:outline-none placeholder:text-[var(--color-text-tertiary)] font-mono text-sm leading-relaxed"
                  placeholder={"Paste your full job description here...\n\nThe AI will extract: required skills, experience level, location, hidden traits, and anti-patterns from the text."}
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                />
              </div>

              <div className="flex items-center justify-between">
                <button
                  onClick={fillSample}
                  className="flex items-center gap-2 text-xs text-[var(--color-text-tertiary)] hover:text-[var(--color-accent-blue)] transition-colors"
                >
                  <Clipboard size={14} />
                  Load sample JD (Senior AI Engineer)
                </button>
                <button
                  onClick={handleAnalyze}
                  disabled={isSearching || !jdText.trim()}
                  className="metal-button px-8 py-3 rounded-xl font-semibold transition-all flex items-center gap-2"
                >
                  {isSearching ? <Loader2 size={18} className="animate-spin" /> : <Zap size={18} />}
                  Analyze & Rank
                </button>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="results"
            ref={resultsRef}
            className="h-[calc(100vh-5rem)] overflow-hidden p-4 md:p-5"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="h-full min-h-0 rounded-[28px] border border-[var(--color-border-subtle)] bg-[var(--color-surface-soft)] shadow-[0_20px_50px_var(--color-shadow-soft)] overflow-hidden backdrop-blur-sm">
              <div className="flex h-full min-h-0 overflow-hidden">
                <div className="w-[350px] h-full min-h-0 flex flex-col shrink-0 overflow-hidden bg-[linear-gradient(180deg,var(--color-bg-elevated),var(--color-bg-surface))] backdrop-blur-sm">
                  {parsedJD && (
                    <div className="p-4 border-b border-[var(--color-border-subtle)] shrink-0">
                      <div className="flex items-center justify-between mb-3">
                        <div className="text-xs font-semibold text-[var(--color-text-tertiary)] uppercase tracking-widest">Parsed JD</div>
                        <button
                          type="button"
                          onClick={resetAnalysis}
                          className="inline-flex items-center gap-2.5 rounded-2xl border border-[var(--color-border-subtle)] bg-[var(--color-button-soft)] px-6 py-3 text-base font-semibold text-[var(--color-button-soft-text)] shadow-[0_12px_28px_var(--color-shadow-soft)] transition-colors hover:bg-[var(--color-button-soft-hover)]"
                        >
                          <RotateCcw size={18} />
                          Start Over
                        </button>
                      </div>
                      <div className="flex flex-wrap gap-1.5 mb-2">
                        {parsedJD.skills.slice(0, 8).map((s, i) => (
                          <span key={i} className="px-2 py-0.5 text-[10px] font-medium rounded-md bg-[var(--color-pill-bg)] text-[var(--color-pill-text)] border border-[var(--color-pill-border)]">
                            {s}
                          </span>
                        ))}
                        {parsedJD.skills.length > 8 && (
                          <span className="px-2 py-0.5 text-[10px] font-medium rounded-md bg-[var(--color-pill-bg)] text-[var(--color-text-tertiary)]">
                            +{parsedJD.skills.length - 8} more
                          </span>
                        )}
                      </div>
                      <div className="flex gap-3 text-[10px] text-[var(--color-text-tertiary)]">
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
                              {p}
                            </span>
                          ))}
                        </div>
                      )}
                      {pipelineStats && (
                        <div className="mt-3 flex gap-2 text-[10px]">
                          <span className="px-2 py-0.5 rounded bg-[var(--color-pill-bg)] text-[var(--color-text-tertiary)]">Indexed: {pipelineStats.total_indexed.toLocaleString()}</span>
                          <span className="px-2 py-0.5 rounded bg-[var(--color-pill-bg)] text-[var(--color-text-tertiary)]">Retrieved: {pipelineStats.retrieved}</span>
                          <span className="px-2 py-0.5 rounded bg-[var(--color-button-soft)] text-[var(--color-button-soft-text)] border border-[var(--color-border-subtle)]">Ranked: {pipelineStats.returned}</span>
                        </div>
                      )}
                    </div>
                  )}

                  <CandidateList
                    candidates={candidates}
                    selectedId={selectedCandidate?.candidate_id}
                    onSelect={setSelectedCandidate}
                  />
                </div>

                <div className="w-px shrink-0 bg-gradient-to-b from-transparent via-[var(--color-divider-soft)] to-transparent" />

                <div className="flex-1 h-full min-h-0 overflow-hidden bg-[linear-gradient(180deg,var(--color-bg-elevated),var(--color-bg-surface))]">
                  <div className="h-full min-h-0 overflow-y-auto overscroll-contain">
                    {selectedCandidate && (
                      <CandidateDetail key={selectedCandidate.candidate_id} candidate={selectedCandidate} />
                    )}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
