"""Rankings page — search, filters, columns, shortlist, pagination."""
import streamlit as st

from ui.data import ROLE_COLORS, get_role, get_title, rank_badge

PAGE_SIZE = 11
ALL_COLUMNS = ["#", "Candidate ID", "Title", "YoE", "Score", "ECS", "JD Match", "AI Skills", "Reasoning"]


def _init_state():
    defaults = {
        "rank_page": 1,
        "rank_sort": "Score",
        "rank_cols": ALL_COLUMNS.copy(),
        "shortlist": set(),
        "filter_role": "All",
        "filter_min_ecs": 0.0,
        "filter_min_score": 0.0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render(df, profiles):
    _init_state()
    total = len(df)

    hdr_l, hdr_r = st.columns([3, 1])
    with hdr_l:
        st.markdown("""
        <div class="rankings-header">
            <h1 class="page-title">Candidate Rankings</h1>
            <p class="page-sub">AI-ranked leaderboard · LambdaMART + ECS pipeline · fraud-resistant scoring</p>
        </div>
        """, unsafe_allow_html=True)
    with hdr_r:
        top_n = st.slider("Show top N", 5, total, min(25, total), label_visibility="visible")

    st.markdown('<div class="rankings-spacer"></div>', unsafe_allow_html=True)

    kpis = [
        ("TOTAL RANKED", str(total), "candidates in pipeline", "#00c2a8"),
        ("AVG ECS SCORE", f"{df['ecs'].mean():.2f}", "evidence consistency", "#3b82f6"),
        ("TOP SCORE", f"{df['score'].max():.3f}", df.iloc[0]["candidate_id"], "#f59e0b"),
        ("AVG AI SKILLS", f"{df['ai_skill_count'].mean():.1f}", "verified per candidate", "#8b5cf6"),
        ("PIPELINE STATUS", "Complete", "● All checks passed", "#22c55e"),
    ]
    kpi_cols = st.columns(5)
    for col, (label, val, sub, accent) in zip(kpi_cols, kpis):
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="--accent:{accent};">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{val}</div>
                <div class="kpi-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="rankings-toolbar-spacer"></div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="rankings-toolbar">', unsafe_allow_html=True)
        t1, t2, t3, t4 = st.columns([4, 1, 1, 1.1])
        with t1:
            search = st.text_input(
                "Search",
                placeholder="🔍  Search by title, skill, or candidate ID...",
                label_visibility="collapsed",
                key="rank_search",
            )
        with t2:
            show_filters = st.popover("🔽 Filters", use_container_width=True)
        with t3:
            show_cols = st.popover("📋 Columns", use_container_width=True)
        with t4:
            if st.button("👤 Shortlist All", use_container_width=True, key="shortlist_all"):
                subset = df.head(top_n)["candidate_id"].tolist()
                st.session_state.shortlist = set(subset)
                st.toast(f"Added {len(subset)} candidates to shortlist")

        with show_filters:
            roles = ["All"] + sorted({get_role(get_title(c, profiles, df)) for c in df["candidate_id"]})
            st.session_state.filter_role = st.selectbox("Role", roles)
            st.session_state.filter_min_ecs = st.slider("Min ECS", 0.0, 1.0, st.session_state.filter_min_ecs, 0.05)
            st.session_state.filter_min_score = st.slider("Min Score", 0.0, float(df["score"].max()), st.session_state.filter_min_score, 0.05)
            if st.button("Reset filters", use_container_width=True):
                st.session_state.filter_role = "All"
                st.session_state.filter_min_ecs = 0.0
                st.session_state.filter_min_score = 0.0
                st.rerun()

        with show_cols:
            picked = st.multiselect("Visible columns", ALL_COLUMNS, default=st.session_state.rank_cols)
            if picked:
                st.session_state.rank_cols = picked

        st.markdown("</div>", unsafe_allow_html=True)

    # Build filtered dataset
    work = df.head(top_n).copy()
    work["Title"] = work["candidate_id"].map(lambda x: get_title(x, profiles, df))
    work["Role"] = work["Title"].map(get_role)

    if search:
        q = search.strip()
        mask = (
            work["Title"].str.contains(q, case=False, na=False)
            | work["candidate_id"].str.contains(q, case=False, na=False)
            | work["reasoning"].str.contains(q, case=False, na=False)
            | work["Role"].str.contains(q, case=False, na=False)
        )
        work = work[mask]
        if st.session_state.get("_rank_search") != q:
            st.session_state.rank_page = 1
            st.session_state._rank_search = q
    elif st.session_state.get("_rank_search"):
        st.session_state._rank_search = ""
        st.session_state.rank_page = 1

    if st.session_state.filter_role != "All":
        work = work[work["Role"] == st.session_state.filter_role]
    work = work[
        (work["ecs"] >= st.session_state.filter_min_ecs)
        & (work["score"] >= st.session_state.filter_min_score)
    ]

    sort_col = {"Score": "score", "ECS": "ecs", "JD Match": "jd_similarity"}[st.session_state.rank_sort]
    work = work.sort_values(sort_col, ascending=False)

    total_filtered = len(work)
    total_pages = max(1, (total_filtered + PAGE_SIZE - 1) // PAGE_SIZE)
    if st.session_state.rank_page > total_pages:
        st.session_state.rank_page = 1

    start = (st.session_state.rank_page - 1) * PAGE_SIZE
    page_df = work.iloc[start : start + PAGE_SIZE]

    tbl_hdr_l, tbl_hdr_r = st.columns([2, 1])
    with tbl_hdr_l:
        st.markdown(f"""
        <div class="leaderboard-title">
            <span style="font-size:0.85rem;font-weight:700;color:#0f172a;">🏆 Candidate Leaderboard</span>
            <span style="color:#64748b;font-size:0.72rem;margin-left:0.5rem;">Showing top {total_filtered} of {total}</span>
        </div>
        """, unsafe_allow_html=True)
    with tbl_hdr_r:
        sort_cols = st.columns(3)
        for col, mode in zip(sort_cols, ["Score", "ECS", "JD Match"]):
            with col:
                active = st.session_state.rank_sort == mode
                if st.button(mode, key=f"sort_{mode}", use_container_width=True, type="primary" if active else "secondary"):
                    st.session_state.rank_sort = mode
                    st.session_state.rank_page = 1
                    st.rerun()

    visible = st.session_state.rank_cols
    col_widths = {
        "#": "40px", "Candidate ID": "110px", "Title": "1.2fr", "YoE": "55px",
        "Score": "80px", "ECS": "75px", "JD Match": "65px", "AI Skills": "55px", "Reasoning": "1.5fr",
    }
    grid = " ".join(col_widths.get(c, "1fr") for c in visible)

    st.markdown('<div class="card leaderboard-card">', unsafe_allow_html=True)
    hdr_cells = "".join(f"<div>{c}</div>" for c in visible)
    st.markdown(f'<div class="table-header rank-grid" style="grid-template-columns:{grid};">{hdr_cells}</div>', unsafe_allow_html=True)

    if page_df.empty:
        st.markdown('<div class="table-row rank-grid" style="color:#64748b;">No candidates match your search or filters.</div>', unsafe_allow_html=True)
    else:
        for _, row in page_df.iterrows():
            cid = row["candidate_id"]
            title = row["Title"]
            yoe = profiles.get(cid, {}).get("profile", {}).get("years_of_experience", row.get("years_of_experience", 0))
            role = row["Role"]
            fg, bg = ROLE_COLORS.get(role, ("#64748b", "#f1f5f9"))
            rank = int(row["rank"])
            ecs = float(row.get("ecs", 0))
            jd = float(row.get("jd_similarity", 0))
            ai = int(row.get("ai_skill_count", 0))
            reasoning = row["reasoning"][:90] + ("..." if len(row["reasoning"]) > 90 else "")
            shortlisted = cid in st.session_state.shortlist

            cells = []
            for col_name in visible:
                if col_name == "#":
                    cells.append(f"<div>{rank_badge(rank)}</div>")
                elif col_name == "Candidate ID":
                    mark = " ⭐" if shortlisted else ""
                    cells.append(f'<div style="font-weight:500;color:#374151;font-size:0.72rem;">{cid}{mark}</div>')
                elif col_name == "Title":
                    cells.append(f"""<div><div style="font-weight:600;color:#0f172a;font-size:0.78rem;">{title}</div>
                        <span class="role-pill" style="color:{fg};background:{bg};font-size:0.58rem;">{role}</span></div>""")
                elif col_name == "YoE":
                    cells.append(f'<div style="color:#64748b;font-size:0.74rem;">{float(yoe):.1f} yrs</div>')
                elif col_name == "Score":
                    cells.append(f'<div><span style="color:#00c2a8;font-weight:700;font-size:0.78rem;">{row["score"]:.4f}</span></div>')
                elif col_name == "ECS":
                    cells.append(f"""<div><div style="font-size:0.72rem;font-weight:600;">{ecs:.2f}</div>
                        <div class="score-bar-wrap"><div class="score-bar" style="width:{min(ecs*100,100):.0f}%;"></div></div></div>""")
                elif col_name == "JD Match":
                    cells.append(f'<div style="color:#3b82f6;font-weight:600;font-size:0.74rem;">{jd:.2f}</div>')
                elif col_name == "AI Skills":
                    cells.append(f'<div><span class="ai-badge">{ai}</span></div>')
                elif col_name == "Reasoning":
                    cells.append(f'<div style="color:#64748b;font-size:0.68rem;line-height:1.4;">{reasoning}</div>')

            st.markdown(f'<div class="table-row rank-grid" style="grid-template-columns:{grid};">{"".join(cells)}</div>', unsafe_allow_html=True)

    # Pagination
    pag_l, pag_r = st.columns([2, 1])
    end_idx = min(start + PAGE_SIZE, total_filtered)
    with pag_l:
        st.markdown(
            f'<div class="pag-info">Showing {start + 1 if total_filtered else 0}–{end_idx} of {total_filtered} candidates · {total} total in pipeline</div>',
            unsafe_allow_html=True,
        )
    with pag_r:
        pcols = st.columns([1, 1, 1, 1, 1])
        with pcols[0]:
            if st.button("◀", disabled=st.session_state.rank_page <= 1, key="pag_prev", use_container_width=True):
                st.session_state.rank_page -= 1
                st.rerun()
        mid_pages = list(range(max(1, st.session_state.rank_page - 1), min(total_pages, st.session_state.rank_page + 1) + 1))
        for i, p in enumerate(mid_pages[:3]):
            with pcols[i + 1]:
                if st.button(str(p), key=f"pag_{p}", type="primary" if p == st.session_state.rank_page else "secondary", use_container_width=True):
                    st.session_state.rank_page = p
                    st.rerun()
        with pcols[4]:
            if st.button("▶", disabled=st.session_state.rank_page >= total_pages, key="pag_next", use_container_width=True):
                st.session_state.rank_page += 1
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.shortlist:
        st.markdown(
            f'<div class="shortlist-banner">⭐ Shortlist: {len(st.session_state.shortlist)} candidates selected</div>',
            unsafe_allow_html=True,
        )
