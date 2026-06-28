"""Global CSS matching Redrob AI mockup designs."""

GLOBAL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
    --teal: #00c2a8;
    --teal-dark: #0d9488;
    --nav-bg: #0f1419;
    --nav-border: #1e293b;
    --page-bg: #f1f5f9;
    --border: #e2e8f0;
    --shadow: 0 1px 3px rgba(15,23,42,0.06);
}

.stApp { background: var(--page-bg) !important; font-family: 'Inter', sans-serif !important; }
.main .block-container { max-width: 100% !important; padding: 0 !important; }
section[data-testid="stSidebar"], header[data-testid="stHeader"], footer, .stDeployButton { display: none !important; }
#MainMenu { visibility: hidden; }
.block-container { padding-top: 0 !important; }
.page-wrap { padding: 0 1.25rem 1.5rem; }

/* ── NAV BAR (HTML) ── */
.top-nav {
    background: var(--nav-bg);
    border-bottom: 1px solid var(--nav-border);
    margin: 0 -1rem;
    padding: 0 1.25rem;
    position: sticky;
    top: 0;
    z-index: 999;
}
.nav-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 56px;
    gap: 1rem;
}
.nav-brand { display: flex; align-items: center; gap: 0.65rem; flex-shrink: 0; }
.nav-logo-icon {
    width: 36px; height: 36px; border-radius: 10px;
    background: linear-gradient(135deg, var(--teal), #14b8a6);
    display: flex; align-items: center; justify-content: center; font-size: 1rem;
}
.nav-logo-title { font-weight: 700; color: #fff; font-size: 0.9rem; line-height: 1.2; }
.nav-logo-sub { color: #64748b; font-size: 0.62rem; }
.nav-status {
    background: rgba(0,194,168,0.12); color: var(--teal);
    padding: 0.4rem 0.85rem; border-radius: 20px;
    font-size: 0.68rem; font-weight: 600; white-space: nowrap;
    border: 1px solid rgba(0,194,168,0.25); flex-shrink: 0;
}
.nav-links {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    flex: 1;
    justify-content: center;
    flex-wrap: wrap;
}
.nav-link {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.45rem 0.85rem;
    border-radius: 8px;
    font-size: 0.78rem;
    font-weight: 500;
    color: #94a3b8 !important;
    text-decoration: none !important;
    white-space: nowrap;
    transition: all 0.15s;
    border: 1px solid transparent;
}
.nav-link:hover {
    color: #e2e8f0 !important;
    background: rgba(255,255,255,0.06);
}
.nav-link.active {
    color: #fff !important;
    background: rgba(0,194,168,0.2);
    border-color: rgba(0,194,168,0.35);
    font-weight: 600;
}

/* ── Cards & typography ── */
.card { background: #fff; border-radius: 14px; border: 1px solid var(--border); box-shadow: var(--shadow); }
.card-header { padding: 0.85rem 1.1rem; border-bottom: 1px solid #f1f5f9; display: flex; align-items: center; justify-content: space-between; }
.card-body { padding: 1rem 1.1rem; }
.card-title-sm { font-size: 0.78rem; font-weight: 700; color: #0f172a; margin-bottom: 0.15rem; }
.card-sub-sm { color: #94a3b8; font-size: 0.6rem; margin-bottom: 0.5rem; }
.section-label { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #94a3b8; }
.page-title { color: var(--teal); font-size: 1.55rem; font-weight: 800; margin: 0; }
.page-title-dark { color: #0f172a; font-size: 1.55rem; font-weight: 800; margin: 0; }
.page-sub { color: #64748b; font-size: 0.8rem; margin: 0.2rem 0 0; }
.teal-link { color: var(--teal); font-weight: 600; font-size: 0.74rem; }

/* ── Hero ── */
.hero-dark {
    background: linear-gradient(135deg, #0a2e2a 0%, #0d3d38 40%, #0a2825 100%);
    border-radius: 16px; padding: 1.75rem 2rem; color: #fff;
    box-shadow: 0 4px 24px rgba(0,0,0,0.15); position: relative; overflow: hidden;
}
.hero-eyebrow { font-size: 0.65rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: var(--teal); margin-bottom: 0.35rem; }
.hero-title { font-size: 1.65rem; font-weight: 800; line-height: 1.15; margin: 0; color: #fff; }
.hero-sub { color: rgba(255,255,255,0.6); font-size: 0.78rem; margin: 0.45rem 0 0.85rem; }
.hero-tags { display: flex; gap: 0.35rem; flex-wrap: wrap; }
.hero-tag { background: rgba(0,194,168,0.12); border: 1px solid rgba(0,194,168,0.3); color: #6ee7b7; padding: 0.2rem 0.55rem; border-radius: 6px; font-size: 0.62rem; }

/* ── Metrics ── */
.metric-card { background: #fff; border-radius: 14px; padding: 1rem 1.15rem; border: 1px solid var(--border); display: flex; align-items: center; gap: 0.85rem; box-shadow: var(--shadow); margin-bottom: 0.55rem; }
.metric-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; flex-shrink: 0; }
.metric-label { color: #94a3b8; font-size: 0.65rem; font-weight: 600; text-transform: uppercase; }
.metric-value { color: #0f172a; font-size: 1.45rem; font-weight: 800; line-height: 1.1; }
.metric-sub { font-size: 0.68rem; font-weight: 500; }
.kpi-card { background: #fff; border-radius: 12px; padding: 0.85rem 1rem; border: 1px solid var(--border); text-align: center; border-bottom: 3px solid var(--accent, var(--teal)); box-shadow: var(--shadow); }
.kpi-label { color: #94a3b8; font-size: 0.58rem; font-weight: 700; text-transform: uppercase; }
.kpi-value { color: #0f172a; font-size: 1.35rem; font-weight: 800; margin: 0.15rem 0; }
.kpi-sub { color: #64748b; font-size: 0.62rem; }

/* ── Pipeline ── */
.pipeline-row { display: flex; align-items: center; gap: 0.3rem; flex-wrap: wrap; }
.pipeline-step { display: inline-flex; align-items: center; gap: 0.4rem; background: #fff; border: 1px solid var(--border); border-radius: 10px; padding: 0.45rem 0.75rem; }
.pipeline-arrow { color: #cbd5e1; }
.pipeline-icon { width: 24px; height: 24px; border-radius: 6px; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 0.62rem; }
.pipeline-title { font-weight: 600; font-size: 0.7rem; }
.pipeline-sub { color: #94a3b8; font-size: 0.58rem; }

/* ── Table ── */
.rank-badge { width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.72rem; }
.rank-1 { background: #f97316; color: #fff; }
.rank-2 { background: #64748b; color: #fff; }
.rank-3 { background: #a16207; color: #fff; }
.rank-default { background: #ccfbf1; color: #0d9488; }
.role-pill { display: inline-block; padding: 0.18rem 0.55rem; border-radius: 6px; font-size: 0.65rem; font-weight: 600; }
.score-bar-wrap { background: #f1f5f9; border-radius: 4px; height: 5px; overflow: hidden; margin-top: 0.2rem; }
.score-bar { height: 100%; background: var(--teal); border-radius: 4px; }
.table-row { display: grid; align-items: center; padding: 0.65rem 1rem; border-bottom: 1px solid #f1f5f9; font-size: 0.78rem; }
.table-row:hover { background: #fafbfc; }
.table-header { display: grid; align-items: center; padding: 0.65rem 1rem; background: #f8fafc; border-bottom: 1px solid var(--border); font-weight: 600; color: #64748b; font-size: 0.65rem; text-transform: uppercase; }
.dash-row { grid-template-columns: 36px 1fr auto 90px 70px; gap: 0.75rem; }
.cand-title { font-weight: 600; font-size: 0.82rem; color: #0f172a; }
.cand-id { color: #94a3b8; font-size: 0.65rem; }
.cand-score { font-weight: 700; font-size: 0.85rem; }
.cand-ecs { color: #94a3b8; font-size: 0.58rem; margin-top: 0.15rem; }
.cand-yoe { text-align: right; color: #64748b; font-size: 0.76rem; }
.ai-badge { background: #f5f3ff; color: #8b5cf6; width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 0.68rem; font-weight: 700; }

/* ── Rankings spacing ── */
.rankings-header { margin: 0.75rem 0 0; }
.rankings-spacer { height: 0.75rem; }
.rankings-toolbar-spacer { height: 1.25rem; }
.rankings-toolbar { margin-bottom: 0.75rem; }
.leaderboard-card { margin-top: 0.5rem; overflow: hidden; }
.leaderboard-title { margin: 0.5rem 0 0.3rem; }
.pag-info { color: #64748b; font-size: 0.72rem; padding: 0.85rem 1rem; }
.shortlist-banner { background: #fef3c7; color: #92400e; padding: 0.5rem 1rem; border-radius: 8px; font-size: 0.75rem; margin-top: 0.5rem; font-weight: 600; }

/* ── Charts ── */
.weight-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.45rem; }
.weight-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.weight-bar-bg { flex: 1.5; background: #f1f5f9; border-radius: 4px; height: 6px; overflow: hidden; }
.weight-bar-fill { height: 100%; border-radius: 4px; }
.dist-chart { display: flex; align-items: flex-end; gap: 4px; height: 55px; }
.dist-bar { flex: 1; background: linear-gradient(180deg, var(--teal), #14b8a6); border-radius: 3px 3px 0 0; min-height: 2px; }
.dist-labels { display: flex; justify-content: space-between; font-size: 0.62rem; color: #94a3b8; margin-top: 0.35rem; }
.status-card { background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 12px; padding: 0.85rem; }
.status-ok { color: var(--teal-dark); font-weight: 600; font-size: 0.78rem; }
.status-grid { display: grid; grid-template-columns: 1fr auto; gap: 0.35rem; font-size: 0.7rem; color: #64748b; }
.status-grid div:nth-child(even) { font-weight: 600; color: #0f172a; text-align: right; }
.status-grid .teal { color: #0d9488 !important; }

/* ── Deep Dive ── */
.deep-header { margin: 0.75rem 0 0.5rem; }
.deep-section-title { font-size: 0.82rem; font-weight: 700; color: #0f172a; margin: 0.65rem 0 0.1rem; }
.deep-section-sub { color: #64748b; font-size: 0.68rem; margin-bottom: 0.5rem; }
.profile-dark { background: linear-gradient(135deg, #111827, #1a2332); border-radius: 16px; padding: 1.5rem 1.75rem; color: #fff; border: 1px solid #1e293b; margin-bottom: 0.5rem; }
.profile-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }
.profile-left { display: flex; align-items: center; gap: 1rem; }
.profile-rank-box { width: 56px; height: 56px; border-radius: 14px; background: linear-gradient(135deg, var(--teal), #14b8a6); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.3rem; box-shadow: 0 0 20px rgba(0,194,168,0.35); flex-shrink: 0; }
.profile-title { color: var(--teal); margin: 0; font-size: 1.25rem; font-weight: 700; }
.profile-badges { display: flex; gap: 0.35rem; margin-top: 0.35rem; flex-wrap: wrap; }
.profile-badge { background: rgba(0,194,168,0.15); border: 1px solid rgba(0,194,168,0.3); color: #6ee7b7; padding: 0.2rem 0.55rem; border-radius: 6px; font-size: 0.62rem; }
.profile-badge-gold { background: rgba(234,179,8,0.15); border: 1px solid rgba(234,179,8,0.3); color: #fde047; padding: 0.2rem 0.55rem; border-radius: 6px; font-size: 0.62rem; }
.profile-score-label { font-size: 0.6rem; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.05em; text-align: right; }
.profile-score-value { font-size: 2rem; font-weight: 800; color: var(--teal); text-align: right; line-height: 1; }
.profile-summary { margin-top: 1rem; padding: 0.85rem; background: rgba(0,0,0,0.3); border-radius: 10px; border: 1px solid #334155; color: #cbd5e1; font-size: 0.82rem; line-height: 1.65; }
.signal-card { background: #fff; border-radius: 12px; padding: 0.85rem; border: 1px solid var(--border); box-shadow: var(--shadow); height: 100%; }
.signal-card-dark { background: #1a2332; border: 1px solid #334155; border-radius: 12px; padding: 0.85rem; color: #fff; height: 100%; }
.signal-label { color: #94a3b8; font-size: 0.6rem; font-weight: 600; text-transform: uppercase; }
.signal-value { font-size: 1.35rem; font-weight: 800; line-height: 1.2; margin: 0.15rem 0; }
.signal-sub { font-size: 0.62rem; color: #64748b; }
.signal-bar-bg { border-radius: 4px; height: 5px; overflow: hidden; margin-top: 0.4rem; }
.signal-bar-fill { height: 100%; border-radius: 4px; }
.axis-card { background: #fff; border-radius: 12px; padding: 0.9rem; border: 1px solid var(--border); box-shadow: var(--shadow); height: 100%; }
.axis-icon { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-bottom: 0.4rem; }
.axis-name { font-size: 0.72rem; font-weight: 600; }
.axis-sub { color: #94a3b8; font-size: 0.58rem; }
.axis-score { font-size: 1.35rem; font-weight: 800; margin: 0.2rem 0; }
.axis-score span { font-size: 0.65rem; font-weight: 500; color: #94a3b8; }
.axis-badge { display: inline-block; margin-top: 0.35rem; background: #f1f5f9; padding: 0.15rem 0.45rem; border-radius: 5px; font-size: 0.58rem; color: #64748b; }
.geo-mean-bar { background: #fff; border: 1px solid var(--border); border-radius: 12px; padding: 1rem 1.25rem; margin: 0.65rem 0; display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; box-shadow: var(--shadow); }
.geo-value { color: var(--teal); font-size: 1.75rem; font-weight: 800; }
.geo-sub { color: #64748b; font-size: 0.68rem; }
.geo-stat-val { font-size: 1.15rem; font-weight: 800; }
.geo-stat-val.green { color: #22c55e; }
.geo-rank-badge { background: var(--teal); color: #fff; padding: 0.5rem 1.1rem; border-radius: 10px; font-weight: 700; font-size: 0.78rem; white-space: nowrap; }
.breakdown-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.45rem; }
.breakdown-label { width: 8.5rem; font-size: 0.68rem; color: #374151; flex-shrink: 0; }
.breakdown-bar-bg { flex: 1; background: #f1f5f9; border-radius: 4px; height: 6px; overflow: hidden; }
.breakdown-bar { height: 100%; border-radius: 4px; }
.breakdown-val { width: 3rem; text-align: right; font-size: 0.68rem; font-weight: 600; }
.qual-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.all-clear { background: #ecfdf5; color: #0d9488; padding: 0.15rem 0.45rem; border-radius: 5px; font-size: 0.6rem; font-weight: 600; }
.qual-item { display: flex; gap: 0.5rem; margin-bottom: 0.5rem; }
.qual-title { font-weight: 600; font-size: 0.72rem; color: #0f172a; }
.qual-desc { color: #64748b; font-size: 0.62rem; }
.sidebar-card { margin-top: 0.5rem; }
.skill-level-label { font-size: 0.62rem; font-weight: 700; margin: 0.4rem 0 0.25rem; text-transform: uppercase; }
.skill-tag { padding: 0.18rem 0.5rem; border-radius: 5px; font-size: 0.62rem; margin: 0.15rem 0.15rem 0 0; display: inline-block; }
.reasoning-text { color: #374151; font-size: 0.78rem; line-height: 1.65; margin: 0; }

/* ── Methodology ── */
.method-header { margin: 0.75rem 0 0.85rem; padding: 1.25rem 1.5rem; display: flex; justify-content: space-between; align-items: center; gap: 1.5rem; }
.method-badge { font-size: 0.65rem; font-weight: 700; color: var(--teal); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.3rem; }
.method-title { font-size: 1.45rem; font-weight: 800; color: #0f172a; margin: 0; }
.method-title span { color: var(--teal); }
.method-desc { color: #64748b; font-size: 0.78rem; margin: 0.35rem 0 0; line-height: 1.55; max-width: 620px; }
.method-status-card { text-align: center; background: #ecfdf5; border-radius: 14px; padding: 1rem 1.5rem; border: 1px solid #a7f3d0; flex-shrink: 0; min-width: 160px; }
.method-status-icon { font-size: 1.5rem; }
.method-status-label { font-size: 0.6rem; font-weight: 700; color: #0d9488; text-transform: uppercase; margin-top: 0.25rem; }
.method-status-val { color: #0d9488; font-size: 1.35rem; font-weight: 800; }
.method-status-sub { color: #64748b; font-size: 0.62rem; }
.method-flow { display: flex; align-items: stretch; gap: 0.35rem; overflow-x: auto; padding-bottom: 0.25rem; }
.method-flow-arrow { color: #cbd5e1; display: flex; align-items: center; font-size: 1.1rem; flex-shrink: 0; }
.method-step-card { background: #fff; border: 1px solid var(--border); border-radius: 12px; padding: 0.85rem 0.75rem; flex: 1; min-width: 155px; position: relative; box-shadow: var(--shadow); }
.method-step-num { position: absolute; top: 0.55rem; left: 0.55rem; width: 20px; height: 20px; border-radius: 50%; color: #fff; font-size: 0.6rem; font-weight: 700; display: flex; align-items: center; justify-content: center; }
.method-step-ico { text-align: center; font-size: 1.2rem; margin: 0.5rem 0 0.3rem; }
.method-step-title { font-size: 0.74rem; font-weight: 700; color: #0f172a; text-align: center; }
.method-step-desc { color: #64748b; font-size: 0.58rem; line-height: 1.45; text-align: center; margin: 0.3rem 0; }
.method-step-tags { text-align: center; }
.method-tag { padding: 0.12rem 0.4rem; border-radius: 4px; font-size: 0.55rem; font-weight: 600; margin: 0.1rem; display: inline-block; }
.layer-card { background: #fff; border-radius: 14px; padding: 1.2rem; border: 1px solid var(--border); box-shadow: var(--shadow); height: 100%; }
.layer-card-highlight { border: 2px solid #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }
.layer-teal { border-top: 3px solid #0d9488; }
.layer-red { border-top: 3px solid #ef4444; }
.layer-header { display: flex; align-items: center; gap: 0.65rem; margin-bottom: 0.5rem; }
.layer-icon { font-size: 1.3rem; }
.layer-num { font-size: 0.6rem; font-weight: 700; text-transform: uppercase; }
.layer-title { font-size: 0.9rem; font-weight: 700; color: #0f172a; }
.layer-desc { color: #64748b; font-size: 0.72rem; line-height: 1.6; margin: 0 0 0.5rem; }
.layer-list { font-size: 0.68rem; margin: 0.4rem 0; padding-left: 1.1rem; line-height: 1.75; color: #64748b; }
.layer-list.teal li { color: #64748b; }
.layer-list.blue { color: #3b82f6; list-style: disc; }
.layer-list.orange { color: #ea580c; list-style: disc; }
.layer-warn { background: #fff7ed; border: 1px solid #fde68a; border-radius: 8px; padding: 0.5rem 0.65rem; font-size: 0.65rem; color: #92400e; margin-top: 0.5rem; }
.layer-footer { color: #64748b; font-size: 0.65rem; margin-top: 0.5rem; }
.formula-table { width: 100%; border-collapse: collapse; font-size: 0.7rem; }
.formula-table td { padding: 0.4rem 0.3rem; vertical-align: middle; border-bottom: 1px solid #f1f5f9; }
.formula-table .fn { font-weight: 600; white-space: nowrap; }
.formula-table .ff { color: #64748b; font-family: monospace; font-size: 0.65rem; }
.formula-table .fn-danger { background: #fef2f2; }
.tag { padding: 0.1rem 0.35rem; border-radius: 4px; font-size: 0.58rem; font-weight: 600; white-space: nowrap; }
.tag-teal { background: #ecfdf5; color: #0d9488; }
.tag-blue { background: #eff6ff; color: #3b82f6; }
.tag-purple { background: #f5f3ff; color: #8b5cf6; }
.tag-red { background: #fef2f2; color: #ef4444; }
.tag-orange { background: #fff7ed; color: #f59e0b; }
.axis-list { display: flex; flex-direction: column; gap: 0.55rem; }
.axis-item { display: flex; align-items: center; gap: 0.65rem; }
.axis-item-title { font-weight: 600; font-size: 0.72rem; }
.axis-item-sub { color: #64748b; font-size: 0.62rem; }

/* ── About ── */
.about-hero {
    background: linear-gradient(135deg, #0a2e2a 0%, #0d3d38 40%, #0a2825 100%);
    border-radius: 16px; padding: 1.75rem 2rem; color: #fff; margin-top: 0.75rem;
    display: flex; justify-content: space-between; gap: 1.5rem; align-items: flex-start;
    box-shadow: 0 4px 24px rgba(0,0,0,0.15);
}
.about-hero-left { flex: 1.4; }
.about-hero-text { color: rgba(255,255,255,0.65); font-size: 0.82rem; margin: 0.5rem 0 0; line-height: 1.65; }
.about-hero-metrics { flex: 0.85; display: flex; flex-direction: column; gap: 0.45rem; }
.hero-metric { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12); border-radius: 12px; padding: 0.7rem 1rem; display: flex; align-items: center; gap: 0.75rem; }
.hm-label { font-size: 0.58rem; font-weight: 600; color: rgba(255,255,255,0.5); text-transform: uppercase; flex: 1; }
.hm-val { font-size: 1.15rem; font-weight: 800; color: #fff; }
.hm-sub { font-size: 0.62rem; font-weight: 600; }
.hm-sub.green { color: #6ee7b7; }
.hm-sub.yellow { color: #fde047; }
.diff-card { background: #fff; border-radius: 14px; padding: 1.2rem; border: 1px solid var(--border); border-top: 3px solid #0d9488; box-shadow: var(--shadow); margin-bottom: 0.65rem; }
.diff-num { font-size: 0.6rem; font-weight: 700; text-transform: uppercase; }
.diff-title { margin: 0.2rem 0 0.35rem; font-size: 0.92rem; font-weight: 700; color: #0f172a; }
.diff-body { color: #64748b; font-size: 0.78rem; line-height: 1.6; margin: 0; }
.diff-tag { display: inline-block; margin-top: 0.45rem; background: #f1f5f9; padding: 0.2rem 0.55rem; border-radius: 6px; font-size: 0.62rem; color: #64748b; }
.tech-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; }
.tech-card { border-radius: 10px; padding: 0.85rem; border: 1px solid; }
.tech-card-head { display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.3rem; }
.tech-icon { width: 26px; height: 26px; border-radius: 6px; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 0.65rem; }
.tech-card-title { font-weight: 600; font-size: 0.76rem; color: #0f172a; }
.tech-card-desc { color: #64748b; font-size: 0.66rem; line-height: 1.45; }
.tech-footnote { color: #94a3b8; font-size: 0.68rem; margin: 0.6rem 0 0; }
.insights-list { display: flex; flex-direction: column; gap: 0.55rem; }
.insight-item { display: flex; gap: 0.5rem; font-size: 0.74rem; color: #374151; line-height: 1.5; }
.dot { font-weight: 700; flex-shrink: 0; }
.dot.teal { color: #0d9488; } .dot.blue { color: #3b82f6; } .dot.purple { color: #8b5cf6; }
.stage-row { display: flex; align-items: center; gap: 0.5rem; padding: 0.45rem 0.65rem; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 0.3rem; }
.stage-num { width: 22px; height: 22px; border-radius: 6px; background: #0d9488; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 0.6rem; font-weight: 700; }
.stage-name { flex: 1; font-size: 0.72rem; font-weight: 500; }
.stage-done { background: #ecfdf5; color: #0d9488; padding: 0.12rem 0.4rem; border-radius: 5px; font-size: 0.58rem; font-weight: 600; }

/* ── Inputs ── */
div[data-testid="stTextInput"] input { border-radius: 10px !important; border: 1px solid var(--border) !important; padding: 0.55rem 0.85rem !important; font-size: 0.78rem !important; }
div[data-testid="stSelectbox"] > div > div { border-radius: 10px !important; border: 1px solid var(--border) !important; }
"""


def inject_styles():
    import streamlit as st
    st.markdown(f"<style>{GLOBAL_CSS}</style>", unsafe_allow_html=True)
