import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import type { Group } from 'three';
import type { Candidate } from '../App';

interface Props {
  candidates: Candidate[];
  coords: any[];
  onHover: (c: Candidate | null) => void;
  onClick: (c: Candidate) => void;
}

export default function TalentGalaxy3D({ candidates, coords, onHover, onClick }: Props) {
  const groupRef = useRef<Group>(null);
  
  // Rotate the entire galaxy slowly
  useFrame(() => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.001;
    }
  });

  const getStarColor = (score: number) => {
    if (score >= 90) return '#10B981'; // Emerald
    if (score >= 80) return '#3B82F6'; // Blue
    if (score >= 70) return '#8B5CF6'; // Purple
    return '#F59E0B'; // Amber
  };

  return (
    <group ref={groupRef}>
      {candidates.map((cand) => {
        // Find 3D coordinate from landscape API
        const coord = coords.find(c => c.candidate_id === cand.candidate_id);
        if (!coord) return null;
        
        const size = (cand.potential_score / 100) * 1.5;
        const color = getStarColor(cand.score);
        
        return (
          <mesh 
            key={cand.candidate_id} 
            position={[coord.x, coord.y, coord.z]}
            onPointerOver={(e: any) => {
              e.stopPropagation();
              onHover(cand);
            }}
            onPointerOut={(e: any) => {
              e.stopPropagation();
              onHover(null);
            }}
            onClick={(e: any) => {
              e.stopPropagation();
              onClick(cand);
            }}
          >
            <sphereGeometry args={[size, 16, 16]} />
            <meshStandardMaterial 
              color={color} 
              emissive={color} 
              emissiveIntensity={0.5} 
              roughness={0.2} 
            />
          </mesh>
        );
      })}
    </group>
  );
}
