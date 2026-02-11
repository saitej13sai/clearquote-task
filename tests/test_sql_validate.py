from app.sql_validate import validate_sql_readonly_allowlist

def test_reject_write_ops():
    vr = validate_sql_readonly_allowlist("DROP TABLE vehicle_cards;")
    assert not vr.ok

def test_allow_select():
    vr = validate_sql_readonly_allowlist("SELECT card_id FROM vehicle_cards;")
    assert vr.ok

def test_reject_unknown_table():
    vr = validate_sql_readonly_allowlist("SELECT * FROM users;")
    assert not vr.ok
