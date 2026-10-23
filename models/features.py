"""Phase 4: build features for the win probability model.

Every feature uses only information from BEFORE the match, so the model
never peeks at the future.
  rating_diff  Elo of A minus Elo of B, before the match
  form_diff    A's recent win rate minus B's (last N matches)
  h2h_diff     A's prior wins over B minus B's prior wins over A
"""
from collections import defaultdict

import pandas as pd

from config import RECENT_FORM_WINDOW

FEATURES = ["rating_diff", "form_diff", "h2h_diff"]


def recent_form(history: pd.DataFrame, window: int = RECENT_FORM_WINDOW) -> pd.DataFrame:
    """Win rate over each wrestler's previous `window` matches (0.5 if no history)."""
    long = pd.concat([
        history[["match_id", "match_date", "wrestler_a_id", "a_won"]]
            .rename(columns={"wrestler_a_id": "wrestler_id", "a_won": "won"}),
        history[["match_id", "match_date", "wrestler_b_id", "a_won"]]
            .rename(columns={"wrestler_b_id": "wrestler_id"})
            .assign(won=lambda d: ~d["a_won"]).drop(columns="a_won"),
    ]).sort_values(["wrestler_id", "match_date", "match_id"])
    long["won"] = long["won"].astype(float)
    long["form"] = (long.groupby("wrestler_id")["won"]
                        .transform(lambda s: s.shift(1).rolling(window, min_periods=1).mean())
                        .fillna(0.5))
    return long[["match_id", "wrestler_id", "form"]]


def head_to_head(history: pd.DataFrame) -> pd.Series:
    """Prior head-to-head record from A's point of view."""
    wins = defaultdict(int)
    out = []
    for row in history.sort_values(["match_date", "match_id"]).itertuples(index=False):
        a, b = row.wrestler_a_id, row.wrestler_b_id
        out.append((row.match_id, wins[(a, b)] - wins[(b, a)]))
        if row.a_won:
            wins[(a, b)] += 1
        else:
            wins[(b, a)] += 1
    return pd.Series(dict(out), name="h2h_diff")


def build(history: pd.DataFrame) -> pd.DataFrame:
    df = history.copy()
    df["rating_diff"] = df["rating_a_pre"] - df["rating_b_pre"]
    form = recent_form(df)
    df = df.merge(form.rename(columns={"wrestler_id": "wrestler_a_id", "form": "form_a"}),
                  on=["match_id", "wrestler_a_id"], how="left")
    df = df.merge(form.rename(columns={"wrestler_id": "wrestler_b_id", "form": "form_b"}),
                  on=["match_id", "wrestler_b_id"], how="left")
    df["form_diff"] = df["form_a"] - df["form_b"]
    df["h2h_diff"] = df["match_id"].map(head_to_head(df))
    df["target"] = df["a_won"].astype(int)
    return df
