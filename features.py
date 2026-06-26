"""
Feature extraction for the actual hackathon data.
Handles nested JSON structure from candidates.jsonl.
"""

import json
import re
import math
import os
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from config import (
    SENTINEL_VALUE, CONSULTING_COMPANIES, RESEARCH_TITLES,
    DOMAIN_MISMATCH_SKILLS, CLAIM_ASSESSMENT_BASELINES,
    AI_CORE_SKILLS
)


def load_candidates(jsonl_path: str) -> List[Dict[str, Any]]:
    """Load candidates from JSONL file."""
    candidates = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))
    return candidates


def safe_float(value: Any, default: float = 0.0) -> float:
    """Convert value to float safely."""
    if value is None or value == SENTINEL_VALUE or value == -1:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def parse_career_history(career_list: List[Dict]) -> Dict[str, Any]:
    """Extract structured info from career history array."""
    if not career_list:
        return {
            "total_duration_months": 0,
            "max_tenure_months": 0,
            "company_count": 0,
            "has_deployment_evidence": False,
            "has_production_metrics": False,
            "title_chasing_count": 0,
            "consulting_only": False,
            "job_count": len(career_list),
        }

    durations = [c.get("duration_months", 0) for c in career_list]
    companies = [c.get("company", "").lower() for c in career_list]
    descriptions = " ".join(c.get("description", "") for c in career_list)

    # Deployment evidence
    deployment_kw = ["deploy", "production", "ship", "launch", "scale", "serving"]
    has_deployment = any(kw in descriptions.lower() for kw in deployment_kw)

    # Production metrics
    metric_patterns = [
        r'\d+[kKmM]?\s*(?:requests|queries|users|calls|transactions)',
        r'(?:latency|throughput|uptime)\s*(?:[:=]|\bis\b)',
        r'\d+%\s*(?:improvement|reduction|increase)',
        r'(?:reduced|improved|increased)\s+(?:by\s+)?\d+',
    ]
    has_metrics = any(re.search(p, descriptions, re.IGNORECASE) for p in metric_patterns)

    # Title chasing (< 18 months)
    title_chasing = sum(1 for d in durations if 0 < d < 18)

    # Consulting only
    consulting_only = len(companies) > 0 and all(
        any(c in comp for comp in CONSULTING_COMPANIES) for c in companies
    )

    return {
        "total_duration_months": sum(durations),
        "max_tenure_months": max(durations) if durations else 0,
        "company_count": len(set(companies)),
        "has_deployment_evidence": has_deployment,
        "has_production_metrics": has_metrics,
        "title_chasing_count": title_chasing,
        "consulting_only": consulting_only,
        "job_count": len(career_list),
    }


def extract_skills_features(skills_list: List[Dict]) -> Dict[str, Any]:
    """Extract features from skills array."""
    if not skills_list:
        return {
            "skill_count": 0,
            "ai_skill_count": 0,
            "backend_skill_count": 0,
            "data_skill_count": 0,
            "avg_proficiency": 0,
            "total_endorsements": 0,
            "has_assessment_skills": False,
        }

    ai_kw = ["machine learning", "deep learning", "nlp", "ai", "ml",
             "ranking", "retrieval", "recommendation", "llm", "transformer",
             "bert", "gpt", "embedding", "neural", "cnn", "rnn", "lstm",
             "tensorflow", "pytorch", "keras", "fine-tuning", "fine tuning",
             "image classification", "object detection", "speech recognition",
             "computer vision", "gan", "vae", "diffusion"]

    backend_kw = ["python", "java", "go", "scala", "sql", "postgresql",
                  "mysql", "redis", "kafka", "docker", "kubernetes", "aws",
                  "gcp", "azure", "flask", "django", "fastapi", "spring",
                  "node", "express", "rest", "grpc"]

    data_kw = ["spark", "airflow", "hadoop", "etl", "data pipeline",
               "data engineering", "hive", "presto", "snowflake", "databricks",
               "bigquery", "redshift", "dbt"]

    skill_names = [s.get("name", "").lower() for s in skills_list]
    prof_map = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}

    proficiencies = [prof_map.get(s.get("proficiency", ""), 0) for s in skills_list]
    endorsements = [s.get("endorsements", 0) for s in skills_list]

    ai_count = sum(1 for name in skill_names if any(kw in name for kw in ai_kw))
    backend_count = sum(1 for name in skill_names if any(kw in name for kw in backend_kw))
    data_count = sum(1 for name in skill_names if any(kw in name for kw in data_kw))

    return {
        "skill_count": len(skills_list),
        "ai_skill_count": ai_count,
        "backend_skill_count": backend_count,
        "data_skill_count": data_count,
        "avg_proficiency": np.mean(proficiencies) if proficiencies else 0,
        "total_endorsements": sum(endorsements),
        "has_assessment_skills": ai_count > 0 or backend_count > 0,
    }


def compute_claim_assessment_gap(
    skills_list: List[Dict],
    assessment_scores: Dict[str, float]
) -> Dict[str, float]:
    """Compute gap between claimed proficiency and actual assessment."""
    if not skills_list or not assessment_scores:
        return {
            "avg_assessment_gap": 0,
            "max_assessment_gap": 0,
            "assessment_count": 0,
            "claim_assessment_consistency": 0.5,
        }

    gaps = []
    for skill in skills_list:
        name = skill.get("name", "")
        claimed = skill.get("proficiency", "")
        if name in assessment_scores and claimed:
            assessment = assessment_scores[name]
            baseline = CLAIM_ASSESSMENT_BASELINES.get(claimed, 50.0)
            gap = abs(assessment - baseline)
            gaps.append(gap)

    if not gaps:
        return {
            "avg_assessment_gap": 0,
            "max_assessment_gap": 0,
            "assessment_count": 0,
            "claim_assessment_consistency": 0.5,
        }

    avg_gap = np.mean(gaps)
    max_gap = max(gaps)

    # Consistency: smaller gap = higher consistency
    if avg_gap <= 10:
        consistency = 1.0
    elif avg_gap <= 20:
        consistency = 0.7 + 0.3 * (1 - (avg_gap - 10) / 10)
    elif avg_gap <= 30:
        consistency = 0.4 + 0.3 * (1 - (avg_gap - 20) / 10)
    else:
        consistency = 0.2

    return {
        "avg_assessment_gap": avg_gap,
        "max_assessment_gap": max_gap,
        "assessment_count": len(gaps),
        "claim_assessment_consistency": consistency,
    }


