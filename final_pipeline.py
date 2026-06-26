"""
Fully Integrated Ranking Pipeline

Uses all components:
1. Semantic Recall (embeddings)
2. Feature Extraction (45 features)
3. JD Disqualifier Gates (soft penalties)
4. Evidence Consistency Engine (4-axis ECS + geometric mean)
5. Behavioral Reality Layer (sentinel-safe)
6. Behavioral Twin Resolution (clusters + counterfactuals)
7. LightGBM LambdaMART (learning-to-rank)
8. Deterministic Reasoning (with counterfactuals)
"""

import sys, os, json, time, gc
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from features import load_candidates, extract_candidate_features
from evidence import compute_ecs
from ranker import train_lambdamart_ranker, prepare_ranking_features, rank_with_lambdamart
from twin_resolution import create_twin_clusters, identify_twin_pairs
from reasoning import generate_reasoning
from config import RECALL_TOP_N, TWIN_N_CLUSTERS, TWIN_TOP_N, SCORE_WEIGHTS


def main(data_dir: str, output_path: str):
    print("=" * 65)
    print("CORROBORATED EVIDENCE RANKING ENGINE — FULL PIPELINE")
    print("=" * 65)

    # 1. Load data
    print("\n[1/8] Loading candidates...")
    t0 = time.time()
    jsonl_path = None
    for root, dirs, files in os.walk(data_dir):
        for f in files:
            if f == "candidates.jsonl":
                jsonl_path = os.path.join(root, f)
                break
        if jsonl_path:
            break

    candidates = load_candidates(jsonl_path)
    cand_lookup = {c["candidate_id"]: c for c in candidates}
    print(f"  Loaded {len(candidates)} candidates in {time.time()-t0:.1f}s")

    # 2. Feature extraction
    print("\n[2/8] Extracting features...")
    t0 = time.time()
    all_features = {}
    all_ecs = {}
    for i, cand in enumerate(candidates):
        cid = cand["candidate_id"]
        feat = extract_candidate_features(cand)
        ecs = compute_ecs(feat)
        all_features[cid] = feat
        all_ecs[cid] = ecs
        if (i + 1) % 25000 == 0:
            print(f"  {i+1}/{len(candidates)}")
    print(f"  Done in {time.time()-t0:.1f}s")
    gc.collect()

    # Build DataFrames
    feature_df = pd.DataFrame(all_features).T
    ecs_df = pd.DataFrame(all_ecs).T
    print(f"  Features: {feature_df.shape}")
    print(f"  ECS computed for {len(ecs_df)} candidates")

    # 3. JD Gates
    print("\n[3/8] JD Disqualifier Gates...")
    gate = pd.Series(0.0, index=feature_df.index)
    gate += feature_df.get("is_hr", 0).astype(float) * 0.4
    gate += feature_df.get("is_accountant", 0).astype(float) * 0.4
    gate += feature_df.get("is_sales", 0).astype(float) * 0.3
    gate += feature_df.get("is_content_writer", 0).astype(float) * 0.3
    gate += feature_df.get("is_designer", 0).astype(float) * 0.3
    gate += feature_df.get("is_civil", 0).astype(float) * 0.3
    gate += feature_df.get("is_mechanical", 0).astype(float) * 0.3
    gate += feature_df.get("consulting_only", 0).astype(float) * 0.2
    gate = gate.clip(upper=0.6)
    n_penalized = (gate > 0).sum()
    print(f"  {n_penalized} candidates gate-penalized")

    # 4. Behavioral + Availability (baseline score)
    print("\n[4/8] Behavioral score...")
    response = feature_df.get("response_rate", pd.Series(0, index=feature_df.index)).astype(float)
    interview = feature_df.get("interview_completion", pd.Series(0, index=feature_df.index)).astype(float)
    behavioral = (response * 0.5 + interview * 0.5).clip(0, 1)

    # 5. Twin Resolution
    print("\n[5/8] Behavioral Twin Resolution...")
    t0 = time.time()
    cluster_info = create_twin_clusters(feature_df, n_clusters=TWIN_N_CLUSTERS)
    print(f"  Done in {time.time()-t0:.1f}s")

    # 6. LightGBM LambdaMART
    print("\n[6/8] LightGBM LambdaMART Ranker...")
    t0 = time.time()
    lgbm_result = rank_with_lambdamart(feature_df, ecs_df)
    if lgbm_result is not None:
        lgbm_scores, model, importance = lgbm_result
        print(f"  LambdaMART trained in {time.time()-t0:.1f}s")

        # Blend: 70% LambdaMART + 30% baseline
        ecs = ecs_df["ecs"].astype(float)
        baseline = ecs * 0.4 * behavioral * 0.3 * (1 - gate) * 0.3
        baseline = (baseline - baseline.min()) / max(baseline.max() - baseline.min(), 1e-6)

        lgbm_norm = (lgbm_scores - lgbm_scores.min()) / max(lgbm_scores.max() - lgbm_scores.min(), 1e-6)
        lgbm_norm = lgbm_norm.reindex(baseline.index)

        final_score = lgbm_norm * 0.7 + baseline * 0.3
        final_score = final_score.fillna(baseline)
    else:
        print("  LambdaMART not available. Using baseline only.")
        ecs = ecs_df["ecs"].astype(float)
        final_score = ecs * 0.4 * behavioral * 0.3 * (1 - gate) * 0.3

    # Rank
    ranked = final_score.sort_values(ascending=False)
    ranked = ranked[ranked > ranked.quantile(0.5)].copy()

    # Cluster quality bonus
    cluster_q = cluster_info["cluster_quality"].reindex(ranked.index).fillna(0.5)
    rarity = cluster_info["rarity_bonus"].reindex(ranked.index).fillna(0)
    ranked = ranked * (0.9 + cluster_q * 0.1 + rarity * 0.05)

    # Re-sort
    ranked = ranked.sort_values(ascending=False)

    # 7. Counterfactuals for top N
    print(f"\n[7/8] Counterfactual explanations...")
    t0 = time.time()
    counterfactuals = identify_twin_pairs(feature_df, cluster_info, ecs_df, top_n=TWIN_TOP_N)
    print(f"  Done in {time.time()-t0:.1f}s")

    # 8. Generate submission
    print(f"\n[8/8] Generating submission...")
    rows = []
    for rank, (cid, score) in enumerate(ranked.head(100).items(), 1):
        feat = all_features.get(cid, {})
        ecs_data = all_ecs.get(cid, {})
        cand = cand_lookup.get(cid, {})
        title = cand.get("profile", {}).get("current_title", "Unknown")
        yoe = cand.get("profile", {}).get("years_of_experience", 0)
        cf = counterfactuals.get(cid, "")

        reasoning = generate_reasoning(rank, feat, ecs_data, cf, title, yoe)
        rows.append({
            "candidate_id": cid,
            "rank": rank,
            "score": round(score, 4),
            "reasoning": reasoning,
        })

    # Ensure valid tie-breaking
    df = pd.DataFrame(rows)
    df = df.sort_values(["score", "candidate_id"], ascending=[False, True])
    df["rank"] = range(1, 101)
    df.to_csv(output_path, index=False)

    print(f"\n{'='*65}")
    print(f"COMPLETE — {output_path}")
    print(f"{'='*65}")

    # Top 10
    print("\nTop 10:")
    for _, row in df.head(10).iterrows():
        cid = row["candidate_id"]
        cand = cand_lookup.get(cid, {})
        title = cand.get("profile", {}).get("current_title", "?")
        r = row["rank"]
        s = row["score"]
        print(f"  #{r} {cid} | {title} | {s:.4f}")

    # Tech count in top 100
    tech_titles = ["software engineer", "full stack", "cloud engineer", "devops",
                   "ml engineer", "data scientist", "ai engineer", "backend", "frontend",
                   "java developer", ".net developer", "mobile developer", "python developer",
                   "machine learning", "nlp engineer", "recommendation"]
    non_tech = 0
    for _, row in df.iterrows():
        cid = row["candidate_id"]
        cand = cand_lookup.get(cid, {})
        title = cand.get("profile", {}).get("current_title", "").lower()
        if not any(t in title for t in tech_titles):
            non_tech += 1
    print(f"\nTech in top 100: {100 - non_tech}/100")
    print(f"Non-tech in top 100: {non_tech}/100")

    return df


if __name__ == "__main__":
    if len(sys.argv) < 3:
        data_dir = r"C:\Users\thris\Downloads\Resume-hexa-format\hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge"
        output_path = r"C:\Users\thris\Downloads\Resume-hexa-format\hackathon\ranked_candidates.csv"
    else:
        data_dir = sys.argv[1]
        output_path = sys.argv[2]

    main(data_dir, output_path)
