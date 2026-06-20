import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Send, Bot } from 'lucide-react';
import axios from 'axios';
import type { Candidate } from '../App';

interface Props {
  candidates: Candidate[];
}

export default function CopilotDock({ candidates }: Props) {
  const [isOpen, setIsOpen] = useState(false);

  const [messages, setMessages] = useState<
    { role: 'user' | 'assistant'; text: string }[]
  >([
    {
      role: 'assistant',
      text: "I'm your Recruiter Copilot. I can explain ranking decisions, compare candidates, identify hidden gems, and recommend the best hires."
    }
  ]);

  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: 'smooth',
    });
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;

    const userMsg = input.trim();

    setMessages(prev => [
      ...prev,
      {
        role: 'user',
        text: userMsg,
      },
    ]);

    setInput('');
    setIsTyping(true);

    try {
      const topCandidates = candidates.slice(
        0,
        Math.min(10, candidates.length)
      );

      const res = await axios.post(
        'http://127.0.0.1:8000/api/copilot',
        {
          question: userMsg,
          candidates: topCandidates,
          totalCandidates: candidates.length,
        }
      );

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          text:
            res.data.answer ||
            'No response received from Copilot.',
        },
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          text: 'Unable to connect to the Intelligence Engine.',
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{
              opacity: 0,
              y: 20,
              scale: 0.95,
            }}
            animate={{
              opacity: 1,
              y: 0,
              scale: 1,
            }}
            exit={{
              opacity: 0,
              y: 20,
              scale: 0.95,
            }}
            className="glass-card w-[380px] mb-4 overflow-hidden flex flex-col border border-violet-500/10 shadow-[0_20px_60px_rgba(139,92,246,0.15)]"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-violet-600 via-fuchsia-600 to-cyan-500 p-4 text-white flex justify-between items-center">
              <div className="flex items-center gap-2 font-semibold">
                <Bot size={18} />
                Recruiter Copilot
              </div>

              <button
                onClick={() => setIsOpen(false)}
                className="hover:bg-white/10 p-1 rounded-md transition-colors"
              >
                <X size={16} />
              </button>
            </div>

            {/* Messages */}
            <div className="h-[350px] overflow-y-auto p-4 bg-[#09090B] space-y-4">
              {messages.map((m, i) => (
                <div
                  key={i}
                  className={`flex ${
                    m.role === 'user'
                      ? 'justify-end'
                      : 'justify-start'
                  }`}
                >
                  <div
                    className={`max-w-[85%] p-3 rounded-xl text-sm ${
                      m.role === 'user'
                        ? 'bg-gradient-to-r from-violet-600 to-cyan-500 text-white rounded-br-sm'
                        : 'bg-white/5 border border-white/10 text-slate-300 rounded-bl-sm'
                    }`}
                  >
                    {m.text}
                  </div>
                </div>
              ))}

              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-white/5 border border-white/10 p-3 rounded-xl rounded-bl-sm flex gap-1">
                    <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></span>

                    <span
                      className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                      style={{
                        animationDelay: '0.2s',
                      }}
                    ></span>

                    <span
                      className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                      style={{
                        animationDelay: '0.4s',
                      }}
                    ></span>
                  </div>
                </div>
              )}

              <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div className="p-3 bg-[#09090B] border-t border-white/10">
              <div className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-xl p-1 pr-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) =>
                    setInput(e.target.value)
                  }
                  onKeyDown={(e) =>
                    e.key === 'Enter' &&
                    handleSend()
                  }
                  placeholder="Ask about the ranking..."
                  className="flex-1 bg-transparent p-2 text-sm text-white placeholder-slate-500 focus:outline-none"
                />

                <button
                  onClick={handleSend}
                  disabled={
                    isTyping || !input.trim()
                  }
                  className="p-2 bg-violet-600 text-white rounded-lg disabled:bg-slate-500 hover:bg-violet-500 transition-colors"
                >
                  <Send size={14} />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="w-14 h-14 bg-gradient-to-r from-violet-600 via-fuchsia-600 to-cyan-500 text-white rounded-full shadow-[0_0_30px_rgba(139,92,246,0.5)] flex items-center justify-center transition-all hover:scale-110 active:scale-95"
        >
          <Bot size={24} />
        </button>
      )}
    </div>
  );
}