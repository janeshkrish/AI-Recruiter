import React, { useState } from 'react';
import axios from 'axios';
import CandidateList from '../components/CandidateList';
import CandidateDetail from '../components/CandidateDetail';
import { Loader2 } from 'lucide-react';

export default function AnalyzeJD() {
  const [jdText, setJdText] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [candidates, setCandidates] = useState<any[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<any | null>(null);

  const handleAnalyze = async () => {
    if (!jdText.trim()) return;
    setIsSearching(true);
    try {
      const res = await axios.post('http://127.0.0.1:8000/api/rank', { 
        job_description: jdText,
        custom_weights: {
          skill_match: 1.0,
          experience_match: 1.0,
          semantic_similarity: 1.0,
          education_match: 0.2
        }
      });
      setCandidates(res.data.ranked_candidates);
      if (res.data.ranked_candidates.length > 0) {
        setSelectedCandidate(res.data.ranked_candidates[0]);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to analyze Job Description.");
    } finally {
      setIsSearching(false);
    }
  };
  
  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-[#FAFAFA]">
      <div className="p-8 shrink-0 bg-white border-b border-slate-200">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-2xl font-bold text-slate-800 mb-2">Analyze Job Description</h1>
          <p className="text-slate-500 mb-6">Paste your job description below to extract requirements and automatically rank the best candidates from the entire dataset.</p>
          
          <textarea
            className="w-full h-32 p-4 border border-slate-300 rounded-lg mb-4 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all font-mono text-sm resize-y"
            placeholder="Paste Job Description here..."
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
          />
          
          <div className="flex justify-end">
            <button 
              onClick={handleAnalyze}
              disabled={isSearching || !jdText.trim()}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium shadow-sm transition-colors flex items-center gap-2 disabled:bg-slate-400"
            >
              {isSearching ? <Loader2 size={18} className="animate-spin" /> : null}
              Analyze & Rank Candidates
            </button>
          </div>
        </div>
      </div>

      {/* Results Area */}
      {candidates.length > 0 && (
        <div className="flex-1 flex overflow-hidden">
          <div className="w-[350px] border-r border-slate-200 bg-white flex flex-col z-10 shadow-[2px_0_10px_rgba(0,0,0,0.02)]">
            <CandidateList 
              candidates={candidates} 
              selectedId={selectedCandidate?.candidate_id} 
              onSelect={setSelectedCandidate} 
            />
          </div>
          <div className="flex-1 bg-[#FAFAFA] overflow-y-auto relative">
            {selectedCandidate && (
              <CandidateDetail key={selectedCandidate.candidate_id} candidate={selectedCandidate} />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
