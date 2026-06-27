"""
Evidence Consistency Engine (Core Innovation)

4 independent axes of evidence:
  A: Claim ↔ Assessment consistency
  B: Claim ↔ Career History consistency
  C: Claim ↔ Corroboration consistency
  D: Seniority ↔ Trajectory consistency

Aggregation: Geometric mean (punishes disagreement)

Uses actual field names from features.py
"""

import math
import numpy as np
import pandas as pd
from typing import Dict, Tuple, List, Any
from config import ECS_WEIGHTS, CLAIM_ASSESSMENT_BASELINES


def axis_claim_assessment(features: Dict[str, float]) -> Tuple[float, str]:
    """
    Axis A: Compare claimed proficiency vs actual assessment.
    Uses pre-computed claim_assessment_consistency from features.py.
    """
    consistency = features.get("claim_assessment_consistency", 0.5)
    assessment_count = features.get("assessment_count", 0)
    avg_gap = features.get("avg_assessment_gap", 0)

    if assessment_count == 0:
        return 0.35, "No assessment data — cannot verify claims"

    # consistency is already 0-1 from features.py
    if consistency > 0.7:
        return consistency, f"Claims align with assessments (avg gap: {avg_gap:.1f} points)"
    elif consistency > 0.4:
        return consistency, f"Claims partially align with assessments (avg gap: {avg_gap:.1f} points)"
    else:
        return consistency, f"Claim-assessment gap detected (avg gap: {avg_gap:.1f} points)"


def axis_claim_experience(features: Dict[str, float]) -> Tuple[float, str]:
    """
    Axis B: Compare claimed skills vs career history evidence.
    
    Signals:
    - Deployment evidence
    - Production metrics
    - Years of experience
    - Career duration
    - Mentions of production in summary
    """
    has_deployment = features.get("has_deployment_evidence", 0)
    has_metrics = features.get("has_production_metrics", 0)
    mentions_production = features.get("mentions_production", 0)
    yoe = features.get("years_of_experience", 0)
    total_duration = features.get("total_duration_months", 0)
    company_count = features.get("company_count", 0)
    job_count = features.get("job_count", 0)

    # Evidence signals
    evidence_signals = [
        has_deployment * 0.35,
        has_metrics * 0.25,
        mentions_production * 0.15,
    ]

    consistency = sum(evidence_signals)

    # Duration sanity check
    if yoe > 0 and total_duration > 0:
        duration_years = total_duration / 12
        ratio = duration_years / yoe
        if ratio < 0.3:
            consistency *= 0.7  # Career span much shorter than claimed YOE

    # Build reason
    evidence_parts = []
    if has_deployment:
        evidence_parts.append("deployment evidence")
    if has_metrics:
        evidence_parts.append("production metrics")
    if mentions_production:
        evidence_parts.append("production mentions in summary")

    if evidence_parts:
        reason = f"Career history shows: {', '.join(evidence_parts)}"
    else:
        reason = "Limited career history evidence"

    return min(consistency, 1.0), reason


def axis_claim_corroboration(features: Dict[str, float]) -> Tuple[float, str]:
    """
    Axis C: Compare claimed skills vs external corroboration.
    
    Sources:
    - GitHub activity
    - Endorsements received
    - Profile completeness
    - Assessment count
    """
    has_github = features.get("has_github", 0)
    github_activity = features.get("github_activity", 0)
    total_endorsements = features.get("total_endorsements", 0)
    profile_completeness = features.get("profile_completeness", 0)
    assessment_count = features.get("assessment_count", 0)

    # Compute corroboration score
    signals = []

    if has_github and github_activity > 0:
        signals.append(("github", min(github_activity / 100, 1.0) * 0.3))

    if total_endorsements > 0:
        signals.append(("endorsements", min(total_endorsements / 50, 1.0) * 0.25))

    if profile_completeness > 50:
        signals.append(("profile", min(profile_completeness / 100, 1.0) * 0.25))

    if assessment_count > 0:
        signals.append(("assessments", min(assessment_count / 5, 1.0) * 0.2))

    if signals:
        consistency = sum(score for _, score in signals)
        reason = f"Corroborated by: {', '.join(name for name, _ in signals)}"
    else:
        consistency = 0.25
        reason = "Limited external corroboration — no endorsements, GitHub, or profile data"

    return min(consistency, 1.0), reason


