"""
AI Recruiter Streamlit Dashboard
================================

User interface for the AI Recruiter system.
Displays advanced hackathon-winning intelligence metrics like 
Learning Velocity and Transferable Skill graph matches.
"""

import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="AI Recruiter | Intelligence Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    with st.spinner("Jury Evaluating 100K Candidates (Skill Transfer, Promotion Velocity, FAISS)..."):
        try:
            res = requests.post(f"{API_URL}/api/rank", json={"job_description": jd_text}, timeout=120)
            if res.status_code == 200:
                data = res.json()
                st.session_state.ranked_candidates = data.get("ranked_candidates", [])
                st.success("Evaluation complete! Multi-Agent Jury has reached a verdict.")
            else:
                st.error(f"Error: {res.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")

st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 6px; }
    .metric-box { background-color: #1E1E2E; padding: 15px; border-radius: 8px; border: 1px solid #4CAF50; text-align: center; }
    .metric-title { font-size: 14px; color: #888; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { font-size: 24px; font-weight: bold; color: #fff; }
</style>
""", unsafe_allow_html=True)


def render_sidebar():
    st.sidebar.title("🧠 Multi-Agent Recruiter")
    st.sidebar.markdown(f"**Status:** {st.session_state.api_status}")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Active Intelligence Engines")
    st.sidebar.markdown("✅ **Technical Agent** (Skill Graph)")
    st.sidebar.markdown("✅ **Career Agent** (Velocity)")
    st.sidebar.markdown("✅ **Behavioral Agent** (Redrob)")
    st.sidebar.markdown("✅ **Potential Agent** (Learning)")
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Check API Health"):
        check_health()


def render_main():
    st.title("Next-Gen Candidate Intelligence")
    st.markdown("Unlike standard semantic search, this platform builds **Skill Transfer Graphs**, computes **Promotion Velocity**, and uses a **Multi-Agent Jury** to evaluate the 100K candidates just like an elite recruiter would.")

    st.subheader("1. Job Description")
    jd_text = st.text_area("Paste the Job Description here:", height=150, placeholder="We are looking for a Senior AI Engineer...")
    
    if st.button("Unleash the Jury (Rank Candidates)", type="primary"):
        if jd_text.strip():
            rank_candidates(jd_text)
        else:
            st.warning("Please enter a Job Description.")

    if st.session_state.ranked_candidates:
        st.markdown("---")
        st.subheader("2. Jury Verdict (Ranked Shortlist)")
        
        df_data = []
        for i, c in enumerate(st.session_state.ranked_candidates):
            df_data.append({
                "Rank": i + 1,
                "Candidate ID": c["candidate_id"],
                "Jury Score": c["score"],
                "Tech/Skill Match": c["skill_match"],
                "Career Momentum": c["experience_match"],
                "Learning Potential": c.get("potential_score", 0.0),
                "Transferable Skills": c.get("transferable_matches", 0),
                "_reasoning": c["reasoning"] 
            })
            
        df = pd.DataFrame(df_data)
        
        search_col, dl_col = st.columns([3, 1])
        with search_col:
            search_term = st.text_input("Filter Candidates...", placeholder="e.g. CAND_000123")
            if search_term:
                df = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)]

        with dl_col:
            csv_data = []
            for i, c in enumerate(st.session_state.ranked_candidates):
                csv_data.append({
                    "candidate_id": c["candidate_id"],
                    "rank": i + 1,
                    "score": round(c["score"] / 100.0, 4),
                    "reasoning": c["reasoning"].replace('\n', ' ')
                })
            submit_df = pd.DataFrame(csv_data)
            csv_buffer = submit_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Official Submission CSV",
                data=csv_buffer,
                file_name="submission.csv",
                mime="text/csv"
            )

        # Highlight highest potential in table
        st.dataframe(
            df.drop(columns=["_reasoning"]),
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Deep Dive Intelligence")
        for index, row in df.iterrows():
            with st.expander(f"#{row['Rank']} | {row['Candidate ID']} | Overall Score: {row['Jury Score']}"):
                st.markdown("**Jury Reasoning:**")
                reasons = row["_reasoning"].split(";")
                for r in reasons:
                    if r.strip():
                        st.markdown(f"- {r.strip()}")
                
                # HTML Metric Boxes for Innovation Look
                cols = st.columns(4)
                cols[0].markdown(f"<div class='metric-box'><div class='metric-title'>Technical Match</div><div class='metric-value'>{row['Tech/Skill Match']}%</div></div>", unsafe_allow_html=True)
                cols[1].markdown(f"<div class='metric-box'><div class='metric-title'>Career Momentum</div><div class='metric-value'>{row['Career Momentum']}%</div></div>", unsafe_allow_html=True)
                cols[2].markdown(f"<div class='metric-box'><div class='metric-title'>Learning Potential</div><div class='metric-value'>{row['Learning Potential']}%</div></div>", unsafe_allow_html=True)
                cols[3].markdown(f"<div class='metric-box'><div class='metric-title'>Transferable Skills</div><div class='metric-value'>{row['Transferable Skills']} Adjacent</div></div>", unsafe_allow_html=True)
                st.write("")

if __name__ == "__main__":
    init_session_state()
    check_health()
    render_sidebar()
    render_main()
