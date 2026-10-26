"""
JSON output schemas and dataclass structures for the AI Decision Simulator System.
Defines expected structure for all AI agent outputs.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional
import json

# Context Schema
CONTEXT_SCHEMA = {
    "decision_type": str,
    "problem_summary": str,
    "primary_goal": str,
    "secondary_goals": list,
    "constraints": list,
    "stakeholders": list,
    "time_horizon": str,
    "urgency": str,
    "complexity": str,
    "key_factors": list,
}

# Scenario Schema

SCENARIO_SCHEMA = {
    "scenarios": [
        {
            "id": str,
            "title": str,
            "description": str,
            "approach": str,
            "key_actions": list,
            "probability": float,
            "timeframe": str,
            "resources_required": list,
            "difficulty": str,
        }
    ]
}

# Outcome Schema
OUTCOME_SCHEMA = {
    "outcomes": [
        {
            "scenario_id": str,
            "positive_impacts": list,
            "negative_impacts": list,
            "financial_impact": str,
            "emotional_impact": str,
            "career_impact": str,
            "success_probability": float,
            "regret_potential": str,
            "reversibility": str,
            "short_term_outlook": str,
            "long_term_outlook": str,
        }
    ]
}

# Final Decision Output Schema

FINAL_DECISION_SCHEMA = {
    "recommended_scenario_id": str,
    "recommended_scenario_title": str,
    "confidence_score": float,
    "reasoning": str,
    "ranked_scenarios": list,
    "risk_summary": str,
    "action_plan": list,
    "warnings": list,
}

# History Record Schema
HISTORY_RECORD_SCHEMA = {
    "id": str,
    "timestamp": str,
    "user_input": str,
    "context": dict,
    "scenarios": dict,
    "outcomes": dict,
    "final_decision": dict,
    "risk_scores": dict,
}
# Dataclasses (for type-safe usage internally)

@dataclass
class DecisionContext:
    decision_type: str = ""
    problem_summary: str = ""
    primary_goal: str = ""
    secondary_goals: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    stakeholders: List[str] = field(default_factory=list)
    time_horizon: str = ""
    urgency: str = ""
    complexity: str = ""
    key_factors: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Scenario:
    id: str = ""
    title: str = ""
    description: str = ""
    approach: str = ""
    key_actions: List[str] = field(default_factory=list)
    probability: float = 0.0
    timeframe: str = ""
    resources_required: List[str] = field(default_factory=list)
    difficulty: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ImpactItem:
    impact: str = ""
    likelihood: str = ""
    magnitude: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ScenarioOutcome:
    scenario_id: str = ""
    positive_impacts: List[dict] = field(default_factory=list)
    negative_impacts: List[dict] = field(default_factory=list)
    financial_impact: str = ""
    emotional_impact: str = ""
    career_impact: str = ""
    success_probability: float = 0.0
    regret_potential: str = ""
    reversibility: str = ""
    short_term_outlook: str = ""
    long_term_outlook: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class FinalDecision:
    recommended_scenario_id: str = ""
    recommended_scenario_title: str = ""
    confidence_score: float = 0.0
    reasoning: str = ""
    ranked_scenarios: List[dict] = field(default_factory=list)
    risk_summary: str = ""
    action_plan: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def validate_schema(data: dict, schema: dict, label: str = "") -> bool:
    """Basic schema validation — checks top-level keys exist."""
    for key in schema:
        if key not in data:
            print(f"[Schema Warning] Missing key '{key}' in {label or 'data'}")
            return False
    return True