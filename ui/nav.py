"""Top navigation — pure HTML links, no radio/export/deploy."""
import streamlit as st

PAGES = [
    ("📊", "Dashboard"),
    ("🏆", "Rankings"),
    ("🔍", "Deep Dive"),
    ("📐", "Methodology"),
    ("ℹ️", "About"),
]
PAGE_NAMES = [name for _, name in PAGES]


def render_nav(total: int) -> str:
    current = st.query_params.get("page", "Dashboard")
    if current not in PAGE_NAMES:
        current = "Dashboard"

    links = ""
    for ico, name in PAGES:
        active = "active" if name == current else ""
        links += f'<a class="nav-link {active}" href="?page={name}" target="_self">{ico}&nbsp;{name}</a>'

    st.markdown(f"""
    <div class="top-nav">
        <div class="nav-inner">
            <div class="nav-brand">
                <div class="nav-logo-icon">🎯</div>
                <div>
                    <div class="nav-logo-title">Redrob AI</div>
                    <div class="nav-logo-sub">Ranking Engine v2.0</div>
                </div>
            </div>
            <nav class="nav-links">{links}</nav>
            <div class="nav-status">● Pipeline Complete — {total} ranked</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    return current
