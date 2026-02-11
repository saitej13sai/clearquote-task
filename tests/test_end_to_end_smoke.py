import os
import pytest
from app.sql_validate import validate_sql_readonly_allowlist

@pytest.mark.skipif(True, reason="Requires running DB + LLM key; run manually as smoke.")
def test_smoke():
    sql = "SELECT COUNT(*) FROM vehicle_cards;"
    assert validate_sql_readonly_allowlist(sql).ok
