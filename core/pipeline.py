"""
Pipeline
Orchestrates the full AI decision simulation workflow:
  user input → ContextAnalyzer → ScenarioGenerator → OutcomePredictor
             → RiskCalculator → DecisionEngine → save to history
"""

import json
import os
from datetime import datetime
from typing import Optional

import google.generativeai as genai

from agents.context_analyzer import ContextAnalyzer
from agents.scenario_generator import ScenarioGenerator
from agents.outcome_predictor import OutcomePredictor
from agents.decision_engine import DecisionEngine
from utils.risk_calculator import calculate_all_risk_scores
from utils.helpers import build_history_id

# History file path
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "history.json")

class DecisionPipeline:

    def __init__(self, api_key: Optional[str] = None):
        # Streamlit exports root-level .streamlit/secrets.toml keys as env vars
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY not set. Add it to .streamlit/secrets.toml or the environment."
            )
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.5-flash")

        self.context_analyzer = ContextAnalyzer(model)
        self.scenario_generator = ScenarioGenerator(model)
        self.outcome_predictor = OutcomePredictor(model)
        self.decision_engine = DecisionEngine()

    def run(self, user_input: str) -> dict:
        timestamp = datetime.now().isoformat(timespec="seconds")

        # Step 1: Analyze context
        context = self.context_analyzer.analyze(user_input)

        # Step 2: Generate scenarios 
        scenarios = self.scenario_generator.generate(context)

        # Step 3: Predict outcomes 
        outcomes = self.outcome_predictor.predict(context, scenarios)

        #  Step 4: Calculate risk scores 
        risk_scores = calculate_all_risk_scores(
            outcomes.get("outcomes", []),
            scenarios.get("scenarios", []),
            context,
        )
        #  Step 5: Run decision engine 
        final_decision = self.decision_engine.decide(
            context, scenarios, outcomes, risk_scores
        )
        # ── Step 6: Assemble full result 
        result = {
            "id": build_history_id(timestamp, user_input),
            "timestamp": timestamp,
            "user_input": user_input,
            "context": context,
            "scenarios": scenarios,
            "outcomes": outcomes,
            "risk_scores": risk_scores,
            "final_decision": final_decision,
        }

        #  Step 7: Save to history 
        self._save_to_history(result)

        return result
    # History management

    def _save_to_history(self, result: dict) -> None:
        """Append a simulation result to the local history JSON file."""
        history = self._load_history()
        history.append({
            "id": result["id"],
            "timestamp": result["timestamp"],
            "user_input": result["user_input"],
            "context": result["context"],
            "scenarios": result["scenarios"],
            "outcomes": result["outcomes"],
            "risk_scores": result["risk_scores"],
            "final_decision": result["final_decision"],
        })
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    def _load_history(self) -> list:
        """Load existing history from JSON file."""
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def get_history(self) -> list:
        """Public method to retrieve past decisions."""
        return self._load_history()

    def clear_history(self) -> None:
        """Clear all stored history."""
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)