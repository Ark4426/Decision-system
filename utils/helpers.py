"""
Helper utilities: JSON parsing, text cleaning, formatting.
"""

import json
import re
import textwrap
from typing import Any, Optional
def parse_json_response(raw_text: str) -> Optional[dict]:
    
    if not raw_text:
        return None

    # Strip markdown code fences
    cleaned = re.sub(r"```(?:json)?", "", raw_text).replace("```", "").strip()

    # Attempt direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try extracting first JSON object or array
    match = re.search(r"(\{.*\}|\[.*\])", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    return None


def clean_text(text: str) -> str:
    """Strip extra whitespace, normalize newlines."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    return text


def truncate(text: str, max_chars: int = 300) -> str:
    """Truncate text to a max character count, appending ellipsis if needed."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "…"


def format_list(items: list, bullet: str = "•") -> str:
    """Format a list of strings into a bulleted string."""
    if not items:
        return "None"
    return "\n".join(f"{bullet} {item}" for item in items)


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert a value to int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def capitalize_words(text: str) -> str:
    """Title-case a string."""
    return text.title() if text else ""


def wrap_text(text: str, width: int = 80) -> str:
    """Wrap long text to a given width."""
    return textwrap.fill(text, width=width)


def label_to_color(label: str) -> str:
    """Map descriptive labels to CSS-friendly color names for UI display."""
    mapping = {
        # urgency
        "critical": "#ef4444",
        "high": "#f97316",
        "medium": "#eab308",
        "low": "#22c55e",
        # difficulty
        "very difficult": "#ef4444",
        "difficult": "#f97316",
        "moderate": "#eab308",
        "easy": "#22c55e",
        # impacts
        "major": "#ef4444",
        "minor": "#22c55e",
        # regret
        "positive": "#22c55e",
        "negative": "#ef4444",
        "neutral": "#94a3b8",
        "mixed": "#a855f7",
    }
    return mapping.get(label.lower(), "#94a3b8")


def build_history_id(timestamp: str, user_input: str) -> str:
    """Build a short unique history record ID."""
    slug = re.sub(r"\W+", "_", user_input[:30]).strip("_").lower()
    ts = re.sub(r"[:\-\. ]", "", timestamp)[:14]
    return f"{ts}_{slug}"


def percentage(value: float) -> str:
    """Format a 0–1 float as a percentage string."""
    return f"{value * 100:.0f}%"


def score_label(score: float) -> str:
    """Convert a 0–100 risk/confidence score to a human label."""
    if score >= 80:
        return "Very High"
    elif score >= 60:
        return "High"
    elif score >= 40:
        return "Moderate"
    elif score >= 20:
        return "Low"
    else:
        return "Very Low"