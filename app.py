"""Redrob AI — Candidate Ranking Dashboard."""
import streamlit as st

from ui.data import is_tech, load_data
from ui.nav import render_nav
from ui.pages import about, dashboard, deep_dive, methodology, rankings
from ui.styles import inject_styles

st.set_page_config(page_title="Redrob AI", page_icon="🎯", layout="wide")
inject_styles()

df, profiles = load_data()
if df.empty:
    st.error("Run `python rank.py` first to generate ranked_candidates.csv")
    st.stop()

tech_count = sum(1 for cid in df["candidate_id"] if is_tech(cid, profiles, df))

page_name = render_nav(len(df))

st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

if page_name == "Dashboard":
    dashboard.render(df, profiles, tech_count)
elif page_name == "Rankings":
    rankings.render(df, profiles)
elif page_name == "Deep Dive":
    deep_dive.render(df, profiles)
elif page_name == "Methodology":
    methodology.render(df)
elif page_name == "About":
    about.render(df)

st.markdown("</div>", unsafe_allow_html=True)
