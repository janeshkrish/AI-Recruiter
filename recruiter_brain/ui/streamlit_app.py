"""
AI Recruiter Streamlit Dashboard
================================

User interface for the AI Recruiter system.
Allows pasting JDs, triggering ranking, and analyzing results.
"""

import json
from io import StringIO

import pandas as pd
import requests
import streamlit as st

# Setup page config
st.set_page_config(
    page_title="AI Recruiter | Dataset Ranker",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_URL = "http://127.0.0.1:8000"

def init_session_state():
    if "ranked_candidates" not in st.session_state:
        st.session_state.ranked_candidates = []
    if "api_status" not in st.session_state:
        st.session_state.api_status = "Unknown"

def check_health():
    try:
        res = requests.get(f"{API_URL}/api/health", timeout=2)
        if res.status_code == 200:
            st.session_state.api_status = "🟢 Online"
        else:
            st.session_state.api_status = "🔴 Offline"
    except:
        st.session_state.api_status = "🔴 Offline"

def rank_candidates(jd_text: str):
    """Call the FastAPI ranking endpoint."""
    with st.spinner("Analyzing JD and Ranking 100K Candidates via FAISS..."):
        try:
            res = requests.post(f"{API_URL}/api/rank", json={"job_description": jd_text}, timeout=120)
            if res.status_code == 200:
                data = res.json()
                st.session_state.ranked_candidates = data.get("ranked_candidates", [])
                st.success("Ranking complete!")
            else:
                st.error(f"Error: {res.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")

# Apply custom CSS
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 6px; }
    .score-card { background-color: #1E1E2E; padding: 10px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)


def render_sidebar():
    st.sidebar.title("🧠 AI Recruiter")
    st.sidebar.markdown(f"**API Status:** {st.session_state.api_status}")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Settings")
    st.sidebar.markdown("Ensure backend is running (`uvicorn recruiter_brain.api.main:app`).")
    if st.sidebar.button("Check API Health"):
        check_health()


def render_main():
    st.title("Intelligent Candidate Ranking")
    st.markdown("Rank candidates directly from the `India_runs_data_and_ai_challenge` dataset.")

    # 1. Upload JD
    st.subheader("1. Job Description")
    jd_text = st.text_area("Paste the Job Description here:", height=200, placeholder="We are looking for a Senior AI Engineer...")
    
    if st.button("Rank Candidates", type="primary"):
        if jd_text.strip():
            rank_candidates(jd_text)
        else:
            st.warning("Please enter a Job Description.")

    # 2. Show Results
    if st.session_state.ranked_candidates:
        st.markdown("---")
        st.subheader("2. Ranked Candidates")
        
        # Prepare DataFrame for table
        df_data = []
        for i, c in enumerate(st.session_state.ranked_candidates):
            df_data.append({
                "Rank": i + 1,
                "Candidate ID": c["candidate_id"],
                "Score (0-100)": c["score"],
                "Skill Match": c["skill_match"],
                "Exp Match": c["experience_match"],
                "Semantics": c["semantic_similarity"],
                "_reasoning": c["reasoning"] # hidden column for logic
            })
            
        df = pd.DataFrame(df_data)
        
        # Filter functionality
        search_col, dl_col = st.columns([3, 1])
        with search_col:
            search_term = st.text_input("Search Candidate ID or Score...", placeholder="e.g. CAND_000123")
            if search_term:
                df = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)]

        # Download functionality
        with dl_col:
            # Format required by submission spec
            csv_data = []
            for i, c in enumerate(st.session_state.ranked_candidates):
                csv_data.append({
                    "candidate_id": c["candidate_id"],
                    "rank": i + 1,
                    "score": round(c["score"] / 100.0, 4), # normalize 0-1 for submission
                    "reasoning": c["reasoning"].replace('\n', ' ')
                })
            submit_df = pd.DataFrame(csv_data)
            csv_buffer = submit_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Submission CSV",
                data=csv_buffer,
                file_name="submission.csv",
                mime="text/csv"
            )

        # Render Table
        st.dataframe(
            df.drop(columns=["_reasoning"]),
            use_container_width=True,
            hide_index=True
        )

        # 3. Expand Reasoning
        st.subheader("Candidate Deep Dive")
        for index, row in df.iterrows():
            with st.expander(f"#{row['Rank']} - {row['Candidate ID']} (Score: {row['Score (0-100)']})"):
                st.markdown("**Recruiter Reasoning:**")
                reasons = row["_reasoning"].split(";")
                for r in reasons:
                    if r.strip():
                        st.markdown(f"- {r.strip()}")
                
                # Breakdown
                cols = st.columns(4)
                cols[0].metric("Skill Match", f"{row['Skill Match']}%")
                cols[1].metric("Exp Match", f"{row['Exp Match']}%")
                cols[2].metric("Semantic Sim", f"{row['Semantics']}%")
                


if __name__ == "__main__":
    init_session_state()
    check_health()
    render_sidebar()
    render_main()
