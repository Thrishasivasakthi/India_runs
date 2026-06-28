"""Methodology page — matches mockup pipeline flow."""
import streamlit as st


def render(df=None):
    total = len(df) if df is not None and not df.empty else 100

    st.markdown(f"""
    <div class="method-header card">
        <div class="method-header-left">
            <div class="method-badge">TECHNICAL DEEP DIVE</div>
            <h1 class="method-title">How the <span>Pipeline</span> Works</h1>
            <p class="method-desc">A transparent look at the 3-layer methodology — from raw data ingestion through ECS scoring and LambdaMART ranking to final fraud-resistant output.</p>
        </div>
        <div class="method-status-card">
            <div class="method-status-icon">✅</div>
            <div class="method-status-label">PIPELINE STATUS</div>
            <div class="method-status-val">Complete</div>
            <div class="method-status-sub">{total} candidates ranked</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    steps = [
        ("1", "📥", "Data Ingestion", "Parse JSONL profiles into structured candidate records with 75 features.", ["75 features", "JSONL"], "#6366f1"),
        ("2", "🎯", "ECS Scoring", "4-axis Evidence Consistency Score computed via geometric mean aggregation.", ["4 axes", "geo-mean"], "#0d9488"),
        ("3", "🔍", "JD Matching", "Semantic alignment between candidate profile and job description.", ["transformers", "cosine-sim"], "#3b82f6"),
        ("4", "🤖", "LambdaMART Rank", "LightGBM learning-to-rank model with MMR diversity re-ranking.", ["LambdaMART", "MMR"], "#f59e0b"),
        ("5", "🛡️", "Honeypot Filter", "Multi-pattern fraud detection and penalty layer before final output.", ["fraud detect", "penalty"], "#ef4444"),
    ]
    flow = ['<div class="method-flow">']
    for i, (num, ico, title, desc, tags, color) in enumerate(steps):
        if i > 0:
            flow.append('<div class="method-flow-arrow">→</div>')
        tags_html = "".join(f'<span class="method-tag" style="background:{color}18;color:{color};">{t}</span>' for t in tags)
        flow.append(f"""
        <div class="method-step-card">
            <div class="method-step-num" style="background:{color};">{num}</div>
            <div class="method-step-ico">{ico}</div>
            <div class="method-step-title">{title}</div>
            <div class="method-step-desc">{desc}</div>
            <div class="method-step-tags">{tags_html}</div>
        </div>""")
    flow.append("</div>")
    st.markdown("".join(flow), unsafe_allow_html=True)

    st.markdown('<div class="section-label" style="margin:1rem 0 0.5rem;">THREE LAYERS</div>', unsafe_allow_html=True)
    l1, l2, l3 = st.columns(3, gap="medium")
    with l1:
        st.markdown("""
        <div class="layer-card layer-teal">
            <div class="layer-header"><span class="layer-icon">🎯</span><div><div class="layer-num" style="color:#0d9488;">LAYER 1</div><div class="layer-title">4-Axis ECS</div></div></div>
            <p class="layer-desc">Evidence Consistency Score — verifies candidate claims across 4 independent axes using geometric mean.</p>
            <ul class="layer-list teal">
                <li>✓ Claim vs Assessment — validates skill self-reports</li>
                <li>✓ Claim vs Experience — cross-checks career progression</li>
                <li>✓ Claim vs GitHub — verifies technical depth</li>
                <li>✓ Seniority vs Trajectory — validates career growth</li>
            </ul>
            <div class="layer-warn">⚠ Geometric mean — one contradiction kills the total score</div>
        </div>
        """, unsafe_allow_html=True)
    with l2:
        st.markdown("""
        <div class="layer-card layer-card-highlight">
            <div class="layer-header"><span class="layer-icon blue">📊</span><div><div class="layer-num" style="color:#3b82f6;">LAYER 2</div><div class="layer-title">Ranking Pipeline</div></div></div>
            <p class="layer-desc">Multi-stage LambdaMART ranking with semantic JD alignment and diversity controls.</p>
            <ul class="layer-list blue">
                <li>75 features from JSONL</li>
                <li>Semantic JD matching — sentence-transformers cosine</li>
                <li>LightGBM LambdaMART — gradient boosting for ranking</li>
                <li>Twin resolution — counterfactual analysis</li>
                <li>MMR diversity — maximal marginal relevance</li>
            </ul>
            <div class="layer-footer">🔗 Tie-break: candidate_id ascending</div>
        </div>
        """, unsafe_allow_html=True)
    with l3:
        st.markdown("""
        <div class="layer-card layer-red">
            <div class="layer-header"><span class="layer-icon orange">🛡️</span><div><div class="layer-num" style="color:#ef4444;">LAYER 3</div><div class="layer-title">Honeypot Detection</div></div></div>
            <p class="layer-desc">Multi-pattern fraud detection that penalizes suspicious profiles before final ranking.</p>
            <ul class="layer-list orange">
                <li>Impossible YoE/duration mismatch</li>
                <li>Expert with &lt;2 years — auto-flags implausible seniority</li>
                <li>50+ skills keyword stuffing</li>
                <li>Expert claims, no assessments — penalizes unvalidated claims</li>
            </ul>
            <div class="layer-footer">🔗 Tie-break: candidate_id ascending</div>
        </div>
        """, unsafe_allow_html=True)

    f1, f2 = st.columns(2, gap="medium")
    with f1:
        st.markdown("""
        <div class="card"><div class="card-body">
            <div class="card-title-sm">📋 Scoring Formula Breakdown</div>
            <table class="formula-table">
                <tr><td class="fn">Final Score</td><td class="ff">LambdaMART(features) × ECS_weight</td><td><span class="tag tag-teal">primary</span></td></tr>
                <tr><td class="fn">ECS Score</td><td class="ff">(a × b × c × d) ^ (1/4)</td><td><span class="tag tag-teal">geometric mean</span></td></tr>
                <tr><td class="fn">JD Match</td><td class="ff">cosine_sim(profile_emb, jd_emb)</td><td><span class="tag tag-blue">semantic</span></td></tr>
                <tr><td class="fn">Diversity</td><td class="ff">MMR(λ=0.15, relevance, sim)</td><td><span class="tag tag-purple">greedy</span></td></tr>
                <tr class="fn-danger"><td class="fn">Honeypot</td><td class="ff">score × penalty_multiplier</td><td><span class="tag tag-red">final flag</span></td></tr>
            </table>
        </div></div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
        <div class="card"><div class="card-body">
            <div class="card-title-sm">🎯 ECS Axis Breakdown</div>
            <div class="axis-list">
                <div class="axis-item"><span>🎯</span><div><div class="axis-item-title">Claim vs Assessment</div><div class="axis-item-sub">Self-reported vs test performance alignment</div></div><span class="tag tag-teal">Axis 1</span></div>
                <div class="axis-item"><span>📅</span><div><div class="axis-item-title">Claim vs Career</div><div class="axis-item-sub">Title/role progression consistency</div></div><span class="tag tag-blue">Axis 2</span></div>
                <div class="axis-item"><span>💻</span><div><div class="axis-item-title">Claim vs GitHub</div><div class="axis-item-sub">Technical depth vs public artifacts</div></div><span class="tag tag-orange">Axis 3</span></div>
                <div class="axis-item"><span>📈</span><div><div class="axis-item-title">Seniority vs Trajectory</div><div class="axis-item-sub">Growth rate vs claimed senior role</div></div><span class="tag tag-purple">Axis 4</span></div>
            </div>
        </div></div>
        """, unsafe_allow_html=True)
