ALLOWED_TABLES = {
    "vehicle_cards": {
        "card_id", "vehicle_type", "manufacturer", "model", "manufacture_year", "created_at",
    },
    "damage_detections": {
        "damage_id", "card_id", "panel_name", "damage_type", "severity", "confidence", "detected_at",
    },
    "repairs": {
        "repair_id", "card_id", "panel_name", "repair_action", "repair_cost", "approved", "created_at",
    },
    "quotes": {
        "quote_id", "card_id", "total_estimated_cost", "currency", "generated_at",
    },
}

# Lightweight normalization dictionary for informal wording
PANEL_SYNONYMS = {
    # front
    "front panel": "bonnet",
    "hood": "bonnet",
    "front bumper": "front_bumper",
    "front side": "front_bumper",
    # rear
    "back bumper": "rear_bumper",
    "rear bumper": "rear_bumper",
    "back side": "rear_bumper",
}

SEVERITY_SYNONYMS = {
    "high": "severe",
    "critical": "severe",
    "low": "minor",
    "medium": "moderate",
}
