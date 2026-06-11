import { BrainCircuit, Eye, Code } from 'lucide-react';

export default function JobUnderstandingPanel() {
  // Mock extracted data based on standard JD
  const extracted = {
    mustHaves: ['Python', 'Machine Learning', 'LLMs', 'Vector Databases', 'PyTorch'],
    hiddenTraits: ['Startup-Fit', 'Shipper Mindset', 'Ambiguity Tolerance'],
    exp: '4-8 Years',
    title: 'Senior AI Engineer'
  };

  return (
    <div className="mt-6 bg-[#151A22] border border-[#2A3140] rounded-xl overflow-hidden shadow-xl shadow-black/20">
      <div className="bg-[#1A202C] px-6 py-4 border-b border-[#2A3140] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BrainCircuit size={18} className="text-emerald-400" />
          <h3 className="font-semibold text-white">AI JD Understanding</h3>
        </div>
        <span className="text-xs bg-emerald-400/10 text-emerald-400 px-2 py-1 rounded-full border border-emerald-400/20">
          Extraction Complete
        </span>
      </div>
      
      <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 className="text-sm font-medium text-slate-400 mb-3 flex items-center gap-2">
            <Code size={14}/> Must-Have Skills
          </h4>
          <div className="flex flex-wrap gap-2">
            {extracted.mustHaves.map((skill, i) => (
              <span key={i} className="px-3 py-1 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-md text-xs font-medium">
                {skill}
              </span>
            ))}
          </div>
        </div>

        <div>
          <h4 className="text-sm font-medium text-slate-400 mb-3 flex items-center gap-2">
            <Eye size={14}/> Hidden Behavioral Traits Detected
          </h4>
          <div className="flex flex-wrap gap-2">
            {extracted.hiddenTraits.map((trait, i) => (
              <span key={i} className="px-3 py-1 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-md text-xs font-medium">
                {trait}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
