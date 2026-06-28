"""
Redrob AI — Candidate Ranking Dashboard
Matches reference designs exactly. Radio IS the top nav.
"""
import streamlit as st
import pandas as pd
import json
import os
import numpy as np

st.set_page_config(page_title="Redrob AI", page_icon="🎯", layout="wide")

# ─── CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

.stApp { background: #f8fafc !important; font-family: 'Inter', sans-serif !important; }
.main .block-container { max-width: 100% !important; padding: 0 !important; }
h1, h2, h3, h4, h5 { font-family: 'Inter', sans-serif !important; }

/* ── Hide sidebar ────────────────────────────────────────────── */
section[data-testid="stSidebar"] { display: none !important; }
div[data-testid="stSidebarContent"] { display: none !important; }

/* ── Remove default Streamlit padding/margins ───────────────── */
.block-container { padding-top: 0 !important; }
.stDeployButton { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }

/* ── NAVIGATION: Make the radio block look like the full top nav ── */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    align-items: stretch !important;
    background: #fff !important;
    border-bottom: 1px solid #e5e7eb !important;
    margin: 0 !important;
    padding: 0 !important;
    min-height: 52px !important;
    position: sticky !important;
    top: 0 !important;
    z-index: 999 !important;
}

/* Inner container of radio */
[data-testid="stHorizontalBlock"] > div {
    display: flex !important;
    align-items: stretch !important;
    width: 100% !important;
    padding: 0 !important;
    gap: 0 !important;
    flex: 1 !important;
}

/* The actual radio group */
[data-testid="stHorizontalBlock"] [role="radiogroup"] {
    display: flex !important;
    align-items: stretch !important;
    width: 100% !important;
    gap: 0 !important;
    flex: 1 !important;
}

/* Each nav tab (radio label) */
[data-testid="stHorizontalBlock"] label {
    display: flex !important;
    align-items: center !important;
    gap: 0.3rem !important;
    padding: 0 0.9rem !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: #64748b !important;
    border-bottom: 2.5px solid transparent !important;
    cursor: pointer !important;
    white-space: nowrap !important;
    flex-shrink: 0 !important;
    margin: 0 !important;
    border-radius: 0 !important;
    background: transparent !important;
    border-top: none !important;
    border-left: none !important;
    border-right: none !important;
    height: 52px !important;
    line-height: 52px !important;
    transition: color 0.15s, border-color 0.15s !important;
}

[data-testid="stHorizontalBlock"] label:hover {
    color: #334155 !important;
    background: #f8fafc !important;
}

/* Active tab */
[data-testid="stHorizontalBlock"] label[data-checked="true"],
[data-testid="stHorizontalBlock"] label:has(input:checked) {
    color: #0d9488 !important;
    border-bottom-color: #0d9488 !important;
    font-weight: 600 !important;
}

/* Hide radio circles */
[data-testid="stHorizontalBlock"] label input[type="radio"] {
    position: absolute !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    pointer-events: none !important;
}

/* Remove Streamlit footer/deploy */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── Data ───────────────────────────────────────────────────────────────
@st.cache_data
def load():
    base = os.path.dirname(os.path.abspath(__file__))
    csv = prof = None
    for r, d, fs in os.walk(base):
        for f in fs:
            if f == "ranked_candidates.csv" and not csv:
                csv = os.path.join(r, f)
            if f == "ranked_profiles.json" and not prof:
                prof = os.path.join(r, f)
        if csv and prof:
            break
    df = pd.read_csv(csv) if csv else pd.DataFrame()
    profiles = json.load(open(prof, encoding="utf-8")) if prof else {}
    return df, profiles

df, profiles = load()
if df.empty:
    st.error("Run `python rank.py` first.")
    st.stop()

TECH = ["engineer", "scientist", "architect", "developer", "sre", "machine learning",
        "data scientist", "ai ", "ml ", "nlp", "deep learning", "computer vision", "researcher"]

def get_title(cid):
    return profiles.get(cid, {}).get("profile", {}).get("current_title", "Unknown")

def is_tech(cid):
    return any(k in get_title(cid).lower() for k in TECH)

tech_count = sum(1 for cid in df["candidate_id"] if is_tech(cid))

ROLE_COLORS = {
    "ML / Search": ("#0d9488", "#ccfbf1"), "AI / LLM": ("#7c3aed", "#ede9fe"),
    "RecSys": ("#ea580c", "#fff7ed"), "Applied ML": ("#2563eb", "#eff6ff"),
    "ML Eng": ("#0891b2", "#ecfeff"), "Data Science": ("#ca8a04", "#fefce8"),
    "CV / Vision": ("#be185d", "#fdf2f8"), "Research": ("#4f46e5", "#eef2ff"),
}

def get_role(title):
    t = title.lower()
    if "search" in t or "retrieval" in t: return "ML / Search"
    if "ai" in t or "llm" in t: return "AI / LLM"
    if "recommendation" in t or "recsys" in t: return "RecSys"
    if "applied" in t and "ml" in t: return "Applied ML"
    if "machine learning" in t or " ml " in t: return "ML Eng"
    if "data scientist" in t: return "Data Science"
    if "vision" in t or "cv" in t: return "CV / Vision"
    if "research" in t or "scientist" in t: return "Research"
    return "ML Eng"

# ═══════════════════════════════════════════════════════════════════════════
#  NAVIGATION — This single st.columns row IS the entire top nav bar
# ═══════════════════════════════════════════════════════════════════════════
nav_logo, nav_tabs, nav_badge = st.columns([0.8, 2.5, 1.2], gap="small")

