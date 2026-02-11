from __future__ import annotations

from datetime import date
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import traceback
import re

from .llm_sql import nl_to_sql
from .sql_validate import validate_sql_readonly_allowlist
from .db import run_readonly_sql
from .answer import format_answer
from .settings import settings


app = FastAPI(title="ClearQuote NL→SQL")


@app.get("/")
def root():
    return {"status": "ok", "service": "clearquote-nl2sql"}


class QueryIn(BaseModel):
    question: str


class QueryOut(BaseModel):
    needs_clarification: bool
    clarification_question: str | None = None
    sql: str | None = None
    answer: str | None = None
    notes: list[str] = Field(default_factory=list)
    rows_returned: int | None = None


@app.post("/query", response_model=QueryOut)
def query(q: QueryIn) -> QueryOut:
    try:
        today = date.today().isoformat()
        llm = nl_to_sql(q.question, now_date_iso=today)

        if llm.needs_clarification:
            return QueryOut(
                needs_clarification=True,
                clarification_question=llm.clarification_question or "Please clarify.",
                notes=llm.assumptions,
            )

        if not llm.sql:
            raise ValueError("No SQL generated")

        # Validate SQL
        vr = validate_sql_readonly_allowlist(llm.sql)
        if not vr.ok:
            return QueryOut(
                needs_clarification=True,
                clarification_question=f"SQL failed validation: {vr.error}",
                sql=llm.sql,
                notes=llm.assumptions,
            )

        sql = llm.sql.strip().rstrip(";")
        import re 
        if not re.search(r"\blimit\s+\d+", sql.lower()):

        #if " limit " not in sql.lower():
            sql = f"{sql} LIMIT {settings.max_rows}"

        params = llm.params or {}

        # 🔒 Ensure no missing bind params
        placeholders = set(re.findall(r":(\w+)", sql))
        missing = placeholders - set(params.keys())
        if missing:
            raise ValueError(f"Missing SQL parameters: {missing}")

        cols, rows = run_readonly_sql(sql, params)
        ans = format_answer(q.question, cols, rows, llm.assumptions)

        return QueryOut(
            needs_clarification=False,
            sql=sql,
            answer=ans.text,
            notes=ans.notes,
            rows_returned=len(rows),
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
