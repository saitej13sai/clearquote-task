import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

EXCEL_PATH = os.environ.get("EXCEL_PATH", "ClearQuote Sample Dataset.xlsx")
DATABASE_URL = os.environ["DATABASE_URL"]

SHEETS = ["vehicle_cards", "damage_detections", "repairs", "quotes"]

DATE_COLS = {
    "vehicle_cards": ["created_at"],
    "damage_detections": ["detected_at"],
    "repairs": ["created_at"],
    "quotes": ["generated_at"],
}

def main() -> None:
    if not os.path.exists(EXCEL_PATH):
        raise FileNotFoundError(
            f"Excel file not found at '{EXCEL_PATH}'. "
            f"Set EXCEL_PATH or place the file at repo root."
        )

    engine = create_engine(DATABASE_URL)

    xl = pd.ExcelFile(EXCEL_PATH)
    missing = [s for s in SHEETS if s not in xl.sheet_names]
    if missing:
        raise ValueError(f"Missing sheets in Excel: {missing}. Found: {xl.sheet_names}")

    with engine.begin() as conn:
        # Load in FK-safe order
        for table in ["damage_detections", "repairs", "quotes", "vehicle_cards"]:
            conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))

    for sheet in ["vehicle_cards", "damage_detections", "repairs", "quotes"]:
        df = xl.parse(sheet)
        # Normalize dates
        for c in DATE_COLS.get(sheet, []):
            df[c] = pd.to_datetime(df[c], errors="raise").dt.date

        # Normalize booleans (approved)
        if sheet == "repairs" and "approved" in df.columns:
            df["approved"] = df["approved"].astype(bool)

        df.to_sql(sheet, engine, if_exists="append", index=False, method="multi")
        print(f"Loaded {len(df):,} rows into {sheet}")

    print("Done.")

if __name__ == "__main__":
    main()
