"""
All Gemini AI prompts for the AI Decision Simulator System.
Prompts are structured for clean, consistent JSON output.
"""

CONTEXT_ANALYZER_PROMPT = """
You are an expert decision analyst. Analyze the user's decision problem and extract structured context.

User's Decision Problem: {user_input}

Return ONLY a valid JSON object with this exact structure (no markdown, no extra text):
{{
  "decision_type": "career|financial|personal|business|health|relationship|education|other",
  "problem_summary": "A concise 1-2 sentence summary of the core problem",
  "primary_goal": "The main objective the user wants to achieve",
  "secondary_goals": ["goal1", "goal2"],
  "constraints": ["constraint1", "constraint2", "constraint3"],
  "stakeholders": ["person/entity affected 1", "person/entity affected 2"],
  "time_horizon": "short-term (< 1 year)|medium-term (1-3 years)|long-term (3+ years)",
  "urgency": "low|medium|high|critical",
  "complexity": "simple|moderate|complex|highly complex",
  "key_factors": ["factor1", "factor2", "factor3"]
}}
"""

SCENARIO_GENERATOR_PROMPT = """
You are a strategic foresight expert. Based on the analyzed decision context, generate 4 distinct, realistic future scenarios.

Decision Context: {context}

Generate scenarios ranging from conservative to bold. Each must be meaningfully different.

Return ONLY a valid JSON object (no markdown, no extra text):
{{
  "scenarios": [
    {{
      "id": "scenario_1",
      "title": "Short scenario title",
      "description": "2-3 sentence description of this scenario path",
      "approach": "conservative|balanced|optimistic|bold|alternative",
      "key_actions": ["action1", "action2", "action3"],
      "probability": 0.0,
      "timeframe": "Estimated time to see results",
      "resources_required": ["resource1", "resource2"],
      "difficulty": "easy|moderate|difficult|very difficult"
    }},
    {{
      "id": "scenario_2",
      "title": "Short scenario title",
      "description": "2-3 sentence description of this scenario path",
      "approach": "conservative|balanced|optimistic|bold|alternative",
      "key_actions": ["action1", "action2", "action3"],
      "probability": 0.0,
      "timeframe": "Estimated time to see results",
      "resources_required": ["resource1", "resource2"],
      "difficulty": "easy|moderate|difficult|very difficult"
    }},
    {{
      "id": "scenario_3",
      "title": "Short scenario title",
      "description": "2-3 sentence description of this scenario path",
      "approach": "conservative|balanced|optimistic|bold|alternative",
      "key_actions": ["action1", "action2", "action3"],
      "probability": 0.0,
      "timeframe": "Estimated time to see results",
      "resources_required": ["resource1", "resource2"],
      "difficulty": "easy|moderate|difficult|very difficult"
    }},
    {{
      "id": "scenario_4",
      "title": "Short scenario title",
      "description": "2-3 sentence description of this scenario path",
      "approach": "conservative|balanced|optimistic|bold|alternative",
      "key_actions": ["action1", "action2", "action3"],
      "probability": 0.0,
      "timeframe": "Estimated time to see results",
      "resources_required": ["resource1", "resource2"],
      "difficulty": "easy|moderate|difficult|very difficult"
    }}
  ]
}}

Ensure probabilities across all scenarios sum to approximately 1.0.
"""

OUTCOME_PREDICTOR_PROMPT = """
You are a risk and outcomes expert. For each scenario, predict detailed positive and negative outcomes.

Decision Context: {context}
Scenarios: {scenarios}

Return ONLY a valid JSON object (no markdown, no extra text):
{{
  "outcomes": [
    {{
      "scenario_id": "scenario_1",
      "positive_impacts": [
        {{"impact": "Description of positive outcome", "likelihood": "high|medium|low", "magnitude": "major|moderate|minor"}}
      ],
      "negative_impacts": [
        {{"impact": "Description of negative outcome", "likelihood": "high|medium|low", "magnitude": "major|moderate|minor"}}
      ],
      "financial_impact": "positive|neutral|negative|highly negative|highly positive",
      "emotional_impact": "positive|neutral|negative|mixed",
      "career_impact": "positive|neutral|negative|not applicable",
      "success_probability": 0.0,
      "regret_potential": "low|medium|high",
      "reversibility": "fully reversible|partially reversible|irreversible",
      "short_term_outlook": "Brief 1-sentence short-term outlook",
      "long_term_outlook": "Brief 1-sentence long-term outlook"
    }}
  ]
}}

Provide outcomes for ALL scenarios. Success probability should be a float between 0.0 and 1.0.
"""