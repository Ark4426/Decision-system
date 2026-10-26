"""
Risk calculator: derives a 0–100 risk score for each scenario
based on AI-predicted outcomes and context metadata.
"""

from typing import List
from utils.helpers import safe_float


# Scoring weight configuration

WEIGHTS = {
    "negative_impact_count": 5,       # per negative impact item
    "high_likelihood_negative": 10,   # extra penalty for high-likelihood negatives
    "major_magnitude_negative": 8,    # extra for major-magnitude negatives
    "low_success_probability": 15,    # penalty when success_prob < 0.4
    "irreversibility": 12,            # penalty if decision is irreversible
    "high_regret": 10,                # penalty for high regret potential
    "urgency_critical": 8,            # penalty for critical urgency
    "urgency_high": 4,
    "complexity_high": 6,
    "complexity_very": 10,
    "difficulty_very": 8,
    "difficulty_hard": 4,
    "financial_negative": 8,
    "financial_highly_negative": 15,
}


def _score_negative_impacts(negative_impacts: list) -> float:
    """Score based on count and severity of negative impacts."""
    score = 0.0
    for item in negative_impacts:
        score += WEIGHTS["negative_impact_count"]
        if isinstance(item, dict):
            if item.get("likelihood", "").lower() == "high":
                score += WEIGHTS["high_likelihood_negative"]
            if item.get("magnitude", "").lower() == "major":
                score += WEIGHTS["major_magnitude_negative"]
    return score


def _score_success_probability(success_prob: float) -> float:
    """Penalize low success probability."""
    if success_prob < 0.4:
        return WEIGHTS["low_success_probability"]
    elif success_prob < 0.6:
        return WEIGHTS["low_success_probability"] * 0.5
    return 0.0


def _score_reversibility(reversibility: str) -> float:
    if "irreversible" in reversibility.lower():
        return WEIGHTS["irreversibility"]
    elif "partially" in reversibility.lower():
        return WEIGHTS["irreversibility"] * 0.5
    return 0.0


def _score_regret(regret: str) -> float:
    if regret.lower() == "high":
        return WEIGHTS["high_regret"]
    elif regret.lower() == "medium":
        return WEIGHTS["high_regret"] * 0.5
    return 0.0


def _score_financial_impact(financial_impact: str) -> float:
    fi = financial_impact.lower()
    if "highly negative" in fi:
        return WEIGHTS["financial_highly_negative"]
    elif "negative" in fi:
        return WEIGHTS["financial_negative"]
    return 0.0


def _score_context_factors(context: dict) -> float:
    """Add risk based on urgency and complexity from the context."""
    score = 0.0
    urgency = context.get("urgency", "").lower()
    complexity = context.get("complexity", "").lower()

    if urgency == "critical":
        score += WEIGHTS["urgency_critical"]
    elif urgency == "high":
        score += WEIGHTS["urgency_high"]

    if "highly complex" in complexity:
        score += WEIGHTS["complexity_very"]
    elif "complex" in complexity:
        score += WEIGHTS["complexity_high"]

    return score


def _score_difficulty(difficulty: str) -> float:
    d = difficulty.lower()
    if "very difficult" in d:
        return WEIGHTS["difficulty_very"]
    elif "difficult" in d:
        return WEIGHTS["difficulty_hard"]
    return 0.0


def calculate_risk_score(outcome: dict, scenario: dict, context: dict) -> float:
    """
    Calculate risk score (0–100) for a single scenario.
    """
    raw_score = 0.0

    raw_score += _score_negative_impacts(outcome.get("negative_impacts", []))
    raw_score += _score_success_probability(safe_float(outcome.get("success_probability", 0.5)))
    raw_score += _score_reversibility(outcome.get("reversibility", ""))
    raw_score += _score_regret(outcome.get("regret_potential", ""))
    raw_score += _score_financial_impact(outcome.get("financial_impact", ""))
    raw_score += _score_context_factors(context)
    raw_score += _score_difficulty(scenario.get("difficulty", ""))

    # Cap at 100
    return min(round(raw_score, 1), 100.0)


def calculate_all_risk_scores(
    outcomes: List[dict],
    scenarios: List[dict],
    context: dict,
) -> dict:
    # Build lookup by scenario_id
    scenario_map = {s["id"]: s for s in scenarios}
    risk_scores = {}

    for outcome in outcomes:
        sid = outcome.get("scenario_id", "")
        scenario = scenario_map.get(sid, {})
        risk_scores[sid] = calculate_risk_score(outcome, scenario, context)

    return risk_scores


def risk_level_label(score: float) -> str:
    """Convert numeric risk score to human-readable label."""
    if score >= 75:
        return "🔴 Very High Risk"
    elif score >= 55:
        return "🟠 High Risk"
    elif score >= 35:
        return "🟡 Moderate Risk"
    elif score >= 15:
        return "🟢 Low Risk"
    else:
        return "✅ Very Low Risk"


def risk_color(score: float) -> str:
    """Return a hex color based on risk level."""
    if score >= 75:
        return "#ef4444"
    elif score >= 55:
        return "#f97316"
    elif score >= 35:
        return "#eab308"
    elif score >= 15:
        return "#22c55e"
    else:
        return "#16a34a"