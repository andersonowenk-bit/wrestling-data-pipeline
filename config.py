"""Shared paths and settings so every script points at the same places."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
SAMPLE_DIR = DATA_DIR / "sample"
DB_PATH = DATA_DIR / "wrestling.duckdb"
ARTIFACTS_DIR = ROOT / "models" / "artifacts"
FIGURES_DIR = ROOT / "reports" / "figures"

# Elo settings (tune these in Phase 3)
ELO_BASE = 1500
ELO_K = 32
ELO_SEASON_REGRESSION = 0.25  # pull ratings 25% toward the mean between seasons

# Modeling
RECENT_FORM_WINDOW = 5
