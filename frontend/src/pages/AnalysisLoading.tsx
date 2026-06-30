import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { CheckCircle2, LoaderCircle } from "lucide-react";

export default function AnalysisLoading() {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate("/candidates");
    }, 5000);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="glass-card p-10 w-[700px]">

        <h1 className="text-4xl font-bold mb-10 text-center">
          AI Analysis Running
        </h1>

        <div className="space-y-6">

          <div className="glass-card p-5">
            <div className="flex items-center gap-3"><CheckCircle2 size={18} className="text-white" /> Parsing JD</div>
          </div>

          <div className="glass-card p-5">
            <div className="flex items-center gap-3"><CheckCircle2 size={18} className="text-white" /> Generating Embeddings</div>
          </div>

          <div className="glass-card p-5">
            <div className="flex items-center gap-3"><CheckCircle2 size={18} className="text-white" /> FAISS Retrieval</div>
          </div>

          <div className="glass-card p-5">
            <div className="flex items-center gap-3"><CheckCircle2 size={18} className="text-white" /> Multi-Agent Jury</div>
          </div>

          <div className="glass-card p-5 animate-pulse">
            <div className="flex items-center gap-3"><LoaderCircle size={18} className="text-zinc-200 animate-spin" /> Final Ranking</div>
          </div>

        </div>

      </div>
    </div>
  );
}
