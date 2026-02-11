from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from .settings import settings

_engine: Engine | None = None

def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
    return _engine

def run_readonly_sql(sql: str, params: dict | None = None) -> tuple[list[str], list[tuple]]:
    """
    Executes SQL in a read-only transaction, with a statement timeout.
    Returns (columns, rows).
    """
    eng = get_engine()
    params = params or {}

    with eng.begin() as conn:
        # Postgres statement timeout
        conn.execute(text(f"SET LOCAL statement_timeout = {settings.statement_timeout_ms};"))
        # "Read-only" transaction hint
        conn.execute(text("SET TRANSACTION READ ONLY;"))

        result = conn.execute(text(sql), params)
        cols = list(result.keys())
        rows = result.fetchall()
        return cols, rows
