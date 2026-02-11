CREATE TABLE IF NOT EXISTS vehicle_cards (
  card_id            INTEGER PRIMARY KEY,
  vehicle_type       TEXT NOT NULL,
  manufacturer       TEXT NOT NULL,
  model              TEXT NOT NULL,
  manufacture_year   INTEGER NOT NULL,
  created_at         DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS damage_detections (
  damage_id     INTEGER PRIMARY KEY,
  card_id       INTEGER NOT NULL REFERENCES vehicle_cards(card_id) ON DELETE CASCADE,
  panel_name    TEXT NOT NULL,
  damage_type   TEXT NOT NULL,
  severity      TEXT NOT NULL CHECK (severity IN ('minor','moderate','severe')),
  confidence    DOUBLE PRECISION NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
  detected_at   DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS repairs (
  repair_id      INTEGER PRIMARY KEY,
  card_id        INTEGER NOT NULL REFERENCES vehicle_cards(card_id) ON DELETE CASCADE,
  panel_name     TEXT NOT NULL,
  repair_action  TEXT NOT NULL,
  repair_cost    NUMERIC(12,2) NOT NULL CHECK (repair_cost >= 0),
  approved       BOOLEAN NOT NULL,
  created_at     DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS quotes (
  quote_id             INTEGER PRIMARY KEY,
  card_id              INTEGER NOT NULL REFERENCES vehicle_cards(card_id) ON DELETE CASCADE,
  total_estimated_cost  NUMERIC(12,2) NOT NULL CHECK (total_estimated_cost >= 0),
  currency             TEXT NOT NULL,
  generated_at         DATE NOT NULL
);

-- Practical indexes for typical filters
CREATE INDEX IF NOT EXISTS idx_damage_card ON damage_detections(card_id);
CREATE INDEX IF NOT EXISTS idx_damage_detected_at ON damage_detections(detected_at);
CREATE INDEX IF NOT EXISTS idx_damage_panel ON damage_detections(panel_name);
CREATE INDEX IF NOT EXISTS idx_damage_severity ON damage_detections(severity);

CREATE INDEX IF NOT EXISTS idx_repairs_card ON repairs(card_id);
CREATE INDEX IF NOT EXISTS idx_repairs_created_at ON repairs(created_at);
CREATE INDEX IF NOT EXISTS idx_repairs_panel ON repairs(panel_name);
CREATE INDEX IF NOT EXISTS idx_repairs_approved ON repairs(approved);

CREATE INDEX IF NOT EXISTS idx_quotes_card ON quotes(card_id);
CREATE INDEX IF NOT EXISTS idx_quotes_generated_at ON quotes(generated_at);
