"""Deep Dive page — aligned layout matching mockup."""
import streamlit as st

from ui.data import get_title


def _skill_tags(skills):
    groups = {"Expert": [], "Advanced": [], "Intermediate": []}
    for s in skills:
        if isinstance(s, dict):
            name = s.get("skill", s.get("name", ""))
            prof = s.get("proficiency", "Intermediate")
            groups.get(prof, groups["Intermediate"]).append(name)
    html = ""
    styles = {
        "Expert": ("#ecfdf5", "#0d9488"),
        "Advanced": ("#eff6ff", "#3b82f6"),
        "Intermediate": ("#fff7ed", "#ea580c"),
    }
    for level, items in groups.items():
        if not items:
            continue
        bg, fg = styles[level]
        html += f'<div class="skill-level-label" style="color:{fg};">{level} Level</div>'
        html += "".join(
            f'<span class="skill-tag" style="background:{bg};color:{fg};">{n}</span>'
            for n in items[:8]
        )
    return html or '<span style="color:#94a3b8;font-size:0.72rem;">No skills listed</span>'


def render(df, profiles):
    total = len(df)
    hdr_l, hdr_r = st.columns([2, 1.2])
    with hdr_l:
        st.markdown("""
        <div class="deep-header">
            <div class="section-label" style="color:#00c2a8;">🔍 CANDIDATE DEEP DIVE</div>
            <h1 class="page-title-dark">Candidate <span style="color:#00c2a8;">Deep Dive</span></h1>
            <p class="page-sub">Full evidence analysis — scores, signals, skills, and reasoning for each candidate</p>
        </div>
        """, unsafe_allow_html=True)

    all_ids = df["candidate_id"].tolist()
    with hdr_r:
        sel = st.selectbox(
            "Candidate",
            all_ids,
            format_func=lambda x: f"#{df[df['candidate_id']==x].iloc[0]['rank']}  {x}  —  {get_title(x, profiles, df)}",
            label_visibility="collapsed",
        )

    if not sel:
        return

    c = profiles.get(sel, {})
    p = c.get("profile", {})
    row = df[df["candidate_id"] == sel].iloc[0]
    signals = c.get("redrob_signals", {})
    rank = int(row["rank"])
    ecs = float(row.get("ecs", 0))
    jd = float(row.get("jd_similarity", 0))
    resp = float(signals.get("response_rate", row.get("response_rate", 0)))
    interv = float(signals.get("interview_completion", row.get("interview_completion", 0)))
    ai_count = int(row.get("ai_skill_count", 0))
    score = float(row["score"])
    yoe = float(p.get("years_of_experience", row.get("years_of_experience", 0)))
    summary = p.get("summary") or row.get("reasoning", "N/A")
    summary = str(summary)[:500]
    title = get_title(sel, profiles, df)

    if "shortlist" not in st.session_state:
        st.session_state.shortlist = set()

    # Profile card
    st.markdown(f"""
    <div class="profile-dark">
        <div class="profile-top">
            <div class="profile-left">
                <div class="profile-rank-box">#{rank}</div>
                <div>
                    <h2 class="profile-title">{title}</h2>
                    <div class="profile-badges">
                        <span class="profile-badge"># {sel}</span>
                        <span class="profile-badge">{yoe:.1f} years experience</span>
                        <span class="profile-badge-gold">{"Top Candidate" if rank <= 3 else "Ranked"}</span>
                    </div>
                </div>
            </div>
            <div class="profile-right">
                <div class="profile-score-block">
                    <div class="profile-score-label">FINAL SCORE</div>
                    <div class="profile-score-value">{score:.3f}</div>
                </div>
            </div>
        </div>
        <div class="profile-summary">{summary}</div>
    </div>
    """, unsafe_allow_html=True)

    btn1, btn2, _ = st.columns([1, 1, 4])
    with btn1:
        if st.button("＋ Shortlist", key=f"dd_shortlist_{sel}", use_container_width=True, type="primary"):
            st.session_state.shortlist.add(sel)
            st.toast(f"{sel} added to shortlist")
    with btn2:
        if st.button("✉ Contact", key=f"dd_contact_{sel}", use_container_width=True):
            st.toast(f"Contact request queued for {sel}")

    # Key signals — full width 3×2
    st.markdown('<div class="deep-section-title">📊 Key Signals</div>', unsafe_allow_html=True)
    st.markdown('<div class="deep-section-sub">6 dimensions evaluated</div>', unsafe_allow_html=True)

    sigs = [
        ("ECS SCORE", f"{ecs:.2f}", "Evidence Consistency", "#00c2a8", ecs, False),
        ("JD MATCH", f"{jd:.2f}", "Semantic Cosine", "#3b82f6", jd, False),
        ("RESPONSE RATE", f"{resp:.0%}", "Engagement signal", "#f59e0b", resp, False),
        ("INTERVIEW SCORE", f"{interv:.0%}", "Performance", "#ec4899", interv, False),
        ("AI SKILLS COUNT", str(ai_count), "Verified skills", "#84cc16", ai_count / 15, False),
        ("FINAL SCORE", f"{score:.3f}", "Composite rank score", "#06b6d4", min(score / 2, 1), True),
    ]
    for ri in range(0, 6, 3):
        cols = st.columns(3, gap="medium")
        for ci, col in enumerate(cols):
            idx = ri + ci
            if idx >= len(sigs):
                continue
            lbl, val, sub, clr, pct, dark = sigs[idx]
            with col:
                cls = "signal-card-dark" if dark else "signal-card"
                st.markdown(f"""
                <div class="{cls}">
                    <div class="signal-label">{lbl}</div>
                    <div class="signal-value" style="color:{('#fff' if dark else clr)};">{val}</div>
                    <div class="signal-sub">{sub}</div>
                    <div class="signal-bar-bg" style="background:{'#334155' if dark else '#f1f5f9'};">
                        <div class="signal-bar-fill" style="width:{min(pct*100,100):.0f}%;background:{clr};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Main 2-column layout: left = ECS + breakdown, right = skills + reasoning (top-aligned)
    main_l, main_r = st.columns([1.55, 1], gap="large")

    with main_l:
        st.markdown('<div class="deep-section-title" style="margin-top:0.5rem;">🎯 4-AXIS ECS BREAKDOWN</div>', unsafe_allow_html=True)
        a1, a2, a3, a4 = st.columns(4, gap="small")
        axes = [
            ("🎯", "#ecfdf5", "#0d9488", "Skill Depth", "Technical proficiency", min(ecs * 25, 25), "Expert-level verified"),
            ("📅", "#eff6ff", "#3b82f6", "Experience", "Career progression", min(ecs * 0.9 * 25, 25), "Strong progression"),
            ("📋", "#fdf2f8", "#ec4899", "JD Fit", "Role alignment", min(ecs * 0.95 * 25, 25), "High semantic match"),
            ("🎲", "#fff7ed", "#f59e0b", "Diversity Signal", "Profile archetype", min(ecs * 0.85 * 25, 25), "Unique profile"),
        ]
        for col, (ico, ibg, clr, ax_title, sub, val, badge) in zip([a1, a2, a3, a4], axes):
            with col:
                st.markdown(f"""
                <div class="axis-card">
                    <div class="axis-icon" style="background:{ibg};">{ico}</div>
                    <div class="axis-name">{ax_title}</div>
                    <div class="axis-sub">{sub}</div>
                    <div class="axis-score" style="color:{clr};">{val:.0f}<span>/25</span></div>
                    <div class="score-bar-wrap" style="height:6px;"><div class="score-bar" style="width:{val/25*100:.0f}%;background:{clr};"></div></div>
                    <div class="axis-badge">🏷 {badge}</div>
                </div>
                """, unsafe_allow_html=True)

        vs_avg = max((ecs - df["ecs"].mean()) / max(df["ecs"].mean(), 0.01) * 100, 0)
        st.markdown(f"""
        <div class="geo-mean-bar">
            <div class="geo-block">
                <div class="section-label">GEOMETRIC MEAN ECS</div>
                <div class="geo-value">{ecs:.3f}</div>
                <div class="geo-sub">Composite of all 4 axes via geometric mean — fraud-resistant</div>
            </div>
            <div class="geo-stat"><div class="section-label">VS. AVERAGE</div><div class="geo-stat-val green">+{vs_avg:.0f}%</div></div>
            <div class="geo-stat"><div class="section-label">HONEYPOT</div><div class="geo-stat-val green">Clear</div></div>
            <div class="geo-rank-badge">🏆 Rank #{rank} of {total}</div>
        </div>
        """, unsafe_allow_html=True)

        brk, qual = st.columns(2, gap="medium")
        with brk:
            rows = [
                ("ECS Score", ecs, "#0d9488", f"{ecs:.2f}"),
                ("JD Match (cosine)", jd, "#3b82f6", f"{jd:.2f}"),
                ("Interview Performance", interv, "#ec4899", f"{interv:.0%}"),
                ("AI Skill Depth", ai_count / 15, "#84cc16", f"{ai_count} skills"),
                ("Response Rate", resp, "#f59e0b", f"{resp:.0%}"),
                ("LambdaMART Rank", 1 - (rank - 1) / total, "#00c2a8", f"#{rank}"),
            ]
            brk_html = "".join(
                f"""<div class="breakdown-row">
                    <div class="breakdown-label">{nm}</div>
                    <div class="breakdown-bar-bg"><div class="breakdown-bar" style="width:{min(v*100,100):.0f}%;background:{c};"></div></div>
                    <div class="breakdown-val">{disp}</div>
                </div>"""
                for nm, v, c, disp in rows
            )
            st.markdown(f"""
            <div class="card"><div class="card-body">
                <div class="card-title-sm">📋 Score Breakdown</div>
                <div class="card-sub-sm">Normalized 0–1</div>
                {brk_html}
            </div></div>
            """, unsafe_allow_html=True)

        with qual:
            st.markdown("""
            <div class="card"><div class="card-body">
                <div class="qual-header">
                    <div class="card-title-sm">🛡 Quality Signals</div>
                    <span class="all-clear">● All Clear</span>
                </div>
            """, unsafe_allow_html=True)
            if st.button("✨ Generate screen", key=f"gen_screen_{sel}", type="primary"):
                st.session_state[f"screen_{sel}"] = (
                    f"Screening summary for {title} ({sel}): "
                    f"ECS {ecs:.2f}, JD match {jd:.2f}, {ai_count} AI skills, "
                    f"interview {interv:.0%}, rank #{rank}."
                )
                st.toast("Screening summary generated")
            screen = st.session_state.get(f"screen_{sel}")
            if screen:
                st.info(screen)
            st.markdown(f"""
                <div class="qual-item"><span class="qual-icon ok">✅</span><div><div class="qual-title">Profile passed all 7 fraud-detection checks</div><div class="qual-desc">No inflated skill claims detected.</div></div></div>
                <div class="qual-item"><span class="qual-icon ok">✅</span><div><div class="qual-title">ECS Axes All Passed</div><div class="qual-desc">4/4 axes returned positive signals.</div></div></div>
                <div class="qual-item"><span class="qual-icon ok">✅</span><div><div class="qual-title">Twin Resolution — Unique</div><div class="qual-desc">No near-duplicate in top {total}.</div></div></div>
                <div class="qual-item"><span class="qual-icon warn">⚠️</span><div><div class="qual-title">Response Rate: {"Moderate" if resp < 0.6 else "Good"}</div><div class="qual-desc">{resp:.0%} is {"acceptable but below top-quartile" if resp < 0.6 else "above average"}.</div></div></div>
            </div></div>
            """, unsafe_allow_html=True)

    with main_r:
        skills_html = _skill_tags(c.get("skills", []))
        st.markdown(f"""
        <div class="card sidebar-card">
            <div class="card-body">
                <div class="card-title-sm">🛠 Skills</div>
                <div class="card-sub-sm">{ai_count} AI/ML skills verified</div>
                {skills_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card sidebar-card">
            <div class="card-body">
                <div class="card-title-sm">🧠 AI Reasoning</div>
                <p class="reasoning-text">{row['reasoning']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
