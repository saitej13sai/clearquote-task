# ClearQuote NL → SQL Analytics API

Natural language analytics system for ClearQuote vehicle damage and repair data.

This project converts user questions into safe, validated PostgreSQL queries using an LLM, executes them against a structured database, and returns formatted analytical answers.

---

## Overview

ClearQuote NL → SQL enables users to query structured vehicle repair data using natural language.

The system:

1. Converts user question → parameterized SQL (GPT-5.2)
2. Validates SQL via AST inspection (SELECT-only enforcement)
3. Executes safely against PostgreSQL (read-only)
4. Returns formatted analytical response

The architecture is designed with strict safety, validation, and production-grade guardrails.

---

## Tech Stack

* FastAPI (API layer)
* PostgreSQL (Neon or local)
* SQLAlchemy (DB access)
* sqlglot (AST-based SQL validation)
* OpenAI GPT-5.2 (NL → SQL)
* Streamlit (Frontend UI)

---

## Architecture

```
User Question
    ↓
LLM (GPT-5.2)
    ↓
Structured JSON (SQL + params)
    ↓
SQL Validator (AST-based, SELECT-only)
    ↓
PostgreSQL (read-only execution)
    ↓
Answer Formatter
    ↓
API Response (JSON)
    ↓
Streamlit UI
```

---

## Key Design Decisions

### 1. Strict Read-Only SQL Enforcement

* Only `SELECT` queries allowed
* AST validation using `sqlglot`
* Blocks:
  * INSERT
  * UPDATE
  * DELETE
  * DROP
  * ALTER
  * TRUNCATE
  * CREATE
  * MERGE
* No raw string execution without validation

---

### 2. Parameterized Queries

The LLM is forced to generate parameterized SQL:

```sql
WHERE r.created_at >= :start_date 
AND r.created_at < :end_date
```

Benefits:

* Prevents SQL injection
* Safe binding via SQLAlchemy
* Deterministic execution

---

### 3. Date Handling Hardening

Enforced at prompt level:

* No `::` casting
* No `INTERVAL` arithmetic in SQL
* Date math computed in Python
* Only parameter binding allowed

This ensures predictable execution and avoids dialect inconsistencies.

---

### 4. Table Allowlist

Only the following tables are accessible:

* `vehicle_cards`
* `damage_detections`
* `repairs`
* `quotes`

The LLM receives explicit schema guidance.

---

## Features

* Natural language → SQL conversion
* Synonym normalization (panel & severity)
* Time filters:
  * "this month"
  * "last 30 days"
* Aggregations:
  * COUNT
  * AVG
  * SUM
  * STDDEV
  * VARIANCE
* Safe JOIN support
* Automatic LIMIT enforcement
* Graceful clarification flow
* Streamlit frontend

---

## Example Queries

### Average Repair Cost

> What is the average repair cost for rear bumper damages in last 30 days?

---

### Severe Damage Count

> How many vehicles had severe damages on the front panel this month?

---

### Variance Analytics

> Which car models have the highest repair cost variance?

---

## Safety Handling

| Risk             | Mitigation            |
| ---------------- | --------------------- |
| SQL Injection    | Parameterized queries |
| Write Operations | AST-level block       |
| Schema Abuse     | Table allowlist       |
| Overfetching     | Enforced LIMIT        |
| Date Misuse      | No INTERVAL / casting |

Example:

User input:

> Delete all rows from repairs

Response:
Clarification returned (write operations blocked)

---

## Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/saitej13sai/clearquote-task.git
cd clearquote-task
```

---

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 3. Configure Environment

Create `.env` file:

```
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5.2
MAX_ROWS=200
```

Neon Postgres is recommended for cloud environments.

---

### 4. Apply Schema

```bash
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
```

---

### 5. Load Dataset

Download the dataset and save as:

```
ClearQuote Sample Dataset.xlsx
```

Then run:

```bash
python scripts/load_data.py
```

---

### 6. Start API

```bash
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/
```

---

### 7. Test API

```bash
python - <<'PY'
import requests

r = requests.post(
    "http://127.0.0.1:8000/query",
    json={"question": "How many vehicle cards are there?"}
)

print(r.json())
PY
```

---

### 8. Run Streamlit UI

```bash
streamlit run ui/streamlit_app.py
```

---

## API Contract

### POST /query

#### Request

```json
{
  "question": "How many vehicle cards are there?"
}
```

#### Response

```json
{
  "needs_clarification": false,
  "sql": "SELECT COUNT(*) FROM vehicle_cards LIMIT 200",
  "answer": "There are 100 records matching your criteria.",
  "rows_returned": 1,
  "notes": []
}
```

---

## Testing

Includes:

* SQL validator unit tests
* End-to-end smoke test
* Manual adversarial tests (DELETE / DROP / UPDATE)

Run:

```bash
pytest
```

---

## Project Structure

```
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
```

---

## Production Improvements (Future Work)

* Strict structured JSON schema enforcement
* Query plan inspection
* Cost-based query guard
* Response caching
* Query logging & analytics
* Role-based row filtering
* Deployment to Railway / Render

---

## Evaluation Readiness

This implementation satisfies:

* Natural language understanding
* Robust SQL generation
* Strict safety validation
* Analytical reasoning
* Clean architecture
* Proper error handling
* Frontend interface
* Clear documentation

---

## License

MIT

## Author

Sai Teja
