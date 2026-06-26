"""
Validation Harness

CRITICAL: Validate before submitting.
Every idea is a hypothesis until proven.

Usage:
  python validate.py <data_dir> <submission_csv>
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any


def compute_ndcg(ranked_labels: List[float], k: int) -> float:
    """Compute NDCG@k for a ranked list of relevance labels."""
    if not ranked_labels or k <= 0:
        return 0.0

    # DCG
    dcg = 0.0
    for i, label in enumerate(ranked_labels[:k]):
        dcg += label / np.log2(i + 2)  # i+2 because log2(1) = 0

    # Ideal DCG
    ideal_labels = sorted(ranked_labels, reverse=True)[:k]
    idcg = 0.0
    for i, label in enumerate(ideal_labels):
        idcg += label / np.log2(i + 2)

    if idcg == 0:
        return 0.0

    return dcg / idcg


def compute_map(ranked_labels: List[float]) -> float:
    """Compute Mean Average Precision."""
    if not ranked_labels:
        return 0.0

    relevant_count = sum(1 for l in ranked_labels if l > 0)
    if relevant_count == 0:
        return 0.0

    ap = 0.0
    relevant_so_far = 0
    for i, label in enumerate(ranked_labels):
        if label > 0:
            relevant_so_far += 1
            ap += relevant_so_far / (i + 1)

    return ap / relevant_count


def compute_precision_at_k(ranked_labels: List[float], k: int) -> float:
    """Compute Precision@k."""
    if not ranked_labels or k <= 0:
        return 0.0
    relevant = sum(1 for l in ranked_labels[:k] if l > 0)
    return relevant / k


def create_manual_labels(
    submission: pd.DataFrame,
    candidates: pd.DataFrame,
    n_samples: int = 50
) -> pd.DataFrame:
    """
    Create manual labels for validation.
    
    In practice, you would manually label these.
    For now, we use heuristics as a starting point.
    """
    print(f"\nCreating {n_samples} manual labels for validation")

    # Sample candidates across the ranking
    sample_ids = []

    # Top 10 (should be strong)
    top_candidates = submission.head(10)["candidate_id"].tolist()
    sample_ids.extend(top_candidates[:10])

    # Middle (ambiguous)
    mid_start = len(submission) // 2
    mid_candidates = submission.iloc[mid_start:mid_start + 10]["candidate_id"].tolist()
    sample_ids.extend(mid_candidates[:10])

    # Bottom (should be weak)
    bottom_candidates = submission.tail(10)["candidate_id"].tolist()
    sample_ids.extend(bottom_candidates[:10])

    # Remove duplicates
    sample_ids = list(set(sample_ids))[:n_samples]

    # Create labels using heuristics
    labels = []
    for cid in sample_ids:
        if cid not in candidates.index:
            continue

        row = candidates.loc[cid]

        # Heuristic labeling
        skill_match = float(row.get("skill_match_score", 0))
        assessment = float(row.get("assessment_score", 0))
        response = float(row.get("recruiter_response_rate", -1))
        title = str(row.get("current_title", "")).lower()

        # Strong candidate heuristics
        score = 0
        if skill_match > 0.7:
            score += 2
        if assessment > 60:
            score += 2
        if response > 0.6:
            score += 1
        if any(kw in title for kw in ["engineer", "developer", "scientist"]):
            score += 1
        if any(kw in title for kw in ["manager", "lead", "senior"]):
            score += 1

        # Weak candidate heuristics
        if skill_match < 0.3:
            score -= 2
        if assessment < 30:
            score -= 1
        if response == 0:
            score -= 1
        if any(kw in title for kw in ["hr", "business analyst", "accountant"]):
            score -= 2

        # Map to label
        if score >= 3:
            label = 3  # Strong
        elif score >= 1:
            label = 2  # Moderate
        elif score >= 0:
            label = 1  # Weak
        else:
            label = 0  # Very weak

        labels.append({
            "candidate_id": cid,
            "manual_label": label,
            "skill_match": skill_match,
            "assessment": assessment,
            "response_rate": response,
            "title": row.get("current_title", ""),
        })

    return pd.DataFrame(labels)


def validate_ranking(
    submission: pd.DataFrame,
    manual_labels: pd.DataFrame
) -> Dict[str, Any]:
    """Validate ranking against manual labels."""
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)

    # Merge submission with labels
    merged = submission.merge(manual_labels, on="candidate_id", how="inner")

    if len(merged) == 0:
        print("No matching candidates found for validation")
        return {}

    # Sort by rank
    merged = merged.sort_values("rank")

    # Compute metrics
    labels = merged["manual_label"].tolist()
    ndcg_10 = compute_ndcg(labels, 10)
    ndcg_50 = compute_ndcg(labels, min(50, len(labels)))
    map_score = compute_map(labels)
    p_at_10 = compute_precision_at_k(labels, 10)

    # Composite score (matching competition formula)
    composite = 0.50 * ndcg_10 + 0.30 * ndcg_50 + 0.15 * map_score + 0.05 * p_at_10

    print(f"\nNDCG@10:        {ndcg_10:.4f}")
    print(f"NDCG@50:        {ndcg_50:.4f}")
    print(f"MAP:            {map_score:.4f}")
    print(f"Precision@10:   {p_at_10:.4f}")
    print(f"Composite:      {composite:.4f}")

    # Tier accuracy
    top_10 = merged.head(10)
    if len(top_10) > 0:
        avg_top_label = top_10["manual_label"].mean()
        print(f"\nTop 10 avg label: {avg_top_label:.2f} (3=strong, 0=weak)")
        if avg_top_label >= 2.5:
            print("  ✓ Top 10 looks strong")
        elif avg_top_label >= 1.5:
            print("  ~ Top 10 is moderate")
        else:
            print("  ✗ Top 10 looks weak — investigate!")

    # Check for honeypots (HR managers in top 10)
    honeypot_titles = ["hr manager", "hr executive", "business analyst", "accountant"]
    honeypots_in_top = sum(
        1 for t in top_10["title"].str.lower()
        if any(hp in str(t) for hp in honeypot_titles)
    )
    if honeypots_in_top > 0:
        print(f"\n  ⚠ WARNING: {honeypots_in_top} potential honeypots in top 10!")
    else:
        print(f"\n  ✓ No honeypots detected in top 10")

    results = {
        "ndcg_10": ndcg_10,
        "ndcg_50": ndcg_50,
        "map": map_score,
        "precision_at_10": p_at_10,
        "composite": composite,
        "honeypots_in_top_10": honeypots_in_top,
    }

    return results


def analyze_ecs_impact(submission: pd.DataFrame, ecs_data: pd.DataFrame):
    """Analyze how ECS affects ranking."""
    print("\n" + "=" * 60)
    print("ECS IMPACT ANALYSIS")
    print("=" * 60)

    # Merge
    merged = submission.merge(
        ecs_data[["ecs", "axes_consistent", "contradiction_count"]],
        left_on="candidate_id",
        right_index=True,
        how="left"
    )

    # Correlation between ECS and rank
    valid = merged.dropna(subset=["ecs", "rank"])
    if len(valid) > 10:
        correlation = valid["ecs"].corr(valid["rank"])
        print(f"ECS-Rank correlation: {correlation:.4f}")
        if correlation < -0.3:
            print("  ✓ Higher ECS → Higher rank (expected)")
        elif correlation > 0.3:
            print("  ⚠ Higher ECS → Lower rank (unexpected)")
        else:
            print("  ~ Weak correlation (ECS may not be impactful)")

    # ECS distribution in top 100
    top_100 = merged.head(100)
    if len(top_100) > 0:
        avg_ecs = top_100["ecs"].mean()
        print(f"\nTop 100 avg ECS: {avg_ecs:.4f}")
        if avg_ecs > 0.6:
            print("  ✓ Top candidates have high evidence consistency")
        else:
            print("  ~ Top candidates have moderate evidence consistency")

    # Contradictions in top 100
    if "contradiction_count" in top_100.columns:
        avg_contradictions = top_100["contradiction_count"].mean()
        print(f"Top 100 avg contradictions: {avg_contradictions:.2f}")
        if avg_contradictions < 0.5:
            print("  ✓ Few contradictions in top candidates")
        else:
            print("  ~ Some contradictions present in top candidates")


def validate_honeypot_detection(
    submission: pd.DataFrame,
    candidates: pd.DataFrame
):
    """Check honeypot detection performance."""
    print("\n" + "=" * 60)
    print("HONEYPOT DETECTION CHECK")
    print("=" * 60)

    # Check for known honeypot indicators
    honeypot_indicators = []

    for _, row in submission.head(100).iterrows():
        cid = row["candidate_id"]
        if cid not in candidates.index:
            continue

        cand = candidates.loc[cid]
        issues = []

        # Title mismatch
        title = str(cand.get("current_title", "")).lower()
        skills = str(cand.get("claimed_skills", "")).lower()
        if "ai" in skills or "ml" in skills:
            if any(t in title for t in ["hr", "accountant", "mechanical"]):
                issues.append("title-skill mismatch")

        # Skill claim vs assessment
        claimed = str(cand.get("claimed_proficiency", "")).lower()
        assessment = float(cand.get("assessment_score", 0))
        if claimed in ["expert", "advanced"] and assessment < 40:
            issues.append("claim-assessment mismatch")

        if issues:
            honeypot_indicators.append({
                "candidate_id": cid,
                "rank": row["rank"],
                "issues": issues,
            })

    if honeypot_indicators:
        print(f"\n⚠ Found {len(honeypot_indicators)} candidates with honeypot indicators in top 100:")
        for h in honeypot_indicators[:5]:
            print(f"  Rank {h['rank']}: {', '.join(h['issues'])}")
    else:
        print("\n✓ No honeypot indicators found in top 100")


def run_validation(data_dir: str, submission_path: str):
    """Run full validation suite."""
    print("=" * 60)
    print("VALIDATION HARNESS")
    print("=" * 60)

    # Load data
    candidates_path = os.path.join(data_dir, "candidates.csv")
    if not os.path.exists(candidates_path):
        for alt in ["candidate_profiles.csv", "profiles.csv", "data.csv"]:
            alt_path = os.path.join(data_dir, alt)
            if os.path.exists(alt_path):
                candidates_path = alt_path
                break

    candidates = pd.read_csv(candidates_path)
    submission = pd.read_csv(submission_path)

    print(f"Loaded {len(candidates)} candidates")
    print(f"Loaded submission with {len(submission)} rows")

    # Create manual labels
    manual_labels = create_manual_labels(submission, candidates)

    # Validate ranking
    results = validate_ranking(submission, manual_labels)

    # Analyze ECS impact (if available)
    try:
        from evidence import compute_all_ecs
        from features import extract_all_features

        features_df = extract_all_features(candidates)
        ecs_data = compute_all_ecs(features_df)
        analyze_ecs_impact(submission, ecs_data)
    except Exception as e:
        print(f"\nCould not analyze ECS impact: {e}")

    # Check honeypot detection
    validate_honeypot_detection(submission, candidates)

    # Save results
    results_path = submission_path.replace(".csv", "_validation.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")

    return results


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python validate.py <data_dir> <submission_csv>")
        sys.exit(1)

    data_dir = sys.argv[1]
    submission_path = sys.argv[2]

    run_validation(data_dir, submission_path)
