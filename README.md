# AI Recruiter Platform

Production-ready AI recruitment platform with a restored React frontend, a modular FastAPI backend, and a deterministic offline ranking engine for the Redrob hackathon submission.

The frontend user experience is preserved from the original project. The communication layer was refactored so all screens call a configurable backend base URL through `frontend/src/lib/api.ts`.

## Project Overview

AI Recruiter helps recruiters inspect candidate profiles, analyze a role, rank the most relevant candidates, view pipeline analytics, ask deterministic copilot-style questions, and upload resumes for lightweight parsing.

The project has two execution modes:

- Application mode: React + FastAPI for local product usage.
- Redrob submission mode: CPU-only offline batch ranking that writes the required top-100 CSV.

Ranking uses deterministic feature engineering and weighted scoring. It does not call OpenAI, Gemini, Claude, Anthropic, Cohere, Groq, Together AI, HuggingFace Inference API, or any hosted model service during ranking. The offline batch runner is designed for CPU execution within the 5 minute challenge limit.

## Architecture

```text
AI-Recruiter/
  backend/                         # Production FastAPI application
    app/
      api/routes/                  # HTTP route modules
      core/                        # config, logging, middleware, errors
      repositories/                # dataset access
      schemas/                     # Pydantic request/response models
      services/                    # ranking, analytics, copilot, resume services
  frontend/                        # Restored React/Vite UI
    src/lib/api.ts                 # Backend base URL configuration
  src/                             # Redrob-compliant offline ranking engine
    parser/                        # candidate parser and JD analyzer
    feature_engineering/           # 100+ deterministic engineered features
    scoring/                       # normalized weighted scoring
    ranking/                       # deterministic top-N ranker
    reasoning/                     # template reasoning without hallucination
    validation/                    # honeypot and submission validators
  docs/
    API.md                         # Complete API documentation
    SANDBOX.md                     # Secure sandbox execution strategy
  rank.py                          # Offline CSV generation entrypoint
  Dockerfile                       # No-network Redrob batch runner
  docker-compose.yml               # No-network ranking compose recipe
  docker-compose.app.yml           # Full app compose recipe
```

## Architectural Changes

- Restored the removed React frontend and preserved the existing UI, routes, spacing, styling, and interactions.
- Replaced hardcoded frontend API URLs with `VITE_API_BASE_URL`.
- Replaced the beginner backend with a layered FastAPI application: routes, schemas, services, repository, dependency providers, config, middleware, logging, and structured errors.
- Moved challenge ranking into the required `src/parser`, `src/feature_engineering`, `src/scoring`, `src/ranking`, `src/reasoning`, and `src/validation` architecture.
- Removed legacy `recruiter_brain/` hosted-model and multi-agent code from the executable ranking path.
- Kept Redrob ranking independent from the web app so submission validation cannot be affected by frontend/backend dependencies.
- Added Docker recipes for both the no-network challenge runner and the local product app.
- Added backend tests for health, stats, candidates, analytics, copilot, and resume upload.

## AI Pipeline

```text
Resume or candidate JSONL
  -> parsing
  -> section normalization
  -> JD requirement extraction
  -> deterministic feature engineering
  -> normalized weighted scoring
  -> honeypot and inconsistency penalties
  -> deterministic ranking
  -> template reasoning
  -> frontend display or submission CSV
```

## Recommendation Engine

The engine creates more than 100 deterministic features across:

- production AI and ML systems
- years in AI, product companies, service companies, startup environments, and research
- retrieval, ranking, search, recommendation systems, embeddings, vector databases, and hybrid search
- Python, evaluation metrics, A/B testing, open source, GitHub activity, and project evidence
- recruiter signals, notice period, response rate, activity, location, relocation, and language evidence
- career stability, title progression, education, certifications, and profile completeness
- risk flags for consulting-only, framework-only, title-chasing, CV-only, speech-only, robotics-only, LangChain-only, manager-only, and keyword-stuffed profiles

The scoring engine uses configurable normalized weights, rewards production evidence, penalizes disqualifiers, and applies a honeypot detector for impossible profiles and inconsistent experience claims.

## Model Improvement Notes

The previous recommendation behavior depended on loosely structured matching and legacy AI plumbing. The refactor improves quality by adding:

- section-aware parsing instead of flattening every field into one text blob
- JD analysis for must-have, nice-to-have, reject, culture, behavior, and hiring-intent signals
- normalized weighted scoring so one feature group cannot dominate by raw count
- deterministic tie breaking by candidate ID
- evidence-only reasoning templates with no hallucinated claims
- risk penalties for impossible dates, inconsistent skill durations, fake expertise, and narrow domain-only profiles
- production-system boosts for candidates with deployed retrieval, ranking, search, vector, evaluation, and experimentation experience

