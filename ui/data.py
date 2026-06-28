"""Shared data loading and helper functions."""
import json
import os

import pandas as pd
import streamlit as st

TECH = [
    "engineer", "scientist", "architect", "developer", "sre", "machine learning",
    "data scientist", "ai ", "ml ", "nlp", "deep learning", "computer vision", "researcher",
]

ROLE_COLORS = {
    "ML / Search": ("#0d9488", "#ccfbf1"),
    "AI / LLM": ("#0891b2", "#ecfeff"),
    "RecSys": ("#ea580c", "#fff7ed"),
    "Applied ML": ("#2563eb", "#eff6ff"),
    "ML Eng": ("#7c3aed", "#ede9fe"),
    "Data Science": ("#ca8a04", "#fefce8"),
    "CV / Vision": ("#be185d", "#fdf2f8"),
    "Research": ("#4f46e5", "#eef2ff"),
}

RANK_COLORS = {1: "#f97316", 2: "#64748b", 3: "#a16207"}


@st.cache_data
def load_data():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = prof_path = None
    for root, _, files in os.walk(base):
        for f in files:
            if f == "ranked_candidates.csv" and not csv_path:
                csv_path = os.path.join(root, f)
            if f == "ranked_profiles.json" and not prof_path:
                prof_path = os.path.join(root, f)
        if csv_path and prof_path:
            break
    df = pd.read_csv(csv_path) if csv_path else pd.DataFrame()
    profiles = json.load(open(prof_path, encoding="utf-8")) if prof_path else {}
    return df, profiles


def get_title(cid, profiles, df=None):
    title = profiles.get(cid, {}).get("profile", {}).get("current_title")
    if title:
        return title
    if df is not None and not df.empty:
        rows = df[df["candidate_id"] == cid]
        if not rows.empty:
            reasoning = str(rows.iloc[0].get("reasoning", ""))
            if reasoning:
                return reasoning.split("—")[0].split(",")[0].strip()
    return "Unknown"


def is_tech(cid, profiles, df=None):
    return any(k in get_title(cid, profiles, df).lower() for k in TECH)


def get_role(title):
    t = title.lower()
    if "search" in t or "retrieval" in t:
        return "ML / Search"
    if "ai" in t or "llm" in t:
        return "AI / LLM"
    if "recommendation" in t or "recsys" in t:
        return "RecSys"
    if "applied" in t and "ml" in t:
        return "Applied ML"
    if "machine learning" in t or " ml " in t:
        return "ML Eng"
    if "data scientist" in t:
        return "Data Science"
    if "vision" in t or "cv" in t:
        return "CV / Vision"
    if "research" in t or "scientist" in t:
        return "Research"
    return "ML Eng"


def rank_badge(rank):
    if rank in RANK_COLORS:
        return f'<div class="rank-badge rank-{rank}">{rank}</div>'
    return f'<div class="rank-badge rank-default">{rank}</div>'
