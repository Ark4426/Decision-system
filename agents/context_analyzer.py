import google.generativeai as genai
from core.prompts import CONTEXT_ANALYZER_PROMPT
from core.schemas import DecisionContext, validate_schema, CONTEXT_SCHEMA
from utils.helpers import parse_json_response, clean_text


class ContextAnalyzer:

    def __init__(self, model: genai.GenerativeModel):
        self.model = model

    def analyze(self, user_input: str) -> dict:
        if not user_input or not user_input.strip():
            raise ValueError("User input cannot be empty.")

        prompt = CONTEXT_ANALYZER_PROMPT.format(user_input=clean_text(user_input))

        response = self.model.generate_content(prompt)
        raw_text = response.text

        parsed = parse_json_response(raw_text)
        if parsed is None:
            raise ValueError(
                f"Context Analyzer: Failed to parse Gemini response.\nRaw: {raw_text[:500]}"
            )

        validate_schema(parsed, CONTEXT_SCHEMA, label="ContextAnalyzer")
        return parsed