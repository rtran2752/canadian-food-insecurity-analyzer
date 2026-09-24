from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

PROVINCES = {
    "BC": "British Columbia", "AB": "Alberta", "SK": "Saskatchewan",
    "MB": "Manitoba", "ON": "Ontario", "QC": "Quebec",
    "NB": "New Brunswick", "NS": "Nova Scotia",
    "PE": "Prince Edward Island", "NL": "Newfoundland and Labrador",
}
