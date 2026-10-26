# AI Decision Simulator

Describe a decision you're facing in plain English. A multi-agent pipeline powered by Google Gemini analyzes it, simulates four possible futures, predicts their outcomes, scores their risk, and recommends the best path — all in a Streamlit web UI.

---

## Architecture

```
                        ┌──────────────────────────┐
  user input ─────────▶ │  app.py (Streamlit UI)   │
                        └────────────┬─────────────┘
                                     ▼
                        ┌──────────────────────────┐
                        │  core/pipeline.py        │  DecisionPipeline.run()
                        └────────────┬─────────────┘
                                     │
   ┌─────────────────────────────────┼──────────────────────────────────┐
   │  1. ContextAnalyzer      (Gemini)  → structured problem context    │
   │  2. ScenarioGenerator    (Gemini)  → 4 future scenarios            │
   │  3. OutcomePredictor     (Gemini)  → impacts + success probability │
   │  4. RiskCalculator       (Python)  → 0–100 risk score per scenario │
   │  5. DecisionEngine       (Python)  → ranked scenarios + verdict    │
   │  6. save to data/history.json                                      │
   └────────────────────────────────────────────────────────────────────┘
```

The three Gemini agents each send a prompt from `core/prompts.py`, parse the JSON reply, and validate it against a schema in `core/schemas.py`. Risk scoring and the final decision are deterministic Python, with no AI calls, so the same AI outputs always produce the same recommendation.

| Path | Role |
|---|---|
| `app.py` | Streamlit UI: input box, example prompts, result tabs, history sidebar |
| `core/pipeline.py` | Orchestrates the agents and saves results to history |
| `core/prompts.py` | Gemini prompt templates (each asks for strict JSON) |
| `core/schemas.py` | Expected JSON shapes and validation |
| `agents/context_analyzer.py` | Extracts decision type, goals, constraints, urgency, complexity |
| `agents/scenario_generator.py` | Generates conservative → bold scenarios and normalizes their probabilities to sum to 1 |
| `agents/outcome_predictor.py` | Predicts positive/negative impacts, success probability, regret, reversibility |
| `agents/decision_engine.py` | Weighted composite scoring, ranking, confidence, action plan, warnings |
| `utils/risk_calculator.py` | Rule-based 0–100 risk score and risk labels/colors |
| `utils/helpers.py` | JSON parsing, text cleanup, formatting helpers |
| `data/history.json` | Stored past simulations |

### Scoring

**Risk score (0–100, higher = riskier)** in `utils/risk_calculator.py` adds penalties for each negative impact (more for high-likelihood or major ones), low success probability, irreversibility, regret potential, negative financial impact, high urgency or complexity, and scenario difficulty. It's capped at 100.

| Score | Label |
|---|---|
| ≥ 75 | 🔴 Very High Risk |
| 55–74 | 🟠 High Risk |
| 35–54 | 🟡 Moderate Risk |
| 15–34 | 🟢 Low Risk |
| < 15 | ✅ Very Low Risk |

**Composite score (0–100)** in `agents/decision_engine.py` ranks the scenarios:

| Component | Weight |
|---|---|
| Success probability | 0.35 |
| Inverted risk score (100 − risk) | 0.25 |
| Positive impact count (10 each, max 40) | 0.20 |
| Regret penalty (low 0 / medium −5 / high −15) | 0.10 |
| Reversibility bonus (fully +10 / partially +5 / irreversible −5) | 0.10 |

**Confidence** grows with the gap between the top score and the average of the others: a 20+ point gap gives 100%, and it never drops below 30%.

---

## Setup Instructions