No 100 percent accuracy claim is made. The expected improvement is better ranking stability, better explainability, stronger alignment with the Senior AI Engineer JD, and lower false positives from keyword-heavy but weak profiles.

Optional embedding or cross-encoder reranking is not enabled in the Redrob ranking path because the submission specification forbids network use and hosted LLM/API ranking. If local embeddings are added later, they must be precomputed offline and made optional.

## Installation

### Python

Use Python 3.11.

```bash
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

`requirements.txt` is intentionally limited to the allowed offline ranking stack. `backend/requirements.txt` contains FastAPI application dependencies.

### Node

Use Node 20 or newer.

```bash
cd frontend
npm ci
cd ..
```

### Environment Variables

Root `.env.example` documents offline ranking paths. `backend/.env.example` documents API configuration. `frontend/.env.example` contains:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

No API keys are required. Do not add hosted model credentials to the ranking workflow.

### Dataset

The default dataset path is:

```text
[PUB] India_runs_data_and_ai_challenge/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl
```

No database setup is required. The backend loads the JSONL dataset into memory at startup for UI browsing.

### Models, Embeddings, and Vector Database

No model download, embedding download, or vector database setup is required for the default implementation. Ranking is deterministic and local.

## Running

### Backend

```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Open the API docs at:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Open:

```text
http://127.0.0.1:5173
```

### Production Frontend Build

```bash
cd frontend
npm run build
```

### Development Validation

```bash
python -m unittest discover -s tests
cd frontend
npm run lint
npm run build
```

## Redrob Submission Reproduction

Single command to reproduce the required CSV:

```bash
python rank.py --candidates "[PUB] India_runs_data_and_ai_challenge/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl" --jd jd.txt --out redrob_senior_ai_engineer_ranking.csv
```

The generated CSV has exactly:

```csv
candidate_id,rank,score,reasoning
```

with 100 rows, unique ranks, unique candidate IDs, non-increasing scores, and deterministic tie ordering.

## Docker

### No-network Redrob Ranking

```bash
docker compose -f docker-compose.yml up --build ranker
```

`docker-compose.yml` sets `network_mode: "none"` for the ranker service.

### Full Application

```bash
docker compose -f docker-compose.app.yml up --build
```

Backend:

```text
http://127.0.0.1:8000
```

Frontend:

```text
http://127.0.0.1:5173
```

## API Documentation

Complete API documentation is in `docs/API.md`. The backend also exposes OpenAPI docs at `/docs`.

Main endpoints:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Service health and ranking mode |
| GET | `/api/status` | Alias for health |
| GET | `/api/stats` | Candidate dataset statistics |
| GET | `/api/candidates` | Paginated candidate search/filter |
| GET | `/api/candidates/{candidate_id}` | Candidate detail |
| GET | `/api/candidates/role-ranking` | Default Senior AI Engineer ranking |
| GET | `/api/candidates/role-ranking.csv` | Ranking CSV download |
| POST | `/api/rank` | Rank candidates for a supplied JD |
| POST | `/api/rank/role` | Alias for JD ranking |
| GET | `/api/pipeline/analytics` | Pipeline analytics |
| POST | `/api/copilot` | Deterministic copilot answer |
| POST | `/api/resumes/upload` | Resume upload and safe text extraction |

## Sandbox Execution

See `docs/SANDBOX.md` for the full sandbox strategy.

The short version:

- run challenge ranking in the no-network Docker compose service
- mount the dataset read-only where possible
- cap CPU and memory for app containers
- store uploaded resumes in temporary isolated directories
- never execute uploaded files
- delete temporary upload files after parsing
- keep API keys out of the ranking path

## Troubleshooting

### Backend cannot find candidates

Check `AI_RECRUITER_DATASET_PATH` or keep the challenge dataset in the default nested folder.

### Frontend cannot reach backend

Set `frontend/.env`:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Restart Vite after changing env variables.

### Ranking takes time

The ranker scans 100,000 profiles and engineers many features. On CPU it should complete within the 5 minute target on the provided machine.

### Docker app cannot access data

Use `docker-compose.app.yml`; it mounts the challenge dataset directory into `/app/data`.

### CSV validation fails

Run the exact Redrob command above. The CLI validates row count, header, unique IDs, ranks, monotonic scores, tie ordering, and repository compliance before exiting.
