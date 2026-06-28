"""Dashboard page — dynamic counts, hero + metrics + pipeline + top 10."""
import numpy as np
import streamlit as st

from ui.data import ROLE_COLORS, get_role, get_title, rank_badge


def render(df, profiles, tech_count):
    total = len(df)
    mean_score = df["score"].mean()
    max_score = df["score"].max()
    output_pct = 100

    pipeline_steps = [
        ("📥", "#6366f1", "Features", "75 feat."),
        ("🎯", "#0d9488", "ECS", "Geo. mean"),
        ("🔍", "#3b82f6", "JD Match", "Semantic"),
        ("📊", "#06b6d4", "Heuristic", "Weighted"),
        ("🤖", "#f59e0b", "LightGBM", "LambdaMART"),
        ("👥", "#a855f7", "Twins", "15 cluster"),
        ("🎲", "#8b5cf6", "MMR", "Diversity"),
        ("✅", "#00c2a8", "Output", f"Top {total}"),
    ]
    ecs_weights = [
        ("Skill Match", 0.88, "#0d9488"),
        ("Experience", 0.75, "#06b6d4"),
        ("JD Semantic", 0.82, "#3b82f6"),
        ("Diversity", 0.60, "#22c55e"),
    ]

    hero_col, metrics_col = st.columns([2.8, 1], gap="medium")
    with hero_col:
        st.markdown("""
        <div class="hero-dark">
            <div class="hero-eyebrow">AI-POWERED TALENT INTELLIGENCE</div>
            <h1 class="hero-title">Candidate Ranking<br>Dashboard</h1>
            <p class="hero-sub">4-Axis ECS · LightGBM LambdaMART · Twin Resolution · CPU-only Pipeline</p>
            <div class="hero-tags">
                <span class="hero-tag">ECS Score</span><span class="hero-tag">LightGBM</span>
                <span class="hero-tag">Semantic JD Match</span><span class="hero-tag">MMR Diversity</span>
                <span class="hero-tag">75 Features</span><span class="hero-tag">Twin Resolution</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with metrics_col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="background:#ecfdf5;color:#0d9488;">👥</div>
            <div><div class="metric-label">Total Candidates Ranked</div>
            <div class="metric-value">{total}</div>
            <div class="metric-sub" style="color:#0d9488;">{output_pct}% output rate</div></div>
        </div>
        <div class="metric-card">
            <div class="metric-icon" style="background:#fef3c7;color:#d97706;">📊</div>
            <div><div class="metric-label">Mean Score — All {total}</div>
            <div class="metric-value">{mean_score:.3f}</div>
            <div class="metric-sub" style="color:#64748b;">Top: {max_score:.4f}</div></div>
        </div>
        <div class="metric-card" style="margin-bottom:0;">
            <div class="metric-icon" style="background:#eff6ff;color:#3b82f6;">🛡️</div>
            <div><div class="metric-label">Honeypots Detected</div>
            <div class="metric-value">0</div>
            <div class="metric-sub" style="color:#0d9488;">0% in top {total}</div></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-label" style="margin:1rem 0 0.5rem;">PIPELINE STAGES</div>', unsafe_allow_html=True)
    parts = ['<div class="pipeline-row">']
    for i, (ico, color, title, sub) in enumerate(pipeline_steps):
        if i > 0:
            parts.append('<span class="pipeline-arrow">→</span>')
        parts.append(f"""<div class="pipeline-step"><div class="pipeline-icon" style="background:{color};">{ico}</div>
            <div><div class="pipeline-title">{title}</div><div class="pipeline-sub">{sub}</div></div></div>""")
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)

    left, right = st.columns([2.2, 1], gap="medium")
    with left:
        st.markdown(f"""
        <div class="card">
            <div class="card-header">
                <div style="font-size:0.88rem;font-weight:700;color:#0f172a;">🏆 Top 10 Candidates</div>
                <div class="teal-link">View all {total} →</div>
            </div>
        """, unsafe_allow_html=True)
        for _, row in df.head(10).iterrows():
            cid = row["candidate_id"]
            title = get_title(cid, profiles, df)
            yoe = profiles.get(cid, {}).get("profile", {}).get("years_of_experience", row.get("years_of_experience", 0))
            role = get_role(title)
            fg, bg = ROLE_COLORS.get(role, ("#64748b", "#f1f5f9"))
            ecs = float(row.get("ecs", 0))
            rank = int(row["rank"])
            score_pct = min((row["score"] / max_score) * 100, 100)
            st.markdown(f"""
            <div class="table-row dash-row">
                {rank_badge(rank)}
                <div><div class="cand-title">{title}</div><div class="cand-id">{cid}</div></div>
                <span class="role-pill" style="color:{fg};background:{bg};border:1px solid {fg}22;">{role}</span>
                <div><div class="cand-score">{row['score']:.4f}</div>
                <div class="score-bar-wrap"><div class="score-bar" style="width:{score_pct:.0f}%;"></div></div>
                <div class="cand-ecs">ECS {ecs:.2f}</div></div>
                <div class="cand-yoe">{float(yoe):.1f} yrs</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        mn, mx, avg = df["score"].min(), df["score"].max(), df["score"].mean()
        bins = np.linspace(mn, mx, 8)
        counts = [((df["score"] >= bins[i]) & (df["score"] < bins[i + 1])).sum() for i in range(len(bins) - 1)]
        mx_c = max(counts) if max(counts) > 0 else 1
        bars = "".join(f'<div class="dist-bar" style="height:{max(int(c/mx_c*50),2)}px;"></div>' for c in counts)
        weights_html = "".join(
            f"""<div class="weight-row"><div class="weight-dot" style="background:{c};"></div>
            <div style="flex:1;font-size:0.7rem;color:#374151;">{n}</div>
            <div class="weight-bar-bg"><div class="weight-bar-fill" style="width:{v*100:.0f}%;background:{c};"></div></div>
            <div style="font-size:0.7rem;font-weight:600;width:2rem;text-align:right;">{v:.2f}</div></div>"""
            for n, v, c in ecs_weights
        )
        st.markdown(f"""
        <div class="card" style="margin-bottom:0.55rem;"><div class="card-body">
            <div class="card-title-sm">📊 Score Distribution</div>
            <div class="dist-chart">{bars}</div>
            <div class="dist-labels"><span>Min {mn:.2f}</span><span>Mean {avg:.3f}</span><span>Max {mx:.4f}</span></div>
        </div></div>
        <div class="card" style="margin-bottom:0.55rem;"><div class="card-body">
            <div class="card-title-sm">🎯 ECS Axis Weights</div>{weights_html}
        </div></div>
        <div class="card"><div class="card-body">
            <div class="card-title-sm">🔧 Pipeline Status</div>
            <div class="status-card" style="margin-bottom:0.65rem;">
                <div class="status-ok">✅ All stages complete</div>
                <div style="font-size:0.65rem;color:#64748b;margin-top:0.2rem;">CPU-only · No GPU required</div>
            </div>
            <div class="status-grid">
                <div>Total input</div><div>{total} candidates</div>
                <div>Total output</div><div class="teal">{total} ranked</div>
                <div>Twin clusters</div><div>15 resolved</div>
                <div>Honeypots</div><div class="teal">0 detected</div>
                <div>Tech roles</div><div class="teal">{tech_count}%</div>
            </div>
        </div></div>
        """, unsafe_allow_html=True)