def axis_seniority_trajectory(features: Dict[str, float]) -> Tuple[float, str]:
    """
    Axis D: Compare current seniority vs career trajectory.
    
    Checks:
    - Years of experience
    - Max tenure (longevity signal)
    - Company count (stability)
    - Title-chasing (frequent short jobs)
    - Job count vs tenure
    """
    yoe = features.get("years_of_experience", 0)
    max_tenure = features.get("max_tenure_months", 0)
    company_count = features.get("company_count", 0)
    title_chasing_count = features.get("title_chasing_count", 0)
    job_count = features.get("job_count", 0)
    total_duration = features.get("total_duration_months", 0)

    if yoe == 0:
        return 0.5, "No experience data"

    # Trajectory score
    trajectory_score = 0.5
    if total_duration > 0:
        duration_years = total_duration / 12
        ratio = min(duration_years / yoe, 1.5)
        if ratio >= 0.7:
            trajectory_score = 0.8
        elif ratio >= 0.4:
            trajectory_score = 0.6
        else:
            trajectory_score = 0.4

    # Tenure stability
    tenure_score = 0.5
    if max_tenure >= 36:
        tenure_score = 0.8
    elif max_tenure >= 24:
        tenure_score = 0.7
    elif max_tenure >= 12:
        tenure_score = 0.6

    # Title-chasing penalty
    chase_penalty = 1.0
    if job_count > 0:
        chase_ratio = title_chasing_count / job_count
        chase_penalty = max(1.0 - chase_ratio * 0.5, 0.5)

    consistency = (trajectory_score * 0.5 + tenure_score * 0.5) * chase_penalty

    # Build reason
    reasons = []
    if total_duration > 0:
        reasons.append(f"{total_duration / 12:.1f} year career span")
    if max_tenure > 0:
        reasons.append(f"max tenure {max_tenure:.0f} months")
    if title_chasing_count > 1:
        reasons.append(f"{title_chasing_count} short stints detected")

    reason = "; ".join(reasons) if reasons else "Trajectory data available"

    return max(0.0, min(consistency, 1.0)), reason


def compute_ecs(features: Dict[str, float]) -> Dict[str, Any]:
    """
    Compute Evidence Consistency Score using geometric mean.
    
    ECS = (A^wA * B^wB * C^wC * D^wD) ^ (1/(wA+wB+wC+wD))
    """
    # Compute each axis
    score_a, reason_a = axis_claim_assessment(features)
    score_b, reason_b = axis_claim_experience(features)
    score_c, reason_c = axis_claim_corroboration(features)
    score_d, reason_d = axis_seniority_trajectory(features)

    # Get weights
    w_a = ECS_WEIGHTS["claim_assessment"]
    w_b = ECS_WEIGHTS["claim_experience"]
    w_c = ECS_WEIGHTS["claim_corroboration"]
    w_d = ECS_WEIGHTS["seniority_trajectory"]

    # Geometric mean aggregation
    epsilon = 1e-6
    scores = [
        max(score_a, epsilon),
        max(score_b, epsilon),
        max(score_c, epsilon),
        max(score_d, epsilon),
    ]
    weights = [w_a, w_b, w_c, w_d]

    total_weight = sum(weights)
    log_sum = sum(w * math.log(s) for w, s in zip(weights, scores))
    ecs = math.exp(log_sum / total_weight)

    # JD-specific ECS bonus: candidates with strong domain evidence
    jd_match_fields = ["jd_match_retrieval", "jd_match_ranking", "jd_match_embeddings", "jd_match_evaluation"]
    jd_match_count = sum(1 for f in jd_match_fields if features.get(f, 0) > 0)
    if jd_match_count >= 3:
        ecs = min(1.0, ecs * 1.15)  # 15% boost for 3+ JD-specific skills
    elif jd_match_count >= 2:
        ecs = min(1.0, ecs * 1.08)  # 8% boost for 2+ JD-specific skills

    # Count consistent axes (score > 0.6)
    axes_consistent = sum(1 for s in [score_a, score_b, score_c, score_d] if s > 0.6)
    total_axes = 4

    # Identify contradictions (score < 0.4)
    contradictions = []
    if score_a < 0.4:
        contradictions.append("assessment mismatch")
    if score_b < 0.4:
        contradictions.append("career history weak")
    if score_c < 0.4:
        contradictions.append("low corroboration")
    if score_d < 0.4:
        contradictions.append("trajectory concerns")

    return {
        "ecs": ecs,
        "axis_a_score": score_a,
        "axis_a_reason": reason_a,
        "axis_b_score": score_b,
        "axis_b_reason": reason_b,
        "axis_c_score": score_c,
        "axis_c_reason": reason_c,
        "axis_d_score": score_d,
        "axis_d_reason": reason_d,
        "axes_consistent": axes_consistent,
        "total_axes": total_axes,
        "contradictions": contradictions,
        "contradiction_count": len(contradictions),
    }


def compute_all_ecs(features_df: pd.DataFrame) -> pd.DataFrame:
    """Compute ECS for all candidates."""
    ecs_results = []
    for idx, row in features_df.iterrows():
        features = row.to_dict()
        ecs_data = compute_ecs(features)
        ecs_data["candidate_id"] = idx
        ecs_results.append(ecs_data)
    return pd.DataFrame(ecs_results).set_index("candidate_id")
