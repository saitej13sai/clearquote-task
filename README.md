# clearquote-task# ClearQuote NL→SQL→Answer (Mini)

## Prereqs
- GitHub Codespaces (recommended)
- Docker enabled in the Codespace
- An OpenAI API key

## 1) Setup env
Copy:
cp .env.example .env

Edit `.env`:
- OPENAI_API_KEY=...
- DATABASE_URL=postgresql+psycopg://clearquote:clearquote@localhost:5432/clearquote

## 2) Start Postgres + create schema
make up

## 3) Load Excel data
Place `ClearQuote Sample Dataset.xlsx` in repo root, then:
make load

## 4) Run API
make api
API: http://localhost:8000
Docs: http://localhost:8000/docs

## 5) Run UI (optional)
make ui
UI: http://localhost:8501

## Notes on safety
- SQL is validated with sqlglot: SELECT-only + allowlist tables/columns
- DB transaction is READ ONLY with statement_timeout
- If question is missing key constraints (e.g., a time range), model must ask a single clarification question
- Answers do not invent facts beyond returned rows
