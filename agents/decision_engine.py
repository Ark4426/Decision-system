"""
Decision Engine
Pure Python scoring and ranking system — no AI API calls.
Analyzes scenario outcomes and risk scores to select the best decision.
"""

from typing import List
from utils.helpers import safe_float, score_label, percentage
from utils.risk_calculator import risk_level_label
# Scoring weights (tunable)
SCORE_WEIGHTS = {
    "success_probability": 0.35,
    "positive_impact_count": 0.20,
    "risk_score_inverted": 0.25,   # lower risk = higher score
    "regret_penalty": 0.10,
    "reversibility_bonus": 0.10,
}

REGRET_PENALTY_MAP = {"low": 0, "medium": -5, "high": -15}
REVERSIBILITY_BONUS_MAP = {
    "fully reversible": 10,
    "partially reversible": 5,
    "irreversible": -5,
}


class DecisionEngine:

    def decide(
        self,
        context: dict,
        scenarios: dict,
        outcomes: dict,
        risk_scores: dict,
    ) -> dict:
        scenario_list = scenarios.get("scenarios", [])
        outcome_list = outcomes.get("outcomes", [])

        # Build lookup maps
        outcome_map = {o["scenario_id"]: o for o in outcome_list}

        scored = []
        for scenario in scenario_list:
            sid = scenario["id"]
            outcome = outcome_map.get(sid, {})
            risk = safe_float(risk_scores.get(sid, 50.0))

            score = self._score_scenario(scenario, outcome, risk)
            scored.append({
                "scenario_id": sid,
                "scenario_title": scenario.get("title", sid),
                "score": round(score, 2),
                "risk_score": risk,
                "risk_label": risk_level_label(risk),
                "success_probability": safe_float(outcome.get("success_probability", 0.5)),
                "approach": scenario.get("approach", ""),
                "difficulty": scenario.get("difficulty", ""),
            })

        # Sort descending by composite score
        scored.sort(key=lambda x: x["score"], reverse=True)
        best = scored[0]
        best_outcome = outcome_map.get(best["scenario_id"], {})
        best_scenario = next(
            (s for s in scenario_list if s["id"] == best["scenario_id"]), {}
        )

        confidence = self._compute_confidence(best["score"], scored)
        action_plan = self._build_action_plan(best_scenario)
        warnings = self._build_warnings(best_outcome, best["risk_score"], context)
        reasoning = self._build_reasoning(best, best_scenario, best_outcome, context)
        risk_summary = self._build_risk_summary(risk_scores, scenario_list)

        return {
            "recommended_scenario_id": best["scenario_id"],
            "recommended_scenario_title": best["scenario_title"],
            "confidence_score": round(confidence, 2),
            "reasoning": reasoning,
            "ranked_scenarios": scored,
            "risk_summary": risk_summary,
            "action_plan": action_plan,
            "warnings": warnings,
        }
    # Internal helpers
    def _score_scenario(self, scenario: dict, outcome: dict, risk: float) -> float:
        """Compute a composite score (0–100) for a single scenario."""
        # Component 1: Success probability (0–100)
        sp = safe_float(outcome.get("success_probability", 0.5)) * 100

        # Component 2: Positive impact count (max cap at 40)
        pos_count = len(outcome.get("positive_impacts", []))
        pos_score = min(pos_count * 10, 40)

        # Component 3: Risk score inverted (0–100)
        risk_inv = 100 - risk

        # Component 4: Regret penalty
        regret_pen = REGRET_PENALTY_MAP.get(
            outcome.get("regret_potential", "medium").lower(), -5
        )

        # Component 5: Reversibility bonus
        rev_bonus = REVERSIBILITY_BONUS_MAP.get(
            outcome.get("reversibility", "partially reversible").lower(), 0
        )

        composite = (
            sp * SCORE_WEIGHTS["success_probability"]
            + pos_score * SCORE_WEIGHTS["positive_impact_count"]
            + risk_inv * SCORE_WEIGHTS["risk_score_inverted"]
            + regret_pen * SCORE_WEIGHTS["regret_penalty"]
            + rev_bonus * SCORE_WEIGHTS["reversibility_bonus"]
        )

        return max(0.0, min(composite, 100.0))

    def _compute_confidence(self, best_score: float, scored: list) -> float:
        if len(scored) <= 1:
            return best_score
        others = [s["score"] for s in scored[1:]]
        avg_others = sum(others) / len(others)
        gap = best_score - avg_others
        # Normalize: gap of 20+ points = high confidence
        confidence = min((gap / 20) * 100, 100) if gap > 0 else 30.0
        return max(confidence, 30.0)

    def _build_action_plan(self, scenario: dict) -> List[str]:
        """Extract key actions from the best scenario as the action plan."""
        actions = scenario.get("key_actions", [])
        if not actions:
            return ["Review your options carefully before proceeding."]
        return actions

    def _build_warnings(self, outcome: dict, risk: float, context: dict) -> List[str]:
        """Generate contextual warnings based on risk and outcome data."""
        warnings = []

        if risk >= 70:
            warnings.append("⚠️ High overall risk detected — proceed with caution.")

        if outcome.get("reversibility", "").lower() == "irreversible":
            warnings.append("⚠️ This decision may be difficult or impossible to reverse.")

        if outcome.get("regret_potential", "").lower() == "high":
            warnings.append("⚠️ High potential for regret — ensure you've explored alternatives.")

        neg_major = [
            n for n in outcome.get("negative_impacts", [])
            if isinstance(n, dict) and n.get("magnitude", "").lower() == "major"
               and n.get("likelihood", "").lower() == "high"
        ]
        if neg_major:
            warnings.append(
                f"⚠️ {len(neg_major)} high-likelihood major negative impact(s) identified."
            )

        if context.get("urgency", "").lower() == "critical":
            warnings.append("⚠️ Critical urgency — time-sensitive decision, act promptly.")

        if not warnings:
            warnings.append("✅ No major red flags detected for the recommended scenario.")

        return warnings

    def _build_reasoning(
        self, best: dict, scenario: dict, outcome: dict, context: dict
    ) -> str:
        """Build a human-readable reasoning paragraph for the recommendation."""
        sp_pct = percentage(best["success_probability"])
        parts = [
            f"The recommended path '{best['scenario_title']}' achieved the highest composite score ({best['score']:.1f}/100) "
            f"with an estimated success probability of {sp_pct}.",
            f"It balances a {best['risk_label'].lower()} profile with a {best['approach']} approach, "
            f"making it well-suited to your {context.get('time_horizon', 'stated')} time horizon.",
        ]
        pos = outcome.get("positive_impacts", [])
        if pos:
            parts.append(
                f"Key upsides include {len(pos)} identified positive impact(s), "
                f"such as: {pos[0].get('impact', '') if pos else ''}."
            )
        parts.append(
            f"The '{outcome.get('reversibility', 'partially reversible')}' nature of this choice "
            f"and '{outcome.get('regret_potential', 'medium')}' regret potential further support this selection."
        )
        return " ".join(parts)

    def _build_risk_summary(self, risk_scores: dict, scenarios: list) -> str:
        """Summarize the risk landscape across all scenarios."""
        if not risk_scores:
            return "Insufficient data to summarize risk."
        avg = sum(risk_scores.values()) / len(risk_scores)
        highest = max(risk_scores, key=risk_scores.get)
        lowest = min(risk_scores, key=risk_scores.get)
        high_name = next((s["title"] for s in scenarios if s["id"] == highest), highest)
        low_name = next((s["title"] for s in scenarios if s["id"] == lowest), lowest)
        return (
            f"Average risk across all scenarios: {avg:.1f}/100. "
            f"Highest risk: '{high_name}' ({risk_scores[highest]:.1f}). "
            f"Lowest risk: '{low_name}' ({risk_scores[lowest]:.1f})."
        )