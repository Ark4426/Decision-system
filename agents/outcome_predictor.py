"""
Outcome Predictor Agent
Predicts positive/negative outcomes for each scenario using Gemini API.
"""

import json
import google.generativeai as genai
from core.prompts import OUTCOME_PREDICTOR_PROMPT
from core.schemas import validate_schema, OUTCOME_SCHEMA
from utils.helpers import parse_json_response, safe_float


class OutcomePredictor:

    def __init__(self, model: genai.GenerativeModel):
        self.model = model

    def predict(self, context: dict, scenarios: dict) -> dict:
        if not context or not scenarios:
            raise ValueError("Context and scenarios cannot be empty.")

        context_str = json.dumps(context, indent=2)
        scenarios_str = json.dumps(scenarios, indent=2)

        prompt = OUTCOME_PREDICTOR_PROMPT.format(
            context=context_str,
            scenarios=scenarios_str,
        )

        response = self.model.generate_content(prompt)
        raw_text = response.text

        parsed = parse_json_response(raw_text)
        if parsed is None:
            raise ValueError(
                f"Outcome Predictor: Failed to parse Gemini response.\nRaw: {raw_text[:500]}"
            )

        validate_schema(parsed, OUTCOME_SCHEMA, label="OutcomePredictor")

        # Clamp success_probability to [0.0, 1.0]
        for outcome in parsed.get("outcomes", []):
            sp = safe_float(outcome.get("success_probability", 0.5))
            outcome["success_probability"] = max(0.0, min(1.0, sp))

        return parsed