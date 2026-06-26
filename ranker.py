"""
LightGBM LambdaMART Ranker

Since there's no ground truth, uses weak supervision:
- JD keywords as labeling function
- Title relevance scoring
- Behavioral consistency signals

Trains on features → outputs ranking score.
CPU-only, trains in seconds.
"""

import warnings
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional

warnings.filterwarnings("ignore")

try:
    import lightgbm as lgb
    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False


def generate_weak_labels(features_df: pd.DataFrame) -> pd.Series:
    """
    Generate weak-supervision labels using JD-aligned heuristics.
    
    Label function encodes what the JD explicitly asks for:
    - Production AI/ML experience
    - Backend/data engineering skills
    - Strong recruiter engagement
    - Evidence consistency
    """
    labels = pd.Series(0.0, index=features_df.index)

    # Signal 1: Technical role with AI/ML skills (must-have)
    tech_role = features_df.get("is_engineer", pd.Series(0, index=features_df.index))
    ai_skills = features_df.get("ai_skill_count", pd.Series(0, index=features_df.index))
    production = features_df.get("has_deployment_evidence", pd.Series(0, index=features_df.index))
    metrics = features_df.get("has_production_metrics", pd.Series(0, index=features_df.index))

    labels += tech_role * 2.0
    labels += (ai_skills > 0).astype(float) * 1.5
    labels += production * 1.0
    labels += metrics * 1.0

    # Signal 2: Real recruiter engagement (behavioral)
    response = features_df.get("response_rate", pd.Series(0, index=features_df.index))
    interview = features_df.get("interview_completion", pd.Series(0, index=features_df.index))
    labels += (response > 0.7).astype(float) * 0.5
    labels += (interview > 0.7).astype(float) * 0.5

    # Penalty: Non-technical roles (what JD explicitly rejects)
    non_tech = (
        features_df.get("is_hr", pd.Series(0, index=features_df.index)) +
        features_df.get("is_accountant", pd.Series(0, index=features_df.index)) +
        features_df.get("is_sales", pd.Series(0, index=features_df.index)) +
        features_df.get("is_content_writer", pd.Series(0, index=features_df.index)) +
        features_df.get("is_designer", pd.Series(0, index=features_df.index)) +
        features_df.get("is_civil", pd.Series(0, index=features_df.index)) +
        features_df.get("is_mechanical", pd.Series(0, index=features_df.index))
    )
    labels -= non_tech * 2.0

    # Normalize to [0, 1]
    labels = (labels - labels.min()) / max(labels.max() - labels.min(), 1e-6)
    return labels


def prepare_ranking_features(features_df: pd.DataFrame, ecs_data: pd.DataFrame) -> pd.DataFrame:
    """Prepare feature matrix for LambdaMART."""
    ranking_features = pd.DataFrame(index=features_df.index)

    # ECS features
    ranking_features["ecs"] = ecs_data.get("ecs", 0.5)
    ranking_features["axis_a"] = ecs_data.get("axis_a_score", 0.5)
    ranking_features["axis_b"] = ecs_data.get("axis_b_score", 0.5)
    ranking_features["axis_c"] = ecs_data.get("axis_c_score", 0.5)
    ranking_features["axis_d"] = ecs_data.get("axis_d_score", 0.5)

    # Behavioral features
    ranking_features["response_rate"] = features_df.get("response_rate", 0)
    ranking_features["interview_completion"] = features_df.get("interview_completion", 0)
    ranking_features["offer_acceptance"] = features_df.get("offer_acceptance", 0)

    # Experience
    ranking_features["yoe"] = features_df.get("years_of_experience", 0)
    ranking_features["tenure_max"] = features_df.get("max_tenure_months", 0)
    ranking_features["company_count"] = features_df.get("company_count", 0)

    # Skills
    ranking_features["ai_skills"] = features_df.get("ai_skill_count", 0)
    ranking_features["backend_skills"] = features_df.get("backend_skill_count", 0)
    ranking_features["data_skills"] = features_df.get("data_skill_count", 0)
    ranking_features["skill_count"] = features_df.get("skill_count", 0)
    ranking_features["proficiency"] = features_df.get("avg_proficiency", 0)

    # Production evidence
    ranking_features["deployment"] = features_df.get("has_deployment_evidence", 0)
    ranking_features["metrics"] = features_df.get("has_production_metrics", 0)

    # Gate features
    ranking_features["is_engineer"] = features_df.get("is_engineer", 0)
    ranking_features["consulting"] = features_df.get("consulting_only", 0)
    ranking_features["has_github"] = features_df.get("has_github", 0)
    ranking_features["github_activity"] = features_df.get("github_activity", 0)

    # Normality
    ranking_features["claim_assessment_consistency"] = features_df.get("claim_assessment_consistency", 0.5)

    # Fill NaN
    ranking_features = ranking_features.fillna(0)

    return ranking_features


def train_lambdamart_ranker(
    features_df: pd.DataFrame,
    ecs_data: pd.DataFrame
) -> Optional[object]:
    """
    Train LightGBM LambdaMART ranker on weak-supervision labels.
    """
    if not HAS_LGBM:
        print("  lightgbm not installed. Skipping ranker.")
        return None

    print("  Preparing ranking features...")
    X = prepare_ranking_features(features_df, ecs_data)

    print("  Generating weak-supervision labels...")
    y = generate_weak_labels(features_df)

    # Create query groups (all candidates are one group for simplicity)
    q = np.full(len(X), len(X))

    print("  Training LightGBM LambdaMART...")
    train_data = lgb.Dataset(
        X.values, label=y.values, group=q,
        feature_name=list(X.columns)
    )

    params = {
        "objective": "lambdarank",
        "metric": "ndcg",
        "eval_at": [10, 50],
        "num_leaves": 31,
        "learning_rate": 0.05,
        "feature_fraction": 0.8,
        "verbose": -1,
        "min_data_in_leaf": 5,
        "num_threads": 4,
    }

    model = lgb.train(
        params,
        train_data,
        num_boost_round=100,
        valid_sets=[train_data],
        callbacks=[lgb.early_stopping(10), lgb.log_evaluation(0)],
    )

    # Feature importance
    importance = pd.DataFrame({
        "feature": list(X.columns),
        "importance": model.feature_importance(),
    }).sort_values("importance", ascending=False)
    print(f"  Top 5 features:\n{importance.head(5).to_string(index=False)}")

    # Predict
    preds = model.predict(X.values)
    return model, preds, importance


def rank_with_lambdamart(
    features_df: pd.DataFrame,
    ecs_data: pd.DataFrame
) -> pd.DataFrame:
    """Rank candidates using LightGBM LambdaMART."""
    result = train_lambdamart_ranker(features_df, ecs_data)

    if result is None:
        return None

    model, preds, importance = result
    preds = preds.flatten() if len(preds.shape) > 1 else preds

    # Normalize to [0, 1]
    preds = (preds - preds.min()) / max(preds.max() - preds.min(), 1e-6)

    scores = pd.Series(preds, index=features_df.index)
    scores = scores.sort_values(ascending=False)

    return scores, model, importance
