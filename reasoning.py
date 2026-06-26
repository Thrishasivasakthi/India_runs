"""
Deterministic Reasoning Generator with Counterfactual Support.

No LLM. No hallucination. Every sentence sourced from features.
Includes twin-resolution counterfactuals for specificity.
"""

from typing import Dict, Any, List, Optional


def generate_reasoning(
    rank: int,
    features: Dict[str, float],
    ecs_data: Dict[str, Any],
    counterfactual: str = "",
    title: str = "",
    yoe: float = 0
) -> str:
    """
    Generate human-readable reasoning from actual features.
    
    Structure:
    1. Rank + title + years
    2. Evidence consistency
    3. Recruiter engagement
    4. Production evidence
    5. Skills alignment
    6. Counterfactual (what differentiates)
    7. Flags (if any)
    """
    parts = []

    # Opening
    if yoe > 0:
        parts.append(f"Ranked #{rank} — {title}, {yoe:.1f} yrs.")

    # Evidence consistency
    ecs = ecs_data.get("ecs", 0)
    axes = ecs_data.get("axes_consistent", 0)
    contradictions = ecs_data.get("contradictions", [])

    if ecs > 0.7:
        parts.append(f"Strong evidence ({ecs*100:.0f}/100) across {axes}/4 axes.")
    elif ecs > 0.4:
        parts.append(f"Moderate evidence ({ecs*100:.0f}/100) across {axes}/4 axes.")
    else:
        parts.append(f"Weak evidence ({ecs*100:.0f}/100).")
        if contradictions:
            parts.append(f"Issues: {'; '.join(contradictions)}.")

    # Assessment alignment
    assess_consistency = features.get("claim_assessment_consistency", 0.5)
    if assess_consistency > 0.7:
        parts.append("Claims align with assessments.")
    elif assess_consistency < 0.3:
        parts.append("Claim-assessment gap detected.")

    # Engagement
    response = features.get("response_rate", 0)
    interview = features.get("interview_completion", 0)
    acceptance = features.get("offer_acceptance", 0)

    eng_signals = []
    if response > 0.7:
        eng_signals.append(f"response {response:.0%}")
    if interview > 0.7:
        eng_signals.append(f"interview completion {interview:.0%}")
    if acceptance > 0.7:
        eng_signals.append(f"offer acceptance {acceptance:.0%}")

    if eng_signals:
        parts.append(f"Engagement: {', '.join(eng_signals)}.")
    elif response > 0 and response < 0.3:
        parts.append(f"Low engagement ({response:.0%} response rate).")

    # Production evidence
    if features.get("has_deployment_evidence", 0) > 0:
        parts.append("Production experience.")
    if features.get("has_production_metrics", 0) > 0:
        parts.append("Measurable impact in career history.")

    # Skills alignment
    ai_count = features.get("ai_skill_count", 0)
    backend_count = features.get("backend_skill_count", 0)
    data_count = features.get("data_skill_count", 0)

    skill_parts = []
    if ai_count > 3:
        skill_parts.append(f"{int(ai_count)} AI/ML skills")
    elif ai_count > 0:
        skill_parts.append(f"{int(ai_count)} AI/ML skills")
    if backend_count > 0:
        skill_parts.append(f"{int(backend_count)} backend skills")
    if data_count > 0:
        skill_parts.append(f"{int(data_count)} data engineering skills")

    if skill_parts:
        parts.append(f"Expertise: {'; '.join(skill_parts)}.")

    # Consulting flag
    if features.get("consulting_only", 0) > 0:
        parts.append("Consulting-only background.")

    # Tie-breaking / counterfactual
    if counterfactual:
        parts.append(f"Decisive: {counterfactual}.")

    # Availability
    notice = features.get("notice_period_days", 0)
    if 0 < notice <= 30:
        parts.append("Available short notice.")
    elif notice > 90:
        parts.append(f"{int(notice)} day notice period.")

    return " ".join(parts)
