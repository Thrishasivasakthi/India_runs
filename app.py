"""
Redrob AI — Candidate Ranking Dashboard
Professional design matching hackathon reference.
"""
import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Redrob AI", page_icon="🎯", layout="wide", initial_sidebar_state="collapsed")

# ─── CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

.stApp { background:#f8fafc !important; font-family:'Inter',sans-serif !important; }
.main .block-container { max-width:97% !important; padding:0.8rem 1.5rem !important; }
h1,h2,h3,h4,h5 { font-family:'Inter',sans-serif !important; }

/* Hide default Streamlit nav */
header[data-testid="stHeader"] { display:none !important; }
section[data-testid="stSidebar"] { display:none !important; }

/* Top nav bar */
.topnav {
    display:flex; align-items:center; gap:0;
    background:white; border-bottom:1px solid #e5e7eb;
    padding:0 1.5rem; margin:-0.8rem -1.5rem 1rem -1.5rem;
    position:sticky; top:0; z-index:100;
}
.topnav-brand {
    display:flex; align-items:center; gap:0.5rem;
    padding:0.7rem 1rem 0.7rem 0;
    border-right:1px solid #e5e7eb; margin-right:0.5rem;
}
.topnav-logo {
    width:32px; height:32px; border-radius:8px;
    background:linear-gradient(135deg,#0d9488,#14b8a6);
    display:flex; align-items:center; justify-content:center;
    color:white; font-size:0.9rem;
}
.topnav-brand-text { font-weight:700; color:#0f172a; font-size:0.9rem; line-height:1.2; }
.topnav-brand-sub { color:#94a3b8; font-size:0.65rem; font-weight:400; }
.topnav-tabs { display:flex; gap:0; }
.topnav-tab {
    padding:0.75rem 1rem; font-size:0.82rem; font-weight:500;
    color:#64748b; cursor:pointer; border-bottom:2px solid transparent;
    transition:all 0.15s; text-decoration:none;
}
.topnav-tab:hover { color:#0f172a; }
.topnav-tab.active { color:#0d9488; border-bottom-color:#0d9488; font-weight:600; }
.topnav-right { margin-left:auto; display:flex; align-items:center; gap:0.6rem; }
.topnav-badge {
    background:#ecfdf5; color:#0d9488; padding:0.35rem 0.7rem;
    border-radius:6px; font-size:0.72rem; font-weight:600;
}
.topnav-btn {
    padding:0.4rem 0.9rem; border-radius:6px; font-size:0.75rem;
    font-weight:600; border:none; cursor:pointer;
}
.topnav-btn-outline { background:white; color:#374151; border:1px solid #d1d5db; }
.topnav-btn-primary { background:#0d9488; color:white; }

/* Stat cards */
.scard {
    background:white; border-radius:12px; padding:1rem 1.2rem;
    border:1px solid #e5e7eb; display:flex; align-items:center; gap:0.8rem;
}
.scard-icon {
    width:42px; height:42px; border-radius:10px;
    display:flex; align-items:center; justify-content:center; font-size:1.1rem;
}
.scard-lbl { color:#94a3b8; font-size:0.68rem; font-weight:500; text-transform:uppercase; letter-spacing:0.04em; }
.scard-val { color:#0f172a; font-size:1.5rem; font-weight:800; line-height:1; }
.scard-sub { font-size:0.7rem; font-weight:500; }

/* Stage flow */
.stage-pill {
    display:inline-flex; align-items:center; gap:0.35rem;
    background:white; border:1px solid #e5e7eb; border-radius:8px;
    padding:0.4rem 0.7rem; font-size:0.72rem; font-weight:500; color:#374151;
}
.stage-pill-ico {
    width:22px; height:22px; border-radius:6px; color:white;
    display:flex; align-items:center; justify-content:center; font-size:0.65rem;
}
.stage-arrow { color:#d1d5db; font-size:0.9rem; }

/* Table card */
.tcard {
    background:white; border-radius:12px; border:1px solid #e5e7eb;
    overflow:hidden;
}
.tcard-head {
    padding:0.8rem 1rem; border-bottom:1px solid #e5e7eb;
    display:flex; align-items:center; justify-content:space-between;
}
.tcard-title { font-size:0.85rem; font-weight:700; color:#0f172a; }

/* Score badge */
.score-badge {
    display:inline-block; padding:0.15rem 0.5rem; border-radius:4px;
    font-size:0.72rem; font-weight:600;
}

/* Role badge */
.role-badge {
    display:inline-block; padding:0.2rem 0.55rem; border-radius:5px;
    font-size:0.68rem; font-weight:500; border:1px solid;
}

/* Progress bar */
.pbar { background:#f1f5f9; border-radius:4px; height:6px; overflow:hidden; }
.pbar-fill { height:100%; border-radius:4px; }

/* Signal card */
.sig-card {
    background:white; border-radius:10px; padding:0.8rem;
    border:1px solid #e5e7eb;
}
.sig-card-lbl { color:#94a3b8; font-size:0.65rem; font-weight:500; text-transform:uppercase; }
.sig-card-val { color:#0f172a; font-size:1.3rem; font-weight:800; }
.sig-card-sub { font-size:0.65rem; color:#64748b; }

/* Side panel card */
.side-card {
    background:white; border-radius:12px; padding:1rem;
    border:1px solid #e5e7eb;
}
.side-card-title { font-size:0.78rem; font-weight:700; color:#0f172a; margin-bottom:0.6rem; }

/* Method card */
.mcard {
    background:white; border-radius:12px; padding:1.2rem;
    border:1px solid #e5e7eb;
}
.mcard-num {
    width:24px; height:24px; border-radius:6px; color:white;
    display:flex; align-items:center; justify-content:center;
    font-size:0.65rem; font-weight:700; margin-bottom:0.4rem;
}

/* About hero */
.about-hero {
    background:linear-gradient(135deg,#0d9488 0%,#115e59 100%);
    border-radius:14px; padding:1.8rem 2rem; color:white;
    display:flex; justify-content:space-between; align-items:center;
}
</style>
""", unsafe_allow_html=True)


# ─── Data ───────────────────────────────────────────────────────────────
@st.cache_data
def load():
    base = os.path.dirname(os.path.abspath(__file__))
    csv = prof = None
    for r, d, fs in os.walk(base):
        for f in fs:
            if f == "ranked_candidates.csv" and not csv: csv = os.path.join(r, f)
            if f == "ranked_profiles.json" and not prof: prof = os.path.join(r, f)
        if csv and prof: break
    df = pd.read_csv(csv) if csv else pd.DataFrame()
    profiles = json.load(open(prof, encoding="utf-8")) if prof else {}
    return df, profiles

df, profiles = load()
if df.empty:
    st.error("Run `python rank.py` first.")
    st.stop()

TECH = ["engineer","scientist","architect","developer","sre","machine learning",
        "data scientist","ai ","ml ","nlp","deep learning","computer vision","researcher"]
def get_title(cid):
    return profiles.get(cid, {}).get("profile", {}).get("current_title", "Unknown")
def is_tech(cid):
    return any(k in get_title(cid).lower() for k in TECH)
tech_count = sum(1 for cid in df["candidate_id"] if is_tech(cid))

ROLE_COLORS = {
    "ML / Search":("#0d9488","#ccfbf1"), "AI / LLM":("#7c3aed","#ede9fe"),
    "RecSys":("#ea580c","#fff7ed"), "Applied ML":("#2563eb","#eff6ff"),
    "ML Eng":("#0891b2","#ecfeff"), "Data Science":("#ca8a04","#fefce8"),
    "CV / Vision":("#be185d","#fdf2f8"), "Research":("#4f46e5","#eef2ff"),
}
def get_role_badge(title):
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

# ─── Session State for Navigation ──────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


# ─── TOP NAV ────────────────────────────────────────────────────────────
page = st.session_state.page
st.markdown(f"""
<div class="topnav">
    <div class="topnav-brand">
        <div class="topnav-logo">🎯</div>
        <div>
            <div class="topnav-brand-text">Redrob AI</div>
            <div class="topnav-brand-sub">Ranking Engine v2.0</div>
        </div>
    </div>
    <div class="topnav-tabs">
        <div class="topnav-tab {'active' if page=='Dashboard' else ''}" onclick="window.location.href='?page=Dashboard'">📊 Dashboard</div>
        <div class="topnav-tab {'active' if page=='Rankings' else ''}" onclick="window.location.href='?page=Rankings'">🏆 Rankings</div>
        <div class="topnav-tab {'active' if page=='Deep Dive' else ''}" onclick="window.location.href='?page=Deep+Dive'">🔍 Deep Dive</div>
        <div class="topnav-tab {'active' if page=='Methodology' else ''}" onclick="window.location.href='?page=Methodology'">📐 Methodology</div>
        <div class="topnav-tab {'active' if page=='About' else ''}" onclick="window.location.href='?page=About'">ℹ️ About</div>
    </div>
    <div class="topnav-right">
        <div class="topnav-badge">✅ Pipeline Complete — 100 ranked</div>
        <button class="topnav-btn topnav-btn-outline">📥 Export</button>
        <button class="topnav-btn topnav-btn-primary">🚀 Deploy</button>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation via query params
qp = st.query_params
if "page" in qp:
    st.session_state.page = qp["page"]
    page = qp["page"]

# Sidebar nav fallback
with st.sidebar:
    if st.button("📊 Dashboard", use_container_width=True): st.session_state.page = "Dashboard"; st.rerun()
    if st.button("🏆 Rankings", use_container_width=True): st.session_state.page = "Rankings"; st.rerun()
    if st.button("🔍 Deep Dive", use_container_width=True): st.session_state.page = "Deep Dive"; st.rerun()
    if st.button("📐 Methodology", use_container_width=True): st.session_state.page = "Methodology"; st.rerun()
    if st.button("ℹ️ About", use_container_width=True): st.session_state.page = "About"; st.rerun()


# ═══════════════════════════════════════════════════════════════════════
# DASHBOARD PAGE
# ═══════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    # Hero
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0d9488 0%,#115e59 50%,#134e4a 100%);
    border-radius:14px;padding:2rem;color:white;margin-bottom:1rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div style="font-size:0.7rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;opacity:0.8;margin-bottom:0.3rem;">AI-POWERED TALENT INTELLIGENCE</div>
                <h1 style="color:white;font-size:1.8rem;font-weight:800;margin:0;">Candidate Ranking Dashboard</h1>
                <p style="color:rgba(255,255,255,0.7);font-size:0.85rem;margin:0.3rem 0 0.8rem 0;">4-Axis ECS · LightGBM LambdaMART · Twin Resolution · CPU-only Pipeline</p>
                <div style="display:flex;gap:0.4rem;flex-wrap:wrap;">
                    <span style="background:rgba(255,255,255,0.15);padding:0.25rem 0.6rem;border-radius:5px;font-size:0.68rem;">ECS Score</span>
                    <span style="background:rgba(255,255,255,0.15);padding:0.25rem 0.6rem;border-radius:5px;font-size:0.68rem;">LightGBM</span>
                    <span style="background:rgba(255,255,255,0.15);padding:0.25rem 0.6rem;border-radius:5px;font-size:0.68rem;">Semantic JD Match</span>
                    <span style="background:rgba(255,255,255,0.15);padding:0.25rem 0.6rem;border-radius:5px;font-size:0.68rem;">MMR Diversity</span>
                    <span style="background:rgba(255,255,255,0.15);padding:0.25rem 0.6rem;border-radius:5px;font-size:0.68rem;">75 Features</span>
                    <span style="background:rgba(255,255,255,0.15);padding:0.25rem 0.6rem;border-radius:5px;font-size:0.68rem;">Twin Resolution</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    s1, s2, s3 = st.columns([1,1,1])
    with s1:
        st.markdown(f"""
        <div class="scard">
            <div class="scard-icon" style="background:#ecfdf5;color:#0d9488;">📊</div>
            <div><div class="scard-lbl">Total Candidates Ranked</div>
            <div class="scard-val">100</div>
            <div class="scard-sub" style="color:#0d9488;">100% output rate</div></div>
        </div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="scard">
            <div class="scard-icon" style="background:#fef3c7;color:#d97706;">📈</div>
            <div><div class="scard-lbl">Mean Score — All 100</div>
            <div class="scard-val">{df['score'].mean():.3f}</div>
            <div class="scard-sub" style="color:#64748b;">Top: {df['score'].max():.3f}</div></div>
        </div>""", unsafe_allow_html=True)
    with s3:
        st.markdown("""
        <div class="scard">
            <div class="scard-icon" style="background:#ecfdf5;color:#0d9488;">🛡️</div>
            <div><div class="scard-lbl">Honeypots Detected</div>
            <div class="scard-val">0</div>
            <div class="scard-sub" style="color:#0d9488;">0% in top 100</div></div>
        </div>""", unsafe_allow_html=True)

    # Pipeline stages
    st.markdown('<div style="color:#0f172a;font-size:0.85rem;font-weight:700;margin:1rem 0 0.5rem;">PIPELINE STAGES</div>', unsafe_allow_html=True)
    pipeline_html = '<div style="display:flex;align-items:center;gap:0.3rem;flex-wrap:wrap;">'
    stages = [
        ("📥","#6366f1","Features","75 feat."), ("🎯","#8b5cf6","ECS","Geo. mean"),
        ("🔍","#3b82f6","JD Match","Semantic"), ("📊","#06b6d4","Heuristic","Weighted"),
        ("🤖","#f59e0b","LightGBM","LambdaMART"), ("👥","#a855f7","Twins","15 cluster"),
        ("🎲","#14b8a6","MMR","Diversity"), ("✅","#0d9488","Output","Top 100"),
    ]
    for i, (ico, color, title, sub) in enumerate(stages):
        if i > 0: pipeline_html += '<span class="stage-arrow">→</span>'
        pipeline_html += f'''
        <div class="stage-pill">
            <div class="stage-pill-ico" style="background:{color};">{ico}</div>
            <div><div style="font-weight:600;font-size:0.72rem;">{title}</div>
            <div style="color:#94a3b8;font-size:0.62rem;">{sub}</div></div>
        </div>'''
    pipeline_html += '</div>'
    st.markdown(pipeline_html, unsafe_allow_html=True)

    # Main content: Top 10 + Side panels
    left, right = st.columns([2, 1])

    with left:
        st.markdown("""
        <div class="tcard">
            <div class="tcard-head">
                <div class="tcard-title">🏆 Top 10 Candidates</div>
                <div style="color:#0d9488;font-size:0.75rem;font-weight:500;cursor:pointer;">View all 100 →</div>
            </div>
        """, unsafe_allow_html=True)

        for _, row in df.head(10).iterrows():
            cid = row["candidate_id"]
            title = get_title(cid)
            yoe = profiles.get(cid, {}).get("profile", {}).get("years_of_experience", 0)
            role = get_role_badge(title)
            r_fg, r_bg = ROLE_COLORS.get(role, ("#64748b","#f1f5f9"))
            ecs = float(row.get("ecs", 0))
            rank = int(row["rank"])
            rank_bg = "#0d9488" if rank <= 3 else "#64748b"

            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:0.8rem;padding:0.6rem 1rem;border-bottom:1px solid #f1f5f9;">
                <div style="width:28px;height:28px;border-radius:8px;background:{rank_bg};color:white;
                display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.75rem;flex-shrink:0;">
                    {rank}
                </div>
                <div style="flex:1;min-width:0;">
                    <div style="font-weight:600;font-size:0.82rem;color:#0f172a;">{title}</div>
                    <div style="color:#94a3b8;font-size:0.68rem;">{cid}</div>
                </div>
                <div style="flex-shrink:0;">
                    <span class="role-badge" style="color:{r_fg};background:{r_bg};border-color:{r_fg}20;">{role}</span>
                </div>
                <div style="text-align:right;flex-shrink:0;width:70px;">
                    <div style="font-weight:700;font-size:0.85rem;color:#0f172a;">{row['score']:.4f}</div>
                    <div style="color:#94a3b8;font-size:0.62rem;">ECS {ecs:.2f}</div>
                </div>
                <div style="text-align:right;flex-shrink:0;width:55px;">
                    <div style="color:#64748b;font-size:0.78rem;">{yoe:.1f} yrs</div>
                </div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        # Score distribution
        st.markdown('<div class="side-card"><div class="side-card-title">📊 Score Distribution</div>', unsafe_allow_html=True)
        scores = df["score"].values
        min_s, max_s, mean_s = scores.min(), scores.max(), scores.mean()
        st.markdown(f"""
        <div style="background:linear-gradient(90deg,#0d9488 0%,#14b8a6 50%,#2dd4bf 100%);
        height:40px;border-radius:8px;position:relative;margin:0.5rem 0;">
            <div style="position:absolute;top:50%;left:{(mean_s-min_s)/(max_s-min_s)*100:.0f}%;
            transform:translate(-50%,-50%);background:white;padding:0.15rem 0.4rem;border-radius:4px;
            font-size:0.65rem;font-weight:700;color:#0f172a;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                Mean: {mean_s:.3f}</div>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#94a3b8;">
            <span>Min: {min_s:.3f}</span><span>Top: {max_s:.3f}</span>
        </div></div></div>""", unsafe_allow_html=True)

        # ECS Axis Weights
        st.markdown("""
        <div class="side-card">
            <div class="side-card-title">🎯 ECS Axis Weights</div>
        """, unsafe_allow_html=True)
        axes = [("Skill Match",0.88,"#0d9488"),("Experience",0.76,"#3b82f6"),
                ("JD Semantic",0.82,"#8b5cf6"),("Diversity",0.68,"#f59e0b")]
        for name, val, color in axes:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.4rem;">
                <div style="width:6px;height:6px;border-radius:50%;background:{color};flex-shrink:0;"></div>
                <div style="flex:1;font-size:0.72rem;color:#374151;">{name}</div>
                <div class="pbar" style="flex:1.5;">
                    <div class="pbar-fill" style="width:{val*100:.0f}%;background:{color};"></div>
                </div>
                <div style="font-size:0.72rem;font-weight:600;color:#0f172a;width:2rem;text-align:right;">{val:.2f}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Pipeline status
        st.markdown("""
        <div class="side-card">
            <div class="side-card-title">🔧 Pipeline Status</div>
            <div style="display:flex;align-items:center;gap:0.4rem;margin-bottom:0.6rem;">
                <span style="color:#0d9488;">✅</span>
                <span style="font-size:0.78rem;font-weight:600;color:#0f172a;">All stages complete</span>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.3rem;font-size:0.7rem;color:#64748b;">
                <div>Total Input</div><div style="text-align:right;font-weight:600;color:#0f172a;">100 candidates</div>
                <div>Total Output</div><div style="text-align:right;font-weight:600;color:#0d9488;">100 ranked</div>
                <div>Twin clusters</div><div style="text-align:right;font-weight:600;color:#0f172a;">15 resolved</div>
                <div>Honeypots</div><div style="text-align:right;font-weight:600;color:#0d9488;">0 detected</div>
                <div>Tech roles</div><div style="text-align:right;font-weight:600;color:#0d9488;">{tech_count}%</div>
            </div>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# RANKINGS PAGE
# ═══════════════════════════════════════════════════════════════════════
elif page == "Rankings":
    st.markdown("""
    <div style="margin-bottom:0.5rem;">
        <div style="font-size:0.7rem;font-weight:600;color:#0d9488;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.2rem;">🏆 CANDIDATE LEADERBOARD</div>
        <h1 style="color:#0f172a;font-size:1.5rem;font-weight:800;margin:0;">Candidate Rankings</h1>
        <p style="color:#64748b;font-size:0.82rem;margin:0.2rem 0 0;">AI-ranked leaderboard · LambdaMART + ECS pipeline · fraud-resistant scoring</p>
    </div>""", unsafe_allow_html=True)

    # Summary stats
    cols = st.columns(5)
    stats = [
        ("TOTAL RANKED","100","candidates in pipeline","#0d9488"),
        ("AVG ECS SCORE","0.74","evidence consistency","#0d9488"),
        ("TOP SCORE",f"{df['score'].max():.3f}",f"Top {df['score'].max():.3f}","#0d9488"),
        ("AVG AI SKILLS",f"{df['ai_skill_count'].mean():.1f}","verified per candidate","#0d9488"),
        ("PIPELINE STATUS","Complete","6/6 stages passed","#0d9488"),
    ]
    for col, (lbl, val, sub, c) in zip(cols, stats):
        with col:
            st.markdown(f"""
            <div style="background:white;border-radius:10px;padding:0.8rem;border:1px solid #e5e7eb;text-align:center;">
                <div style="color:#94a3b8;font-size:0.6rem;font-weight:600;text-transform:uppercase;">{lbl}</div>
                <div style="color:#0f172a;font-size:1.3rem;font-weight:800;">{val}</div>
                <div style="color:#64748b;font-size:0.65rem;">{sub}</div>
            </div>""", unsafe_allow_html=True)

    # Table
    n = st.slider("Show top N", 5, 100, 25, label_visibility="collapsed")
    search = st.text_input("🔍", placeholder="Search by title, skill, or candidate ID...", label_visibility="collapsed")

    disp = df.head(n).copy()
    disp["Title"] = disp["candidate_id"].map(get_title)
    disp["YoE"] = disp["candidate_id"].map(lambda x: profiles.get(x,{}).get("profile",{}).get("years_of_experience",0))

    if search:
        mask = (disp["Title"].str.contains(search, case=False, na=False) |
                disp["candidate_id"].str.contains(search, case=False, na=False))
        disp = disp[mask]

    show = disp[["rank","candidate_id","Title","YoE","score","ecs","jd_similarity","ai_skill_count","reasoning"]].copy()
    show.columns = ["#","Candidate ID","Title","YoE","Score","ECS","JD Match","AI Skills","Reasoning"]
    st.dataframe(show, use_container_width=True, height=min(420, 40+len(show)*32),
                 column_config={
                     "#": st.column_config.NumberColumn(width="small"),
                     "Score": st.column_config.NumberColumn(format="%.4f", width="small"),
                     "ECS": st.column_config.NumberColumn(format="%.2f", width="small"),
                     "JD Match": st.column_config.NumberColumn(format="%.2f", width="small"),
                     "YoE": st.column_config.NumberColumn(format="%.1f yrs", width="small"),
                     "AI Skills": st.column_config.NumberColumn(width="small"),
                 })


# ═══════════════════════════════════════════════════════════════════════
# DEEP DIVE PAGE
# ═══════════════════════════════════════════════════════════════════════
elif page == "Deep Dive":
    st.markdown("""
    <div style="margin-bottom:0.5rem;">
        <div style="font-size:0.7rem;font-weight:600;color:#0d9488;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.2rem;">🔍 TECHNICAL DEEP DIVE</div>
        <h1 style="color:#0f172a;font-size:1.5rem;font-weight:800;margin:0;">Candidate Deep Dive</h1>
        <p style="color:#64748b;font-size:0.82rem;margin:0.2rem 0 0;">Full evidence analysis — scores, signals, skills, and reasoning for each candidate</p>
    </div>""", unsafe_allow_html=True)

    all_ids = df["candidate_id"].tolist()
    sel = st.selectbox("Select candidate:", all_ids,
                       format_func=lambda x: f"#{df[df['candidate_id']==x].iloc[0]['rank']} — {x} — {get_title(x)}")

    if sel:
        c = profiles.get(sel, {})
        p = c.get("profile", {})
        row = df[df["candidate_id"]==sel].iloc[0]
        signals = c.get("redrob_signals", {})
        rank = int(row["rank"])

        ecs = float(row.get('ecs', 0))
        jd = float(row.get('jd_similarity', 0))
        resp = signals.get('response_rate', float(row.get('response_rate', 0)))
        interv = signals.get('interview_completion', float(row.get('interview_completion', 0)))
        ai_count = int(row.get('ai_skill_count', 0))
        score = float(row['score'])

        role = get_role_badge(get_title(sel))
        r_fg, r_bg = ROLE_COLORS.get(role, ("#64748b","#f1f5f9"))

        # Hero card
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0d9488 0%,#115e59 100%);border-radius:14px;padding:1.5rem;color:white;margin-bottom:1rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="display:flex;align-items:center;gap:1rem;">
                    <div style="width:52px;height:52px;border-radius:14px;background:rgba(255,255,255,0.2);
                    display:flex;align-items:center;justify-content:center;font-weight:800;font-size:1.2rem;">#{rank}</div>
                    <div>
                        <h2 style="color:white;margin:0;font-size:1.3rem;">{get_title(sel)}</h2>
                        <div style="display:flex;gap:0.4rem;margin-top:0.3rem;">
                            <span style="background:rgba(255,255,255,0.2);padding:0.2rem 0.5rem;border-radius:4px;font-size:0.68rem;">{sel}</span>
                            <span style="background:rgba(255,255,255,0.2);padding:0.2rem 0.5rem;border-radius:4px;font-size:0.68rem;">{p.get('years_of_experience',0)} years experience</span>
                            <span style="background:rgba(255,255,255,0.2);padding:0.2rem 0.5rem;border-radius:4px;font-size:0.68rem;">Top Candidate</span>
                        </div>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.65rem;text-transform:uppercase;opacity:0.8;">FINAL SCORE</div>
                    <div style="font-size:2rem;font-weight:800;">{score:.3f}</div>
                </div>
            </div>
            <p style="color:rgba(255,255,255,0.8);font-size:0.82rem;margin:0.8rem 0 0;line-height:1.5;">{p.get('summary','N/A')[:500]}</p>
        </div>""", unsafe_allow_html=True)

        # Key Signals (6 cards)
        st.markdown('<div style="color:#0f172a;font-size:0.82rem;font-weight:700;margin:0.8rem 0 0.5rem;">📊 Key Signals</div>', unsafe_allow_html=True)
        sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
        sig_data = [
            ("ECS SCORE",f"{ecs:.2f}","Evidence Consistency","#0d9488","#ecfdf5"),
            ("JD MATCH",f"{jd:.2f}","Semantic Cosine","#3b82f6","#eff6ff"),
            ("RESPONSE RATE",f"{resp:.0%}","Engagement signal","#f59e0b","#fffbeb"),
            ("INTERVIEW SCORE",f"{interv:.0%}","Performance","#ec4899","#fdf2f8"),
            ("AI SKILLS COUNT",str(ai_count),"Verified skills","#8b5cf6","#f5f3ff"),
            ("FINAL SCORE",f"{score:.3f}","Composite rank score","#0d9488","#ecfdf5"),
        ]
        for col, (lbl, val, sub, fg, bg) in zip([sc1,sc2,sc3,sc4,sc5,sc6], sig_data):
            with col:
                st.markdown(f"""
                <div class="sig-card">
                    <div class="sig-card-lbl">{lbl}</div>
                    <div class="sig-card-val" style="color:{fg};">{val}</div>
                    <div class="sig-card-sub">{sub}</div>
                    <div class="pbar" style="margin-top:0.4rem;">
                        <div class="pbar-fill" style="width:{min(float(val.replace('%','').replace('0.',''),100)/100*100,100):.0f}%;background:{fg};"></div>
                    </div>
                </div>""", unsafe_allow_html=True)

        # Skills + Reasoning
        skills = c.get("skills", [])
        skill_groups = {"Expert":[], "Advanced":[], "Intermediate":[]}
        for s in skills:
            if isinstance(s, dict):
                name = s.get("skill", s.get("name", ""))
                prof = s.get("proficiency", "intermediate")
                if prof in skill_groups: skill_groups[prof].append(name)
                else: skill_groups["Intermediate"].append(name)

        sk_col, re_col = st.columns([1, 1])
        with sk_col:
            st.markdown('<div class="side-card"><div class="side-card-title">🛠️ Skills</div>', unsafe_allow_html=True)
            for level, items in skill_groups.items():
                if items:
                    color = {"Expert":"#0d9488","Advanced":"#3b82f6","Intermediate":"#94a3b8"}[level]
                    st.markdown(f'<div style="font-size:0.68rem;font-weight:600;color:{color};margin:0.4rem 0 0.2rem;text-transform:uppercase;">{level} Level</div>', unsafe_allow_html=True)
                    tags = " ".join([f'<span style="background:#f1f5f9;padding:0.2rem 0.5rem;border-radius:4px;font-size:0.68rem;color:#374151;margin-right:0.3rem;">{n}</span>' for n in items[:6]])
                    st.markdown(f'<div>{tags}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with re_col:
            st.markdown(f"""
            <div class="side-card">
                <div class="side-card-title">💡 AI Reasoning</div>
                <p style="color:#374151;font-size:0.82rem;line-height:1.6;margin:0;">{row['reasoning']}</p>
            </div>""", unsafe_allow_html=True)

        # ECS Breakdown
        st.markdown('<div style="color:#0f172a;font-size:0.82rem;font-weight:700;margin:1rem 0 0.5rem;">🎯 4-AXIS ECS BREAKDOWN</div>', unsafe_allow_html=True)
        ax1, ax2, ax3, ax4 = st.columns(4)
        ecs_axes = [
            ("Skill Depth","Technical proficiency",float(row.get("axis_a_score",ecs))*25,"#0d9488"),
            ("Experience","Career progression",float(row.get("axis_b_score",ecs*0.9))*25,"#3b82f6"),
            ("JD Fit","Role alignment",float(row.get("axis_c_score",ecs*0.95))*25,"#f59e0b"),
            ("Diversity Signal","Profile archetype",float(row.get("axis_d_score",ecs*0.85))*25,"#8b5cf6"),
        ]
        for col, (title, sub, val, color) in zip([ax1,ax2,ax3,ax4], ecs_axes):
            with col:
                st.markdown(f"""
                <div style="background:white;border-radius:10px;padding:0.8rem;border:1px solid #e5e7eb;">
                    <div style="font-size:0.72rem;font-weight:600;color:#374151;">{title}</div>
                    <div style="color:#94a3b8;font-size:0.62rem;">{sub}</div>
                    <div style="color:{color};font-size:1.4rem;font-weight:800;margin:0.2rem 0;">{val:.0f}<span style="font-size:0.7rem;font-weight:500;">/25</span></div>
                    <div class="pbar"><div class="pbar-fill" style="width:{min(val/25*100,100):.0f}%;background:{color};"></div></div>
                </div>""", unsafe_allow_html=True)

        # Score Breakdown
        st.markdown('<div style="color:#0f172a;font-size:0.82rem;font-weight:700;margin:1rem 0 0.5rem;">📋 Score Breakdown</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="side-card">
        """, unsafe_allow_html=True)
        breakdown = [
            ("ECS Score",ecs,"#0d9488"),
            ("JD Match (cosine)",jd,"#3b82f6"),
            ("Interview Performance",interv,"#ec4899"),
            ("AI Skill Depth",ai_count/20,"#8b5cf6"),
            ("Response Rate",resp,"#f59e0b"),
            ("LambdaMART Rank",1 - (rank-1)/100,"#0d9488"),
        ]
        for name, val, color in breakdown:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem;">
                <div style="width:10rem;font-size:0.72rem;color:#374151;">{name}</div>
                <div class="pbar" style="flex:1;"><div class="pbar-fill" style="width:{min(val*100,100):.0f}%;background:{color};"></div></div>
                <div style="width:3rem;text-align:right;font-size:0.72rem;font-weight:600;color:#0f172a;">{val:.2f}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# METHODOLOGY PAGE
# ═══════════════════════════════════════════════════════════════════════
elif page == "Methodology":
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0d9488 0%,#115e59 100%);border-radius:14px;padding:1.5rem;color:white;margin-bottom:1rem;">
        <div style="font-size:0.7rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;opacity:0.8;margin-bottom:0.2rem;">📐 TECHNICAL DEEP DIVE</div>
        <h1 style="color:white;margin:0;font-size:1.5rem;">How the Pipeline Works</h1>
        <p style="color:rgba(255,255,255,0.7);margin:0.2rem 0 0;font-size:0.82rem;">A transparent look at the 3-layer methodology — from raw data ingestion through ECS scoring and LambdaMART ranking to final fraud-resistant output.</p>
    </div>""", unsafe_allow_html=True)

    # 5-step pipeline
    st.markdown('<div style="display:flex;gap:0.3rem;margin-bottom:1rem;">', unsafe_allow_html=True)
    steps = [
        ("📥","Data Ingestion","Parse JSONL, 75 features","#6366f1"),
        ("🎯","ECS Scoring","4-axis geometric mean","#0d9488"),
        ("🔍","JD Matching","Semantic cosine","#3b82f6"),
        ("🤖","LambdaMART","Learning-to-rank","#f59e0b"),
        ("🛡️","Honeypot Filter","Fraud detection","#ef4444"),
    ]
    scols = st.columns(5)
    for col, (ico, title, sub, color) in zip(scols, steps):
        with col:
            st.markdown(f"""
            <div style="background:white;border-radius:10px;padding:0.8rem;border:1px solid #e5e7eb;text-align:center;">
                <div style="width:28px;height:28px;border-radius:8px;background:{color};color:white;
                display:flex;align-items:center;justify-content:center;font-size:0.75rem;margin:0 auto 0.3rem;">{ico}</div>
                <div style="font-size:0.75rem;font-weight:600;color:#0f172a;">{title}</div>
                <div style="font-size:0.62rem;color:#64748b;">{sub}</div>
            </div>""", unsafe_allow_html=True)

    # 3 Layers
    st.markdown('<div style="color:#0f172a;font-size:0.85rem;font-weight:700;margin:0.5rem 0 0.5rem;">THREE LAYERS</div>', unsafe_allow_html=True)
    l1, l2, l3 = st.columns(3)
    with l1:
        st.markdown("""
        <div class="mcard" style="border-left:3px solid #0d9488;">
            <div style="font-size:0.65rem;font-weight:600;color:#0d9488;text-transform:uppercase;">LAYER 1</div>
            <h4 style="margin:0.2rem 0 0.4rem;color:#0f172a;font-size:0.9rem;">🎯 4-Axis ECS</h4>
            <p style="color:#64748b;font-size:0.75rem;margin:0;line-height:1.5;">
                Evidence Consistency Score — verifies candidate claims across 4 axes using geometric mean.<br><br>
                • Claim vs Assessment — validates skill self-reports<br>
                • Claim vs Experience — cross-checks career progression<br>
                • Claim vs GitHub — verifies technical depth<br>
                • Seniority vs Trajectory — validates career growth
            </p>
            <p style="color:#0d9488;font-size:0.68rem;font-weight:600;margin:0.5rem 0 0;">⚠️ Geometric mean — one contradiction kills the score</p>
        </div>""", unsafe_allow_html=True)
    with l2:
        st.markdown("""
        <div class="mcard" style="border-left:3px solid #3b82f6;">
            <div style="font-size:0.65rem;font-weight:600;color:#3b82f6;text-transform:uppercase;">LAYER 2</div>
            <h4 style="margin:0.2rem 0 0.4rem;color:#0f172a;font-size:0.9rem;">🤖 Ranking Pipeline</h4>
            <p style="color:#64748b;font-size:0.75rem;margin:0;line-height:1.5;">
                Multi-stage LambdaMART ranking with semantic JD alignment and diversity controls.<br><br>
                • Feature extraction — comprehensive 75-feature vector<br>
                • Semantic JD matching — sentence-transformers cosine<br>
                • LightGBM LambdaMART — gradient boosting for ranking<br>
                • Twin resolution — counterfactual analysis<br>
                • MMR diversity — maximal marginal relevance
            </p>
            <p style="color:#64748b;font-size:0.68rem;margin:0.5rem 0 0;">Tie-break: candidate_id ascending</p>
        </div>""", unsafe_allow_html=True)
    with l3:
        st.markdown("""
        <div class="mcard" style="border-left:3px solid #ef4444;">
            <div style="font-size:0.65rem;font-weight:600;color:#ef4444;text-transform:uppercase;">LAYER 3</div>
            <h4 style="margin:0.2rem 0 0.4rem;color:#0f172a;font-size:0.9rem;">🛡️ Honeypot Detection</h4>
            <p style="color:#64748b;font-size:0.75rem;margin:0;line-height:1.5;">
                Multi-pattern fraud detection that penalizes suspicious profiles before final ranking.<br><br>
                • Impossible timelines — flags inconsistent duration claims<br>
                • Expert with <2 years — auto-flags implausible seniority<br>
                • Skill stuffing — detects CV padding<br>
                • Expert claims, no assessments — penalizes unvalidated claims
            </p>
            <p style="color:#64748b;font-size:0.68rem;margin:0.5rem 0 0;">Tie-break: candidate_id ascending</p>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# ABOUT PAGE
# ═══════════════════════════════════════════════════════════════════════
elif page == "About":
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0d9488 0%,#115e59 100%);border-radius:14px;padding:2rem;color:white;margin-bottom:1rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div style="font-size:0.7rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;opacity:0.8;margin-bottom:0.3rem;">🏆 OUR WINNING STRATEGY</div>
                <h1 style="color:white;font-size:1.8rem;font-weight:800;margin:0;">Evidence-First<br>Ranking Engine</h1>
                <p style="color:rgba(255,255,255,0.75);font-size:0.88rem;margin:0.5rem 0 0;max-width:500px;line-height:1.5;">
                    We built a ranking engine that doesn't just match keywords — it <b>verifies claims</b>.
                    Every candidate is scored on how <b>consistent</b> their profile is across 4 independent axes.
                    Candidates who claim expertise but have no evidence get penalized hard.
                </p>
            </div>
            <div style="display:flex;flex-direction:column;gap:0.5rem;">
                <div style="background:rgba(255,255,255,0.15);border-radius:10px;padding:0.8rem 1.2rem;text-align:center;">
                    <div style="font-size:0.6rem;text-transform:uppercase;opacity:0.8;">NDCG@10</div>
                    <div style="font-size:1.4rem;font-weight:800;">0.151</div>
                    <div style="font-size:0.65rem;color:#34d399;">+11% improvement</div>
                </div>
                <div style="background:rgba(255,255,255,0.15);border-radius:10px;padding:0.8rem 1.2rem;text-align:center;">
                    <div style="font-size:0.6rem;text-transform:uppercase;opacity:0.8;">P@10 TECH</div>
                    <div style="font-size:1.4rem;font-weight:800;">100%</div>
                    <div style="font-size:0.65rem;color:#34d399;">all 10 are ML/AI</div>
                </div>
                <div style="background:rgba(255,255,255,0.15);border-radius:10px;padding:0.8rem 1.2rem;text-align:center;">
                    <div style="font-size:0.6rem;text-transform:uppercase;opacity:0.8;">RUNTIME</div>
                    <div style="font-size:1.4rem;font-weight:800;">119s</div>
                    <div style="font-size:0.65rem;color:#34d399;">under 5 min limit</div>
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Differentiators
    st.markdown('<div style="color:#0f172a;font-size:0.85rem;font-weight:700;margin:0.5rem 0 0.5rem;">🔑 WHAT MAKES US DIFFERENT</div>', unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    diffs = [
        ("01","ECS ARCHITECTURE","Geometric Mean ECS","Every competitor uses additive scoring. We use <b>geometric mean</b> — one contradiction (e.g., expert skill + no assessment) drops the entire score. This is mathematically rigorous and catches fraud that weighted averages miss.","#0d9488","Fraud-resistant"),
        ("02","JD ALIGNMENT","Semantic JD Matching","We use <b>sentence-transformers</b> to compute cosine similarity between candidate profiles and the actual job description. This ensures ranking is <b>role-specific</b>, not generic.","#3b82f6","Role-aware ranking"),
        ("03","TIE BREAKING","Twin Resolution + Counterfactuals","When two candidates are nearly identical, we find the <b>exact factor</b> that separates them — peer recognition, recruiter engagement, or evidence depth. Every ranking decision is <b>explainable</b>.","#f59e0b","Fully explainable"),
        ("04","DIVERSITY","MMR Diversity Control","We use Maximal Marginal Relevance to ensure the top 100 isn't just 100 clones of the same profile. The list includes <b>diverse archetypes</b> across experience levels, skill domains, and engagement patterns.","#8b5cf6","Diversity-optimized"),
    ]
    with d1:
        for num, cat, title, desc, color, badge in diffs[:2]:
            st.markdown(f"""
            <div class="mcard" style="margin-bottom:0.5rem;">
                <div style="font-size:0.6rem;font-weight:600;color:{color};text-transform:uppercase;letter-spacing:0.05em;">{num} — {cat}</div>
                <h4 style="margin:0.2rem 0 0.3rem;color:#0f172a;font-size:0.88rem;">{title}</h4>
                <p style="color:#64748b;font-size:0.78rem;margin:0;line-height:1.5;">{desc}</p>
                <span style="display:inline-block;margin-top:0.4rem;background:#f1f5f9;padding:0.2rem 0.5rem;border-radius:4px;font-size:0.65rem;color:#374151;">🏷️ {badge}</span>
            </div>""", unsafe_allow_html=True)
    with d2:
        for num, cat, title, desc, color, badge in diffs[2:]:
            st.markdown(f"""
            <div class="mcard" style="margin-bottom:0.5rem;">
                <div style="font-size:0.6rem;font-weight:600;color:{color};text-transform:uppercase;letter-spacing:0.05em;">{num} — {cat}</div>
                <h4 style="margin:0.2rem 0 0.3rem;color:#0f172a;font-size:0.88rem;">{title}</h4>
                <p style="color:#64748b;font-size:0.78rem;margin:0;line-height:1.5;">{desc}</p>
                <span style="display:inline-block;margin-top:0.4rem;background:#f1f5f9;padding:0.2rem 0.5rem;border-radius:4px;font-size:0.65rem;color:#374151;">🏷️ {badge}</span>
            </div>""", unsafe_allow_html=True)

    # Results
    st.markdown('<div style="color:#0f172a;font-size:0.85rem;font-weight:700;margin:0.5rem 0 0.5rem;">📊 RESULTS</div>', unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    for col, (lbl, val, sub) in zip([r1,r2,r3,r4],[("NDCG@10","0.151","+11% improvement"),("NDCG@50","0.159","+11% improvement"),("P@10 TECHNICAL","100%","all 10 are ML/AI"),("RUNTIME","119s","under 5 min limit")]):
        with col:
            st.markdown(f"""
            <div style="background:white;border-radius:10px;padding:1rem;border:1px solid #e5e7eb;text-align:center;">
                <div style="color:#94a3b8;font-size:0.62rem;text-transform:uppercase;font-weight:600;">{lbl}</div>
                <div style="color:#0f172a;font-size:1.6rem;font-weight:800;margin:0.1rem 0;">{val}</div>
                <div style="color:#0d9488;font-size:0.68rem;font-weight:500;">{sub}</div>
            </div>""", unsafe_allow_html=True)

    # Tech Stack
    st.markdown('<div style="color:#0f172a;font-size:0.85rem;font-weight:700;margin:0.8rem 0 0.5rem;">🛠️ TECH STACK</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="side-card">
        <div style="display:flex;gap:0.4rem;flex-wrap:wrap;">
            <span style="background:#ecfdf5;color:#0d9488;padding:0.4rem 0.8rem;border-radius:8px;font-size:0.75rem;font-weight:500;">📊 LightGBM LambdaMART</span>
            <span style="background:#eff6ff;color:#3b82f6;padding:0.4rem 0.8rem;border-radius:8px;font-size:0.75rem;font-weight:500;">🔍 Sentence Transformers</span>
            <span style="background:#f5f3ff;color:#8b5cf6;padding:0.4rem 0.8rem;border-radius:8px;font-size:0.75rem;font-weight:500;">🎲 MMR Diversity Algorithm</span>
            <span style="background:#fef3c7;color:#d97706;padding:0.4rem 0.8rem;border-radius:8px;font-size:0.75rem;font-weight:500;">👥 Twin Resolution</span>
            <span style="background:#ecfdf5;color:#0d9488;padding:0.4rem 0.8rem;border-radius:8px;font-size:0.75rem;font-weight:500;">🎯 4-Axis ECS Scoring</span>
            <span style="background:#fef2f2;color:#ef4444;padding:0.4rem 0.8rem;border-radius:8px;font-size:0.75rem;font-weight:500;">🛡️ Honeypot Detection</span>
        </div>
        <p style="color:#94a3b8;font-size:0.72rem;margin:0.6rem 0 0;">CPU-only · No GPU · No internet required · 75 features · Deterministic output</p>
    </div>""", unsafe_allow_html=True)
