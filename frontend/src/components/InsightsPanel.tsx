import { useState } from 'react';
import {
  Sparkles,
  BrainCircuit,
  MessageSquare,
  TrendingUp,
} from 'lucide-react';
import axios from 'axios';
import type { Candidate } from '../App';
import { motion } from 'framer-motion';
import { API_BASE_URL } from '../lib/api';

export default function InsightsPanel({
  candidates,
}: {
  candidates: Candidate[];
}) {
  const [copilotQuery, setCopilotQuery] = useState('');
  const [copilotResponse, setCopilotResponse] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  if (!candidates.length) return null;

  const hiddenGem = candidates.find(
    c =>
      c.potential_score > 85 &&
      c.experience_match < 60
  );

  const highestProb = [...candidates].sort(
    (a, b) => b.location_match - a.location_match
  )[0];

  const techBeast = [...candidates].sort(
    (a, b) => b.skill_match - a.skill_match
  )[0];

  const askCopilot = async (q: string) => {
    if (!q.trim()) return;

    setIsTyping(true);

    try {
      const res = await axios.post(
        `${API_BASE_URL}/api/copilot`,
        {
          question: q,
          candidates: candidates.slice(0, 5),
        }
      );

      setCopilotResponse(res.data.answer);
    } catch {
      setCopilotResponse(
        'Backend connection unavailable.'
      );
    }

    setIsTyping(false);
    setCopilotQuery('');
  };

  return (
    <div className="space-y-4 sticky top-4">

      {/* Live Insights */}
      <div className="glass-card p-5">
        <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
          <Sparkles
            size={16}
            className="text-violet-400"
          />
          Live Insights
        </h3>

        <div className="space-y-3">

          {hiddenGem && (
            <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl">
              <div className="text-[10px] uppercase tracking-wider text-amber-400 font-bold mb-1 flex items-center gap-1">
                <TrendingUp size={10} />
                Hidden Gem
              </div>

              <div className="text-sm text-amber-200">
                Candidate{' '}
                <b>{hiddenGem.candidate_id}</b> has
                exceptional potential (
                {hiddenGem.potential_score.toFixed(0)})
                despite lower experience alignment.
              </div>
            </div>
          )}

          {highestProb && (
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
              <div className="text-[10px] uppercase tracking-wider text-emerald-400 font-bold mb-1">
                Highest Hiring Probability
              </div>

              <div className="text-sm text-emerald-200">
                Candidate{' '}
                <b>{highestProb.candidate_id}</b> shows
                the strongest hiring readiness.
              </div>
            </div>
          )}

          {techBeast && (
            <div className="p-3 bg-cyan-500/10 border border-cyan-500/20 rounded-xl">
              <div className="text-[10px] uppercase tracking-wider text-cyan-400 font-bold mb-1">
                Technical Beast
              </div>

              <div className="text-sm text-cyan-200">
                Candidate{' '}
                <b>{techBeast.candidate_id}</b> achieves{' '}
                {techBeast.skill_match.toFixed(0)}%
                technical match.
              </div>
            </div>
          )}

        </div>
      </div>

      {/* Recruiter Copilot */}
      <div className="glass-card overflow-hidden flex flex-col h-[420px]">

        <div className="p-4 border-b border-white/5 bg-gradient-to-r from-violet-500/10 to-cyan-500/10 flex items-center gap-2">
          <BrainCircuit
            size={16}
            className="text-violet-400"
          />

          <span className="text-sm font-semibold text-white">
            Recruiter Copilot
          </span>
        </div>

        <div className="flex-1 p-4 overflow-y-auto space-y-4 text-sm">

          <div className="bg-white/5 p-3 rounded-xl border border-white/10 text-slate-300">
            I've analyzed the candidate ranking and
            identified key patterns. Ask me anything
            about the results.
          </div>

          {copilotResponse && (
            <motion.div
              initial={{
                opacity: 0,
                y: 10,
              }}
              animate={{
                opacity: 1,
                y: 0,
              }}
              className="bg-violet-500/10 p-3 rounded-xl border border-violet-500/20 text-violet-200"
            >
              {copilotResponse}
            </motion.div>
          )}

          {isTyping && (
            <div className="text-xs text-slate-500 animate-pulse">
              Copilot is analyzing...
            </div>
          )}

        </div>

        <div className="p-3 border-t border-white/5">

          <div className="flex flex-wrap gap-2 mb-3">

            <button
              onClick={() =>
                askCopilot(
                  'Why is candidate 1 ranked highest?'
                )
              }
              className="text-[10px] px-2 py-1 bg-white/5 rounded border border-white/10 hover:bg-white/10 text-slate-400"
            >
              Why Rank #1?
            </button>

            <button
              onClick={() =>
                askCopilot(
                  'Compare the top 2 candidates'
                )
              }
              className="text-[10px] px-2 py-1 bg-white/5 rounded border border-white/10 hover:bg-white/10 text-slate-400"
            >
              Compare Top 2
            </button>

            <button
              onClick={() =>
                askCopilot(
                  'Are there any hidden gems?'
                )
              }
              className="text-[10px] px-2 py-1 bg-white/5 rounded border border-white/10 hover:bg-white/10 text-slate-400"
            >
              Find Gems
            </button>

          </div>

          <div className="relative">

            <input
              type="text"
              value={copilotQuery}
              onChange={e =>
                setCopilotQuery(e.target.value)
              }
              onKeyDown={e =>
                e.key === 'Enter' &&
                askCopilot(copilotQuery)
              }
              placeholder="Ask the AI Copilot..."
              className="w-full bg-white/5 border border-white/10 rounded-xl pl-3 pr-10 py-2 text-sm focus:outline-none focus:border-violet-500 text-white"
            />

            <button
              onClick={() =>
                askCopilot(copilotQuery)
              }
              className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-violet-400"
            >
              <MessageSquare size={14} />
            </button>

          </div>

        </div>
      </div>
    </div>
  );
}