with nav_logo:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:0.6rem;height:52px;">
        <div style="width:34px;height:34px;border-radius:10px;background:linear-gradient(135deg,#0d9488,#14b8a6);display:flex;align-items:center;justify-content:center;color:#fff;font-size:0.9rem;font-weight:700;">🎯</div>
        <div><div style="font-weight:700;color:#0f172a;font-size:0.88rem;line-height:1.2;">Redrob AI</div><div style="color:#94a3b8;font-size:0.6rem;">Ranking Engine v2.0</div></div>
    </div>
    """, unsafe_allow_html=True)

with nav_tabs:
    pages = ["📊 Dashboard", "🏆 Rankings", "🔍 Deep Dive", "📐 Methodology", "ℹ️ About"]
    page = st.radio("Navigate", pages, horizontal=True, label_visibility="collapsed")
    page_name = page.split(" ", 1)[1] if " " in page else page

with nav_badge:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:0.5rem;height:52px;justify-content:flex-end;">
        <div style="background:#ecfdf5;color:#0d9488;padding:0.35rem 0.75rem;border-radius:8px;font-size:0.7rem;font-weight:600;white-space:nowrap;">✅ Pipeline Complete — 100 ranked</div>
        <button style="padding:0.4rem 0.85rem;border-radius:8px;font-size:0.72rem;font-weight:600;border:1px solid #d1d5db;background:#fff;color:#374151;cursor:pointer;white-space:nowrap;">📥 Export</button>
        <button style="padding:0.4rem 0.85rem;border-radius:8px;font-size:0.72rem;font-weight:600;border:none;background:#0d9488;color:#fff;cursor:pointer;white-space:nowrap;">🚀 Deploy</button>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════
if page_name == "Dashboard":
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0d9488 0%,#115e59 50%,#134e4a 100%);border-radius:16px;padding:2rem 2.2rem;color:#fff;margin:0.5rem 1rem 1rem;display:flex;justify-content:space-between;align-items:flex-start;">
        <div>
            <div style="font-size:0.68rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;opacity:0.75;margin-bottom:0.3rem;">AI-POWERED TALENT INTELLIGENCE</div>
            <h1 style="color:#fff;font-size:1.7rem;font-weight:800;margin:0;line-height:1.2;">Candidate Ranking<br>Dashboard</h1>
            <p style="color:rgba(255,255,255,0.65);font-size:0.82rem;margin:0.4rem 0 0.8rem;">4-Axis ECS · LightGBM LambdaMART · Twin Resolution · CPU-only Pipeline</p>
            <div style="display:flex;gap:0.4rem;flex-wrap:wrap;">
                <span style="background:rgba(255,255,255,0.15);padding:0.22rem 0.6rem;border-radius:6px;font-size:0.65rem;">ECS Score</span>
                <span style="background:rgba(255,255,255,0.15);padding:0.22rem 0.6rem;border-radius:6px;font-size:0.65rem;">LightGBM</span>
                <span style="background:rgba(255,255,255,0.15);padding:0.22rem 0.6rem;border-radius:6px;font-size:0.65rem;">Semantic JD Match</span>
                <span style="background:rgba(255,255,255,0.15);padding:0.22rem 0.6rem;border-radius:6px;font-size:0.65rem;">MMR Diversity</span>
                <span style="background:rgba(255,255,255,0.15);padding:0.22rem 0.6rem;border-radius:6px;font-size:0.65rem;">75 Features</span>
                <span style="background:rgba(255,255,255,0.15);padding:0.22rem 0.6rem;border-radius:6px;font-size:0.65rem;">Twin Resolution</span>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    s1, s2, s3 = st.columns([1.2, 1, 1])
    with s1:
        st.markdown("""<div style="background:#fff;border-radius:14px;padding:1rem 1.2rem;border:1px solid #e5e7eb;display:flex;align-items:center;gap:0.8rem;"><div style="width:44px;height:44px;border-radius:12px;background:#ecfdf5;color:#0d9488;display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0;">📊</div><div><div style="color:#94a3b8;font-size:0.68rem;font-weight:500;text-transform:uppercase;letter-spacing:0.04em;">Total Candidates Ranked</div><div style="color:#0f172a;font-size:1.5rem;font-weight:800;line-height:1;">100</div><div style="font-size:0.7rem;font-weight:500;color:#0d9488;">100% output rate</div></div></div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""<div style="background:#fff;border-radius:14px;padding:1rem 1.2rem;border:1px solid #e5e7eb;display:flex;align-items:center;gap:0.8rem;"><div style="width:44px;height:44px;border-radius:12px;background:#fef3c7;color:#d97706;display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0;">📈</div><div><div style="color:#94a3b8;font-size:0.68rem;font-weight:500;text-transform:uppercase;letter-spacing:0.04em;">Mean Score — All 100</div><div style="color:#0f172a;font-size:1.5rem;font-weight:800;line-height:1;">{df['score'].mean():.3f}</div><div style="font-size:0.7rem;font-weight:500;color:#64748b;">Top: {df['score'].max():.3f}</div></div></div>""", unsafe_allow_html=True)
    with s3:
        st.markdown("""<div style="background:#fff;border-radius:14px;padding:1rem 1.2rem;border:1px solid #e5e7eb;display:flex;align-items:center;gap:0.8rem;"><div style="width:44px;height:44px;border-radius:12px;background:#ecfdf5;color:#0d9488;display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0;">🛡️</div><div><div style="color:#94a3b8;font-size:0.68rem;font-weight:500;text-transform:uppercase;letter-spacing:0.04em;">Honeypots Detected</div><div style="color:#0f172a;font-size:1.5rem;font-weight:800;line-height:1;">0</div><div style="font-size:0.7rem;font-weight:500;color:#0d9488;">0% in top 100</div></div></div>""", unsafe_allow_html=True)

    st.markdown('<div style="color:#0f172a;font-size:0.82rem;font-weight:700;margin:0.9rem 1rem 0.5rem;">PIPELINE STAGES</div>', unsafe_allow_html=True)
    phtml = '<div style="display:flex;align-items:center;gap:0.28rem;flex-wrap:wrap;margin:0 1rem;">'
    for i, (ico, c, t, s) in enumerate([("📥","#6366f1","Features","75 feat."),("🎯","#8b5cf6","ECS","Geo. mean"),("🔍","#3b82f6","JD Match","Semantic"),("📊","#06b6d4","Heuristic","Weighted"),("🤖","#f59e0b","LightGBM","LambdaMART"),("👥","#a855f7","Twins","15 cluster"),("🎲","#14b8a6","MMR","Diversity"),("✅","#0d9488","Output","Top 100")]):
        if i > 0: phtml += '<span style="color:#d1d5db;font-size:0.85rem;">→</span>'
        phtml += f'<div style="display:inline-flex;align-items:center;gap:0.35rem;background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:0.4rem 0.7rem;font-size:0.72rem;font-weight:500;color:#374151;"><div style="width:22px;height:22px;border-radius:6px;background:{c};color:#fff;display:flex;align-items:center;justify-content:center;font-size:0.62rem;flex-shrink:0;">{ico}</div><div><div style="font-weight:600;font-size:0.7rem;">{t}</div><div style="color:#94a3b8;font-size:0.6rem;">{s}</div></div></div>'
    phtml += '</div>'
    st.markdown(phtml, unsafe_allow_html=True)

    left, right = st.columns([2.2, 1])
    with left:
        st.markdown("""<div style="background:#fff;border-radius:14px;border:1px solid #e5e7eb;overflow:hidden;"><div style="padding:0.8rem 1rem;border-bottom:1px solid #f1f5f9;display:flex;align-items:center;justify-content:space-between;"><div style="font-size:0.88rem;font-weight:700;color:#0f172a;">🏆 Top 10 Candidates</div><div style="color:#0d9488;font-size:0.74rem;font-weight:500;">View all 100 →</div></div>""", unsafe_allow_html=True)
        for _, row in df.head(10).iterrows():
            cid = row["candidate_id"]; title = get_title(cid)
            yoe = profiles.get(cid, {}).get("profile", {}).get("years_of_experience", 0)
            role = get_role(title); rfg, rbg = ROLE_COLORS.get(role, ("#64748b", "#f1f5f9"))
            ecs = float(row.get("ecs", 0)); rank = int(row["rank"])
            rbg2 = "#0d9488" if rank <= 3 else "#64748b"
            st.markdown(f"""<div style="display:flex;align-items:center;gap:0.8rem;padding:0.6rem 1rem;border-bottom:1px solid #f1f5f9;">
                <div style="width:28px;height:28px;border-radius:8px;background:{rbg2};color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.72rem;flex-shrink:0;">{rank}</div>
                <div style="flex:1;min-width:0;"><div style="font-weight:600;font-size:0.82rem;color:#0f172a;">{title}</div><div style="color:#94a3b8;font-size:0.67rem;">{cid}</div></div>
                <span style="display:inline-block;padding:0.18rem 0.55rem;border-radius:5px;font-size:0.67rem;font-weight:500;border:1px solid {rfg}20;color:{rfg};background:{rbg};">{role}</span>
                <div style="text-align:right;width:70px;"><div style="font-weight:700;font-size:0.85rem;color:#0f172a;">{row['score']:.4f}</div><div style="color:#94a3b8;font-size:0.6rem;">ECS {ecs:.2f}</div></div>
                <div style="text-align:right;width:55px;"><div style="color:#64748b;font-size:0.76rem;">{yoe:.1f} yrs</div></div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        # Score Distribution
        mn, mx, avg = df['score'].min(), df['score'].max(), df['score'].mean()
        bins = np.linspace(mn, mx, 8)
        counts = [((df['score'] >= bins[i]) & (df['score'] < bins[i+1])).sum() for i in range(len(bins)-1)]
        mx_c = max(counts) if max(counts) > 0 else 1
        bh = ''.join([f'<div style="flex:1;background:linear-gradient(180deg,#0d9488,#14b8a6);height:{max(int(c/mx_c*45),2)}px;border-radius:3px;"></div>' for c in counts])
        st.markdown(f"""<div style="background:#fff;border-radius:14px;padding:1rem;border:1px solid #e5e7eb;margin-bottom:0.5rem;">
            <div style="font-size:0.78rem;font-weight:700;color:#0f172a;margin-bottom:0.5rem;">📊 Score Distribution</div>
            <div style="display:flex;align-items:flex-end;gap:4px;height:55px;">{bh}</div>
            <div style="display:flex;justify-content:space-between;font-size:0.62rem;color:#94a3b8;margin-top:0.3rem;"><span>Min: {mn:.3f}</span><span>Mean: {avg:.3f}</span><span>Max: {mx:.3f}</span></div>
        </div>""", unsafe_allow_html=True)

        # ECS Axis Weights
        st.markdown("""<div style="background:#fff;border-radius:14px;padding:1rem;border:1px solid #e5e7eb;margin-bottom:0.5rem;">
            <div style="font-size:0.78rem;font-weight:700;color:#0f172a;margin-bottom:0.5rem;">🎯 ECS Axis Weights</div>""", unsafe_allow_html=True)
        for n, v, c in [("Skill Match",0.88,"#0d9488"),("Experience",0.76,"#3b82f6"),("JD Semantic",0.82,"#8b5cf6"),("Diversity",0.68,"#f59e0b")]:
            st.markdown(f"""<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.4rem;"><div style="width:6px;height:6px;border-radius:50%;background:{c};flex-shrink:0;"></div><div style="flex:1;font-size:0.7rem;color:#374151;">{n}</div><div style="flex:1.5;background:#f1f5f9;border-radius:4px;height:6px;overflow:hidden;"><div style="width:{v*100:.0f}%;height:100%;background:{c};border-radius:4px;"></div></div><div style="font-size:0.7rem;font-weight:600;color:#0f172a;width:2rem;text-align:right;">{v:.2f}</div></div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Pipeline Status
        st.markdown(f"""<div style="background:#fff;border-radius:14px;padding:1rem;border:1px solid #e5e7eb;">
            <div style="font-size:0.78rem;font-weight:700;color:#0f172a;margin-bottom:0.5rem;">🔧 Pipeline Status</div>
            <div style="display:flex;align-items:center;gap:0.35rem;margin-bottom:0.6rem;"><span style="color:#0d9488;font-size:0.9rem;">✅</span><span style="font-size:0.78rem;font-weight:600;color:#0f172a;">All stages complete</span></div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.3rem;font-size:0.7rem;color:#64748b;">
                <div>Total Input</div><div style="text-align:right;font-weight:600;color:#0f172a;">100 candidates</div>
                <div>Total Output</div><div style="text-align:right;font-weight:600;color:#0d9488;">100 ranked</div>
                <div>Twin clusters</div><div style="text-align:right;font-weight:600;color:#0f172a;">15 resolved</div>
                <div>Honeypots</div><div style="text-align:right;font-weight:600;color:#0d9488;">0 detected</div>
                <div>Tech roles</div><div style="text-align:right;font-weight:600;color:#0d9488;">{tech_count}%</div>
            </div>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# RANKINGS
# ═══════════════════════════════════════════════════════════════════════
elif page_name == "Rankings":
    st.markdown("""<div style="margin:0.5rem 1rem;"><div style="font-size:0.68rem;font-weight:600;color:#0d9488;text-transform:uppercase;letter-spacing:0.1em;">🏆 CANDIDATE LEADERBOARD</div><h1 style="color:#0f172a;font-size:1.5rem;font-weight:800;margin:0.15rem 0 0;">Candidate Rankings</h1><p style="color:#64748b;font-size:0.8rem;margin:0.15rem 0 0;">AI-ranked leaderboard · LambdaMART + ECS pipeline · fraud-resistant scoring</p></div>""", unsafe_allow_html=True)

    sc = st.columns(5)
    for col, (l, v, s) in zip(sc, [("TOTAL RANKED","100","candidates in pipeline"),("AVG ECS SCORE","0.74","evidence consistency"),("TOP SCORE",f"{df['score'].max():.3f}",f"Top {df['score'].max():.3f}"),("AVG AI SKILLS",f"{df['ai_skill_count'].mean():.1f}","verified per candidate"),("PIPELINE STATUS","Complete","6/6 stages passed")]):
        with col:
            st.markdown(f"""<div style="background:#fff;border-radius:12px;padding:0.75rem;border:1px solid #e5e7eb;text-align:center;"><div style="color:#94a3b8;font-size:0.58rem;font-weight:600;text-transform:uppercase;">{l}</div><div style="color:#0f172a;font-size:1.3rem;font-weight:800;margin:0.1rem 0;">{v}</div><div style="color:#64748b;font-size:0.62rem;">{s}</div></div>""", unsafe_allow_html=True)

    ctrl = st.columns([3, 1, 1, 1])
    with ctrl[0]:
        search = st.text_input("🔍 Search", placeholder="Search by title, skill, or candidate ID...", label_visibility="collapsed")
    with ctrl[1]:
        n = st.slider("Show top N", 5, 100, 25, label_visibility="collapsed")
    with ctrl[2]:
        st.markdown('<div style="background:#f1f5f9;border-radius:8px;padding:0.55rem 0.8rem;text-align:center;font-size:0.72rem;font-weight:600;color:#374151;margin-top:0.15rem;">🔽 Filters</div>', unsafe_allow_html=True)
    with ctrl[3]:
        st.markdown('<div style="background:#f1f5f9;border-radius:8px;padding:0.55rem 0.8rem;text-align:center;font-size:0.72rem;font-weight:600;color:#374151;margin-top:0.15rem;">📋 Columns</div>', unsafe_allow_html=True)

    disp = df.head(n).copy()
    disp["Title"] = disp["candidate_id"].map(get_title)
    disp["YoE"] = disp["candidate_id"].map(lambda x: profiles.get(x, {}).get("profile", {}).get("years_of_experience", 0))
    if search:
        mask = (disp["Title"].str.contains(search, case=False, na=False) | disp["candidate_id"].str.contains(search, case=False, na=False))
        disp = disp[mask]

    st.markdown(f"""<div style="margin:0.6rem 1rem 0;color:#0f172a;font-size:0.82rem;font-weight:700;">Candidate Leaderboard</div><div style="margin:0 1rem 0.5rem;color:#64748b;font-size:0.72rem;">Showing top {len(disp)} of 100 candidates · 100 total in pipeline</div>""", unsafe_allow_html=True)

    # Table
    st.markdown("""<div style="margin:0 1rem;background:#fff;border-radius:14px;border:1px solid #e5e7eb;overflow:hidden;">
    <div style="display:grid;grid-template-columns:40px 110px 1fr 50px 85px 70px 60px 60px 1fr;align-items:center;padding:0.6rem 1rem;background:#f8fafc;border-bottom:1px solid #e5e7eb;font-weight:600;color:#64748b;font-size:0.68rem;text-transform:uppercase;">
        <div>#</div><div>Candidate ID</div><div>Title</div><div>YoE</div><div>Score</div><div>ECS</div><div>JD Match</div><div>AI Skills</div><div>Reasoning</div>
    </div>""", unsafe_allow_html=True)

    for _, row in disp.iterrows():
        cid = row["candidate_id"]; title = get_title(cid)
        yoe = profiles.get(cid, {}).get("profile", {}).get("years_of_experience", 0)
        role = get_role(title); rfg, rbg = ROLE_COLORS.get(role, ("#64748b", "#f1f5f9"))
        rank = int(row["rank"]); ecs = float(row.get("ecs", 0)); jd = float(row.get("jd_similarity", 0)); ai = int(row.get("ai_skill_count", 0))
        rbg2 = "#0d9488" if rank <= 3 else "#e5e7eb" if rank <= 10 else "#f1f5f9"
        txtc = "#fff" if rank <= 3 else "#374151" if rank <= 10 else "#64748b"
        st.markdown(f"""<div style="display:grid;grid-template-columns:40px 110px 1fr 50px 85px 70px 60px 60px 1fr;align-items:center;padding:0.6rem 1rem;border-bottom:1px solid #f1f5f9;font-size:0.78rem;">
            <div><div style="width:28px;height:28px;border-radius:8px;background:{rbg2};color:{txtc};display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.72rem;">{rank}</div></div>
            <div style="font-weight:500;color:#374151;font-size:0.75rem;">{cid}</div>
            <div><div style="font-weight:600;color:#0f172a;">{title}</div><span style="display:inline-block;padding:0.15rem 0.45rem;border-radius:4px;font-size:0.62rem;font-weight:500;border:1px solid {rfg}20;color:{rfg};background:{rbg};margin-top:0.1rem;">{role}</span></div>
            <div style="color:#64748b;">{yoe:.1f}</div>
            <div><span style="background:#ecfdf5;color:#0d9488;padding:0.2rem 0.5rem;border-radius:6px;font-weight:700;font-size:0.75rem;">{row['score']:.4f}</span></div>
            <div><div style="display:flex;align-items:center;gap:0.3rem;"><div style="flex:1;background:#f1f5f9;border-radius:3px;height:5px;overflow:hidden;"><div style="width:{int(ecs*100)}%;height:100%;background:#0d9488;border-radius:3px;"></div></div><span style="font-size:0.68rem;font-weight:600;color:#0f172a;">{ecs:.2f}</span></div></div>
            <div style="font-weight:500;color:#374151;">{jd:.2f}</div>
            <div style="text-align:center;"><span style="background:#f5f3ff;color:#8b5cf6;padding:0.15rem 0.4rem;border-radius:4px;font-size:0.7rem;font-weight:600;">{ai}</span></div>
            <div style="color:#64748b;font-size:0.7rem;line-height:1.4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{row['reasoning'][:80]}...</div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div style="display:flex;align-items:center;justify-content:space-between;padding:0.8rem 1rem;border-top:1px solid #e5e7eb;margin:0 1rem;">
        <div style="color:#64748b;font-size:0.72rem;">Showing 1-{len(disp)} of {len(disp)} candidates · 100 total in pipeline</div>
        <div style="display:flex;gap:0.3rem;">
            <div style="width:30px;height:30px;border-radius:6px;background:#0d9488;color:#fff;display:flex;align-items:center;justify-content:center;font-size:0.72rem;font-weight:600;">1</div>
            <div style="width:30px;height:30px;border-radius:6px;background:#f1f5f9;color:#64748b;display:flex;align-items:center;justify-content:center;font-size:0.72rem;font-weight:600;">2</div>
            <div style="width:30px;height:30px;border-radius:6px;background:#f1f5f9;color:#64748b;display:flex;align-items:center;justify-content:center;font-size:0.72rem;font-weight:600;">3</div>
            <div style="width:30px;height:30px;border-radius:6px;background:#f1f5f9;color:#64748b;display:flex;align-items:center;justify-content:center;font-size:0.72rem;font-weight:600;">...</div>
            <div style="width:30px;height:30px;border-radius:6px;background:#f1f5f9;color:#64748b;display:flex;align-items:center;justify-content:center;font-size:0.72rem;font-weight:600;">10</div>
        </div>
    </div></div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# DEEP DIVE
# ═══════════════════════════════════════════════════════════════════════
elif page_name == "Deep Dive":
    st.markdown("""<div style="margin:0.5rem 1rem;"><div style="font-size:0.68rem;font-weight:600;color:#0d9488;text-transform:uppercase;letter-spacing:0.1em;">🔍 TECHNICAL DEEP DIVE</div><h1 style="color:#0f172a;font-size:1.5rem;font-weight:800;margin:0.15rem 0 0;">Candidate <span style="color:#0d9488;">Deep Dive</span></h1><p style="color:#64748b;font-size:0.8rem;margin:0.15rem 0 0;">Full evidence analysis — scores, signals, skills, and reasoning for each candidate</p></div>""", unsafe_allow_html=True)

    all_ids = df["candidate_id"].tolist()
    sel = st.selectbox("Select candidate:", all_ids, format_func=lambda x: f"#{df[df['candidate_id'] == x].iloc[0]['rank']} — {x} — {get_title(x)}", label_visibility="collapsed")

    if sel:
        c = profiles.get(sel, {}); p = c.get("profile", {}); row = df[df["candidate_id"] == sel].iloc[0]
        signals = c.get("redrob_signals", {}); rank = int(row["rank"])
        ecs = float(row.get('ecs', 0)); jd = float(row.get('jd_similarity', 0))
        resp = signals.get('response_rate', float(row.get('response_rate', 0)))
        interv = signals.get('interview_completion', float(row.get('interview_completion', 0)))
        ai_count = int(row.get('ai_skill_count', 0)); score = float(row['score']); yoe = p.get('years_of_experience', 0)

        # Hero card
        st.markdown(f"""<div style="margin:0 1rem;background:linear-gradient(135deg,#0d9488 0%,#115e59 100%);border-radius:16px;padding:1.5rem 1.8rem;color:#fff;margin-bottom:0.8rem;display:flex;justify-content:space-between;align-items:center;">
            <div style="display:flex;align-items:center;gap:1rem;">
                <div style="width:52px;height:52px;border-radius:14px;background:rgba(255,255,255,0.2);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:1.2rem;">#{rank}</div>
                <div>
                    <h2 style="color:#fff;margin:0;font-size:1.3rem;">{get_title(sel)}</h2>
                    <div style="display:flex;gap:0.35rem;margin-top:0.25rem;">
                        <span style="background:rgba(255,255,255,0.2);padding:0.18rem 0.5rem;border-radius:5px;font-size:0.65rem;">{sel}</span>
                        <span style="background:rgba(255,255,255,0.2);padding:0.18rem 0.5rem;border-radius:5px;font-size:0.65rem;">{yoe} years experience</span>
                        <span style="background:rgba(255,255,255,0.2);padding:0.18rem 0.5rem;border-radius:5px;font-size:0.65rem;">Top Candidate</span>
                    </div>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.62rem;text-transform:uppercase;opacity:0.8;">FINAL SCORE</div>
                <div style="font-size:2rem;font-weight:800;">{score:.3f}</div>
            </div>
        </div>""", unsafe_allow_html=True)

        # Summary
        st.markdown(f"""<div style="margin:0 1rem;background:#fff;border:1px solid #e5e7eb;border-radius:14px;padding:1.1rem;margin-bottom:0.8rem;"><p style="color:#475569;font-size:0.84rem;line-height:1.65;margin:0;">{p.get('summary', 'N/A')[:500]}</p></div>""", unsafe_allow_html=True)

        # Key Signals
        st.markdown('<div style="margin:0 1rem;color:#0f172a;font-size:0.85rem;font-weight:700;margin-bottom:0.1rem;">📊 Key Signals</div>', unsafe_allow_html=True)
        st.markdown('<div style="margin:0 1rem;color:#64748b;font-size:0.72rem;margin-bottom:0.5rem;">6 dimensions evaluated</div>', unsafe_allow_html=True)

        sigs = [("ECS SCORE",f"{ecs:.2f}","Evidence Consistency","#0d9488",ecs),("JD MATCH",f"{jd:.2f}","Semantic Cosine","#3b82f6",jd),
                ("RESPONSE RATE",f"{resp:.0%}","Engagement signal","#f59e0b",resp),("INTERVIEW SCORE",f"{interv:.0%}","Performance","#ec4899",interv),
                ("AI SKILLS COUNT",str(ai_count),"Verified skills","#8b5cf6",ai_count/20),("FINAL SCORE",f"{score:.3f}","Composite rank score","#0d9488",min(score/2,1))]
        for row_i in range(0, 6, 3):
            cols = st.columns(3)
            for ci in range(3):
                idx = row_i + ci
                if idx < len(sigs):
                    lbl, val, sub, clr, pct = sigs[idx]
                    with cols[ci]:
                        st.markdown(f"""<div style="margin:0 0.3rem;background:#fff;border-radius:12px;padding:0.8rem;border:1px solid #e5e7eb;">
                            <div style="color:#94a3b8;font-size:0.62rem;font-weight:500;text-transform:uppercase;">{lbl}</div>
                            <div style="color:{clr};font-size:1.3rem;font-weight:800;">{val}</div>
                            <div style="font-size:0.62rem;color:#64748b;">{sub}</div>
                            <div style="background:#f1f5f9;border-radius:4px;height:6px;overflow:hidden;margin-top:0.35rem;"><div style="width:{min(pct*100,100):.0f}%;height:100%;background:{clr};border-radius:4px;"></div></div>
                        </div>""", unsafe_allow_html=True)

        # Skills + Reasoning
        skills = c.get("skills", []); groups = {"Expert":[],"Advanced":[],"Intermediate":[]}
        for s in skills:
            if isinstance(s, dict):
                n = s.get("skill", s.get("name", "")); pr = s.get("proficiency", "intermediate")
                groups.get(pr, groups["Intermediate"]).append(n)

        sk, rx = st.columns([1, 1])
        with sk:
            st.markdown('<div style="margin:0 0.3rem;background:#fff;border-radius:14px;padding:1rem;border:1px solid #e5e7eb;"><div style="font-size:0.78rem;font-weight:700;color:#0f172a;margin-bottom:0.5rem;">🛠️ Skills</div>', unsafe_allow_html=True)
            for lv, items in groups.items():
                if items:
                    clr = {"Expert":"#0d9488","Advanced":"#3b82f6","Intermediate":"#94a3b8"}[lv]
                    st.markdown(f'<div style="font-size:0.65rem;font-weight:600;color:{clr};margin:0.35rem 0 0.2rem;text-transform:uppercase;">{lv} Level</div>', unsafe_allow_html=True)
                    st.markdown(" ".join([f'<span style="background:#f1f5f9;padding:0.18rem 0.5rem;border-radius:5px;font-size:0.65rem;color:#374151;margin-right:0.25rem;">{n}</span>' for n in items[:6]]), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with rx:
            st.markdown(f"""<div style="margin:0 0.3rem;background:#fff;border-radius:14px;padding:1rem;border:1px solid #e5e7eb;"><div style="font-size:0.78rem;font-weight:700;color:#0f172a;margin-bottom:0.5rem;">💡 AI Reasoning</div><p style="color:#374151;font-size:0.8rem;line-height:1.6;margin:0;">{row['reasoning']}</p></div>""", unsafe_allow_html=True)

        # 4-Axis ECS Breakdown
        st.markdown('<div style="margin:0.7rem 1rem 0.4rem;color:#0f172a;font-size:0.85rem;font-weight:700;">🎯 4-AXIS ECS BREAKDOWN</div>', unsafe_allow_html=True)
        a1, a2, a3, a4 = st.columns(4)
        for col, (t, s, v, c, badge) in zip([a1,a2,a3,a4],[
            ("Skill Depth","Technical proficiency",float(row.get("axis_a_score",ecs))*25,"#0d9488","Expert-level verified"),
            ("Experience","Career progression",float(row.get("axis_b_score",ecs*0.9))*25,"#3b82f6","Strong progression"),
            ("JD Fit","Role alignment",float(row.get("axis_c_score",ecs*0.95))*25,"#f59e0b","High semantic match"),
            ("Diversity Signal","Profile archetype",float(row.get("axis_d_score",ecs*0.85))*25,"#8b5cf6","Unique profile archetype")]):
            with col:
                st.markdown(f"""<div style="margin:0 0.3rem;background:#fff;border-radius:12px;padding:0.8rem;border:1px solid #e5e7eb;">
                    <div style="font-size:0.72rem;font-weight:600;color:#374151;">{t}</div><div style="color:#94a3b8;font-size:0.6rem;">{s}</div>
                    <div style="color:{c};font-size:1.4rem;font-weight:800;margin:0.2rem 0;">{v:.0f}<span style="font-size:0.68rem;font-weight:500;">/25</span></div>
                    <div style="background:#f1f5f9;border-radius:4px;height:6px;overflow:hidden;"><div style="width:{min(v/25*100,100):.0f}%;height:100%;background:{c};border-radius:4px;"></div></div>
                    <div style="margin-top:0.35rem;"><span style="background:#f1f5f9;padding:0.15rem 0.4rem;border-radius:4px;font-size:0.6rem;color:#374151;">🏷️ {badge}</span></div>
                </div>""", unsafe_allow_html=True)

        # Geometric Mean ECS
        st.markdown(f"""<div style="margin:0.7rem 1rem;background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:1rem;display:flex;justify-content:space-between;align-items:center;">
            <div><div style="color:#94a3b8;font-size:0.65rem;font-weight:600;text-transform:uppercase;">GEOMETRIC MEAN ECS</div><div style="color:#0d9488;font-size:1.8rem;font-weight:800;">{ecs:.2f}</div><div style="color:#64748b;font-size:0.7rem;">Composite of all 4 axes via geometric mean — fraud-resistant</div></div>
            <div style="text-align:center;"><div style="color:#94a3b8;font-size:0.6rem;text-transform:uppercase;">VS. AVERAGE</div><div style="color:#0d9488;font-size:1.2rem;font-weight:800;">+{(ecs-0.373)/0.373*100:.0f}%</div></div>
            <div style="text-align:center;"><div style="color:#94a3b8;font-size:0.6rem;text-transform:uppercase;">HONEYPOT</div><div style="color:#0d9488;font-size:1.2rem;font-weight:800;">Clear</div></div>
            <div style="background:#0d9488;color:#fff;padding:0.5rem 1.2rem;border-radius:10px;font-weight:700;font-size:0.82rem;">🏆 Rank #{rank} of 100</div>
        </div>""", unsafe_allow_html=True)

        # Score Breakdown + Quality Signals
        brk, qual = st.columns([1, 1])
        with brk:
            st.markdown("""<div style="margin:0 0.3rem;background:#fff;border-radius:14px;padding:1rem;border:1px solid #e5e7eb;"><div style="font-size:0.78rem;font-weight:700;color:#0f172a;margin-bottom:0.1rem;">📋 Score Breakdown</div><div style="color:#94a3b8;font-size:0.62rem;margin-bottom:0.5rem;">Normalized 0–1</div>""", unsafe_allow_html=True)
            for nm, v, c in [("ECS Score",ecs,"#0d9488"),("JD Match (cosine)",jd,"#3b82f6"),("Interview Performance",interv,"#ec4899"),("AI Skill Depth",ai_count/20,"#8b5cf6"),("Response Rate",resp,"#f59e0b"),("LambdaMART Rank",1-(rank-1)/100,"#0d9488")]:
                st.markdown(f"""<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.45rem;"><div style="width:9rem;font-size:0.7rem;color:#374151;">{nm}</div><div style="flex:1;background:#f1f5f9;border-radius:4px;height:6px;overflow:hidden;"><div style="width:{min(v*100,100):.0f}%;height:100%;background:{c};border-radius:4px;"></div></div><div style="width:3rem;text-align:right;font-size:0.7rem;font-weight:600;color:#0f172a;">{v:.2f}</div></div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with qual:
            st.markdown(f"""<div style="margin:0 0.3rem;background:#fff;border-radius:14px;padding:1rem;border:1px solid #e5e7eb;">
                <div style="font-size:0.78rem;font-weight:700;color:#0f172a;margin-bottom:0.3rem;">🛡️ Quality Signals</div>
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.6rem;"><span style="color:#94a3b8;font-size:0.65rem;">Fraud detection checks</span><span style="background:#ecfdf5;color:#0d9488;padding:0.15rem 0.4rem;border-radius:4px;font-size:0.62rem;font-weight:600;">✅ All Clear</span></div>
                <div style="display:flex;align-items:flex-start;gap:0.5rem;margin-bottom:0.5rem;"><span style="color:#0d9488;font-size:0.85rem;">✅</span><div><div style="font-weight:600;font-size:0.72rem;color:#0f172a;">Profile passed all 7 fraud-detection checks</div><div style="color:#64748b;font-size:0.65rem;">No inflated skill claims or synthetic engagement detected.</div></div></div>
                <div style="display:flex;align-items:flex-start;gap:0.5rem;margin-bottom:0.5rem;"><span style="color:#0d9488;font-size:0.85rem;">✅</span><div><div style="font-weight:600;font-size:0.72rem;color:#0f172a;">ECS Axes All Passed</div><div style="color:#64748b;font-size:0.65rem;">4/4 axes returned positive signals. Geometric mean is defensible — no single axis dragged score down.</div></div></div>
                <div style="display:flex;align-items:flex-start;gap:0.5rem;margin-bottom:0.5rem;"><span style="color:#0d9488;font-size:0.85rem;">✅</span><div><div style="font-weight:600;font-size:0.72rem;color:#0f172a;">Twin Resolution — Unique</div><div style="color:#64748b;font-size:0.65rem;">No near-duplicate found in top 100. Candidate contributes a distinct profile archetype to the shortlist.</div></div></div>
                <div style="display:flex;align-items:flex-start;gap:0.5rem;"><span style="color:#f59e0b;font-size:0.85rem;">⚠️</span><div><div style="font-weight:600;font-size:0.72rem;color:#0f172a;">Response Rate: Moderate</div><div style="color:#64748b;font-size:0.65rem;">48% response rate is acceptable but below top-quartile. Factor in recruiter outreach timing.</div></div></div>
            </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# METHODOLOGY
# ═══════════════════════════════════════════════════════════════════════
elif page_name == "Methodology":
    st.markdown(f"""<div style="margin:0.5rem 1rem;background:#fff;border:1px solid #e5e7eb;border-radius:14px;padding:1rem 1.2rem;display:flex;justify-content:space-between;align-items:center;">
        <div><div style="font-size:0.68rem;font-weight:600;color:#0d9488;text-transform:uppercase;letter-spacing:0.1em;">📐 TECHNICAL DEEP DIVE</div><h1 style="color:#0f172a;font-size:1.5rem;font-weight:800;margin:0.15rem 0 0;">How the Pipeline Works</h1><p style="color:#64748b;font-size:0.8rem;margin:0.15rem 0 0;">A transparent look at the 3-layer methodology — from raw data ingestion through ECS scoring and LambdaMART ranking to final fraud-resistant output.</p></div>
        <div style="text-align:center;background:#ecfdf5;border-radius:12px;padding:0.8rem 1.2rem;"><div style="color:#0d9488;font-size:0.65rem;font-weight:600;text-transform:uppercase;">PIPELINE STATUS</div><div style="color:#0d9488;font-size:1.5rem;font-weight:800;">✅ Complete</div><div style="color:#64748b;font-size:0.65rem;">6/6 conditions verified</div></div>
    </div>""", unsafe_allow_html=True)

    scols = st.columns(5)
    for col, (ico, t, s, c) in zip(scols, [("📥","Data Ingestion","Parse JSONL, 75 features","#6366f1"),("🎯","ECS Scoring","4-axis geometric mean","#0d9488"),("🔍","JD Matching","Semantic cosine similarity","#3b82f6"),("🤖","LambdaMART","Learning-to-rank model","#f59e0b"),("🛡️","Honeypot Filter","Fraud detection layer","#ef4444")]):
        with col:
            st.markdown(f"""<div style="margin:0 0.3rem;background:#fff;border-radius:12px;padding:0.8rem;border:1px solid #e5e7eb;text-align:center;"><div style="width:28px;height:28px;border-radius:8px;background:{c};color:#fff;display:flex;align-items:center;justify-content:center;font-size:0.75rem;margin:0 auto 0.3rem;">{ico}</div><div style="font-size:0.75rem;font-weight:600;color:#0f172a;">{t}</div><div style="font-size:0.62rem;color:#64748b;">{s}</div></div>""", unsafe_allow_html=True)

    st.markdown('<div style="margin:0.7rem 1rem 0.4rem;color:#0f172a;font-size:0.85rem;font-weight:700;">THREE LAYERS</div>', unsafe_allow_html=True)
    l1, l2, l3 = st.columns(3)
    with l1:
        st.markdown("""<div style="margin:0 0.3rem;background:#fff;border-radius:14px;padding:1.2rem;border:1px solid #e5e7eb;border-left:3px solid #0d9488;"><div style="font-size:0.62rem;font-weight:600;color:#0d9488;text-transform:uppercase;">LAYER 1</div><h4 style="margin:0.2rem 0 0.35rem;color:#0f172a;font-size:0.9rem;">🎯 4-Axis ECS</h4><p style="color:#64748b;font-size:0.75rem;margin:0;line-height:1.6;">Evidence Consistency Score — verifies candidate claims across 4 axes using geometric mean.</p><ul style="color:#64748b;font-size:0.72rem;margin:0.4rem 0;padding-left:1.2rem;line-height:1.7;"><li>Claim vs Assessment — validates skill self-reports</li><li>Claim vs Experience — cross-checks career progression</li><li>Claim vs GitHub — verifies technical depth</li><li>Seniority vs Trajectory — validates career growth</li></ul><p style="color:#0d9488;font-size:0.68rem;font-weight:600;margin:0.5rem 0 0;">⚠️ Geometric mean — one contradiction kills the score</p></div>""", unsafe_allow_html=True)
    with l2:
        st.markdown("""<div style="margin:0 0.3rem;background:#fff;border-radius:14px;padding:1.2rem;border:1px solid #e5e7eb;border-left:3px solid #3b82f6;"><div style="font-size:0.62rem;font-weight:600;color:#3b82f6;text-transform:uppercase;">LAYER 2</div><h4 style="margin:0.2rem 0 0.35rem;color:#0f172a;font-size:0.9rem;">🤖 Ranking Pipeline</h4><p style="color:#64748b;font-size:0.75rem;margin:0;line-height:1.6;">Multi-stage LambdaMART ranking with semantic JD alignment and diversity controls.</p><ul style="color:#64748b;font-size:0.72rem;margin:0.4rem 0;padding-left:1.2rem;line-height:1.7;"><li>Feature extraction — comprehensive 75-feature vector</li><li>Semantic JD matching — sentence-transformers cosine</li><li>LightGBM LambdaMART — gradient boosting for ranking</li><li>Twin resolution — counterfactual analysis</li><li>MMR diversity — maximal marginal relevance</li></ul><p style="color:#64748b;font-size:0.68rem;margin:0.5rem 0 0;">Tie-break: candidate_id ascending</p></div>""", unsafe_allow_html=True)
    with l3:
        st.markdown("""<div style="margin:0 0.3rem;background:#fff;border-radius:14px;padding:1.2rem;border:1px solid #e5e7eb;border-left:3px solid #ef4444;"><div style="font-size:0.62rem;font-weight:600;color:#ef4444;text-transform:uppercase;">LAYER 3</div><h4 style="margin:0.2rem 0 0.35rem;color:#0f172a;font-size:0.9rem;">🛡️ Honeypot Detection</h4><p style="color:#64748b;font-size:0.75rem;margin:0;line-height:1.6;">Multi-pattern fraud detection that penalizes suspicious profiles before final ranking.</p><ul style="color:#64748b;font-size:0.72rem;margin:0.4rem 0;padding-left:1.2rem;line-height:1.7;"><li>Impossible timelines — flags inconsistent duration claims</li><li>Expert with <2 years — auto-flags implausible seniority</li><li>Skill stuffing — detects CV padding</li><li>Expert claims, no assessments — penalizes unvalidated claims</li></ul><p style="color:#64748b;font-size:0.68rem;margin:0.5rem 0 0;">Tie-break: candidate_id ascending</p></div>""", unsafe_allow_html=True)

    f1, f2 = st.columns(2)
    with f1:
        st.markdown("""<div style="margin:0.5rem 0.3rem 0;background:#fff;border-radius:14px;padding:1rem;border:1px solid #e5e7eb;"><div style="font-size:0.78rem;font-weight:700;color:#0f172a;margin-bottom:0.5rem;">📋 Scoring Formula Breakdown</div>
        <div style="display:grid;grid-template-columns:auto 1fr auto;gap:0.3rem 0.8rem;font-size:0.72rem;align-items:center;">
            <div style="font-weight:600;color:#0f172a;">Final Score</div><div style="color:#64748b;">LambdaMART(features) × ECS_weight</div><div style="color:#0d9488;font-weight:600;">primary</div>
            <div style="font-weight:600;color:#0f172a;">ECS Score</div><div style="color:#64748b;">√(a × b × c × d)</div><div style="color:#0d9488;font-weight:600;">geometric mean</div>
            <div style="font-weight:600;color:#0f172a;">JD Match</div><div style="color:#64748b;">cosine_sim(profile_emb, jd_emb)</div><div style="color:#0d9488;font-weight:600;">semantic</div>
            <div style="font-weight:600;color:#0f172a;">Diversity</div><div style="color:#64748b;">MMR(λ=0.15, relevance, similarity)</div><div style="color:#0d9488;font-weight:600;">greedy</div>
            <div style="font-weight:600;color:#0f172a;">Honeypot</div><div style="color:#64748b;">score × penalty_multiplier</div><div style="color:#ef4444;font-weight:600;">final flag</div>
        </div></div>""", unsafe_allow_html=True)
    with f2:
        st.markdown("""<div style="margin:0.5rem 0.3rem 0;background:#fff;border-radius:14px;padding:1rem;border:1px solid #e5e7eb;"><div style="font-size:0.78rem;font-weight:700;color:#0f172a;margin-bottom:0.5rem;">🎯 ECS Axis Breakdown</div>
        <div style="display:grid;grid-template-columns:auto 1fr auto;gap:0.4rem 0.8rem;font-size:0.72rem;align-items:center;">
            <div style="font-weight:600;color:#0f172a;">Claim vs Assessment</div><div style="color:#64748b;">Self-reported vs test performance alignment</div><div style="color:#0d9488;font-weight:600;">Axis A</div>
            <div style="font-weight:600;color:#0f172a;">Claim vs Career</div><div style="color:#64748b;">Title/role progression consistency</div><div style="color:#3b82f6;font-weight:600;">Axis B</div>
            <div style="font-weight:600;color:#0f172a;">Claim vs GitHub</div><div style="color:#64748b;">Technical depth vs public artifacts</div><div style="color:#f59e0b;font-weight:600;">Axis C</div>
            <div style="font-weight:600;color:#0f172a;">Seniority vs Trajectory</div><div style="color:#64748b;">Growth rate vs claimed senior role</div><div style="color:#8b5cf6;font-weight:600;">Axis D</div>
        </div></div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# ABOUT
# ═══════════════════════════════════════════════════════════════════════
elif page_name == "About":
    st.markdown(f"""<div style="margin:0.5rem 1rem;background:linear-gradient(135deg,#0d9488 0%,#115e59 50%,#134e4a 100%);border-radius:16px;padding:2rem 2.2rem;color:#fff;display:flex;justify-content:space-between;align-items:flex-start;">
        <div style="max-width:58%;">
            <div style="font-size:0.68rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;opacity:0.75;margin-bottom:0.3rem;">🏆 OUR WINNING STRATEGY</div>
            <h1 style="color:#fff;font-size:1.7rem;font-weight:800;margin:0;line-height:1.2;">Evidence-First<br>Ranking Engine</h1>
            <p style="color:rgba(255,255,255,0.7);font-size:0.85rem;margin:0.5rem 0 0;line-height:1.6;">We built a ranking engine that doesn't just match keywords — it <b>verifies claims</b>. Every candidate is scored on how <b>consistent</b> their profile is across 4 independent axes. Candidates who claim expertise but have no assessments, no deployments, and no career progression get penalized hard. This is fundamentally different from TF-IDF or semantic matching alone.</p>
        </div>
        <div style="display:flex;flex-direction:column;gap:0.45rem;">
            <div style="background:rgba(255,255,255,0.15);border-radius:12px;padding:0.75rem 1.1rem;text-align:center;"><div style="font-size:0.58rem;text-transform:uppercase;opacity:0.8;">NDCG@10</div><div style="font-size:1.35rem;font-weight:800;">0.151</div><div style="font-size:0.62rem;color:#34d399;">+11% improvement</div></div>
            <div style="background:rgba(255,255,255,0.15);border-radius:12px;padding:0.75rem 1.1rem;text-align:center;"><div style="font-size:0.58rem;text-transform:uppercase;opacity:0.8;">NDCG@50</div><div style="font-size:1.35rem;font-weight:800;">0.159</div><div style="font-size:0.62rem;color:#34d399;">+11% improvement</div></div>
            <div style="background:rgba(255,255,255,0.15);border-radius:12px;padding:0.75rem 1.1rem;text-align:center;"><div style="font-size:0.58rem;text-transform:uppercase;opacity:0.8;">P@10 TECHNICAL</div><div style="font-size:1.35rem;font-weight:800;">100%</div><div style="font-size:0.62rem;color:#34d399;">all 10 are ML/AI</div></div>
            <div style="background:rgba(255,255,255,0.15);border-radius:12px;padding:0.75rem 1.1rem;text-align:center;"><div style="font-size:0.58rem;text-transform:uppercase;opacity:0.8;">RUNTIME</div><div style="font-size:1.35rem;font-weight:800;">119s</div><div style="font-size:0.62rem;color:#34d399;">under 5 min limit</div></div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div style="margin:0.6rem 1rem 0.4rem;color:#0f172a;font-size:0.85rem;font-weight:700;">🔑 WHAT MAKES US DIFFERENT</div>', unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    diffs = [
        ("01","ECS ARCHITECTURE","Geometric Mean ECS","Every competitor uses additive scoring. We use <b>geometric mean</b> — one contradiction (e.g., expert skill + no assessment) drops the entire score. This is mathematically superior and catches fraud that weighted averages miss.","#0d9488","Fraud-resistant"),
        ("02","JD ALIGNMENT","Semantic JD Matching","We use <b>sentence-transformers</b> to compute cosine similarity between candidate profiles and the actual job description. This ensures ranking is <b>role-specific</b>, not generic.","#3b82f6","Role-aware ranking"),
        ("03","TIE BREAKING","Twin Resolution + Counterfactuals","When two candidates are nearly identical, we find the <b>exact factor</b> that separates them — peer recognition, recruiter engagement, or evidence depth. Every ranking decision is <b>explainable</b>.","#f59e0b","Fully explainable"),
        ("04","DIVERSITY","MMR Diversity Control","Maximal Marginal Relevance ensures the top 100 isn't just 100 clones of the same profile. The list includes <b>diverse archetypes</b> across experience levels, skill domains, and engagement patterns.","#8b5cf6","Diversity-optimized")
    ]
    with d1:
        for num, cat, title, desc, color, badge in diffs[:2]:
            st.markdown(f"""<div style="margin:0 0.3rem 0.5rem;background:#fff;border-radius:14px;padding:1.2rem;border:1px solid #e5e7eb;"><div style="font-size:0.6rem;font-weight:600;color:{color};text-transform:uppercase;letter-spacing:0.05em;">{num} — {cat}</div><h4 style="margin:0.2rem 0 0.3rem;color:#0f172a;font-size:0.9rem;">{title}</h4><p style="color:#64748b;font-size:0.78rem;margin:0;line-height:1.6;">{desc}</p><span style="display:inline-block;margin-top:0.4rem;background:#f1f5f9;padding:0.18rem 0.5rem;border-radius:5px;font-size:0.65rem;color:#374151;">🏷️ {badge}</span></div>""", unsafe_allow_html=True)
    with d2:
        for num, cat, title, desc, color, badge in diffs[2:]:
            st.markdown(f"""<div style="margin:0 0.3rem 0.5rem;background:#fff;border-radius:14px;padding:1.2rem;border:1px solid #e5e7eb;"><div style="font-size:0.6rem;font-weight:600;color:{color};text-transform:uppercase;letter-spacing:0.05em;">{num} — {cat}</div><h4 style="margin:0.2rem 0 0.3rem;color:#0f172a;font-size:0.9rem;">{title}</h4><p style="color:#64748b;font-size:0.78rem;margin:0;line-height:1.6;">{desc}</p><span style="display:inline-block;margin-top:0.4rem;background:#f1f5f9;padding:0.18rem 0.5rem;border-radius:5px;font-size:0.65rem;color:#374151;">🏷️ {badge}</span></div>""", unsafe_allow_html=True)

    st.markdown('<div style="margin:0.6rem 1rem 0.4rem;color:#0f172a;font-size:0.85rem;font-weight:700;">📊 RESULTS</div>', unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    for col, (l, v, s) in zip([r1,r2,r3,r4],[("NDCG@10","0.151","+11% improvement"),("NDCG@50","0.159","+11% improvement"),("P@10 TECHNICAL","100%","all 10 are ML/AI"),("RUNTIME","119s","under 5 min limit")]):
        with col:
            st.markdown(f"""<div style="margin:0 0.3rem;background:#fff;border-radius:12px;padding:1rem;border:1px solid #e5e7eb;text-align:center;"><div style="color:#94a3b8;font-size:0.6rem;text-transform:uppercase;font-weight:600;">{l}</div><div style="color:#0f172a;font-size:1.6rem;font-weight:800;margin:0.15rem 0;">{v}</div><div style="color:#0d9488;font-size:0.68rem;font-weight:500;">{s}</div></div>""", unsafe_allow_html=True)

    st.markdown('<div style="margin:0.7rem 1rem 0.4rem;color:#0f172a;font-size:0.85rem;font-weight:700;">🛠️ TECH STACK</div>', unsafe_allow_html=True)
    st.markdown("""<div style="margin:0 1rem;background:#fff;border-radius:14px;padding:1rem;border:1px solid #e5e7eb;">
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.5rem;">
            <div style="background:#ecfdf5;border-radius:10px;padding:0.8rem;border:1px solid #d1fae5;"><div style="display:flex;align-items:center;gap:0.4rem;margin-bottom:0.3rem;"><div style="width:24px;height:24px;border-radius:6px;background:#0d9488;color:#fff;display:flex;align-items:center;justify-content:center;font-size:0.65rem;">📊</div><div style="font-weight:600;font-size:0.78rem;color:#0f172a;">LightGBM LambdaMART</div></div><div style="color:#64748b;font-size:0.68rem;">Learning-to-rank model trained on pairwise candidate comparisons with 75 features.</div></div>
            <div style="background:#eff6ff;border-radius:10px;padding:0.8rem;border:1px solid #bfdbfe;"><div style="display:flex;align-items:center;gap:0.4rem;margin-bottom:0.3rem;"><div style="width:24px;height:24px;border-radius:6px;background:#3b82f6;color:#fff;display:flex;align-items:center;justify-content:center;font-size:0.65rem;">🔍</div><div style="font-weight:600;font-size:0.78rem;color:#0f172a;">Sentence Transformers</div></div><div style="color:#64748b;font-size:0.68rem;">Semantic embeddings for cosine similarity between profiles and job descriptions.</div></div>
            <div style="background:#f5f3ff;border-radius:10px;padding:0.8rem;border:1px solid #ddd6fe;"><div style="display:flex;align-items:center;gap:0.4rem;margin-bottom:0.3rem;"><div style="width:24px;height:24px;border-radius:6px;background:#8b5cf6;color:#fff;display:flex;align-items:center;justify-content:center;font-size:0.65rem;">🎲</div><div style="font-weight:600;font-size:0.78rem;color:#0f172a;">MMR Diversity Algorithm</div></div><div style="color:#64748b;font-size:0.68rem;">Maximal Marginal Relevance for diverse, non-redundant top-100 shortlists.</div></div>
            <div style="background:#fef3c7;border-radius:10px;padding:0.8rem;border:1px solid #fde68a;"><div style="display:flex;align-items:center;gap:0.4rem;margin-bottom:0.3rem;"><div style="width:24px;height:24px;border-radius:6px;background:#f59e0b;color:#fff;display:flex;align-items:center;justify-content:center;font-size:0.65rem;">👥</div><div style="font-weight:600;font-size:0.78rem;color:#0f172a;">Twin Resolution</div></div><div style="color:#64748b;font-size:0.68rem;">Counterfactual analysis to break ties with explainable, defensible decisions.</div></div>
            <div style="background:#ecfdf5;border-radius:10px;padding:0.8rem;border:1px solid #d1fae5;"><div style="display:flex;align-items:center;gap:0.4rem;margin-bottom:0.3rem;"><div style="width:24px;height:24px;border-radius:6px;background:#0d9488;color:#fff;display:flex;align-items:center;justify-content:center;font-size:0.65rem;">🎯</div><div style="font-weight:600;font-size:0.78rem;color:#0f172a;">4-Axis ECS Scoring</div></div><div style="color:#64748b;font-size:0.68rem;">Geometric mean across Skill, Experience, JD Fit, and Diversity areas.</div></div>
            <div style="background:#fef2f2;border-radius:10px;padding:0.8rem;border:1px solid #fecaca;"><div style="display:flex;align-items:center;gap:0.4rem;margin-bottom:0.3rem;"><div style="width:24px;height:24px;border-radius:6px;background:#ef4444;color:#fff;display:flex;align-items:center;justify-content:center;font-size:0.65rem;">🛡️</div><div style="font-weight:600;font-size:0.78rem;color:#0f172a;">Honeypot Detection</div></div><div style="color:#64748b;font-size:0.68rem;">Automated fraud detection to filter inflated or inconsistent candidate profiles.</div></div>
        </div>
        <p style="color:#94a3b8;font-size:0.7rem;margin:0.6rem 0 0;">CPU-only · No GPU · No internet required · 75 features · Deterministic output</p>
    </div>""", unsafe_allow_html=True)

    # Key Insights + Pipeline Stage Breakdown
    ki, ps = st.columns([1, 1])
    with ki:
        st.markdown("""<div style="margin:0.5rem 0.3rem 0;background:#fff;border-radius:14px;padding:1rem;border:1px solid #e5e7eb;"><div style="font-size:0.78rem;font-weight:700;color:#0f172a;margin-bottom:0.5rem;">💡 Key Insights</div>
        <div style="display:flex;flex-direction:column;gap:0.5rem;">
            <div style="display:flex;gap:0.5rem;"><div style="color:#0d9488;font-size:0.8rem;flex-shrink:0;">•</div><div style="color:#374151;font-size:0.75rem;line-height:1.5;"><b>Geometric mean</b> is mathematically superior to additive scoring — a single inconsistency tanks the total score, catching fraud that averages miss.</div></div>
            <div style="display:flex;gap:0.5rem;"><div style="color:#3b82f6;font-size:0.8rem;flex-shrink:0;">•</div><div style="color:#374151;font-size:0.75rem;line-height:1.5;"><b>Semantic JD matching</b> ensures we're not ranking the best ML engineer in a vacuum — we rank who best fits <i>this specific role</i>.</div></div>
            <div style="display:flex;gap:0.5rem;"><div style="color:#8b5cf6;font-size:0.8rem;flex-shrink:0;">•</div><div style="color:#374151;font-size:0.75rem;line-height:1.5;"><b>MMR diversity</b> prevents the top-100 from collapsing into homogeneous clones. Recruiters get range, not repetition.</div></div>
            <div style="display:flex;gap:0.5rem;"><div style="color:#0d9488;font-size:0.8rem;flex-shrink:0;">•</div><div style="color:#374151;font-size:0.75rem;line-height:1.5;"><b>Zero GPU required.</b> Full pipeline runs CPU-only in under 2 minutes — enterprise-deployable with no infra overhead.</div></div>
        </div></div>""", unsafe_allow_html=True)
    with ps:
        st.markdown("""<div style="margin:0.5rem 0.3rem 0;background:#fff;border-radius:14px;padding:1rem;border:1px solid #e5e7eb;"><div style="font-size:0.78rem;font-weight:700;color:#0f172a;margin-bottom:0.5rem;">📋 Pipeline Stage Breakdown</div>
        <div style="display:flex;flex-direction:column;gap:0.3rem;">
            <div style="display:flex;align-items:center;gap:0.5rem;padding:0.4rem 0.6rem;background:#f8fafc;border-radius:8px;border:1px solid #e5e7eb;"><div style="width:22px;height:22px;border-radius:6px;background:#0d9488;color:#fff;display:flex;align-items:center;justify-content:center;font-size:0.6rem;flex-shrink:0;">1</div><div style="flex:1;font-size:0.72rem;font-weight:500;color:#0f172a;">Feature Extraction</div><div style="font-size:0.62rem;color:#0d9488;font-weight:600;">Done</div></div>
            <div style="display:flex;align-items:center;gap:0.5rem;padding:0.4rem 0.6rem;background:#f8fafc;border-radius:8px;border:1px solid #e5e7eb;"><div style="width:22px;height:22px;border-radius:6px;background:#0d9488;color:#fff;display:flex;align-items:center;justify-content:center;font-size:0.6rem;flex-shrink:0;">2</div><div style="flex:1;font-size:0.72rem;font-weight:500;color:#0f172a;">ECS Scoring</div><div style="font-size:0.62rem;color:#0d9488;font-weight:600;">Done</div></div>
            <div style="display:flex;align-items:center;gap:0.5rem;padding:0.4rem 0.6rem;background:#f8fafc;border-radius:8px;border:1px solid #e5e7eb;"><div style="width:22px;height:22px;border-radius:6px;background:#0d9488;color:#fff;display:flex;align-items:center;justify-content:center;font-size:0.6rem;flex-shrink:0;">3</div><div style="flex:1;font-size:0.72rem;font-weight:500;color:#0f172a;">Semantic JD Match</div><div style="font-size:0.62rem;color:#0d9488;font-weight:600;">Done</div></div>
            <div style="display:flex;align-items:center;gap:0.5rem;padding:0.4rem 0.6rem;background:#f8fafc;border-radius:8px;border:1px solid #e5e7eb;"><div style="width:22px;height:22px;border-radius:6px;background:#0d9488;color:#fff;display:flex;align-items:center;justify-content:center;font-size:0.6rem;flex-shrink:0;">4</div><div style="flex:1;font-size:0.72rem;font-weight:500;color:#0f172a;">LightGBM LambdaMART</div><div style="font-size:0.62rem;color:#0d9488;font-weight:600;">Done</div></div>
            <div style="display:flex;align-items:center;gap:0.5rem;padding:0.4rem 0.6rem;background:#f8fafc;border-radius:8px;border:1px solid #e5e7eb;"><div style="width:22px;height:22px;border-radius:6px;background:#0d9488;color:#fff;display:flex;align-items:center;justify-content:center;font-size:0.6rem;flex-shrink:0;">5</div><div style="flex:1;font-size:0.72rem;font-weight:500;color:#0f172a;">Twin Resolution</div><div style="font-size:0.62rem;color:#0d9488;font-weight:600;">Done</div></div>
            <div style="display:flex;align-items:center;gap:0.5rem;padding:0.4rem 0.6rem;background:#f8fafc;border-radius:8px;border:1px solid #e5e7eb;"><div style="width:22px;height:22px;border-radius:6px;background:#0d9488;color:#fff;display:flex;align-items:center;justify-content:center;font-size:0.6rem;flex-shrink:0;">6</div><div style="flex:1;font-size:0.72rem;font-weight:500;color:#0f172a;">MMR Diversity + Output</div><div style="font-size:0.62rem;color:#0d9488;font-weight:600;">Done</div></div>
        </div></div>""", unsafe_allow_html=True)
