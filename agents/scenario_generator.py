"""
Scenario Generator Agent
Generates 3–5 realistic future scenarios from decision context using Gemini API.
"""
import json
import google.generativeai as genai
from core.prompts import SCENARIO_GENERATOR_PROMPT
from core.schemas import validate_schema, SCENARIO_SCHEMA
from utils.helpers import parse_json_response

class ScenarioGenerator:

    def __init__(self, model: genai.GenerativeModel):
        self.model = model

    def generate(self, context: dict) -> dict:
        if not context:
            raise ValueError("Context cannot be empty.")

        context_str = json.dumps(context, indent=2)
        prompt = SCENARIO_GENERATOR_PROMPT.format(context=context_str)

        response = self.model.generate_content(prompt)
        raw_text = response.text

        parsed = parse_json_response(raw_text)
        if parsed is None:
            raise ValueError(
                f"Scenario Generator: Failed to parse Gemini response.\nRaw: {raw_text[:500]}"
            )

        validate_schema(parsed, SCENARIO_SCHEMA, label="ScenarioGenerator")

        # Normalize probabilities so they sum to ~1.0
        scenarios = parsed.get("scenarios", [])
        total_prob = sum(float(s.get("probability", 0)) for s in scenarios)
        if total_prob > 0:
            for s in scenarios:
                s["probability"] = round(float(s.get("probability", 0)) / total_prob, 3)

        parsed["scenarios"] = scenarios
        return parsed