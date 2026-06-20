import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function AnalysisLoading() {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate("/candidates");
    }, 5000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="glass-card p-10 w-[700px]">

        <h1 className="text-4xl font-bold mb-10 text-center">
          AI Analysis Running
        </h1>

        <div className="space-y-6">

          <div className="glass-card p-5">
            ✓ Parsing JD
          </div>

          <div className="glass-card p-5">
            ✓ Generating Embeddings
          </div>

          <div className="glass-card p-5">
            ✓ FAISS Retrieval
          </div>

          <div className="glass-card p-5">
            ✓ Multi-Agent Jury
          </div>

          <div className="glass-card p-5 animate-pulse">
            ⟳ Final Ranking
          </div>

        </div>

      </div>
    </div>
  );
}