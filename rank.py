"""
Main Ranking Pipeline - Version 2

Works with actual hackathon data (JSONL format).

Pipeline:
  1. Load JSONL data
  2. Feature extraction
  3. JD disqualifier gates (soft penalties)
  4. Evidence consistency engine (4-axis ECS)
  5. Behavioral reality layer (sentinel-safe)
  6. Score computation (multiplicative)
  7. Ranking
  8. Reasoning generation
  9. CSV output
"""

import os
import sys
import json
import warnings
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional

warnings.filterwarnings("ignore")

from config import SCORE_WEIGHTS, SENTINEL_VALUE, AI_CORE_SKILLS
from features import load_candidates, extract_all_features
from evidence import compute_ecs, compute_all_ecs
from reasoning import generate_reasoning, identify_decisive_signal


def load_jd(jd_path: str) -> str:
    """Load job description text."""
    if not os.path.exists(jd_path):
        print(f"Warning: JD not found at {jd_path}")
        return ""

    # Try reading as text first
    try:
        with open(jd_path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        pass

    # Try reading docx
    try:
        from docx import Document
        doc = Document(jd_path)
        return "\n".join([p.text for p in doc.paragraphs])
    except:
        pass

    return ""


def compute_skill_match_score(
    candidate: Dict[str, Any],
    jd_text: str
) -> float:
    """Compute how well candidate skills match the JD."""
    skills = candidate.get("skills", [])
    skill_names = [s.get("name", "").lower() for s in skills]

    # Count AI core skills
    ai_skills = sum(1 for s in skill_names if any(kw in s for kw in AI_CORE_SKILLS))

    # Simple skill matching
    jd_lower = jd_text.lower() if jd_text else ""
    matched = sum(1 for s in skill_names if s in jd_lower)

    # Base score from AI skills
    if len(skill_names) > 0:
        skill_score = ai_skills / max(len(skill_names), 1)
    else:
        skill_score = 0

    # Bonus for deployment evidence
    career = candidate.get("career_history", [])
    descriptions = " ".join(c.get("description", "") for c in career)
    has_production = any(kw in descriptions.lower() for kw in [
        "production", "deploy", "ship", "scale", "serving"
    ])
    production_bonus = 0.2 if has_production else 0

    return min(skill_score + production_bonus, 1.0)


def compute_jd_gates(features_df: pd.DataFrame) -> pd.DataFrame:
    """
    Stage 2: JD Disqualifier Gates (soft penalties)
    """
    print("\nStage 2: JD Disqualifier Gates")

    gate_scores = pd.DataFrame(index=features_df.index)

    # Gate 1: Non-technical titles
    non_tech = (
        features_df.get("is_hr", 0) +
        features_df.get("is_accountant", 0) +
        features_df.get("is_sales", 0) +
        features_df.get("is_content_writer", 0) +
        features_df.get("is_designer", 0) +
        features_df.get("is_civil", 0) +
        features_df.get("is_mechanical", 0)
    )
    gate_scores["gate_non_tech"] = non_tech * 0.4

    # Gate 2: Consulting-only
    gate_scores["gate_consulting"] = features_df.get("consulting_only", 0) * 0.3

    # Gate 3: Title-chasing
    gate_scores["gate_chasing"] = (features_df.get("title_chasing_count", 0) / 
                                    features_df.get("job_count", 1).clip(lower=1)) * 0.2

    # Gate 4: No AI skills
    gate_scores["gate_no_ai"] = (features_df.get("ai_skill_count", 0) == 0).astype(float) * 0.15

    # Gate 5: No deployment for senior
    senior_no_deploy = (
        (features_df.get("years_of_experience", 0) > 5) &
        (features_df.get("has_deployment_evidence", 0) == 0)
    ).astype(float)
    gate_scores["gate_senior_no_deploy"] = senior_no_deploy * 0.1

    # Total gate penalty (capped)
    gate_scores["gate_penalty"] = gate_scores.sum(axis=1).clip(upper=0.6)

    n_penalized = (gate_scores["gate_penalty"] > 0).sum()
    print(f"  {n_penalized} candidates received gate penalties")

    return gate_scores


def compute_behavioral_score(features_df: pd.DataFrame) -> pd.DataFrame:
    """
    Stage 4: Behavioral Reality Layer
    Sentinel values (-1) treated as UNKNOWN, not BAD.
    """
    print("\nStage 4: Behavioral Reality Layer")

    behavioral = pd.DataFrame(index=features_df.index)

    behavioral["response_rate"] = features_df.get("response_rate", 0)
    behavioral["interview_completion"] = features_df.get("interview_completion", 0)
    behavioral["offer_acceptance"] = features_df.get("offer_acceptance", 0)

    # Weighted recruitability
    signal_sum = (
        behavioral["response_rate"] * 0.4 +
        behavioral["interview_completion"] * 0.35 +
        behavioral["offer_acceptance"] * 0.25
    )
    signal_count = (
        (behavioral["response_rate"] > 0).astype(float) * 0.4 +
        (behavioral["interview_completion"] > 0).astype(float) * 0.35 +
        (behavioral["offer_acceptance"] > 0).astype(float) * 0.25
    )

    behavioral["recruitability"] = np.where(
        signal_count > 0,
        signal_sum / signal_count,
        0.5
    )

    n_with_data = (signal_count > 0).sum()
    print(f"  {n_with_data} candidates have behavioral data")

    return behavioral


def compute_availability_score(features_df: pd.DataFrame) -> pd.DataFrame:
    """Compute availability signals."""
    print("\nComputing availability scores")

    availability = pd.DataFrame(index=features_df.index)

    notice = features_df.get("notice_period_days", 0)
    availability["notice_score"] = np.where(
        notice > 0,
        np.clip(1.0 - (notice / 90), 0.3, 1.0),
        0.5
    )

    github = features_df.get("github_activity", 0)
    has_github = features_df.get("has_github", 0)
    availability["activity_score"] = np.where(
        has_github > 0,
        np.clip(github / 100, 0, 1),
        0.5
    )

    availability["availability"] = (
        availability["notice_score"] * 0.5 +
        availability["activity_score"] * 0.5
    )

    return availability


def compute_final_scores(
    ecs_data: pd.DataFrame,
    behavioral: pd.DataFrame,
    availability: pd.DataFrame,
    gate_scores: pd.DataFrame
) -> pd.DataFrame:
    """Compute final ranking scores."""
    print("\nStage 6: Computing final scores")

    scores = pd.DataFrame(index=ecs_data.index)

    ecs = ecs_data["ecs"].reindex(scores.index).fillna(0.5)
    recruit = behavioral["recruitability"].reindex(scores.index).fillna(0.5)
    avail = availability["availability"].reindex(scores.index).fillna(0.5)
    gates = gate_scores["gate_penalty"].reindex(scores.index).fillna(0)

    w = SCORE_WEIGHTS
    scores["ecs_score"] = ecs
    scores["recruitability_score"] = recruit
    scores["availability_score"] = avail
    scores["gate_penalty_score"] = gates

    scores["final_score"] = (
        ecs ** w["ecs"] *
        recruit ** w["recruitability"] *
        avail ** w["availability"] *
        (1 - gates) ** w["gate_penalty"]
    )

    scores["rank"] = scores["final_score"].rank(ascending=False, method="min").astype(int)
    scores = scores.sort_values("rank")

    n_high = (scores["final_score"] > 0.7).sum()
    n_low = (scores["final_score"] < 0.3).sum()
    print(f"  Score distribution: {n_high} high (>0.7), {n_low} low (<0.3)")

    return scores


def generate_reasoning_for_candidate(
    rank: int,
    features: Dict[str, float],
    ecs_data: Dict[str, Any]
) -> str:
    """Generate reasoning for a single candidate."""
    parts = []

    # Opening
    yoe = features.get("years_of_experience", 0)
    title = ""
    # Try to get title from features (we'll pass it separately)
    parts.append(f"Ranked #{rank}.")

    # Experience
    if yoe > 0:
        parts[0] = f"Ranked #{rank} based on {yoe:.1f} years of experience."

    # ECS
    ecs = ecs_data.get("ecs", 0)
    axes = ecs_data.get("axes_consistent", 0)
    if ecs > 0:
        parts.append(f"Evidence consistency: {ecs * 100:.0f}/100 across {axes}/4 axes.")

    # Engagement
    response = features.get("response_rate", 0)
    if response > 0.7:
        parts.append(f"Strong recruiter engagement ({response:.0%} response rate).")
    elif response > 0.4:
        parts.append(f"Moderate recruiter engagement ({response:.0%} response rate).")
    elif response > 0:
        parts.append(f"Low recruiter engagement ({response:.0%} response rate).")

    # Production evidence
    if features.get("has_deployment_evidence", 0) > 0:
        parts.append("Career history shows deployment experience.")
    if features.get("has_production_metrics", 0) > 0:
        parts.append("Career history includes production metrics.")

    # AI skills
    ai_count = features.get("ai_skill_count", 0)
    if ai_count > 3:
        parts.append(f"Strong AI/ML skill set ({ai_count} AI-related skills).")
    elif ai_count > 0:
        parts.append(f"Some AI/ML skills ({ai_count} AI-related skills).")

    # Flags
    flags = []
    if features.get("is_hr", 0) > 0:
        flags.append("non-technical role")
    if features.get("is_accountant", 0) > 0:
        flags.append("non-technical role")
    if features.get("consulting_only", 0) > 0:
        flags.append("consulting-only background")
    if features.get("title_chasing_count", 0) > 2:
        flags.append("frequent job changes")

    if flags:
        parts.append(f"Notes: {', '.join(flags)}.")

    return " ".join(parts)


def create_submission(
    ranked_scores: pd.DataFrame,
    features_df: pd.DataFrame,
    ecs_data: pd.DataFrame,
    candidates: List[Dict[str, Any]],
    output_path: str
):
    """Create submission CSV."""
    print(f"\nCreating submission: {output_path}")

    # Build candidate lookup
    cand_lookup = {c["candidate_id"]: c for c in candidates}

    submission_rows = []
    for idx, row in ranked_scores.iterrows():
        cid = idx
        rank = int(row["rank"])
        score = round(row["final_score"], 4)

        # Get features
        features = features_df.loc[cid].to_dict() if cid in features_df.index else {}
        ecs = ecs_data.loc[cid].to_dict() if cid in ecs_data.index else {}

        # Get candidate info
        cand = cand_lookup.get(cid, {})
        profile = cand.get("profile", {})
        title = profile.get("current_title", "Unknown")

        # Generate reasoning
        reasoning = generate_reasoning_for_candidate(rank, features, ecs)
        reasoning = f"{title}: {reasoning}"

        submission_rows.append({
            "candidate_id": cid,
            "rank": rank,
            "score": score,
            "reasoning": reasoning,
        })

    submission_df = pd.DataFrame(submission_rows)
    submission_df = submission_df.sort_values("rank")
    submission_df.to_csv(output_path, index=False)

    print(f"  Written {len(submission_df)} rows")
    return submission_df


def run_pipeline(data_dir: str, output_path: str):
    """Run the full ranking pipeline."""
    print("=" * 60)
    print("CORROBORATED EVIDENCE RANKING ENGINE v2")
    print("=" * 60)

    # Find data files
    jsonl_path = None
    for root, dirs, files in os.walk(data_dir):
        for f in files:
            if f == "candidates.jsonl":
                jsonl_path = os.path.join(root, f)
                break
        if jsonl_path:
            break

    if not jsonl_path:
        print("ERROR: candidates.jsonl not found")
        return

    print(f"\nData file: {jsonl_path}")

    # Load candidates
    candidates = load_candidates(jsonl_path)
    print(f"Loaded {len(candidates)} candidates")

    # Feature extraction
    print("\nStage 1: Feature Extraction")
    features_df = extract_all_features(candidates)
    print(f"  Extracted {len(features_df.columns)} features")

    # JD Gates
    gate_scores = compute_jd_gates(features_df)

    # Evidence Consistency
    print("\nStage 3: Evidence Consistency Engine")
    ecs_data = compute_all_ecs(features_df)
    n_high_ecs = (ecs_data["ecs"] > 0.7).sum()
    n_low_ecs = (ecs_data["ecs"] < 0.4).sum()
    print(f"  ECS distribution: {n_high_ecs} high (>0.7), {n_low_ecs} low (<0.4)")

    # Behavioral
    behavioral = compute_behavioral_score(features_df)

    # Availability
    availability = compute_availability_score(features_df)

    # Final Scores
    ranked_scores = compute_final_scores(ecs_data, behavioral, availability, gate_scores)

    # Create submission
    submission = create_submission(ranked_scores, features_df, ecs_data, candidates, output_path)

    # Summary
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"Total candidates: {len(candidates)}")
    print(f"Ranked candidates: {len(submission)}")
    print(f"\nTop 10:")
    print(submission[["rank", "candidate_id", "score"]].head(10).to_string(index=False))

    # Check for honeypots in top 10
    honeypot_titles = ["hr manager", "hr executive", "accountant", "mechanical engineer",
                       "civil engineer", "graphic designer", "content writer", "sales executive"]
    top_10_cands = [cand_lookup.get(cid, {}) for cid in submission.head(10)["candidate_id"]]
    honeypots = sum(1 for c in top_10_cands
                    if any(ht in c.get("profile", {}).get("current_title", "").lower()
                           for ht in honeypot_titles))
    print(f"\nHoneypots in top 10: {honeypots}/10")
    if honeypots > 0:
        print("  WARNING: Non-technical roles in top 10!")

    return submission


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python rank.py <data_dir> <output_csv>")
        sys.exit(1)

    data_dir = sys.argv[1]
    output_path = sys.argv[2]

    run_pipeline(data_dir, output_path)
