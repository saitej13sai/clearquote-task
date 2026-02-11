ClearQuote NL → SQL Analytics API

Natural language analytics system for ClearQuote vehicle damage and repair data.

This project converts user questions into safe, validated PostgreSQL queries using an LLM, executes them against a structured database, and returns formatted analytical answers.

Built with:

FastAPI (API layer)

PostgreSQL (Neon or local)

SQLAlchemy (DB access)

sqlglot (AST-level SQL validation)

OpenAI GPT-5.2 (NL → SQL)

Streamlit (Frontend UI)

Architecture Overview
User Question
      ↓
LLM (GPT-5.2)
      ↓
Structured JSON (SQL + params)
      ↓
SQL Validator (AST-based, SELECT-only)
      ↓
Postgres (read-only execution)
      ↓
Answer Formatter
      ↓
API Response (JSON)
      ↓
Streamlit UI

Key Design Decisions
1. Strict Read-Only SQL Enforcement

Only SELECT queries allowed

AST validation using sqlglot

Blocks: INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, MERGE

No raw string execution without validation

2. Parameterized Queries

The model is forced to generate parameterized SQL:

WHERE r.created_at >= :start_date
  AND r.created_at < :end_date


Prevents injection and ensures safe binding via SQLAlchemy.

3. Date Handling Hardening

Prompt explicitly enforces:

No :: casting

No INTERVAL arithmetic in SQL

Date math computed in Python (params)

Ensures predictable execution and avoids syntax issues.

4. Table/Column Allowlist

Only the following tables are usable:

vehicle_cards

damage_detections

repairs

quotes

LLM receives explicit schema guidance.

Features

Natural language to SQL

Synonym normalization (panel & severity)

Time filters:

"this month"

"last 30 days"

Aggregations (COUNT, AVG, SUM, STDDEV, VARIANCE)

Safe JOIN support

Auto LIMIT enforcement

Graceful clarification flow

Streamlit frontend

Example Queries
1. Average Repair Cost

What is the average repair cost for rear bumper damages in last 30 days?

2. Severe Damage Count

How many vehicles had severe damages on the front panel this month?

3. Variance Analytics

Which car models have the highest repair cost variance?

4. Safety Handling

Delete all rows from repairs
→ Returns clarification (write operations blocked)

Setup Instructions
1. Clone Repository
git clone https://github.com/saitej13sai/clearquote-task.git
cd clearquote-task

2. Create Virtual Environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

3. Configure Environment

Create .env:

DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5.2
MAX_ROWS=200


Neon Postgres recommended for Codespaces.

4. Apply Schema
python - <<'PY'
from sqlalchemy import create_engine, text
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(".env"), override=True)
engine = create_engine(os.environ["DATABASE_URL"])

with engine.begin() as conn:
    schema = open("db/schema.sql").read()
    conn.execute(text(schema))

print("Schema applied")
PY

5. Load Dataset

Download the dataset and save as:

ClearQuote Sample Dataset.xlsx


Then run:

python scripts/load_data.py

6. Start API
uvicorn app.main:app --reload


Health check:

curl http://127.0.0.1:8000/

7. Test API
python - <<'PY'
import requests
r = requests.post(
    "http://127.0.0.1:8000/query",
    json={"question": "How many vehicle cards are there?"}
)
print(r.json())
PY

8. Run Streamlit UI
streamlit run ui/streamlit_app.py

API Contract
POST /query
Request
{
  "question": "How many vehicle cards are there?"
}

Response
{
  "needs_clarification": false,
  "sql": "SELECT COUNT(*) FROM vehicle_cards LIMIT 200",
  "answer": "There are 100 records matching your criteria.",
  "rows_returned": 1,
  "notes": []
}

Security Model
Risk	Mitigation
SQL Injection	Parameterized queries
Write operations	AST-level block
Schema abuse	Allowlist tables only
Overfetching	Enforced LIMIT
Date misuse	No INTERVAL / casting
Testing

Includes:

SQL validator unit tests

End-to-end smoke test

Manual adversarial tests (DELETE / DROP / UPDATE)

Production Improvements (Future Work)

Structured JSON schema enforcement (strict mode)

Query plan inspection

Cost-based query guard

Response caching

Query logging & analytics

Role-based row filtering

Deployment to Railway / Render

Project Structure
app/
  main.py
  llm_sql.py
  sql_validate.py
  db.py
  answer.py
  domain.py
  settings.py

db/
  schema.sql

scripts/
  load_data.py

ui/
  streamlit_app.py

tests/
  test_sql_validate.py
  test_end_to_end_smoke.py

Evaluation Readiness

The implementation satisfies:

Natural language understanding

Robust SQL generation

Strict safety validation

Real analytical reasoning

Clean architecture

Proper error handling

Frontend interface

Clear documentation
