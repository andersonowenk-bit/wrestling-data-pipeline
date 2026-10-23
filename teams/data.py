"""Load every dual from data/duals/<season>.csv, oldest season first."""
from pathlib import Path

import pandas as pd

from teams.names import is_d1, normalize

DUALS_DIR = Path(__file__).resolve().parents[1] / "data" / "duals"
COLUMNS = ["date", "home", "away", "home_score", "away_score", "neutral", "winner", "event"]


def load_duals(d1_only: bool = True) -> pd.DataFrame:
    frames = []
    for path in sorted(DUALS_DIR.glob("*.csv")):
        df = pd.read_csv(path, dtype=str).fillna("")
        if df.empty:
            continue
        df["season"] = path.stem
        frames.append(df)
    if not frames:
        return pd.DataFrame(columns=COLUMNS + ["season"])
    df = pd.concat(frames, ignore_index=True)
    df["home"] = df["home"].map(normalize)
    df["away"] = df["away"].map(normalize)
    df["winner"] = df.get("winner", "").map(lambda w: normalize(w) if w else "")
    df["home_score"] = df["home_score"].astype(float).astype(int)
    df["away_score"] = df["away_score"].astype(float).astype(int)
    df["neutral"] = df["neutral"].str.lower().isin(["1", "true", "yes", "y"])
    df["date"] = pd.to_datetime(df["date"])
    if d1_only:
        df = df[df["home"].map(is_d1) & df["away"].map(is_d1)]
    return df.sort_values(["date"]).reset_index(drop=True)
