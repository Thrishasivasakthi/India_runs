"""
Redrob AI — Intelligent Candidate Discovery & Ranking Dashboard
Streamlit demo for hackathon submission.
Run: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import sys
import time

# ─── Page Config ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Redrob AI — Candidate Ranking Engine",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { color: white; margin-bottom: 0.3rem; font-size: 2rem; }
    .main-header p { color: #a0aec0; margin: 0; font-size: 1rem; }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .metric-card h3 { color: #2d3748; font-size: 0.85rem; margin: 0 0 0.3rem 0; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-card .value { color: #1a365d; font-size: 2rem; font-weight: 700; }
    .metric-card .sub { color: #718096; font-size: 0.8rem; }
    .rank-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .rank-1 { background: #ffd700; color: #000; }
    .rank-2 { background: #c0c0c0; color: #000; }
    .rank-3 { background: #cd7f32; color: #fff; }
    .rank-top10 { background: #ebf8ff; color: #2b6cb0; }
    .tech-tag { background: #c6f6d5; color: #22543d; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; }
    .non-tech-tag { background: #fed7d7; color: #9b2c2c; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; }
    .ecs-bar { height: 8px; border-radius: 4px; background: #e2e8f0; }
    .ecs-fill { height: 100%; border-radius: 4px; }
    .section-header { color: #1a365d; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.5rem; margin: 1.5rem 0 1rem 0; }
    div[data-testid="stMetric"] { background: #f7fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; }
    div[data-testid="stMetric"] label { font-size: 0.8rem !important; color: #718096 !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { font-size: 1.5rem !important; color: #1a365d !important; }
</style>
""", unsafe_allow_html=True)


# ─── Data Loading ───────────────────────────────────────────────────────
@st.cache_data
def load_ranked(path):
    return pd.read_csv(path)


@st.cache_data
def load_candidates(jsonl_path):
    cands = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            cands.append(json.loads(line.strip()))
    return cands


def find_files():
    """Auto-detect data files."""
    data_dir = None
    csv_path = None
    jsonl_path = None
    jd_path = None

    for root, dirs, files in os.walk(os.path.dirname(os.path.abspath(__file__))):
        for f in files:
            if f == "candidates.jsonl" and not jsonl_path:
                jsonl_path = os.path.join(root, f)
                data_dir = root
            if f == "ranked_candidates.csv" and not csv_path:
                csv_path = os.path.join(root, f)
            if "job_description" in f.lower() and not jd_path:
                jd_path = os.path.join(root, f)
        if jsonl_path:
            break

    # Also check common locations
    if not jsonl_path:
        base = os.path.dirname(os.path.abspath(__file__))
        for sub in ["", "data", "."]:
            for root, dirs, files in os.walk(os.path.join(base, sub) if sub else base):
                for f in files:
                    if f == "candidates.jsonl" and not jsonl_path:
                        jsonl_path = os.path.join(root, f)
                        data_dir = root
                    if f == "ranked_candidates.csv" and not csv_path:
                        csv_path = os.path.join(root, f)
                if jsonl_path:
                    break
            if jsonl_path:
                break

    return data_dir, csv_path, jsonl_path, jd_path


