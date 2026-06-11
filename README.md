# AI Recruiter Brain 🧠

**Multi-Agent Recruitment Intelligence System**

A production-grade AI recruitment ranking system that scores candidates the way an elite recruiter would — not through keyword matching. Uses a 6-agent architecture that evaluates candidates across technical fit, career trajectory, behavioral signals, skill transfer potential, and LLM-based recruiter reasoning.

---

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │        Streamlit Dashboard           │
                    │  JD Upload │ Rankings │ Explainability│
                    └──────────────────┬──────────────────┘
                                       │
                              ┌────────▼────────┐
                              │   FastAPI API    │
                              └────────┬────────┘
                                       │
                         ┌─────────────▼──────────────┐
                         │   Hybrid Ranking Engine     │
                         │  4-Stage Candidate Funnel   │
                         └─────────────┬──────────────┘
                                       │
            ┌──────┬───────┬───────────┼───────┬───────┬──────┐
            ▼      ▼       ▼           ▼       ▼       ▼      │
         Agent1  Agent2  Agent3     Agent4  Agent5  Agent6     │
          Role   Tech    Career    Behav.  Potent. Recruiter   │
          Parse   Fit    Intel.    Intel.   Graph   LLM Eval   │
            │      │       │         │       │       │         │
            │   ┌──▼──┐    │         │    ┌──▼──┐    │         │
            │   │Qdrant│   │         │    │Graph│    │         │
            │   │Vector│   │         │    │ DB  │    │         │
            │   └──────┘   │         │    └─────┘    │         │
            └──────┴───────┴─────────┴───────┴───────┘         │
                                                               │
                    ┌──────────────────────────────────────────┘
                    │  Explainability Engine
                    │  Strengths · Risks · Missing Skills · Growth
                    └──────────────────────────────────────────
```

## 4-Stage Pipeline

| Stage | Operation | Candidates | Agents |
|-------|-----------|------------|--------|
| 1 | Embedding Retrieval | 100,000 → 2,000 | Agent 2 (vector search) |
| 2 | Hybrid Multi-Agent Scoring | 2,000 → 500 | Agents 2, 3, 4, 5 |
| 3 | LLM Recruiter Reasoning | 500 → 200 | Agent 6 (GPT-4.1) |
| 4 | Final Weighted Ranking | 200 → **Top 25** | All agents combined |

## Agents

| # | Agent | Function | Score |
|---|-------|----------|-------|
| 1 | **Role Understanding** | Extracts structured requirements from JD | Parsed JD |
| 2 | **Technical Capability** | Embedding similarity + skill overlap | `technical_fit_score` |
| 3 | **Career Intelligence** | Progression, company quality, stability | `career_fit_score` |
| 4 | **Behavioral Intelligence** | Platform engagement, response rates | `behavioral_fit_score` |
| 5 | **Potential Intelligence** | Skill transfer graph, adjacent skills | `potential_score` |
| 6 | **Recruiter Reasoning** | LLM holistic evaluation | `recruiter_reasoning_score` |

### Final Score Formula

```
final_score = 0.35 × technical + 0.20 × career + 0.15 × behavioral
            + 0.15 × potential + 0.15 × recruiter
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- (Optional) Docker & Docker Compose
- (Optional) OpenAI API key for LLM agents

### 1. Local Development

```bash
# Clone and enter project
cd "AI Recruiter"

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Copy environment config
copy .env.example .env
# Edit .env with your API keys (optional — simulation mode works without them)

# Generate synthetic dataset (100K candidates)
python -m recruiter_brain.data.generate_synthetic_data -n 1000

# Run the pipeline (CLI)
python -m recruiter_brain.scoring.ranking_engine -n 1000

# Start the API server
uvicorn recruiter_brain.api.main:app --reload --port 8000

# Start the Streamlit dashboard (separate terminal)
streamlit run recruiter_brain/ui/streamlit_app.py
```

### 2. Docker Deployment

