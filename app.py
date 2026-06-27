"""
Streamlit Demo — Corroborated Evidence Ranking Engine
Run: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import json
import os
import sys

st.set_page_config(page_title="Candidate Ranking Engine", layout="wide")

st.title("Corroborated Evidence Ranking Engine")
st.markdown("*4-axis Evidence Consistency + LightGBM + Twin Resolution*")

st.sidebar.header("Controls")
uploaded = st.sidebar.file_uploader("Upload candidates.jsonl", type=["jsonl"])
run_btn = st.sidebar.button("Run Pipeline")

if run_btn:
    if uploaded:
        with st.spinner("Processing..."):
            os.makedirs("/tmp/upload", exist_ok=True)
            path = "/tmp/upload/candidates.jsonl"
            with open(path, "wb") as f:
                f.write(uploaded.read())
            sys.argv = ["rank.py", "/tmp/upload", "/tmp/upload/output.csv"]
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from rank import main
            main()
            result = pd.read_csv("/tmp/upload/output.csv")
        st.success(f"Ranked {len(result)} candidates")
        st.dataframe(result, use_container_width=True)
    else:
        st.info("Upload candidates.jsonl to get started")
else:
    st.markdown("""
    ### How it works
    1. Upload your `candidates.jsonl` file
    2. The pipeline extracts 52 features per candidate
    3. 4-axis ECS computes evidence consistency
    4. LightGBM LambdaMART + heuristic blend ranks candidates
    5. Twin resolution finds counterfactuals

    ### Architecture
    ```
    100K Candidates → Features + ECS → LightGBM + Heuristic
    → Twin Resolution → Ranked Top 100
    ```
    """)
