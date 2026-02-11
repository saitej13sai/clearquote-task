from dataclasses import dataclass
import sqlglot
from sqlglot import exp
from .domain import ALLOWED_TABLES


FORBIDDEN_EXPRESSIONS = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Create,
    exp.Drop,
    exp.Alter,
    exp.Merge,
)


@dataclass
class ValidationResult:
    ok: bool
    error: str | None = None


def validate_sql_readonly_allowlist(sql: str) -> ValidationResult:
    try:
        parsed = sqlglot.parse_one(sql, read="postgres")
    except Exception as e:
        return ValidationResult(False, f"Invalid SQL: {str(e)}")

    # Only SELECT allowed
    if not isinstance(parsed, exp.Select):
        return ValidationResult(False, "Only SELECT queries are allowed.")

    # Block dangerous operations
    for node in parsed.walk():
        if isinstance(node, FORBIDDEN_EXPRESSIONS):
            return ValidationResult(
                False,
                f"Forbidden operation detected: {node.__class__.__name__}",
            )

    # Enforce table allowlist
    tables = {t.name for t in parsed.find_all(exp.Table)}
    allowed_tables = set(ALLOWED_TABLES.keys())

    if not tables.issubset(allowed_tables):
        return ValidationResult(
            False,
            f"Query references disallowed tables: {tables - allowed_tables}",
        )

    return ValidationResult(True)
