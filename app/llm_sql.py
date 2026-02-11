from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field
from openai import OpenAI
import re

from .settings import settings
from .domain import ALLOWED_TABLES, PANEL_SYNONYMS, SEVERITY_SYNONYMS


client = OpenAI(api_key=settings.openai_api_key)


# -------------------------------
# System Instruction
# -------------------------------
def _schema_description() -> str:
    return (
        "You generate a single Postgres SELECT query.\n\n"

        "If clarification is NOT needed, you MUST provide:\n"
        "- needs_clarification = false\n"
        "- sql = a valid SELECT statement\n"
        "- params = {} if none\n\n"

        "If clarification IS needed:\n"
        "- needs_clarification = true\n"
        "- clarification_question must be provided\n"
        "- sql must be null\n\n"

        "STRICT RULES:\n"
        "- Only SELECT queries allowed.\n"
        "- Never use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE.\n"
        "- Never use :: casting syntax.\n"
        "- Never use INTERVAL arithmetic inside SQL.\n"
        "- Do NOT compute date math inside SQL.\n"
        "- Use simple comparisons only:\n"
        "    column >= :start_date\n"
        "    column < :end_date\n"
        "- Compute any date arithmetic in params.\n\n"

        "DATE COLUMN RULES (VERY IMPORTANT):\n"
        "- Use damage_detections.detected_at for damage time filters.\n"
        "- Use repairs.created_at for repair time filters.\n"
        "- Use vehicle_cards.created_at for vehicle creation filters.\n\n"

        "Return STRICT JSON only. No markdown. No explanation."
    )


# -------------------------------
# Response Schema
# -------------------------------
class NL2SQLResponse(BaseModel):
    needs_clarification: bool
    clarification_question: Optional[str] = None
    sql: Optional[str] = None
    params: dict[str, Any] = Field(default_factory=dict)
    assumptions: list[str] = Field(default_factory=list)
    normalized_terms: dict[str, str] = Field(default_factory=dict)


# -------------------------------
# JSON Extractor
# -------------------------------
def _extract_json(text: str) -> str:
    """
    Extract first valid JSON object from model output.
    Handles markdown and extra commentary.
    """
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in model output")

    return match.group(0)


# -------------------------------
# NL → SQL
# -------------------------------
def nl_to_sql(question: str, now_date_iso: str) -> NL2SQLResponse:
    allowed = {t: sorted(list(cols)) for t, cols in ALLOWED_TABLES.items()}

    guidance = {
        "panel_synonyms": PANEL_SYNONYMS,
        "severity_synonyms": SEVERITY_SYNONYMS,
        "today": now_date_iso,
        "tables": allowed,
        "rules": [
            "Use only allowed tables.",
            "Use parameterized queries (:start_date, :end_date).",
            "Do not perform date arithmetic inside SQL.",
            "Compute end_date in params.",
            "Follow DATE COLUMN RULES strictly.",
        ],
    }

    prompt = f"""
Question:
{question}

Context:
{guidance}

Respond with STRICT JSON only.
"""

    resp = client.responses.create(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": _schema_description()},
            {"role": "user", "content": prompt},
        ],
    )

    raw = resp.output_text
    clean_json = _extract_json(raw)
    parsed = NL2SQLResponse.model_validate_json(clean_json)

    # Runtime enforcement guard
    if not parsed.needs_clarification and not parsed.sql:
        raise ValueError("Model returned no SQL while needs_clarification=false")

    return parsed