```bash
# Copy environment config
copy .env.example .env

# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Access:
# - API: http://localhost:8000
# - Dashboard: http://localhost:8501
# - Qdrant: http://localhost:6333/dashboard
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/rank` | Submit JD, run full pipeline, return ranked candidates |
| `POST` | `/api/jd/parse` | Parse JD only (Agent 1) |
| `GET` | `/api/candidates/{id}` | Get candidate detail with scores |
| `GET` | `/api/candidates/{id}/explain` | Get explainability report |
| `GET` | `/api/status` | Health check |
| `GET` | `/api/pipeline/status` | Pipeline execution status |
| `GET` | `/api/rankings` | Get last ranking results |

### Example: Rank Candidates

```bash
curl -X POST http://localhost:8000/api/rank \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Senior ML Engineer with 5+ years Python, PyTorch...",
    "job_title": "Senior ML Engineer",
    "top_k": 25
  }'
```

---

## Configuration

All settings are configurable via `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `openai` | LLM provider (`openai` or `deepseek`) |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `SIMULATION_MODE` | `true` | Run without API keys |
| `EMBEDDING_MODEL` | `BAAI/bge-large-en-v1.5` | Embedding model |
| `QDRANT_USE_INMEMORY` | `true` | Use in-memory Qdrant |
| `STAGE1_TOP_K` | `2000` | Stage 1 retrieval count |
| `WEIGHT_TECHNICAL` | `0.35` | Technical score weight |

---

## Project Structure

```
recruiter_brain/
├── __init__.py
├── config.py                  # Central configuration
├── data/
│   ├── models.py              # Pydantic data models
│   └── generate_synthetic_data.py  # 100K candidate generator
├── agents/
│   ├── role_agent.py          # Agent 1: JD Parser
│   ├── technical_agent.py     # Agent 2: Embedding + Skill Match
│   ├── career_agent.py        # Agent 3: Career Trajectory
│   ├── behavior_agent.py      # Agent 4: Behavioral Signals
│   ├── potential_agent.py     # Agent 5: Skill Transfer Graph
│   └── recruiter_agent.py     # Agent 6: LLM Reasoning
├── embeddings/
│   ├── embedding_service.py   # Sentence-transformers wrapper
│   └── vector_store.py        # Qdrant integration
├── scoring/
│   ├── feature_engineering.py # Score normalization
│   ├── ranking_engine.py      # 4-stage pipeline orchestrator
│   └── explainability.py      # Human-readable explanations
├── api/
│   └── main.py                # FastAPI endpoints
├── ui/
│   └── streamlit_app.py       # Dashboard (5 pages)
└── tests/
    ├── test_agents.py
    ├── test_ranking.py
    └── test_vector_store.py

Dockerfile
docker-compose.yml
requirements.txt
.env.example
README.md
```

---

## Testing

```bash
# Run all tests
python -m pytest recruiter_brain/tests/ -v

# Run specific test
python -m pytest recruiter_brain/tests/test_agents.py -v

# Run with coverage
python -m pytest recruiter_brain/tests/ -v --cov=recruiter_brain
```

---

## Key Differentiator: Skill Transfer Graph (Agent 5)

Unlike keyword matching, Agent 5 builds a directed graph of ~200 skill transfer edges:

```
Python → Machine Learning → Deep Learning → NLP → LLM Engineering
Spark → Data Engineering → ML Pipelines → AI Engineering
Docker → Kubernetes → Platform Engineering → SRE
React → Next.js → Full Stack
```

A candidate with **Python + Deep Learning** but not **LLM Engineering** still gets partial credit because the graph shows a clear transfer path. This captures the way real recruiters think about talent potential.

---

## Evaluation Metrics

- **Pipeline Throughput**: Processing time per stage
- **Score Distribution**: Verify scores are well-distributed
- **Ranking Stability**: Same JD → same ranking (deterministic)
- **NDCG@25**: Against relevance labels (when available)
- **Agent Agreement**: Cross-agent score correlation

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Embedding Model | BAAI/bge-large-en-v1.5 (1024-dim) |
| Vector Database | Qdrant |
| LLM | GPT-4.1 / DeepSeek V3 |
| Skill Graph | NetworkX |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit + Plotly |
| Data Validation | Pydantic |
| Containerization | Docker + Docker Compose |

---

## License

MIT