# ─── Main ───────────────────────────────────────────────────────────────
def main():
    data_dir, csv_path, jsonl_path, jd_path = find_files()

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Redrob AI — Candidate Ranking Engine</h1>
        <p>Intelligent Candidate Discovery & Ranking Challenge | 4-Axis Evidence Consistency + LightGBM + Twin Resolution</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.markdown("## 🎛️ Controls")

    if csv_path:
        df = load_ranked(csv_path)
        st.sidebar.success(f"Loaded {len(df)} ranked candidates")
    else:
        st.sidebar.error("No ranked_candidates.csv found. Run `python rank.py` first.")
        st.stop()

    candidates_map = {}
    if jsonl_path:
        candidates = load_candidates(jsonl_path)
        candidates_map = {c["candidate_id"]: c for c in candidates}
        st.sidebar.info(f"Loaded {len(candidates_map)} raw candidates")

    # Show/hide sections
    show_architecture = st.sidebar.checkbox("Show Architecture", True)
    show_charts = st.sidebar.checkbox("Show Analytics Charts", True)
    show_top_n = st.sidebar.slider("Show Top N candidates", 10, 100, 20)

    # ─── Metrics Row ────────────────────────────────────────────────────
    st.markdown('<h2 class="section-header">📊 Pipeline Results</h2>', unsafe_allow_html=True)

    tech_kw = ["engineer", "scientist", "architect", "developer", "sre",
                "machine learning", "data scientist", "ai ", "ml ", "nlp",
                "deep learning", "computer vision", "researcher"]
    tech_count = sum(1 for _, r in df.iterrows()
                     if any(k in str(candidates_map.get(r["candidate_id"], {})
                                     .get("profile", {})
                                     .get("current_title", "")).lower() for k in tech_kw))

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Ranked", f"{len(df)}")
    with col2:
        st.metric("Technical Roles", f"{tech_count}", f"{tech_count}%")
    with col3:
        st.metric("Non-Technical", f"{len(df) - tech_count}")
    with col4:
        avg_ecs = df.get("score", pd.Series([0])).mean()
        st.metric("Mean Score", f"{avg_ecs:.4f}")
    with col5:
        honeypots = sum(1 for _, r in df.head(100).iterrows()
                        if any(k in str(candidates_map.get(r["candidate_id"], {})
                                        .get("profile", {})
                                        .get("current_title", "")).lower()
                               for k in ["hr", "human resource", "accountant", "sales",
                                         "content writer", "designer"]))
        st.metric("Honeypots (Top 100)", f"{honeypots}", "0% target")

    # ─── Architecture ───────────────────────────────────────────────────
    if show_architecture:
        st.markdown('<h2 class="section-header">🏗️ Architecture</h2>', unsafe_allow_html=True)

        arch_col1, arch_col2 = st.columns([2, 1])
        with arch_col1:
            st.markdown("""
            ```
            ┌─────────────┐    ┌──────────────┐    ┌───────────────┐
            │  100K JSONL  │───▶│ 75 Features  │───▶│ 4-Axis ECS    │
            │  Candidates  │    │ + JD Match   │    │ (Geo. Mean)   │
            └─────────────┘    └──────────────┘    └───────┬───────┘
                                                           │
            ┌─────────────┐    ┌──────────────┐    ┌───────▼───────┐
            │  Ranked Top  │◀──│ MMR Diversity│◀──│ LightGBM +    │
            │  100 + CSV   │    │ + Twin Res.  │    │ Heuristic     │
            └─────────────┘    └──────────────┘    └───────────────┘
            ```
            """)

        with arch_col2:
            st.markdown("""
            **Pipeline Stages:**

            1. **Feature Extraction** — 75 features from JSONL
            2. **ECS Computation** — 4 axes, geometric mean
            3. **Semantic JD Match** — sentence-transformers
            4. **Heuristic Score** — weighted component blend
            5. **LightGBM LambdaMART** — learning-to-rank
            6. **Twin Resolution** — cluster-based comparison
            7. **MMR Diversity** — greedy archetype selection
            8. **Counterfactuals** — decision explanations
            """)

    # ─── Score Distribution ─────────────────────────────────────────────
    if show_charts:
        st.markdown('<h2 class="section-header">📈 Analytics</h2>', unsafe_allow_html=True)

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            fig_hist = px.histogram(
                df, x="score", nbins=40,
                title="Score Distribution (All 100 Ranked)",
                labels={"score": "Final Score"},
                color_discrete_sequence=["#3182ce"],
            )
            fig_hist.update_layout(
                height=320, margin=dict(l=40, r=20, t=40, b=40),
                xaxis_title="Score", yaxis_title="Count",
                bargap=0.1,
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        with chart_col2:
            # Top titles
            titles = []
            for _, r in df.head(50).iterrows():
                c = candidates_map.get(r["candidate_id"], {})
                t = c.get("profile", {}).get("current_title", "Unknown")
                titles.append(t)
            title_counts = pd.Series(titles).value_counts().head(10)
            fig_titles = px.bar(
                x=title_counts.values, y=title_counts.index,
                orientation="h",
                title="Top 10 Job Titles (Top 50 Candidates)",
                labels={"x": "Count", "y": "Title"},
                color_discrete_sequence=["#38a169"],
            )
            fig_titles.update_layout(
                height=320, margin=dict(l=40, r=20, t=40, b=40),
                yaxis=dict(autorange="reversed"),
            )
            st.plotly_chart(fig_titles, use_container_width=True)

        chart_col3, chart_col4 = st.columns(2)

        with chart_col3:
            # Score vs Rank
            fig_scatter = px.scatter(
                df, x="rank", y="score",
                title="Score vs Rank",
                labels={"rank": "Rank", "score": "Score"},
                color_discrete_sequence=["#805ad5"],
                hover_data=["candidate_id"],
            )
            fig_scatter.update_traces(marker=dict(size=6, opacity=0.7))
            fig_scatter.update_layout(
                height=320, margin=dict(l=40, r=20, t=40, b=40),
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        with chart_col4:
            # Experience distribution of top 50
            yoes = []
            for _, r in df.head(50).iterrows():
                c = candidates_map.get(r["candidate_id"], {})
                y = c.get("profile", {}).get("years_of_experience", 0)
                yoes.append(y)
            fig_yoe = px.histogram(
                x=yoes, nbins=15,
                title="Years of Experience (Top 50)",
                labels={"x": "Years"},
                color_discrete_sequence=["#d69e2e"],
            )
            fig_yoe.update_layout(
                height=320, margin=dict(l=40, r=20, t=40, b=40),
                xaxis_title="Years of Experience", yaxis_title="Count",
            )
            st.plotly_chart(fig_yoe, use_container_width=True)

    # ─── Candidate Table ────────────────────────────────────────────────
    st.markdown(f'<h2 class="section-header">🏆 Top {show_top_n} Candidates</h2>', unsafe_allow_html=True)

    # Search box
    search = st.text_input("🔍 Search candidates by name, title, or skills...")

    display_df = df.head(show_top_n).copy()
    display_df["title"] = display_df["candidate_id"].map(
        lambda x: candidates_map.get(x, {}).get("profile", {}).get("current_title", "Unknown")
    )
    display_df["yoe"] = display_df["candidate_id"].map(
        lambda x: candidates_map.get(x, {}).get("profile", {}).get("years_of_experience", 0)
    )
    display_df["skills_list"] = display_df["candidate_id"].map(
        lambda x: ", ".join([s.get("skill", "") if isinstance(s, dict) else str(s)
                             for s in candidates_map.get(x, {}).get("skills", [])[:5]])
    )

    if search:
        mask = (
            display_df["title"].str.contains(search, case=False, na=False) |
            display_df["candidate_id"].str.contains(search, case=False, na=False) |
            display_df["skills_list"].str.contains(search, case=False, na=False)
        )
        display_df = display_df[mask]

    # Format for display
    stlyed_df = display_df[["rank", "candidate_id", "title", "yoe", "score", "reasoning", "skills_list"]].copy()
    stlyed_df.columns = ["Rank", "Candidate ID", "Title", "YoE", "Score", "Reasoning", "Top Skills"]

    st.dataframe(
        stlyed_df,
        use_container_width=True,
        height=min(400, 40 + len(stlyed_df) * 35),
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", width="small"),
            "Score": st.column_config.NumberColumn("Score", format="%.4f", width="small"),
            "YoE": st.column_config.NumberColumn("YoE", format="%.1f yrs", width="small"),
            "Reasoning": st.column_config.TextColumn("Reasoning", width="large"),
            "Top Skills": st.column_config.TextColumn("Top Skills", width="medium"),
        },
    )

    # ─── Candidate Detail ───────────────────────────────────────────────
    st.markdown('<h2 class="section-header">🔍 Candidate Deep Dive</h2>', unsafe_allow_html=True)

    candidate_ids = [r["candidate_id"] for _, r in df.head(100).iterrows()]
    selected_id = st.selectbox("Select a candidate to inspect:", candidate_ids)

    if selected_id:
        c = candidates_map.get(selected_id, {})
        profile = c.get("profile", {})
        rank_row = df[df["candidate_id"] == selected_id].iloc[0]

        det_col1, det_col2 = st.columns([1, 1])

        with det_col1:
            st.markdown(f"### {profile.get('current_title', 'Unknown')}")
            st.markdown(f"**Candidate ID:** `{selected_id}`")
            st.markdown(f"**Rank:** #{int(rank_row['rank'])} | **Score:** {rank_row['score']:.4f}")
            st.markdown(f"**Experience:** {profile.get('years_of_experience', 0)} years")
            st.markdown(f"**Summary:** {profile.get('summary', 'N/A')[:500]}")

        with det_col2:
            st.markdown("### Key Signals")

            signals_data = {
                "ECS Score": f"{rank_row.get('ecs', 0):.3f}" if 'ecs' in rank_row else "N/A",
                "JD Similarity": f"{rank_row.get('jd_similarity', 0):.3f}" if 'jd_similarity' in rank_row else "N/A",
                "Response Rate": f"{candidates_map.get(selected_id, {}).get('redrob_signals', {}).get('response_rate', 0):.0%}",
                "Interview Rate": f"{candidates_map.get(selected_id, {}).get('redrob_signals', {}).get('interview_completion', 0):.0%}",
            }
            for k, v in signals_data.items():
                st.markdown(f"**{k}:** {v}")

            skills = c.get("skills", [])
            if skills:
                skill_text = ", ".join([s.get("skill", "") if isinstance(s, dict) else str(s) for s in skills[:10]])
                st.markdown(f"**Skills:** {skill_text}")

            st.markdown(f"**Reasoning:** {rank_row['reasoning']}")

    # ─── Methodology ────────────────────────────────────────────────────
    st.markdown('<h2 class="section-header">📐 Methodology</h2>', unsafe_allow_html=True)

    meth_col1, meth_col2, meth_col3 = st.columns(3)

    with meth_col1:
        st.markdown("""
        **4-Axis Evidence Consistency Score (ECS)**

        We verify candidate claims from 4 independent angles:
        - **Claim-Assessment**: Do self-reported skills match assessment scores?
        - **Claim-Experience**: Does career history support claimed expertise?
        - **Claim-Corroboration**: Are claims backed by GitHub, publications, projects?
        - **Seniority-Trajectory**: Does career progression match claimed level?

        ECS uses **geometric mean** (not additive) — one contradiction kills the score.
        """)

    with meth_col2:
        st.markdown("""
        **Ranking Pipeline**

        - **Feature Extraction**: 75 features from JSONL profiles
        - **Semantic JD Match**: sentence-transformers cosine similarity
        - **Heuristic Score**: Weighted blend of ECS, skills, engagement, experience
        - **LightGBM LambdaMART**: Learning-to-rank on weak supervision labels
        - **Twin Resolution**: KMeans clustering + counterfactual generation
        - **MMR Diversity**: Greedy selection for archetype diversity
        """)

    with meth_col3:
        st.markdown("""
        **Honeypot Detection**

        Automatic penalties for impossible profiles:
        - YoE claimed > 3 but career history < 1 year
        - Expert-level skills with < 2 years experience
        - 50+ skills listed (keyword stuffing)
        - Expert claims with zero assessments + zero GitHub

        **Tie-breaking**: Equal scores sorted by candidate_id ascending.
        """)

    # ─── Footer ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        "*Built for the Redrob Intelligent Candidate Discovery & Ranking Challenge | "
        "CPU-only, no GPU, no network | Runtime: <5 min*"
    )


if __name__ == "__main__":
    main()
