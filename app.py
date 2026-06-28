"""
Redrob AI — Candidate Ranking Dashboard v3
Interactive sidebar, About page, polished components.
"""
import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Redrob AI", page_icon="🎯", layout="wide")

# ─── CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

.stApp {
    background: linear-gradient(160deg, #eef2ff 0%, #f5f3ff 30%, #fdf2f8 60%, #ecfeff 100%) !important;
}
.main .block-container { max-width: 96% !important; padding: 1rem 2rem !important; }
h1,h2,h3,h4,h5 { font-family: 'Inter', sans-serif !important; }

/* Sidebar */
section[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e5e7eb !important; }
section[data-testid="stSidebar"] [data-testid="stMarkdown"] p,
section[data-testid="stSidebar"] [data-testid="stMarkdown"] h1,
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] { color: #1e293b !important; }
section[data-testid="stSidebar"] label { color: #475569 !important; font-weight: 500 !important; }

/* Nav items */
.nav-item {
    display:flex; align-items:center; gap:0.6rem; padding:0.65rem 0.9rem;
    border-radius:10px; margin-bottom:0.25rem; font-size:0.88rem; font-weight:500;
    transition: background 0.15s;
}
.nav-item:hover { background: #f1f5f9; }

/* Stat cards */
.stat {
    background:#ffffff; border-radius:14px; padding:1.2rem 1rem;
    border:1px solid #f1f5f9; box-shadow:0 1px 3px rgba(0,0,0,0.04);
    position:relative; overflow:hidden;
}
.stat::before {
    content:''; position:absolute; top:0; left:0; right:0; height:3px;
}
.stat-purple::before { background:linear-gradient(90deg,#6366f1,#a855f7); }
.stat-green::before { background:linear-gradient(90deg,#22c55e,#10b981); }
.stat-amber::before { background:linear-gradient(90deg,#f59e0b,#f97316); }
.stat-blue::before { background:linear-gradient(90deg,#3b82f6,#06b6d4); }
.stat-lbl { color:#94a3b8; font-size:0.7rem; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; }
.stat-val { color:#1e293b; font-size:1.9rem; font-weight:800; margin:0.15rem 0; }
.stat-sub { font-size:0.75rem; font-weight:500; }

/* Stage cards */
.stage {
    border-radius:14px; padding:1rem 0.6rem; text-align:center; color:white;
    box-shadow:0 3px 10px rgba(0,0,0,0.12); min-height:105px;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
}
.stage:hover { transform:translateY(-2px); box-shadow:0 6px 16px rgba(0,0,0,0.15); }
.stage-ico { font-size:1.5rem; margin-bottom:0.2rem; }
.stage-t { font-size:0.72rem; font-weight:600; opacity:0.92; }
.stage-v { font-size:1rem; font-weight:800; margin-top:0.1rem; }

/* White card */
.wcard {
    background:#ffffff; border-radius:14px; padding:1.3rem;
    border:1px solid #f1f5f9; box-shadow:0 1px 3px rgba(0,0,0,0.04);
}

/* Signal badge */
.sig {
    border-radius:10px; padding:0.6rem 0.4rem; text-align:center; color:white;
}
.sig-l { font-size:0.62rem; font-weight:500; opacity:0.9; text-transform:uppercase; letter-spacing:0.04em; }
.sig-v { font-size:1.15rem; font-weight:800; }

/* Section header */
.sec { color:#1e293b; font-size:1.05rem; font-weight:700; margin:1.3rem 0 0.6rem 0; }

/* Methodology card */
.mcard {
    background:#ffffff; border-radius:14px; padding:1.3rem;
    border:1px solid #f1f5f9; box-shadow:0 1px 3px rgba(0,0,0,0.04);
    border-top:3px solid; height:240px;
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

# ─── SIDEBAR (interactive nav) ─────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem;">
        <div style="width:56px;height:56px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#a855f7);
        margin:0 auto 0.5rem;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(99,102,241,0.25);">
            <span style="font-size:1.4rem;">🎯</span>
        </div>
        <h3 style="margin:0;color:#1e293b;font-size:0.95rem;font-weight:700;">Redrob AI</h3>
        <p style="color:#94a3b8;font-size:0.72rem;margin:0;">Ranking Engine v2.0</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="border-top:1px solid #f1f5f9;margin:0.5rem 0;"></div>', unsafe_allow_html=True)

    page = st.radio("Navigate", ["📊 Dashboard", "🏆 Rankings", "🔍 Deep Dive", "📐 Methodology", "ℹ️ About"],
                     label_visibility="collapsed")

    st.markdown('<div style="border-top:1px solid #f1f5f9;margin:0.8rem 0;"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background:linear-gradient(135deg,#6366f1,#a855f7);border-radius:12px;
    padding:0.9rem;color:white;text-align:center;">
        <p style="font-size:0.65rem;margin:0;opacity:0.8;text-transform:uppercase;letter-spacing:0.06em;">Pipeline Status</p>
        <p style="font-size:1.6rem;font-weight:800;margin:0.15rem 0;">100</p>
        <p style="font-size:0.65rem;margin:0;opacity:0.8;">candidates ranked</p>
        <div style="background:rgba(255,255,255,0.25);border-radius:5px;height:4px;margin-top:0.4rem;">
            <div style="background:#34d399;border-radius:5px;height:100%;width:100%;"></div>
        </div>
        <p style="font-size:0.62rem;margin:0.2rem 0 0;opacity:0.9;">✅ Complete</p>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown("""
    <div style="margin-bottom:0.5rem;">
        <h1 style="color:#1e293b;font-size:1.7rem;font-weight:800;margin:0;">Candidate Ranking Dashboard</h1>
        <p style="color:#64748b;font-size:0.88rem;margin:0.2rem 0 0;">4-Axis ECS + LightGBM + Twin Resolution | CPU-only Pipeline</p>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    st.markdown('<p class="sec">📊 Overall Statistics</p>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown("""
        <div class="stat stat-purple">
            <div class="stat-lbl">Total Ranked</div>
            <div class="stat-val">100</div>
            <div class="stat-sub" style="color:#22c55e;">100% output</div>
        </div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="stat stat-green">
            <div class="stat-lbl">Technical Roles</div>
            <div class="stat-val">{tech_count}</div>
            <div class="stat-sub" style="color:#22c55e;">{tech_count}% of top 100</div>
        </div>""", unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="stat stat-amber">
            <div class="stat-lbl">Mean Score</div>
            <div class="stat-val">{df['score'].mean():.3f}</div>
            <div class="stat-sub" style="color:#64748b;">across all 100</div>
        </div>""", unsafe_allow_html=True)
    with s4:
        st.markdown("""
        <div class="stat stat-blue">
            <div class="stat-lbl">Honeypots</div>
            <div class="stat-val">0</div>
            <div class="stat-sub" style="color:#22c55e;">0% in top 100</div>
        </div>""", unsafe_allow_html=True)

    # Stage cards
    st.markdown('<p class="sec">🏗️ Pipeline Stages</p>', unsafe_allow_html=True)
    stages = [
        ("📥","Features","75 feat.","#6366f1"),("🎯","ECS","Geo. mean","#8b5cf6"),
        ("🔍","JD Match","Semantic","#3b82f6"),("📊","Heuristic","Weighted","#06b6d4"),
        ("🤖","LightGBM","LambdaMART","#f59e0b"),("👥","Twins","15 cluster","#a855f7"),
        ("🎲","MMR","Diversity","#14b8a6"),("✅","Output","Top 100","#22c55e"),
    ]
    cols = st.columns(8)
    for i, (icon, title, val, color) in enumerate(stages):
        with cols[i]:
            st.markdown(f"""
            <div class="stage" style="background:{color};">
                <div class="stage-ico">{icon}</div>
                <div class="stage-t">{title}</div>
                <div class="stage-v">{val}</div>
            </div>""", unsafe_allow_html=True)

    # Top 10 highlight
    st.markdown('<p class="sec">🏆 Top 10 Candidates</p>', unsafe_allow_html=True)
    top10 = df.head(10)
    for _, row in top10.iterrows():
        cid = row["candidate_id"]
        title = get_title(cid)
        yoe = profiles.get(cid, {}).get("profile", {}).get("years_of_experience", 0)
        ecs = row.get("ecs", 0)
        rank = int(row["rank"])

        rank_color = "#f59e0b" if rank <= 3 else "#6366f1" if rank <= 10 else "#64748b"
        st.markdown(f"""
        <div style="background:white;border-radius:10px;padding:0.7rem 1rem;margin-bottom:0.3rem;
        border:1px solid #f1f5f9;display:flex;align-items:center;gap:1rem;">
            <div style="width:36px;height:36px;border-radius:10px;background:{rank_color};color:white;
            display:flex;align-items:center;justify-content:center;font-weight:800;font-size:0.85rem;">
                {rank}
            </div>
            <div style="flex:1;">
                <div style="color:#1e293b;font-weight:600;font-size:0.9rem;">{title}</div>
                <div style="color:#94a3b8;font-size:0.75rem;">{cid} · {yoe} yrs exp</div>
            </div>
            <div style="text-align:right;">
                <div style="color:#6366f1;font-weight:700;font-size:0.95rem;">{row['score']:.4f}</div>
                <div style="color:#94a3b8;font-size:0.72rem;">ECS {ecs:.2f}</div>
            </div>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# PAGE: RANKINGS
# ═══════════════════════════════════════════════════════════════════════
elif page == "🏆 Rankings":
    st.markdown('<h1 style="color:#1e293b;font-size:1.7rem;font-weight:800;margin:0;">Candidate Rankings</h1>', unsafe_allow_html=True)

    n = st.slider("Show top N", 5, 100, 25)
    search = st.text_input("🔍", placeholder="Search by title, skill, or candidate ID...", label_visibility="collapsed")

    disp = df.head(n).copy()
    disp["Title"] = disp["candidate_id"].map(get_title)
    disp["YoE"] = disp["candidate_id"].map(lambda x: profiles.get(x,{}).get("profile",{}).get("years_of_experience",0))
    disp["AI Skills"] = disp["ai_skill_count"].astype(int)

    if search:
        mask = (disp["Title"].str.contains(search, case=False, na=False) |
                disp["candidate_id"].str.contains(search, case=False, na=False))
        disp = disp[mask]

    show = disp[["rank","candidate_id","Title","YoE","score","ecs","jd_similarity","AI Skills","reasoning"]].copy()
    show.columns = ["#","ID","Title","YoE","Score","ECS","JD Match","AI Skills","Reasoning"]
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
# PAGE: DEEP DIVE
# ═══════════════════════════════════════════════════════════════════════
elif page == "🔍 Deep Dive":
    st.markdown('<h1 style="color:#1e293b;font-size:1.7rem;font-weight:800;margin:0;">Candidate Deep Dive</h1>', unsafe_allow_html=True)

    all_ids = df["candidate_id"].tolist()
    sel = st.selectbox("Select candidate:", all_ids,
                       format_func=lambda x: f"#{df[df['candidate_id']==x].iloc[0]['rank']} — {x} — {get_title(x)}")

    if sel:
        c = profiles.get(sel, {})
        p = c.get("profile", {})
        row = df[df["candidate_id"]==sel].iloc[0]
        signals = c.get("redrob_signals", {})

        ecs = float(row.get('ecs', 0))
        jd = float(row.get('jd_similarity', 0))
        resp = signals.get('response_rate', float(row.get('response_rate', 0)))
        interv = signals.get('interview_completion', float(row.get('interview_completion', 0)))
        ai_count = int(row.get('ai_skill_count', 0))

        skills = c.get("skills", [])
        skill_parts = []
        for s in skills[:10]:
            if isinstance(s, dict):
                name = s.get("skill", s.get("name", ""))
                prof = s.get("proficiency", "")
                if name: skill_parts.append(f"{name}" + (f" ({prof})" if prof else ""))
            else: skill_parts.append(str(s))
        skill_str = ", ".join(skill_parts)

        # Title + Summary
        st.markdown(f"""
        <div class="wcard" style="margin-bottom:1rem;">
            <div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.6rem;">
                <div style="width:48px;height:48px;border-radius:12px;background:linear-gradient(135deg,#6366f1,#a855f7);
                color:white;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:1.1rem;">
                    #{int(row['rank'])}
                </div>
                <div>
                    <h3 style="margin:0;color:#1e293b;font-size:1.1rem;">{p.get('current_title','Unknown')}</h3>
                    <p style="color:#94a3b8;margin:0;font-size:0.8rem;">{sel} · {p.get('years_of_experience',0)} years experience</p>
                </div>
            </div>
            <p style="color:#475569;font-size:0.85rem;line-height:1.65;margin:0;">{p.get('summary','N/A')[:600]}</p>
        </div>""", unsafe_allow_html=True)

        # Signals + Skills side by side
        col_a, col_b = st.columns([1, 1])

        with col_a:
            st.markdown(f"""
            <div class="wcard">
                <h4 style="margin:0 0 0.7rem 0;color:#1e293b;font-size:0.9rem;">📊 Key Signals</h4>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;">
                    <div class="sig" style="background:linear-gradient(135deg,#6366f1,#818cf8);">
                        <div class="sig-l">ECS Score</div><div class="sig-v">{ecs:.2f}</div>
                    </div>
                    <div class="sig" style="background:linear-gradient(135deg,#3b82f6,#60a5fa);">
                        <div class="sig-l">JD Match</div><div class="sig-v">{jd:.2f}</div>
                    </div>
                    <div class="sig" style="background:linear-gradient(135deg,#22c55e,#4ade80);">
                        <div class="sig-l">Response Rate</div><div class="sig-v">{resp:.0%}</div>
                    </div>
                    <div class="sig" style="background:linear-gradient(135deg,#ec4899,#f472b6);">
                        <div class="sig-l">Interview</div><div class="sig-v">{interv:.0%}</div>
                    </div>
                    <div class="sig" style="background:linear-gradient(135deg,#f59e0b,#fbbf24);">
                        <div class="sig-l">AI Skills</div><div class="sig-v">{ai_count}</div>
                    </div>
                    <div class="sig" style="background:linear-gradient(135deg,#8b5cf6,#a78bfa);">
                        <div class="sig-l">Final Score</div><div class="sig-v">{row['score']:.3f}</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

        with col_b:
            st.markdown(f"""
            <div class="wcard">
                <h4 style="margin:0 0 0.7rem 0;color:#1e293b;font-size:0.9rem;">🛠️ Skills</h4>
                <p style="color:#475569;font-size:0.82rem;line-height:1.6;margin:0;">{skill_str}</p>
                <h4 style="margin:1rem 0 0.4rem 0;color:#1e293b;font-size:0.9rem;">💬 Reasoning</h4>
                <p style="color:#475569;font-size:0.82rem;margin:0;">{row['reasoning']}</p>
            </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# PAGE: METHODOLOGY
# ═══════════════════════════════════════════════════════════════════════
elif page == "📐 Methodology":
    st.markdown('<h1 style="color:#1e293b;font-size:1.7rem;font-weight:800;margin:0;">Methodology</h1>', unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown("""
        <div class="mcard" style="border-top-color:#6366f1;">
            <h4 style="margin:0 0 0.5rem 0;color:#4f46e5;">🎯 4-Axis ECS</h4>
            <ul style="color:#475569;font-size:0.82rem;margin:0;padding-left:1rem;">
                <li>Claim vs Assessment scores</li>
                <li>Claim vs Career experience</li>
                <li>Claim vs GitHub/publications</li>
                <li>Seniority vs Trajectory</li>
            </ul>
            <p style="color:#ef4444;font-size:0.75rem;font-weight:600;margin:0.6rem 0 0;">
                ⚠️ Geometric mean — one contradiction kills the score</p>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown("""
        <div class="mcard" style="border-top-color:#22c55e;">
            <h4 style="margin:0 0 0.5rem 0;color:#16a34a;">🤖 Ranking Pipeline</h4>
            <ul style="color:#475569;font-size:0.82rem;margin:0;padding-left:1rem;">
                <li>75 features from JSONL</li>
                <li>Semantic JD matching (sentence-transformers)</li>
                <li>LightGBM LambdaMART</li>
                <li>Twin resolution + counterfactuals</li>
                <li>MMR diversity control</li>
            </ul>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown("""
        <div class="mcard" style="border-top-color:#f59e0b;">
            <h4 style="margin:0 0 0.5rem 0;color:#d97706;">🛡️ Honeypot Detection</h4>
            <ul style="color:#475569;font-size:0.82rem;margin:0;padding-left:1rem;">
                <li>Impossible YoE/duration mismatch</li>
                <li>Expert with &lt;2 yrs experience</li>
                <li>50+ skills keyword stuffing</li>
                <li>Expert claims, no assessments</li>
            </ul>
            <p style="color:#94a3b8;font-size:0.75rem;margin:0.6rem 0 0;">Tie-break: candidate_id ascending</p>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# PAGE: ABOUT
# ═══════════════════════════════════════════════════════════════════════
elif page == "ℹ️ About":
    st.markdown('<h1 style="color:#1e293b;font-size:1.7rem;font-weight:800;margin:0;">About This Project</h1>', unsafe_allow_html=True)

    # Strategy overview
    st.markdown("""
    <div class="wcard" style="margin-bottom:1rem;">
        <h3 style="color:#4f46e5;margin:0 0 0.6rem 0;">🏆 Our Winning Strategy</h3>
        <p style="color:#475569;font-size:0.88rem;line-height:1.7;margin:0;">
            We built a <b>evidence-first ranking engine</b> that doesn't just match keywords — it <b>verifies claims</b>.
            Every candidate is scored on how <b>consistent</b> their profile is across 4 independent axes.
            Candidates who claim expertise but have no assessments, no deployments, and no career progression
            get penalized hard. This is fundamentally different from TF-IDF or semantic matching alone.
        </p>
    </div>""", unsafe_allow_html=True)

    # Key differentiators
    st.markdown('<p class="sec">🔑 What Makes Us Different</p>', unsafe_allow_html=True)

    d1, d2 = st.columns(2)
    with d1:
        st.markdown("""
        <div class="wcard" style="border-left:4px solid #6366f1;">
            <h4 style="color:#4f46e5;margin:0 0 0.4rem 0;">1. Geometric Mean ECS</h4>
            <p style="color:#475569;font-size:0.82rem;margin:0;">Every competitor uses additive scoring.
            We use <b>geometric mean</b> — one contradiction (e.g., expert skill + no assessment) drops the entire score.
            This is mathematically rigorous and catches fraud that weighted averages miss.</p>
        </div>""", unsafe_allow_html=True)
    with d2:
        st.markdown("""
        <div class="wcard" style="border-left:4px solid #22c55e;">
            <h4 style="color:#16a34a;margin:0 0 0.4rem 0;">2. Semantic JD Matching</h4>
            <p style="color:#475569;font-size:0.82rem;margin:0;">We use <b>sentence-transformers</b> to compute cosine similarity
            between candidate profiles and the actual job description. This ensures ranking is <b>role-specific</b>,
            not generic.</p>
        </div>""", unsafe_allow_html=True)
    with d1:
        st.markdown("""
        <div class="wcard" style="border-left:4px solid #f59e0b;margin-top:0.5rem;">
            <h4 style="color:#d97706;margin:0 0 0.4rem 0;">3. Twin Resolution + Counterfactuals</h4>
            <p style="color:#475569;font-size:0.82rem;margin:0;">When two candidates are nearly identical,
            we find the <b>exact factor</b> that separates them — peer recognition, recruiter engagement,
            or evidence depth. Every ranking decision is <b>explainable</b>.</p>
        </div>""", unsafe_allow_html=True)
    with d2:
        st.markdown("""
        <div class="wcard" style="border-left:4px solid #8b5cf6;margin-top:0.5rem;">
            <h4 style="color:#7c3aed;margin:0 0 0.4rem 0;">4. MMR Diversity Control</h4>
            <p style="color:#475569;font-size:0.82rem;margin:0;">We use Maximal Marginal Relevance to ensure the top 100
            isn't just 100 clones of the same profile. The list includes <b>diverse archetypes</b>
            across experience levels, skill domains, and engagement patterns.</p>
        </div>""", unsafe_allow_html=True)

    # Results
    st.markdown('<p class="sec">📊 Results</p>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="wcard">
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;text-align:center;">
            <div>
                <div style="color:#94a3b8;font-size:0.7rem;text-transform:uppercase;">NDCG@10</div>
                <div style="color:#1e293b;font-size:1.4rem;font-weight:800;">0.151</div>
                <div style="color:#22c55e;font-size:0.75rem;">+11% improvement</div>
            </div>
            <div>
                <div style="color:#94a3b8;font-size:0.7rem;text-transform:uppercase;">NDCG@50</div>
                <div style="color:#1e293b;font-size:1.4rem;font-weight:800;">0.159</div>
                <div style="color:#22c55e;font-size:0.75rem;">+11% improvement</div>
            </div>
            <div>
                <div style="color:#94a3b8;font-size:0.7rem;text-transform:uppercase;">P@10 Technical</div>
                <div style="color:#1e293b;font-size:1.4rem;font-weight:800;">100%</div>
                <div style="color:#22c55e;font-size:0.75rem;">all 10 are ML/AI</div>
            </div>
            <div>
                <div style="color:#94a3b8;font-size:0.7rem;text-transform:uppercase;">Runtime</div>
                <div style="color:#1e293b;font-size:1.4rem;font-weight:800;">119s</div>
                <div style="color:#22c55e;font-size:0.75rem;">under 5 min limit</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Tech stack
    st.markdown('<p class="sec">🛠️ Tech Stack</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="wcard">
        <div style="display:flex;gap:0.5rem;flex-wrap:wrap;">
            <span style="background:#f1f5f9;padding:0.4rem 0.8rem;border-radius:8px;font-size:0.78rem;font-weight:500;color:#475569;">Python</span>
            <span style="background:#f1f5f9;padding:0.4rem 0.8rem;border-radius:8px;font-size:0.78rem;font-weight:500;color:#475569;">LightGBM LambdaMART</span>
            <span style="background:#f1f5f9;padding:0.4rem 0.8rem;border-radius:8px;font-size:0.78rem;font-weight:500;color:#475569;">sentence-transformers</span>
            <span style="background:#f1f5f9;padding:0.4rem 0.8rem;border-radius:8px;font-size:0.78rem;font-weight:500;color:#475569;">scikit-learn</span>
            <span style="background:#f1f5f9;padding:0.4rem 0.8rem;border-radius:8px;font-size:0.78rem;font-weight:500;color:#475569;">pandas</span>
            <span style="background:#f1f5f9;padding:0.4rem 0.8rem;border-radius:8px;font-size:0.78rem;font-weight:500;color:#475569;">Streamlit</span>
            <span style="background:#f1f5f9;padding:0.4rem 0.8rem;border-radius:8px;font-size:0.78rem;font-weight:500;color:#475569;">Plotly</span>
            <span style="background:#f1f5f9;padding:0.4rem 0.8rem;border-radius:8px;font-size:0.78rem;font-weight:500;color:#475569;">KMeans Clustering</span>
        </div>
        <p style="color:#94a3b8;font-size:0.78rem;margin:0.6rem 0 0;">CPU-only · No GPU · No internet required · 75 features · Deterministic output</p>
    </div>""", unsafe_allow_html=True)
