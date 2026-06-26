"""
Behavioral Twin Resolution

Clusters similar candidates and uses cluster membership as a ranking signal.
Candidates from clusters with high historical conversion are boosted.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances


def extract_twin_features(features_df: pd.DataFrame) -> pd.DataFrame:
    """Extract features for clustering."""
    twin_feats = pd.DataFrame(index=features_df.index)

    # Title similarity features
    for col in ["is_engineer", "is_hr", "is_accountant", "is_sales", "is_content_writer", "is_designer", "is_manager"]:
        if col in features_df.columns:
            twin_feats[col] = features_df[col].astype(float)
        else:
            twin_feats[col] = 0.0

    # Behavior similarity features
    feat_map = {
        "yoe": "years_of_experience",
        "response_rate": "response_rate",
        "interview_completion": "interview_completion",
        "offer_acceptance": "offer_acceptance",
        "profile_views": "profile_views",
        "recruiter_saves": "recruiter_saves",
        "search_appearances": "search_appearances",
        "github_activity": "github_activity",
        "ai_skills": "ai_skill_count",
        "backend_skills": "backend_skill_count",
        "data_skills": "data_skill_count",
        "skill_count": "skill_count",
        "proficiency": "avg_proficiency",
        "endorsements": "total_endorsements",
    }
    for new_col, src_col in feat_map.items():
        if src_col in features_df.columns:
            twin_feats[new_col] = features_df[src_col].astype(float)
        else:
            twin_feats[new_col] = 0.0

    return twin_feats


def create_twin_clusters(
    features_df: pd.DataFrame,
    n_clusters: int = 20
) -> pd.DataFrame:
    """
    Create behavioral twin clusters.
    
    Candidates within same cluster are "behavioral twins" — they
    look similar on paper. Twin resolution separates them by
    evidence consistency and recruiter engagement.
    """
    print(f"\nBehavioral Twin Resolution ({n_clusters} clusters)")

    twin_feats = extract_twin_features(features_df)

    # Normalize
    scaler = StandardScaler()
    scaled = scaler.fit_transform(twin_feats.fillna(0).values)

    # Cluster
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=5, max_iter=100)
    clusters = kmeans.fit_predict(scaled)

    cluster_info = pd.DataFrame(index=features_df.index)
    cluster_info["twin_cluster"] = clusters

    # For each cluster, compute historical conversion signal
    # (high response + interview completion + offer acceptance = cluster quality)
    cluster_scores = {}
    for cluster_id in range(n_clusters):
        mask = clusters == cluster_id
        cluster_size = mask.sum()
        if cluster_size == 0:
            cluster_scores[cluster_id] = 0.5
            continue

        # Average behavioral signals in this cluster
        avg_response = features_df.loc[mask, "response_rate"].mean() if "response_rate" in features_df.columns else 0
        avg_interview = features_df.loc[mask, "interview_completion"].mean() if "interview_completion" in features_df.columns else 0
        avg_acceptance = features_df.loc[mask, "offer_acceptance"].mean() if "offer_acceptance" in features_df.columns else 0
        avg_ai = features_df.loc[mask, "ai_skill_count"].mean() if "ai_skill_count" in features_df.columns else 0

        # Cluster quality: high response + medium-high AI skills = high quality
        cluster_scores[cluster_id] = (avg_response * 0.35 + avg_interview * 0.25 + avg_acceptance * 0.15 + (avg_ai > 0) * 0.25)

    # Map back
    cluster_info["cluster_quality"] = [cluster_scores[c] for c in clusters]
    cluster_info["cluster_size"] = [(clusters == c).sum() for c in clusters]

    # Rarity bonus: high-quality candidate in a low-quality cluster = hidden gem
    ece = features_df.get("claim_assessment_consistency", pd.Series(0.5, index=features_df.index))
    cluster_info["rarity_bonus"] = 0.0
    for cluster_id in range(n_clusters):
        mask = clusters == cluster_id
        cluster_quality = cluster_scores[cluster_id]
        if cluster_quality < 0.4:  # Low quality cluster
            # High consistency candidates in low quality clusters are rare
            cluster_info.loc[mask, "rarity_bonus"] = ece[mask].clip(upper=0.3)

    print(f"  Clusters: {n_clusters}")
    print(f"  Avg cluster size: {len(features_df) // n_clusters}")
    print(f"  Candidates with rarity bonus: {(cluster_info['rarity_bonus'] > 0).sum()}")

    return cluster_info


def identify_twin_pairs(
    features_df: pd.DataFrame,
    cluster_info: pd.DataFrame,
    ecs_data: pd.DataFrame,
    top_n: int = 100
) -> Dict[str, str]:
    """
    Identify twin pairs in top candidates and explain why one outranks the other.
    Returns counterfactual explanations for each candidate.
    """
    counterfactuals = {}

    # Get top candidates
    ranked_candidates = list(cluster_info.index[:top_n])

    for cid in ranked_candidates:
        if cid not in cluster_info.index:
            counterfactuals[cid] = ""
            continue

        cluster = cluster_info.loc[cid, "twin_cluster"]
        cluster_mask = cluster_info["twin_cluster"] == cluster
        twins = cluster_info[cluster_mask].index.tolist()

        # Remove self
        twins = [t for t in twins if t != cid]

        if not twins:
            counterfactuals[cid] = "unique profile in cluster"
            continue

        # Find closest twin by feature distance
        twin_feats = extract_twin_features(features_df)
        cid_feats = twin_feats.loc[cid].values.astype(float)

        min_dist = float("inf")
        closest_twin = None
        for twin in twins[:50]:  # Check first 50 twins
            if twin in twin_feats.index:
                twin_f = twin_feats.loc[twin].values.astype(float)
                dist = np.linalg.norm(cid_feats - twin_f)
                if dist < min_dist:
                    min_dist = dist
                    closest_twin = twin

        if closest_twin is None:
            counterfactuals[cid] = "no close twin found"
            continue

        # Compare features between candidate and twin
        # Find the single most differentiating feature
        cid_ecs = ecs_data.loc[cid, "ecs"] if cid in ecs_data.index else 0
        twin_ecs = ecs_data.loc[closest_twin, "ecs"] if closest_twin in ecs_data.index else 0
        cid_response = features_df.loc[cid, "response_rate"] if cid in features_df.index else 0
        twin_response = features_df.loc[closest_twin, "response_rate"] if closest_twin in features_df.index else 0

        # Determine decisive factor
        if cid_ecs > twin_ecs + 0.1:
            counterfactuals[cid] = f"evidence consistency ({cid_ecs:.2f} vs {twin_ecs:.2f})"
        elif cid_response > twin_response + 0.2:
            counterfactuals[cid] = f"recruiter engagement ({cid_response:.0%} vs {twin_response:.0%})"
        elif cid_ecs < twin_ecs - 0.1:
            counterfactuals[cid] = f"higher evidence consistency than comparable profile"
        else:
            counterfactuals[cid] = "balanced profile across signals"

    return counterfactuals
