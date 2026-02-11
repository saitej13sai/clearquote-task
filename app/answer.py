from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from decimal import Decimal


@dataclass
class Answer:
    text: str
    notes: list[str]


def _format_number(value: Any) -> str:
    if value is None:
        return "0"

    if isinstance(value, (int,)):
        return f"{value:,}"

    if isinstance(value, (float, Decimal)):
        return f"{float(value):,.2f}"

    return str(value)


def format_answer(
    question: str,
    columns: list[str],
    rows: list[tuple],
    assumptions: list[str],
) -> Answer:

    notes: list[str] = []

    if assumptions:
        notes.append("Assumptions: " + "; ".join(assumptions))

    if not rows:
        return Answer(
            text="No results matched your query for the specified filters.",
            notes=notes,
        )

    # ---------------------------------------------------------
    # SINGLE VALUE (count, avg, sum, etc.)
    # ---------------------------------------------------------
    if len(columns) == 1 and len(rows) == 1:
        column = columns[0].lower()
        value = rows[0][0]
        formatted = _format_number(value)

        if "count" in column:
            text = f"There are {formatted} records matching your criteria."

        elif "avg" in column or "average" in column:
            text = f"The average value is {formatted}."

        elif "sum" in column or "total" in column:
            text = f"The total value is {formatted}."

        elif "min" in column:
            text = f"The minimum value is {formatted}."

        elif "max" in column:
            text = f"The maximum value is {formatted}."

        else:
            text = f"{columns[0]} = {formatted}"

        return Answer(text=text, notes=notes)

    # ---------------------------------------------------------
    # MULTI-COLUMN AGGREGATION (group by results)
    # ---------------------------------------------------------
    if len(rows) <= 20:
        lines = []
        for r in rows:
            parts = []
            for col, val in zip(columns, r):
                parts.append(f"{col}: {_format_number(val)}")
            lines.append(", ".join(parts))

        text = "Here are the results:\n\n" + "\n".join(lines)
        return Answer(text=text, notes=notes)

    # ---------------------------------------------------------
    # TABLE OUTPUT (large result sets)
    # ---------------------------------------------------------
    max_show = 20
    show_rows = rows[:max_show]

    header = " | ".join(columns)
    separator = " | ".join(["---"] * len(columns))
    table_lines = [header, separator]

    for r in show_rows:
        table_lines.append(" | ".join(_format_number(x) for x in r))

    if len(rows) > max_show:
        notes.append(f"Showing first {max_show} of {len(rows)} rows.")

    return Answer(
        text="Here are the results:\n\n" + "\n".join(table_lines),
        notes=notes,
    )
