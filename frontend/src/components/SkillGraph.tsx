import { ReactFlow, Background, useNodesState, useEdgesState } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

export default function SkillGraph({ skills }: { skills: any[] }) {
  // Generate nodes and edges from candidate skills dynamically
  const initialNodes = skills.map((s, i) => ({
    id: `node-${i}`,
    position: { x: (i % 3) * 150 + Math.random() * 50, y: Math.floor(i / 3) * 100 + Math.random() * 50 },
    data: { label: s.name },
    style: { 
      background: 'rgba(99, 102, 241, 0.1)', 
      color: '#fff', 
      border: '1px solid rgba(99, 102, 241, 0.5)',
      borderRadius: '8px',
      fontSize: '12px'
    }
  }));

  const initialEdges = [];
  for (let i = 0; i < skills.length - 1; i++) {
    // Arbitrary connections for visualization (in reality, connect related skills)
    if (Math.random() > 0.5) {
      initialEdges.push({
        id: `e-${i}-${i+1}`,
        source: `node-${i}`,
        target: `node-${i+1}`,
        animated: true,
        style: { stroke: 'rgba(99, 102, 241, 0.5)' }
      });
    }
  }

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div style={{ width: '100%', height: '300px' }} className="rounded-xl overflow-hidden border border-white/10 bg-[#030712]">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        colorMode="dark"
      >
        <Background gap={12} size={1} color="rgba(255,255,255,0.05)" />
      </ReactFlow>
    </div>
  );
}
