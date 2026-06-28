"""About page — winning strategy matching mockup."""
import streamlit as st


def render(df=None):
    total = len(df) if df is not None and not df.empty else 100

    st.markdown(f"""
    <div class="about-hero">
        <div class="about-hero-left">
            <div class="hero-eyebrow">🏆 OUR WINNING STRATEGY</div>
            <h1 class="hero-title" style="font-size:1.55rem;">Evidence-First<br>Ranking Engine</h1>
            <p class="about-hero-text">
                We built a ranking engine that doesn't just match keywords — it <b>verifies claims</b>.
                Every candidate is scored on how <b>consistent</b> their profile is across 4 independent axes.
                Candidates who claim expertise but have no assessments, no deployments, and no career progression get penalized hard.
                This is fundamentally different from TF-IDF or semantic matching alone.
            </p>
        </div>
        <div class="about-hero-metrics">
            <div class="hero-metric"><div class="hm-label">NDCG@10</div><div class="hm-val">0.151</div><div class="hm-sub green">+11% improvement</div></div>
            <div class="hero-metric"><div class="hm-label">NDCG@50</div><div class="hm-val">0.159</div><div class="hm-sub green">+11% improvement</div></div>
            <div class="hero-metric"><div class="hm-label">P@10 TECHNICAL</div><div class="hm-val">100%</div><div class="hm-sub green">all 10 are ML/AI</div></div>
            <div class="hero-metric"><div class="hm-label">RUNTIME</div><div class="hm-val">119s</div><div class="hm-sub yellow">under 5 min limit</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label" style="margin:1rem 0 0.5rem;">🔑 WHAT MAKES US DIFFERENT</div>', unsafe_allow_html=True)
    diffs = [
        ("01", "ECS ARCHITECTURE", "Geometric Mean ECS", "Every competitor uses additive scoring. We use <b>geometric mean</b> — one contradiction drops the entire score. Mathematically superior and catches fraud that weighted averages miss.", "#0d9488", "🛡 Fraud-resistant"),
        ("02", "JD ALIGNMENT", "Semantic JD Matching", "We use <b>sentence-transformers</b> to compute cosine similarity between candidate profiles and the job description. Ranking is <b>role-specific</b>, not generic.", "#3b82f6", "🎯 Role-aware ranking"),
        ("03", "TIE BREAKING", "Twin Resolution + Counterfactuals", "When two candidates are nearly identical, we find the <b>exact factor</b> that separates them. Every ranking decision is <b>fully explainable</b>.", "#f59e0b", "💡 Fully explainable"),
        ("04", "DIVERSITY", "MMR Diversity Control", "Maximal Marginal Relevance ensures the top {total} isn't homogeneous clones. The list includes <b>diverse archetypes</b> across experience levels and skill domains.".format(total=total), "#8b5cf6", "🎲 Diversity-optimized"),
    ]
    d1, d2 = st.columns(2, gap="medium")
    for col, items in zip([d1, d2], [diffs[:2], diffs[2:]]):
        with col:
            for num, cat, title, desc, color, badge in items:
                st.markdown(f"""
                <div class="diff-card" style="border-top-color:{color};">
                    <div class="diff-num" style="color:{color};">{num} — {cat}</div>
                    <div class="diff-title">{title}</div>
                    <p class="diff-body">{desc}</p>
                    <span class="diff-tag">{badge}</span>
                </div>
                """, unsafe_allow_html=True)

    st.markdown('<div class="section-label" style="margin:0.75rem 0 0.5rem;">📊 RESULTS</div>', unsafe_allow_html=True)
    results = [
        ("NDCG@10", "0.151", "+11% improvement", "#00c2a8"),
        ("NDCG@50", "0.159", "+11% improvement", "#3b82f6"),
        ("P@10 TECHNICAL", "100%", "all 10 are ML/AI", "#00c2a8"),
        ("RUNTIME", "119s", "under 5 min limit", "#f59e0b"),
    ]
    rcols = st.columns(4)
    for col, (label, val, sub, accent) in zip(rcols, results):
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="--accent:{accent};">
                <div class="kpi-label">{label}</div><div class="kpi-value">{val}</div>
                <div class="kpi-sub" style="color:{accent};">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="section-label" style="margin:0.75rem 0 0.5rem;">🛠 TECH STACK</div>', unsafe_allow_html=True)
    tech = [
        ("#0d9488", "#ecfdf5", "#d1fae5", "📊", "LightGBM LambdaMART", "Learning-to-rank model trained on pairwise comparisons with 75 features."),
        ("#3b82f6", "#eff6ff", "#bfdbfe", "🔍", "Sentence Transformers", "Semantic embeddings for cosine similarity between profiles and JD."),
        ("#8b5cf6", "#f5f3ff", "#ddd6fe", "🎲", "MMR Diversity Algorithm", "Maximal Marginal Relevance for diverse, non-redundant shortlists."),
        ("#f59e0b", "#fef3c7", "#fde68a", "👥", "Twin Resolution", "Counterfactual analysis to break ties with explainable decisions."),
        ("#0d9488", "#ecfdf5", "#d1fae5", "🎯", "4-Axis ECS Scoring", "Geometric mean across Skill, Experience, JD Fit, and Diversity axes."),
        ("#ef4444", "#fef2f2", "#fecaca", "🛡️", "Honeypot Detection", "Automated fraud detection to filter inflated or inconsistent profiles."),
    ]
    t_html = '<div class="tech-grid">'
    for fg, bg, border, ico, title, desc in tech:
        t_html += f"""<div class="tech-card" style="background:{bg};border-color:{border};">
            <div class="tech-card-head"><div class="tech-icon" style="background:{fg};">{ico}</div>
            <div class="tech-card-title">{title}</div></div>
            <div class="tech-card-desc">{desc}</div></div>"""
    t_html += "</div>"
    st.markdown(f'<div class="card"><div class="card-body">{t_html}<p class="tech-footnote">CPU-only · No GPU · No internet required · 75 features · Deterministic output</p></div></div>', unsafe_allow_html=True)

    ki, ps = st.columns(2, gap="medium")
    with ki:
        st.markdown("""
        <div class="card"><div class="card-body">
            <div class="card-title-sm">💡 Key Insights</div>
            <div class="insights-list">
                <div class="insight-item"><span class="dot teal">•</span><div><b>Geometric mean</b> is mathematically superior — a single inconsistency tanks the total score, catching fraud that averages miss.</div></div>
                <div class="insight-item"><span class="dot blue">•</span><div><b>Semantic JD matching</b> ensures we're not ranking the best ML engineer in a vacuum — we rank who best fits <i>this specific role</i>.</div></div>
                <div class="insight-item"><span class="dot purple">•</span><div><b>MMR diversity</b> prevents the shortlist from collapsing into homogeneous clones. Recruiters get range, not repetition.</div></div>
                <div class="insight-item"><span class="dot teal">•</span><div><b>Zero GPU required.</b> Full pipeline runs CPU-only in under 2 minutes — enterprise-deployable with no infra overhead.</div></div>
            </div>
        </div></div>
        """, unsafe_allow_html=True)
    with ps:
        stages = ["Feature Extraction", "ECS Scoring", "Semantic JD Match", "LightGBM LambdaMART", "Twin Resolution", "MMR Diversity + Output"]
        stages_html = "".join(
            f"""<div class="stage-row"><div class="stage-num">{i}</div><div class="stage-name">{n}</div><span class="stage-done">Done</span></div>"""
            for i, n in enumerate(stages, 1)
        )
        st.markdown(f"""
        <div class="card"><div class="card-body">
            <div class="card-title-sm">📋 Pipeline Stage Breakdown</div>
            {stages_html}
        </div></div>
        """, unsafe_allow_html=True)
