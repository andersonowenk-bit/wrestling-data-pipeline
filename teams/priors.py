"""Preseason starting ratings from data/priors/<season>.csv.

Each team starts at the average of two rank-based ratings: its place at last
season's NCAA Championships and its rank in the NWCA preseason coaches poll.
See data/priors/README.md for how blanks are handled.
"""
from pathlib import Path

import pandas as pd

from teams.names import normalize
from teams.wrestlestat import BOTTOM, TOP

PRIORS_DIR = Path(__file__).resolve().parents[1] / "data" / "priors"


def rank_to_rating(rank: float, last: float) -> float:
    """No. 1 gets TOP, the last place gets BOTTOM, straight line in between."""
    if last <= 1:
        return TOP
    return TOP - (min(rank, last) - 1) * (TOP - BOTTOM) / (last - 1)


def blended(df: pd.DataFrame) -> dict:
    """{team: starting rating} from a priors table."""
    ncaa = pd.to_numeric(df["ncaa_place"], errors="coerce")
    poll = pd.to_numeric(df["poll_rank"], errors="coerce")
    last = ncaa.max() + 1 if ncaa.notna().any() else len(df)  # teams that didn't score
    ncaa = ncaa.fillna(last)
    unranked = poll.max() + 1 if poll.notna().any() else last
    poll = poll.fillna(ncaa.clip(lower=unranked))  # no votes: no better than the first unranked spot
    return {normalize(t): (rank_to_rating(n, last) + rank_to_rating(p, last)) / 2
            for t, n, p in zip(df["team"], ncaa, poll)}


def file_priors(first_dual: dict | None = None) -> dict:
    """{season: (date, {team: rating})} for every priors file.

    The date is the day before that season's first dual, so the starting
    ratings appear first in the rating history.
    """
    out = {}
    for path in sorted(PRIORS_DIR.glob("*.csv")):
        season = path.stem
        start = int(season[:4])
        when = (first_dual or {}).get(season)
        when = (pd.Timestamp(when) - pd.Timedelta(days=1)) if when is not None else pd.Timestamp(f"{start}-10-01")
        out[season] = (when.date(), blended(pd.read_csv(path, dtype=str)))
    return out
