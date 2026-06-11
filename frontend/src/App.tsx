import { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Search, Swords } from 'lucide-react';
import axios from 'axios';
import { Canvas } from '@react-three/fiber';
import { Stars, OrbitControls } from '@react-three/drei';

import TalentGalaxy3D from './components/TalentGalaxy3D';
import CandidatePreviewCard from './components/CandidatePreviewCard';
import CandidateNetflixProfile from './components/CandidateNetflixProfile';
import BattleMode from './components/BattleMode';

// We must export Candidate type here
export interface Candidate {
  candidate_id: string;
  score: number;
  skill_match: number;
  experience_match: number;
  semantic_similarity: number;
  location_match: number;
  potential_score: number;
  transferable_matches: number;
  reasoning: string;
  candidate_details?: any;
}

export default function App() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [landscapeCoords, setLandscapeCoords] = useState<any[]>([]);
  
  const [hoveredCandidate, setHoveredCandidate] = useState<Candidate | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  
  const [jdText, setJdText] = useState('');
  const [hasSearched, setHasSearched] = useState(false);
  const [isBattleMode, setIsBattleMode] = useState(false);

  const handleSearch = async () => {
    if (!jdText) return;
    try {
      // Fetch rankings
      const rankRes = await axios.post('http://127.0.0.1:8000/api/rank', { job_description: jdText });
      setCandidates(rankRes.data.ranked_candidates);
      
      // Fetch 3D coordinates for the galaxy
      const landRes = await axios.get('http://127.0.0.1:8000/api/landscape');
      setLandscapeCoords(landRes.data.points);
      
      setHasSearched(true);
    } catch (err) {
      console.error(err);
      alert("AI Brain offline.");
    }
  };

  return (
    <div className="w-screen h-screen bg-[#030712] text-white overflow-hidden relative font-sans">
      
      {/* 3D Cosmic Background & Galaxy */}
      <div className="absolute inset-0 z-0">
        <Canvas camera={{ position: [0, 0, 50], fov: 60 }}>
          <color attach="background" args={['#030712']} />
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} intensity={1} />
          
          <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
          
          {hasSearched && !isBattleMode && (
            <TalentGalaxy3D 
              candidates={candidates} 
              coords={landscapeCoords} 
              onHover={setHoveredCandidate}
              onClick={setSelectedCandidate}
            />
          )}
          
          <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
        </Canvas>
      </div>

      {/* Floating UI Overlay */}
      <div className="absolute inset-0 z-10 pointer-events-none flex flex-col">
        
        {/* Top Search Bar */}
        <div className={`p-6 transition-all duration-1000 ${hasSearched ? 'opacity-100' : 'opacity-100 mt-[30vh]'} pointer-events-auto`}>
          <div className="max-w-2xl mx-auto backdrop-blur-2xl bg-white/5 border border-white/10 rounded-2xl p-2 shadow-2xl flex items-center group relative">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-emerald-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>
            <div className="relative flex w-full">
              <Search className="text-slate-400 m-3" size={20} />
              <input 
                type="text" 
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Find senior AI engineers..." 
                className="w-full bg-transparent p-2 text-lg focus:outline-none text-white placeholder-slate-500"
              />
              <button 
                onClick={handleSearch}
                className="px-6 py-2 bg-indigo-500 hover:bg-indigo-600 rounded-xl font-medium transition-colors"
              >
                Launch
              </button>
            </div>
          </div>
        </div>

        {/* Floating Tools */}
        {hasSearched && (
          <div className="absolute top-6 right-6 pointer-events-auto flex gap-4">
            <button 
              onClick={() => setIsBattleMode(!isBattleMode)}
              className="flex items-center gap-2 px-4 py-2 bg-rose-500/20 border border-rose-500/50 text-rose-300 rounded-xl hover:bg-rose-500/30 transition-all backdrop-blur-md"
            >
              <Swords size={18} /> Battle Mode
            </button>
          </div>
        )}

      </div>

      {/* Interactive 2D Overlays (Pointer Events Auto) */}
      <div className="absolute inset-0 z-20 pointer-events-none">
        <AnimatePresence>
          {hoveredCandidate && !selectedCandidate && (
            <CandidatePreviewCard candidate={hoveredCandidate} />
          )}
        </AnimatePresence>
        
        <AnimatePresence>
          {selectedCandidate && (
            <CandidateNetflixProfile candidate={selectedCandidate} onClose={() => setSelectedCandidate(null)} />
          )}
        </AnimatePresence>

        <AnimatePresence>
          {isBattleMode && (
            <BattleMode candidates={candidates} onClose={() => setIsBattleMode(false)} />
          )}
        </AnimatePresence>
      </div>

    </div>
  );
}