def extract_candidate_features(candidate: Dict[str, Any]) -> Dict[str, float]:
    """Extract all features from a single candidate."""
    features = {}

    # === Profile features ===
    profile = candidate.get("profile", {})
    features["years_of_experience"] = safe_float(profile.get("years_of_experience", 0))

    title = profile.get("current_title", "").lower()
    features["is_engineer"] = float(any(kw in title for kw in [
        "engineer", "developer", "scientist", "architect", "sre"
    ]))
    features["is_manager"] = float(any(kw in title for kw in [
        "manager", "lead", "director", "head"
    ]))
    features["is_hr"] = float(any(kw in title for kw in ["hr", "human resource"]))
    features["is_accountant"] = float("accountant" in title)
    features["is_sales"] = float(any(kw in title for kw in ["sales", "business development"]))
    features["is_content_writer"] = float(any(kw in title for kw in ["content", "writer", "copywriter"]))
    features["is_designer"] = float(any(kw in title for kw in ["designer", "graphic"]))
    features["is_civil"] = float("civil" in title)
    features["is_mechanical"] = float("mechanical" in title)

    # === Career history ===
    career = parse_career_history(candidate.get("career_history", []))
    features["total_duration_months"] = career["total_duration_months"]
    features["max_tenure_months"] = career["max_tenure_months"]
    features["company_count"] = career["company_count"]
    features["has_deployment_evidence"] = float(career["has_deployment_evidence"])
    features["has_production_metrics"] = float(career["has_production_metrics"])
    features["title_chasing_count"] = career["title_chasing_count"]
    features["consulting_only"] = float(career["consulting_only"])
    features["job_count"] = career["job_count"]

    # === Skills ===
    skills = extract_skills_features(candidate.get("skills", []))
    features["skill_count"] = skills["skill_count"]
    features["ai_skill_count"] = skills["ai_skill_count"]
    features["backend_skill_count"] = skills["backend_skill_count"]
    features["data_skill_count"] = skills["data_skill_count"]
    features["avg_proficiency"] = skills["avg_proficiency"]
    features["total_endorsements"] = skills["total_endorsements"]

    # === Claim vs Assessment ===
    signals = candidate.get("redrob_signals", {})
    assessment_scores = signals.get("skill_assessment_scores", {})
    claim_assess = compute_claim_assessment_gap(
        candidate.get("skills", []), assessment_scores
    )
    features["avg_assessment_gap"] = claim_assess["avg_assessment_gap"]
    features["assessment_count"] = claim_assess["assessment_count"]
    features["claim_assessment_consistency"] = claim_assess["claim_assessment_consistency"]

    # === Behavioral features (sentinel-safe) ===
    features["response_rate"] = safe_float(signals.get("recruiter_response_rate", 0))
    features["interview_completion"] = safe_float(signals.get("interview_completion_rate", 0))
    features["offer_acceptance"] = safe_float(signals.get("offer_acceptance_rate", 0))
    features["profile_views"] = safe_float(signals.get("profile_views_received_30d", 0))
    features["recruiter_saves"] = safe_float(signals.get("saved_by_recruiters_30d", 0))
    features["search_appearances"] = safe_float(signals.get("search_appearance_30d", 0))
    features["notice_period_days"] = safe_float(signals.get("notice_period_days", 0))
    features["github_activity"] = safe_float(signals.get("github_activity_score", 0))
    features["profile_completeness"] = safe_float(signals.get("profile_completeness_score", 0))
    features["open_to_work"] = float(signals.get("open_to_work_flag", False))

    # Sentinels as separate features
    features["has_offer_history"] = float(
        signals.get("offer_acceptance_rate", SENTINEL_VALUE) != SENTINEL_VALUE
    )
    features["has_github"] = float(
        signals.get("github_activity_score", SENTINEL_VALUE) != SENTINEL_VALUE
    )

    # === Education ===
    education = candidate.get("education", [])
    features["education_count"] = len(education)
    if education:
        tiers = [e.get("tier", "unknown") for e in education]
        features["has_tier1"] = float("tier_1" in tiers)
        features["has_tier2"] = float("tier_2" in tiers)
    else:
        features["has_tier1"] = 0
        features["has_tier2"] = 0

    # === Summary text features ===
    summary = profile.get("summary", "")
    features["summary_length"] = len(summary)
    features["mentions_ai"] = float(any(kw in summary.lower() for kw in [
        "ai", "machine learning", "ml", "deep learning", "nlp",
        "artificial intelligence", "data science"
    ]))
    features["mentions_production"] = float(any(kw in summary.lower() for kw in [
        "production", "deploy", "ship", "scale", "serving"
    ]))

    return features


def extract_all_features(candidates: List[Dict[str, Any]]) -> pd.DataFrame:
    """Extract features for all candidates."""
    feature_rows = []
    for candidate in candidates:
        features = extract_candidate_features(candidate)
        features["candidate_id"] = candidate.get("candidate_id", "")
        feature_rows.append(features)

    return pd.DataFrame(feature_rows).set_index("candidate_id")
