<p align="center">
  <img src="https://img.shields.io/badge/Team-SOULX-b15c3e?style=for-the-badge&labelColor=1a1a2e" alt="Team SOULX" />
  <img src="https://img.shields.io/badge/Python-3.11-3776ab?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11" />
  <img src="https://img.shields.io/badge/Node.js-20+-339933?style=for-the-badge&logo=node.js&logoColor=white" alt="Node.js 20+" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-19-61dafb?style=for-the-badge&logo=react&logoColor=black" alt="React 19" />
  <img src="https://img.shields.io/badge/Vite-8-646cff?style=for-the-badge&logo=vite&logoColor=white" alt="Vite 8" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ed?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Ready" />
</p>

# 🤖 AI Recruiter — Intelligent Talent Ranking Platform

> **A production-ready AI recruitment platform** that helps recruiters analyze job descriptions, explore candidate datasets, rank the most relevant profiles using 100+ deterministic features, and make data-driven hiring decisions — all without relying on external AI APIs.

Built by **Team SOULX** for the [Redrob India Runs Data & AI Challenge](https://redrob.io).

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Getting Started](#-getting-started)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Backend Setup (Python)](#2-backend-setup-python)
  - [3. Frontend Setup (Node.js)](#3-frontend-setup-nodejs)
  - [4. Environment Configuration](#4-environment-configuration)
  - [5. Run the Application](#5-run-the-application)
- [Offline Ranking (Redrob Submission)](#-offline-ranking-redrob-submission)
- [Docker Deployment](#-docker-deployment)
- [API Reference](#-api-reference)
- [AI Pipeline](#-ai-pipeline)
- [Recommendation Engine](#-recommendation-engine)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Team](#-team)
- [License](#-license)

---

## 🎯 Overview

AI Recruiter is an end-to-end talent intelligence platform with **two execution modes**:

| Mode | Purpose | Network Required? |
|------|---------|:-:|
| **🖥️ Application Mode** | Interactive web app (React + FastAPI) for browsing candidates, analyzing JDs, and exploring rankings | Yes (local only) |
| **📦 Submission Mode** | CPU-only offline batch ranking that produces the required top-100 CSV | ❌ No |

The ranking engine uses **deterministic feature engineering and weighted scoring** — it does **not** call OpenAI, Gemini, Claude, Anthropic, Cohere, Groq, Together AI, HuggingFace Inference API, or any hosted model service during ranking.

---

## ✨ Key Features

### 🏠 Dashboard
- Live dataset statistics with animated counters
- Quick navigation to all platform modules
- Dark/light theme with persistent preference

### 📊 Dataset Explorer
- Paginated browsing of 100K+ candidate profiles
- Search by name, skills, or company
- Filter by skills, minimum experience, and current role
- Autocomplete suggestions from dataset

### 🎯 JD Analyzer
- Paste any job description and get AI-ranked candidates
- Real-time processing overlay with pipeline visualization
- Score breakdown: skill match, experience, semantic similarity, behavioral signals
- Download ranked results as CSV

### 🏆 Role Ranking
- One-click Senior AI Engineer ranking across the full dataset
- Medal-style top-3 highlighting (🥇🥈🥉)
- Click any candidate to view their detailed profile

### 👤 Candidate Profile
- Comprehensive profile view: experience, education, skills, certifications, projects
- AI-generated score breakdown with evidence-based reasoning
- Risk factors and missing requirements analysis
- Role ranking context when navigated from rankings

### 📈 Pipeline Analytics
- Radar charts for multi-agent scoring dimensions
- Pipeline funnel visualization
- Per-agent contribution breakdown

### 🤖 Copilot
- Deterministic Q&A about the candidate dataset
- Dockable chat interface

---

## 🏗 Architecture

```
AI-Recruiter/
│
├── backend/                          # FastAPI application server
│   ├── app/
│   │   ├── api/routes/               # HTTP route modules
│   │   ├── core/                     # Config, logging, middleware, errors
│   │   ├── repositories/            # Dataset access layer
│   │   ├── schemas/                  # Pydantic request/response models
│   │   ├── services/                 # Ranking, analytics, copilot, resume services
│   │   ├── dependencies.py           # FastAPI dependency injection
│   │   └── main.py                   # Application entrypoint
│   ├── requirements.txt              # Backend-specific dependencies
│   └── Dockerfile                    # Backend container
│
├── frontend/                         # React + Vite UI
│   ├── src/
│   │   ├── components/               # Reusable UI components (20+)
│   │   ├── pages/                    # Route pages (Home, Candidates, Analyze, Analytics, Profile)
│   │   ├── lib/api.ts                # Backend base URL configuration
│   │   ├── App.tsx                   # Root component with routing & theming
│   │   └── index.css                 # Design system & theme tokens
│   └── package.json
│
├── src/                              # Offline ranking engine (Redrob-compliant)
│   ├── parser/                       # Candidate parser & JD analyzer
│   ├── feature_engineering/          # 100+ deterministic engineered features
│   ├── scoring/                      # Normalized weighted scoring
│   ├── ranking/                      # Deterministic top-N ranker
│   ├── reasoning/                    # Template reasoning (no hallucination)
│   └── validation/                   # Honeypot detection & submission validators
│
├── tests/                            # Backend API & pipeline tests
├── docs/                             # API.md & SANDBOX.md
├── rank.py                           # Offline CSV generation CLI
├── jd.txt                            # Senior AI Engineer JD
├── Dockerfile                        # No-network ranking container
├── docker-compose.yml                # Offline ranking compose (network_mode: none)
└── docker-compose.app.yml            # Full application compose
```

### Data Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  candidates.jsonl│────▶│  Parsing &        │────▶│  Feature         │
│  (100K profiles) │     │  Normalization    │     │  Engineering     │
└─────────────────┘     └──────────────────┘     │  (100+ features) │
                                                  └────────┬────────┘
                                                           │
┌─────────────────┐     ┌──────────────────┐              │
│  Frontend UI /   │◀────│  Template         │◀─────────────┤
│  Submission CSV  │     │  Reasoning        │     ┌────────▼────────┐
└─────────────────┘     └──────────────────┘     │  Weighted        │
                                                  │  Scoring &       │
                        ┌──────────────────┐     │  Honeypot        │
                        │  JD Requirement   │────▶│  Detection       │
                        │  Extraction       │     └─────────────────┘
                        └──────────────────┘
```

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 19, Vite 8, TypeScript, TailwindCSS 4, Framer Motion, Recharts, React Query, React Router |
| **Backend** | Python 3.11, FastAPI, Pydantic, Uvicorn |
| **Ranking Engine** | NumPy, Pandas, RapidFuzz, Scikit-learn |
| **Containerization** | Docker, Docker Compose |
| **Testing** | Python unittest |

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

| Tool | Version | Download |
|------|---------|----------|
| **Python** | 3.11+ | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 20+ | [nodejs.org](https://nodejs.org/) |
| **npm** | 9+ | Bundled with Node.js |
| **Git** | Latest | [git-scm.com](https://git-scm.com/) |
| **Docker** *(optional)* | Latest | [docker.com](https://www.docker.com/) |

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/janeshkrish/AI-Recruiter.git
cd AI-Recruiter
```

### 2. Backend Setup (Python)

Create a virtual environment and install dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install offline ranking dependencies
pip install -r requirements.txt

# Install backend API dependencies
pip install -r backend/requirements.txt
```

### 3. Frontend Setup (Node.js)

```bash
cd frontend
npm install
cd ..
```

### 4. Environment Configuration

The project includes `.env.example` files for reference. Copy and customize them if needed:

```bash
# Root .env (for offline ranking paths)
copy .env.example .env

# Backend .env (for API configuration)
copy backend\.env.example backend\.env
```

**Key environment variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_RECRUITER_DATASET_PATH` | `[PUB] India_runs.../candidates` folder | Path to candidate dataset directory |
| `AI_RECRUITER_CANDIDATES_FILE` | `candidates.jsonl` | Candidate data filename |
| `VITE_API_BASE_URL` | `http://127.0.0.1:8000` | Backend URL for the frontend |

> **Note:** No API keys are required. The ranking engine is fully local and deterministic.

### 5. Run the Application

You need **two terminals** — one for the backend, one for the frontend.

#### Terminal 1 — Start the Backend

```bash
# Make sure your virtual environment is activated
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

✅ Backend will be available at: **http://127.0.0.1:8000**  
📖 API docs (Swagger UI): **http://127.0.0.1:8000/docs**

#### Terminal 2 — Start the Frontend

```bash
cd frontend
npx vite --host 127.0.0.1 --port 5173
```

✅ Frontend will be available at: **http://127.0.0.1:5173**

> **Tip:** Make sure the backend is running before opening the frontend — the UI fetches dataset stats on load.

---

## 📦 Offline Ranking (Redrob Submission)

Generate the required top-100 candidate ranking CSV with a single command:

```bash
python rank.py \
  --candidates "[PUB] India_runs_data_and_ai_challenge/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl" \
  --jd jd.txt \
  --out redrob_senior_ai_engineer_ranking.csv
```

**Output format:**

```csv
candidate_id,rank,score,reasoning
```

The CLI automatically validates:
- ✅ Exactly 100 rows
- ✅ Correct CSV headers
- ✅ Unique candidate IDs
- ✅ Unique ranks (1-100)
- ✅ Non-increasing (monotonic) scores
- ✅ Deterministic tie ordering
- ✅ Repository structure compliance

---

## 🐳 Docker Deployment

### Option A: No-Network Offline Ranking

Runs the ranking engine with `network_mode: "none"` — fully air-gapped:

```bash
docker compose -f docker-compose.yml up --build ranker
```

The output CSV will be generated at the project root.

### Option B: Full Application Stack

Runs both backend and frontend in containers:

```bash
docker compose -f docker-compose.app.yml up --build
```

| Service | URL |
|---------|-----|
| Backend API | http://127.0.0.1:8000 |
| Frontend UI | http://127.0.0.1:5173 |
| API Docs | http://127.0.0.1:8000/docs |

---

## 📡 API Reference

Full API documentation is available in [`docs/API.md`](docs/API.md) and via the interactive Swagger UI at `/docs`.

| Method | Endpoint | Description |
|:------:|----------|-------------|
| `GET` | `/api/health` | Service health check & ranking mode |
| `GET` | `/api/status` | Alias for health |
| `GET` | `/api/stats` | Dataset statistics (total candidates, avg experience, etc.) |
| `GET` | `/api/candidates` | Paginated candidate search with filters |
| `GET` | `/api/candidates/{id}` | Individual candidate detail |
| `GET` | `/api/candidates/role-ranking` | Senior AI Engineer ranking (top 100) |
| `GET` | `/api/candidates/role-ranking.csv` | Download ranking as CSV |
| `POST` | `/api/rank` | Rank candidates for a custom JD |
| `POST` | `/api/rank/role` | Alias for JD-based ranking |
| `GET` | `/api/pipeline/analytics` | Pipeline analytics & agent metrics |
| `POST` | `/api/copilot` | Deterministic copilot Q&A |
| `POST` | `/api/resumes/upload` | Resume upload & safe text extraction |

---

## 🧠 AI Pipeline

The ranking pipeline is fully deterministic and runs entirely on CPU:

```
Resume / Candidate JSONL
    │
    ▼
┌──────────────────────┐
│  Parsing &            │  Parse profiles, normalize sections,
│  Section Normalization│  extract structured data
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  JD Requirement       │  Extract must-have, nice-to-have,
│  Extraction           │  reject signals, culture & behavior
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  Feature Engineering  │  100+ deterministic features across
│  (100+ features)      │  skills, experience, risk, behavior
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  Normalized Weighted  │  Configurable weights, production
│  Scoring              │  evidence boosts, disqualifier penalties
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  Honeypot &           │  Detect impossible profiles,
│  Inconsistency Check  │  fake expertise, inflated timelines
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  Deterministic        │  Rank by score, break ties by
│  Ranking              │  candidate ID
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  Template Reasoning   │  Evidence-only explanations,
│                       │  no hallucinated claims
└──────────┬───────────┘
           ▼
    Frontend UI / CSV
```

---

## 🔬 Recommendation Engine

The engine creates **100+ deterministic features** across the following dimensions:

| Category | Features |
|----------|----------|
| **Production AI/ML** | Production ML systems, deployed models, inference pipelines |
| **Experience Breakdown** | Years in AI, product companies, service companies, startups, research |
| **Retrieval & Ranking** | Search, recommendation, embeddings, vector DBs, hybrid search |
| **Technical Skills** | Python proficiency, evaluation metrics, A/B testing, open source |
| **Behavioral Signals** | 23 Redrob signals — response rate, activity, notice period, engagement |
| **Career Trajectory** | Stability, title progression, education, certifications, completeness |
| **Risk Detection** | Consulting-only, framework-only, title-chasing, keyword-stuffing, etc. |

### Scoring Highlights

- ✅ **Normalized weighted scoring** — no single feature group dominates
- ✅ **Production evidence boosts** — deployed retrieval, ranking, vector, evaluation, experimentation
- ✅ **Honeypot detection** — impossible profiles, inconsistent experience claims
- ✅ **Risk penalties** — fake dates, narrow domain-only, manager-only, keyword-stuffed
- ✅ **Deterministic tie-breaking** — by candidate ID for reproducibility
- ✅ **Evidence-only reasoning** — templates populated with computed evidence, never hallucinated

---

## 🧪 Testing

### Run Backend & Pipeline Tests

```bash
python -m unittest discover -s tests
```

### Lint & Build Frontend

```bash
cd frontend
npm run lint
npm run build
```

### Validate Submission CSV

```bash
python rank.py \
  --candidates "[PUB] India_runs_data_and_ai_challenge/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl" \
  --jd jd.txt \
  --out submission.csv
```

The CLI runs all validation checks automatically and exits with code 1 if any check fails.

---

## ❓ Troubleshooting

<details>
<summary><b>Backend: "Cannot find candidates" or dataset error</b></summary>

Check that the dataset path is correct. Either:
- Keep the challenge dataset in the default nested folder structure
- Set `AI_RECRUITER_DATASET_PATH` in your `.env` to point to the directory containing `candidates.jsonl`
</details>

<details>
<summary><b>Frontend: "Failed to resolve import" or blank page</b></summary>

1. Make sure `frontend/src/lib/api.ts` exists
2. Clear Vite's cache and reinstall:
   ```bash
   cd frontend
   Remove-Item -Recurse -Force node_modules  # Windows
   # rm -rf node_modules                     # macOS/Linux
   npm install
   ```
3. Use `npx vite` instead of `npm run dev` if argument passing causes issues
</details>

<details>
<summary><b>Frontend: Cannot reach backend (network errors)</b></summary>

1. Make sure the backend is running on port 8000
2. Create `frontend/.env` if it doesn't exist:
   ```
   VITE_API_BASE_URL=http://127.0.0.1:8000
   ```
3. Restart the Vite dev server after changing env variables
</details>

<details>
<summary><b>Ranking takes too long</b></summary>

The ranker scans 100,000 profiles with 100+ features each. On a modern CPU it should complete well within the 5-minute target. If it's slow:
- Ensure no other CPU-intensive processes are running
- Check available RAM (the dataset loads into memory)
</details>

<details>
<summary><b>Docker: App cannot access data</b></summary>

Use `docker-compose.app.yml` — it mounts the challenge dataset directory into `/app/data` as a read-only volume.
</details>

<details>
<summary><b>CSV validation fails</b></summary>

Run the exact `rank.py` command shown above. The CLI validates row count, headers, unique IDs/ranks, monotonic scores, tie ordering, and repository structure before exiting.
</details>

---

## 🔒 Sandbox & Security

See [`docs/SANDBOX.md`](docs/SANDBOX.md) for the full sandbox execution strategy.

**Key principles:**
- 🔒 Challenge ranking runs with `network_mode: "none"` in Docker
- 📁 Dataset mounted read-only where possible
- 🧱 CPU and memory caps on app containers
- 🗑️ Uploaded resumes stored in isolated temp directories, never executed, deleted after parsing
- 🚫 No API keys in the ranking path

---

## 👥 Team

| Name | Role | Email |
|------|------|-------|
| **Janesh Krishna R** | Backend Engineer | janeshkrishna12@gmail.com |
| **Shrija Dhanalakshmi SM** | ML Engineer | shrijasm@gmail.com |
| **Thivakar T** | Frontend Engineer | thivakart2006@gmail.com |

---

## 📄 License

This project was built for the **Redrob India Runs Data & AI Challenge**. All code is original work by Team SOULX.

---

<p align="center">
  <b>Built with ❤️ by Team SOULX</b><br/>
  <sub>Deterministic. Explainable. Production-ready.</sub>
</p>
