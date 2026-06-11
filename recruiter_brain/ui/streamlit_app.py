"""
AI Recruiter Brain — Streamlit Dashboard
==========================================

Multi-page dashboard for the AI Recruitment Intelligence System.

Pages:
1. Job Description Upload & Parsing
2. Top Candidates Ranking
3. Candidate Deep Dive (radar charts, scores, career)
4. Explainability (strengths, risks, growth)
5. Recruiter Notes & LLM Reasoning

Usage:
    streamlit run recruiter_brain/ui/streamlit_app.py
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add project root to path
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from recruiter_brain.data.models import (
    CandidateRanking,
    Explanation,
    RankResponse,
    RoleParsedOutput,
)

# ===========================================================================
# Page Config
# ===========================================================================

st.set_page_config(
    page_title="AI Recruiter Brain",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===========================================================================
# Custom CSS for Premium Design
# ===========================================================================

st.markdown("""
<style>
    /* --- Global --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* --- Sidebar --- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f23 0%, #1a1a3e 50%, #0f0f23 100%);
    }

    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown label {
        color: #e2e8f0 !important;
    }

    /* --- Hero Header --- */
    .hero-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    .hero-header h1 {
        color: white !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
        letter-spacing: -0.02em;
    }
    .hero-header p {
        color: rgba(255,255,255,0.85) !important;
        font-size: 1rem !important;
        margin: 0.5rem 0 0 0 !important;
    }

    /* --- Score Cards --- */
    .score-card {
        background: linear-gradient(145deg, #1e1e3f, #2a2a5a);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .score-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
    }
    .score-card .score-value {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .score-card .score-label {
        color: #a0aec0;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.3rem;
    }

    /* --- Candidate Card --- */
    .candidate-card {
        background: linear-gradient(145deg, #1a1a3e, #252552);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .candidate-card:hover {
        border-color: rgba(102, 126, 234, 0.4);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.15);
    }
    .candidate-name {
        font-size: 1.15rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 0.3rem;
    }
    .candidate-title {
        font-size: 0.85rem;
        color: #a0aec0;
    }

    /* --- Badges --- */
    .skill-badge {
        display: inline-block;
        background: rgba(102, 126, 234, 0.15);
        color: #667eea;
        border: 1px solid rgba(102, 126, 234, 0.3);
        padding: 0.2rem 0.65rem;
        border-radius: 20px;
        font-size: 0.75rem;
        margin: 0.15rem;
        font-weight: 500;
    }
    .skill-badge.missing {
        background: rgba(245, 101, 101, 0.12);
        color: #fc8181;
        border-color: rgba(245, 101, 101, 0.3);
    }
    .skill-badge.match {
        background: rgba(72, 187, 120, 0.12);
        color: #68d391;
        border-color: rgba(72, 187, 120, 0.3);
    }

    /* --- Status Badge --- */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .status-badge.green {
        background: rgba(72, 187, 120, 0.15);
        color: #68d391;
    }
    .status-badge.yellow {
        background: rgba(236, 201, 75, 0.15);
        color: #ecc94b;
    }
    .status-badge.red {
        background: rgba(245, 101, 101, 0.15);
        color: #fc8181;
    }

    /* --- Pipeline Stage --- */
    .pipeline-stage {
        background: linear-gradient(145deg, #1a1a3e, #252552);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    .pipeline-stage .stage-number {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* --- Misc --- */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent);
        margin: 1.5rem 0;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)


# ===========================================================================
# Session State Init
# ===========================================================================

def init_session_state():
    """Initialize session state variables."""
    defaults = {
        "engine": None,
        "rank_result": None,
        "parsed_role": None,
        "candidates_loaded": False,
        "num_candidates": 1000,
        "jd_text": "",
        "jd_title": "",
        "selected_candidate_idx": 0,
        "explanations": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()


# ===========================================================================
# Engine Initialization
# ===========================================================================

@st.cache_resource(show_spinner=False)
def get_engine(num_candidates: int = 1000):
    """Initialize and cache the ranking engine."""
    from recruiter_brain.data.generate_synthetic_data import load_candidates
    from recruiter_brain.scoring.ranking_engine import HybridRankingEngine

    engine = HybridRankingEngine()
    candidates = load_candidates(limit=num_candidates)
    engine.index_candidates(candidates)
    return engine


def get_explainer(engine):
    """Get explainability engine."""
    from recruiter_brain.scoring.explainability import ExplainabilityEngine
    return ExplainabilityEngine(engine.potential_agent)


# ===========================================================================
# Helper Functions
# ===========================================================================

def score_color(score: float) -> str:
    """Get color class based on score value."""
    if score >= 0.7:
        return "green"
    elif score >= 0.4:
        return "yellow"
    return "red"


def score_emoji(score: float) -> str:
    """Get emoji indicator for score."""
    if score >= 0.8:
        return "🟢"
    elif score >= 0.6:
        return "🟡"
    elif score >= 0.4:
        return "🟠"
    return "🔴"


def render_score_card(label: str, value: float, col):
    """Render a styled score card."""
    color = score_color(value)
    col.markdown(f"""
    <div class="score-card">
        <div class="score-value">{value:.0%}</div>
        <div class="score-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def create_radar_chart(scores: dict, title: str = "Agent Scores") -> go.Figure:
    """Create a radar chart for candidate scores."""
    categories = list(scores.keys())
    values = list(scores.values())
    # Close the polygon
    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.2)',
        line=dict(color='#667eea', width=2),
        marker=dict(size=6, color='#667eea'),
        name=title,
    ))

    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                gridcolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='rgba(255,255,255,0.5)', size=10),
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='#e2e8f0', size=11),
            ),
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=60, r=60, t=40, b=40),
        height=350,
    )

    return fig


def create_score_bar_chart(rankings: list[CandidateRanking]) -> go.Figure:
    """Create a horizontal bar chart of top candidates."""
    names = [f"#{r.rank} {r.name}" for r in rankings[:15]]
    scores = [r.final_score for r in rankings[:15]]

    colors = [
        f'rgba(102, 126, 234, {0.4 + 0.6 * (1 - i / len(names))})'
        for i in range(len(names))
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=names[::-1],
        x=scores[::-1],
        orientation='h',
        marker=dict(
            color=colors[::-1],
            line=dict(width=0),
            cornerradius=6,
        ),
        text=[f"{s:.1%}" for s in scores[::-1]],
        textposition='outside',
        textfont=dict(color='#e2e8f0', size=11),
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            range=[0, 1],
            gridcolor='rgba(255,255,255,0.05)',
            tickfont=dict(color='#a0aec0'),
            title="Final Score",
            titlefont=dict(color='#a0aec0'),
        ),
        yaxis=dict(
            tickfont=dict(color='#e2e8f0', size=11),
        ),
        margin=dict(l=200, r=80, t=20, b=50),
        height=max(400, len(names) * 35),
    )

    return fig


def create_breakdown_chart(scores) -> go.Figure:
    """Create stacked breakdown of score components."""
    categories = ["Technical", "Career", "Behavioral", "Potential", "Recruiter"]
    values = [
        scores.technical_fit_score,
        scores.career_fit_score,
        scores.behavioral_fit_score,
        scores.potential_score,
        scores.recruiter_reasoning_score,
    ]
    weights = [0.35, 0.20, 0.15, 0.15, 0.15]
    weighted = [v * w for v, w in zip(values, weights)]

    colors = ['#667eea', '#764ba2', '#f093fb', '#4fd1c5', '#f6ad55']

    fig = go.Figure()

    for i, (cat, val, wval, color) in enumerate(
        zip(categories, values, weighted, colors)
    ):
        fig.add_trace(go.Bar(
            name=cat,
            x=[wval],
            y=["Final Score"],
            orientation='h',
            marker=dict(color=color, cornerradius=4),
            text=f"{cat}: {val:.0%} × {weights[i]:.0%}",
            textposition='inside',
            textfont=dict(color='white', size=10),
            hovertemplate=f"{cat}<br>Raw: {val:.1%}<br>Weight: {weights[i]:.0%}<br>Contribution: {wval:.1%}<extra></extra>",
        ))

    fig.update_layout(
        barmode='stack',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            range=[0, 1],
            gridcolor='rgba(255,255,255,0.05)',
            tickfont=dict(color='#a0aec0'),
        ),
        yaxis=dict(visible=False),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            font=dict(color='#e2e8f0'),
        ),
        margin=dict(l=20, r=20, t=10, b=60),
        height=120,
    )

    return fig


# ===========================================================================
# Sidebar
# ===========================================================================

with st.sidebar:
    st.markdown("# 🧠 Recruiter Brain")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        [
            "📝 Job Description",
            "🏆 Top Candidates",
            "🔍 Candidate Deep Dive",
            "💡 Explainability",
            "📋 Recruiter Notes",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    st.markdown("### ⚙️ Settings")
    num_candidates = st.select_slider(
        "Candidate Pool Size",
        options=[100, 500, 1000, 2000, 5000],
        value=1000,
    )

    st.markdown("### 📊 Scoring Weights")
    w_tech = st.slider("Technical", 0.0, 1.0, 0.35, 0.05)
    w_career = st.slider("Career", 0.0, 1.0, 0.20, 0.05)
    w_behav = st.slider("Behavioral", 0.0, 1.0, 0.15, 0.05)
    w_potent = st.slider("Potential", 0.0, 1.0, 0.15, 0.05)
    w_recruit = st.slider("Recruiter LLM", 0.0, 1.0, 0.15, 0.05)

    total_w = w_tech + w_career + w_behav + w_potent + w_recruit
    if abs(total_w - 1.0) > 0.01:
        st.warning(f"Weights sum to {total_w:.2f} (should be 1.0)")

    custom_weights = {
        "technical": w_tech,
        "career": w_career,
        "behavioral": w_behav,
        "potential": w_potent,
        "recruiter": w_recruit,
    }

    st.markdown("---")
    st.markdown(
        '<p style="color: #64748b; font-size: 0.75rem;">'
        "AI Recruiter Brain v1.0.0<br>"
        "Multi-Agent Intelligence System"
        "</p>",
        unsafe_allow_html=True,
    )


# ===========================================================================
# Page 1: Job Description
# ===========================================================================

if page == "📝 Job Description":
    st.markdown("""
    <div class="hero-header">
        <h1>📝 Job Description Analysis</h1>
        <p>Upload or paste a job description to begin the AI-powered candidate ranking pipeline</p>
    </div>
    """, unsafe_allow_html=True)

    # Sample JDs
    sample_jds = {
        "Custom": "",
        "Senior AI/ML Engineer": """We are looking for a Senior AI/ML Engineer to join our Applied AI team.

Requirements:
- 5+ years of experience in machine learning and software engineering
- Strong proficiency in Python, PyTorch, and TensorFlow
- Experience building and deploying production ML systems
- Deep understanding of NLP, LLMs, and transformer architectures
- Experience with RAG systems, vector databases, and embedding models
- Familiarity with MLOps practices (CI/CD for ML, model monitoring)
- Strong system design skills for scalable ML infrastructure

Preferred:
- Experience with LLM fine-tuning and RLHF
- Knowledge of distributed training (DeepSpeed, FSDP)
- Experience with Kubernetes and cloud platforms (AWS/GCP)
- Published research or contributions to open-source ML projects

We value candidates who think like product owners, have a startup mindset,
and can drive technical decisions independently.""",
        "Staff Data Engineer": """Staff Data Engineer needed to architect our next-generation data platform.

Must-have:
- 8+ years in data engineering
- Expert in Apache Spark, Kafka, and Airflow
- Strong SQL and data modeling skills
- Experience with cloud data warehouses (Snowflake, BigQuery, or Redshift)
- Track record of building petabyte-scale data pipelines

Nice-to-have:
- Experience with real-time streaming architectures
- Knowledge of data governance and quality frameworks
- Leadership experience managing data engineering teams""",
        "ML Platform Engineer": """ML Platform Engineer to build the infrastructure powering our AI products.

Requirements:
- 4+ years of experience in ML infrastructure or platform engineering
- Strong Python and Go programming skills
- Experience with Kubernetes, Docker, and container orchestration
- Familiarity with ML frameworks (PyTorch, TensorFlow)
- Experience building feature stores, model serving, or training platforms

Fast-paced startup, product-minded engineers preferred.""",
    }

    selected_sample = st.selectbox(
        "Choose a sample JD or write your own:",
        list(sample_jds.keys()),
    )

    default_text = sample_jds.get(selected_sample, "")

    col1, col2 = st.columns([2, 1])

    with col1:
        jd_title = st.text_input(
            "Job Title",
            value=selected_sample if selected_sample != "Custom" else "",
            placeholder="e.g., Senior AI/ML Engineer",
        )

        jd_text = st.text_area(
            "Job Description",
            value=default_text,
            height=350,
            placeholder="Paste the full job description here...",
        )

    with col2:
        st.markdown("### 🚀 Pipeline Configuration")
        st.markdown(f"""
        <div class="pipeline-stage">
            <div class="stage-number">{num_candidates:,}</div>
            <div style="color: #a0aec0; font-size: 0.8rem;">Total Candidates</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        stages = [
            ("Stage 1", "Vector Retrieval", "→ Top 2,000"),
            ("Stage 2", "Multi-Agent Scoring", "→ Top 500"),
            ("Stage 3", "LLM Reasoning", "→ Top 200"),
            ("Stage 4", "Final Ranking", "→ Top 25"),
        ]
        for stage, desc, result in stages:
            st.markdown(f"**{stage}** — {desc}  \n`{result}`")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    col_btn1, col_btn2, _ = st.columns([1, 1, 3])

    with col_btn1:
        run_pipeline = st.button(
            "🚀 Run Full Pipeline",
            type="primary",
            use_container_width=True,
        )

    with col_btn2:
        parse_only = st.button(
            "📋 Parse JD Only",
            use_container_width=True,
        )

    if run_pipeline and jd_text:
        with st.spinner("⏳ Initializing engine & loading candidates..."):
            engine = get_engine(num_candidates)

        with st.spinner("🔄 Running 4-stage ranking pipeline..."):
            progress = st.progress(0, "Starting pipeline...")

            async def run():
                return await engine.rank(
                    job_description=jd_text,
                    job_title=jd_title,
                    top_k=25,
                    custom_weights=custom_weights,
                )

            progress.progress(25, "Stage 1: Vector retrieval...")
            result = asyncio.run(run())
            progress.progress(100, "✅ Pipeline complete!")

            st.session_state.rank_result = result
            st.session_state.parsed_role = result.parsed_role
            st.session_state.engine = engine
            st.session_state.jd_text = jd_text
            st.session_state.jd_title = jd_title

        st.success(
            f"✅ Pipeline complete! {result.pipeline_stages['stage4_final']} "
            f"candidates ranked from {result.total_candidates_processed:,} total."
        )

        # Show parsed role
        pr = result.parsed_role
        st.markdown("### 🎯 Extracted Requirements")

        mc1, mc2 = st.columns(2)
        with mc1:
            st.markdown("**Must-Have Skills:**")
            for skill in pr.must_have_skills:
                st.markdown(
                    f'<span class="skill-badge match">{skill}</span>',
                    unsafe_allow_html=True,
                )
        with mc2:
            st.markdown("**Nice-to-Have Skills:**")
            for skill in pr.nice_to_have_skills:
                st.markdown(
                    f'<span class="skill-badge">{skill}</span>',
                    unsafe_allow_html=True,
                )

        sc1, sc2, sc3, sc4 = st.columns(4)
        render_score_card("Leadership", pr.leadership, sc1)
        render_score_card("Startup Mindset", pr.startup_mindset, sc2)
        render_score_card("Research", pr.research_orientation, sc3)
        render_score_card("Product Thinking", pr.product_thinking, sc4)

    elif parse_only and jd_text:
        with st.spinner("Parsing job description..."):
            engine = get_engine(num_candidates)
            parsed = asyncio.run(engine.role_agent.parse(jd_text))
            st.session_state.parsed_role = parsed

        st.json(parsed.model_dump())


# ===========================================================================
# Page 2: Top Candidates
# ===========================================================================

elif page == "🏆 Top Candidates":
    st.markdown("""
    <div class="hero-header">
        <h1>🏆 Top Candidates</h1>
        <p>Ranked candidates with multi-agent scoring breakdown</p>
    </div>
    """, unsafe_allow_html=True)

    result = st.session_state.rank_result

    if result is None:
        st.info("👈 Go to **Job Description** page and run the pipeline first.")
    else:
        # Pipeline summary
        ps = result.pipeline_stages
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Pool", f"{ps.get('total_candidates', 0):,}")
        col2.metric("Stage 1 (Vector)", f"{ps.get('stage1_retrieved', 0):,}")
        col3.metric("Stage 2 (Scored)", f"{ps.get('stage2_scored', 0):,}")
        col4.metric("Stage 3 (LLM)", f"{ps.get('stage3_llm_evaluated', 0):,}")
        col5.metric("Final Top-K", f"{ps.get('stage4_final', 0)}")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Score chart
        st.markdown("### 📊 Final Scores")
        fig = create_score_bar_chart(result.rankings)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Data table
        st.markdown("### 📋 Detailed Rankings")

        table_data = []
        for r in result.rankings:
            table_data.append({
                "Rank": r.rank,
                "Name": r.name,
                "Title": r.current_title,
                "Company": r.current_company,
                "Final Score": f"{r.final_score:.1%}",
                "Technical": f"{r.scores.technical_fit_score:.1%}",
                "Career": f"{r.scores.career_fit_score:.1%}",
                "Behavioral": f"{r.scores.behavioral_fit_score:.1%}",
                "Potential": f"{r.scores.potential_score:.1%}",
                "Recruiter": f"{r.scores.recruiter_reasoning_score:.1%}",
            })

        df = pd.DataFrame(table_data)
        st.dataframe(
            df,
            use_container_width=True,
            height=600,
            hide_index=True,
        )


# ===========================================================================
# Page 3: Candidate Deep Dive
# ===========================================================================

elif page == "🔍 Candidate Deep Dive":
    st.markdown("""
    <div class="hero-header">
        <h1>🔍 Candidate Deep Dive</h1>
        <p>Detailed analysis with radar charts and score breakdowns</p>
    </div>
    """, unsafe_allow_html=True)

    result = st.session_state.rank_result

    if result is None:
        st.info("👈 Go to **Job Description** page and run the pipeline first.")
    else:
        # Candidate selector
        candidate_names = [
            f"#{r.rank} — {r.name} ({r.final_score:.1%})"
            for r in result.rankings
        ]
        selected = st.selectbox("Select a candidate:", candidate_names)
        idx = candidate_names.index(selected)
        ranking = result.rankings[idx]
        scores = ranking.scores

        # Get full profile
        engine = st.session_state.engine
        candidate = engine.get_candidate(ranking.candidate_id) if engine else None

        # Top section: Score cards
        st.markdown(f"### {ranking.name}")
        st.markdown(
            f"**{ranking.current_title}** at **{ranking.current_company}**"
        )

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        render_score_card("Final", ranking.final_score, col1)
        render_score_card("Technical", scores.technical_fit_score, col2)
        render_score_card("Career", scores.career_fit_score, col3)
        render_score_card("Behavioral", scores.behavioral_fit_score, col4)
        render_score_card("Potential", scores.potential_score, col5)
        render_score_card("Recruiter", scores.recruiter_reasoning_score, col6)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Radar chart + Score breakdown
        chart_col, detail_col = st.columns([1, 1])

        with chart_col:
            st.markdown("#### 🎯 Agent Score Radar")
            radar_data = {
                "Technical": scores.technical_fit_score,
                "Career": scores.career_fit_score,
                "Behavioral": scores.behavioral_fit_score,
                "Potential": scores.potential_score,
                "Recruiter": scores.recruiter_reasoning_score,
            }
            fig = create_radar_chart(radar_data)
            st.plotly_chart(fig, use_container_width=True)

        with detail_col:
            st.markdown("#### 📊 Score Contribution Breakdown")
            fig = create_breakdown_chart(scores)
            st.plotly_chart(fig, use_container_width=True)

            # Sub-scores
            st.markdown("#### 🔬 Technical Sub-Scores")
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            sub_col1.metric("Cosine Sim", f"{scores.cosine_similarity:.1%}")
            sub_col2.metric("Semantic Overlap", f"{scores.semantic_overlap:.1%}")
            sub_col3.metric("Skill Overlap", f"{scores.skill_overlap:.1%}")

            st.markdown("#### 📈 Career Sub-Scores")
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            sub_col1.metric("Promotion", f"{scores.promotion_score:.1%}")
            sub_col2.metric("Growth", f"{scores.career_growth_score:.1%}")
            sub_col3.metric("Stability", f"{scores.stability_score:.1%}")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Candidate details
        if candidate:
            det1, det2 = st.columns(2)

            with det1:
                st.markdown("#### 🎓 Skills")
                for skill in candidate.skills:
                    st.markdown(
                        f'<span class="skill-badge">{skill}</span>',
                        unsafe_allow_html=True,
                    )

                st.markdown("")
                st.markdown("#### 🎓 Education")
                for edu in candidate.education:
                    st.markdown(
                        f"- **{edu.degree} in {edu.field}** — "
                        f"{edu.institution} ({edu.graduation_year})"
                    )

                if candidate.certifications:
                    st.markdown("#### 📜 Certifications")
                    for cert in candidate.certifications:
                        st.markdown(f"- {cert.name} ({cert.issuer}, {cert.year})")

            with det2:
                st.markdown("#### 💼 Career History")
                for entry in reversed(candidate.career_history):
                    status = "🟢 Current" if entry.end_date is None else ""
                    st.markdown(
                        f"**{entry.title}** at {entry.company} {status}  \n"
                        f"_{entry.start_date} → {entry.end_date or 'Present'}_ "
                        f"({entry.duration_months}mo) · {entry.industry}"
                    )

                st.markdown("#### 📊 Behavioral Signals")
                bs = candidate.behavioral_signals
                behav_data = {
                    "Response Rate": bs.recruiter_response_rate,
                    "Engagement": bs.platform_engagement,
                    "Profile Completeness": bs.profile_completeness,
                    "Interview Completion": bs.interview_completion_rate,
                    "Activity Score": bs.activity_score,
                }
                for label, val in behav_data.items():
                    st.progress(val, text=f"{label}: {val:.0%}")


# ===========================================================================
# Page 4: Explainability
# ===========================================================================

elif page == "💡 Explainability":
    st.markdown("""
    <div class="hero-header">
        <h1>💡 Explainability Engine</h1>
        <p>Transparent AI reasoning — understand why each candidate was ranked</p>
    </div>
    """, unsafe_allow_html=True)

    result = st.session_state.rank_result
    engine = st.session_state.engine

    if result is None or engine is None:
        st.info("👈 Go to **Job Description** page and run the pipeline first.")
    else:
        explainer = get_explainer(engine)

        for ranking in result.rankings[:10]:
            candidate = engine.get_candidate(ranking.candidate_id)
            scores = ranking.scores

            if candidate is None:
                continue

            explanation = explainer.explain(candidate, scores, result.parsed_role)

            with st.expander(
                f"#{ranking.rank} — {ranking.name} "
                f"({ranking.final_score:.1%}) "
                f"{score_emoji(ranking.final_score)}",
                expanded=(ranking.rank <= 3),
            ):
                st.markdown(f"**{ranking.current_title}** at {ranking.current_company}")
                st.markdown(
                    f'<span class="status-badge {score_color(explanation.confidence)}">'
                    f"Confidence: {explanation.confidence:.0%}</span>",
                    unsafe_allow_html=True,
                )

                st.markdown(f"**Why matched:** {explanation.why_matched}")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### ✅ Strengths")
                    for s in explanation.strengths:
                        st.markdown(f"- 💪 {s}")

                    st.markdown("#### 🚀 Growth Potential")
                    st.markdown(explanation.growth_potential)

                with col2:
                    st.markdown("#### ⚠️ Risks")
                    for r in explanation.risks:
                        st.markdown(f"- ⚠️ {r}")

                    st.markdown("#### ❌ Missing Skills")
                    for skill in explanation.missing_skills:
                        st.markdown(
                            f'<span class="skill-badge missing">{skill}</span>',
                            unsafe_allow_html=True,
                        )

                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ===========================================================================
# Page 5: Recruiter Notes
# ===========================================================================

elif page == "📋 Recruiter Notes":
    st.markdown("""
    <div class="hero-header">
        <h1>📋 Recruiter Notes & LLM Reasoning</h1>
        <p>AI-generated recruiter insights for each shortlisted candidate</p>
    </div>
    """, unsafe_allow_html=True)

    result = st.session_state.rank_result

    if result is None:
        st.info("👈 Go to **Job Description** page and run the pipeline first.")
    else:
        st.markdown("### 🤖 Agent 6 — Recruiter Reasoning Output")
        st.markdown(
            "These notes are generated by the LLM-based Recruiter Reasoning Agent, "
            "which evaluates candidates holistically across 6 dimensions."
        )

        for ranking in result.rankings[:15]:
            reasoning = ranking.scores.recruiter_reasoning_text

            with st.expander(
                f"#{ranking.rank} — {ranking.name} "
                f"(LLM Score: {ranking.scores.recruiter_reasoning_score:.1%})",
                expanded=(ranking.rank <= 3),
            ):
                st.markdown(
                    f"**{ranking.current_title}** at **{ranking.current_company}**"
                )

                # Score badges
                st.markdown(
                    f"{score_emoji(ranking.scores.recruiter_reasoning_score)} "
                    f"**LLM Recruiter Score:** {ranking.scores.recruiter_reasoning_score:.1%}"
                )

                if reasoning:
                    st.markdown("#### 💬 LLM Reasoning")
                    st.info(reasoning)
                else:
                    st.markdown(
                        "*No LLM reasoning available (simulation mode)*"
                    )

                # Editable notes
                st.markdown("#### 📝 Your Notes")
                note_key = f"note_{ranking.candidate_id}"
                st.text_area(
                    "Add your notes:",
                    key=note_key,
                    height=80,
                    placeholder="Add your recruiter notes here...",
                    label_visibility="collapsed",
                )
