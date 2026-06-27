"""
Deterministic Reasoning Generator — Concise (1-2 sentences max per spec).

No LLM. No hallucination. Every sentence sourced from features.
"""

from typing import Dict, Any


def generate_reasoning(
    rank: int,
    features: Dict[str, float],
    ecs_data: Dict[str, Any],
    counterfactual: str = "",
    title: str = "",
    yoe: float = 0
) -> str:
    """
    Generate 1-2 sentence reasoning from actual features.
    Truncated to 300 chars max per submission spec.
    """
    parts = []

    # Opening: title + years + evidence
    ecs = ecs_data.get("ecs", 0)
    axes = ecs_data.get("axes_consistent", 0)
    if yoe > 0:
        parts.append(f"{title}, {yoe:.0f} yrs")
    parts.append(f"ECS {ecs*100:.0f}/100 ({axes}/4 axes)")

    # Key signal: engagement or skills
    response = features.get("response_rate", 0)
    interview = features.get("interview_completion", 0)
    ai_count = features.get("ai_skill_count", 0)
    jd_sim = features.get("jd_similarity", 0)

    signals = []
    if response > 0.7:
        signals.append(f"{response:.0%} response")
    if interview > 0.7:
        signals.append(f"{interview:.0%} interview")
    if ai_count > 3:
        signals.append(f"{int(ai_count)} AI skills")
    if jd_sim > 0.3:
        signals.append(f"JD match {jd_sim:.0%}")
    if features.get("has_deployment_evidence", 0) > 0:
        signals.append("production exp")

    if signals:
        parts.append(", ".join(signals[:2]))

    # Counterfactual (the decisive factor)
    if counterfactual:
        parts.append(f"vs twin: {counterfactual}")

    result = " — ".join(parts[:3])
    return result[:300]