**Requirements:** Python 3.10+ and a Google Gemini API key (create one at [Google AI Studio](https://aistudio.google.com/apikey)).

```bash
git clone https://github.com/Ark4426/Decision-system.git
cd Decision-system

python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

Add your API key (see [Configuration](#configuration)), then start the app:

```bash
streamlit run app.py
```

It opens at http://localhost:8501.

---

## Example Inputs & Outputs

### Inputs

Type any decision into the text box, or click one of the examples in the sidebar:

- Should I switch jobs to a startup for 30% more pay?
- Should I relocate to another country for my career?
- Should I start my own business or stay employed?
- Should I invest my savings in real estate or stocks?
- Should I go back to school for a master's degree?

### Output

Results appear in five tabs: **Overview**, **Scenarios**, **Outcomes**, **Risk Analysis**, and **Recommendation**.

Below is a real run for the input `should i choose money or job?`, shortened.

**Context:**

```json
{
  "decision_type": "career",
  "primary_goal": "Achieve an optimal balance between financial security and career fulfillment.",
  "time_horizon": "medium-term (1-3 years)",
  "urgency": "medium",
  "complexity": "moderate"
}
```

**Scenarios, ranked:**

| Rank | Scenario | Approach | Composite score | Risk score |
|---|---|---|---|---|
| 1 | Value-Aligned Mid-Tier Growth | balanced | 54.8 | 20.0 🟢 |
| 2 | Immediate Capital Accumulation Strategy | conservative | 45.5 | 39.0 🟡 |
| 3 | High-Upside Aggressive Leap | bold | 33.6 | 58.5 🟠 |
| 4 | Fulfillment-Centric Lean Strategy | — | 26.1 | 79.5 🔴 |

**Final decision:**

```json
{
  "recommended_scenario_title": "Value-Aligned Mid-Tier Growth",
  "confidence_score": 98.35,
  "reasoning": "The recommended path 'Value-Aligned Mid-Tier Growth' achieved the highest composite score (54.8/100) with an estimated success probability of 85%. ...",
  "risk_summary": "Average risk across all scenarios: 49.2/100. Highest risk: 'Fulfillment-Centric Lean Strategy' (79.5). Lowest risk: 'Value-Aligned Mid-Tier Growth' (20.0).",
  "action_plan": [
    "Negotiate performance-based bonuses and remote flexibility",
    "Build specialized, high-demand skills during regular work hours",
    "Maintain steady upward progression without acute burnout"
  ],
  "warnings": ["✅ No major red flags detected for the recommended scenario."]
}
```

### Using it from Python

```python
from core.pipeline import DecisionPipeline

result = DecisionPipeline().run("Should I go back to school for a master's degree?")
print(result["final_decision"]["recommended_scenario_title"])
```

`result` contains `id`, `timestamp`, `user_input`, `context`, `scenarios`, `outcomes`, `risk_scores`, and `final_decision`.

---

## Configuration

### API key

The key is read from the `GOOGLE_API_KEY` environment variable. **Never hardcode it in source files.**

**Option 1 — Streamlit secrets (recommended).** Create `.streamlit/secrets.toml`:

```toml
GOOGLE_API_KEY = "your-key-here"
```

Streamlit automatically exposes top-level secrets as environment variables. This file is listed in `.gitignore`, so it won't be committed.

**Option 2 — environment variable:**

```bash
# macOS / Linux
export GOOGLE_API_KEY="your-key-here"
# Windows PowerShell
$env:GOOGLE_API_KEY = "your-key-here"
```

You can also pass it directly: `DecisionPipeline(api_key="...")`.

If no key is found, the app shows: `GOOGLE_API_KEY not set. Add it to .streamlit/secrets.toml or the environment.`

### Model

The Gemini model is set in `core/pipeline.py`:

```python
model = genai.GenerativeModel("gemini-3.5-flash")
```

You can switch it to any model your key can access, for example `gemini-2.5-flash`. If a model is overloaded (HTTP 503), the SDK keeps retrying and the app looks frozen. Switching models fixes that.

### Tuning

- **Risk penalties:** `WEIGHTS` in `utils/risk_calculator.py`
- **Ranking weights:** `SCORE_WEIGHTS`, `REGRET_PENALTY_MAP`, and `REVERSIBILITY_BONUS_MAP` in `agents/decision_engine.py`
- **Agent behavior:** the prompt templates in `core/prompts.py`. If you change the JSON shape, update `core/schemas.py` too.

---

## History

Every completed simulation is appended to `data/history.json`, with the full context, scenarios, outcomes, risk scores, and final decision. The file is created automatically if it's missing, and a corrupt file is treated as empty.

- **In the UI:** the sidebar's 🗂️ History section shows how many decisions are stored and the last five inputs.
- **In code:**

  ```python
  p = DecisionPipeline()
  p.get_history()    # list of past results
  p.clear_history()  # reset to []
  ```

Each entry's `id` is built from its timestamp and a slug of the input, for example `20261026T21353_should_i_choose_money_or_job`.

> `data/history.json` holds everything you typed into the app. Clear it, or add it to `.gitignore`, before pushing to a public repo.
