"""Save a snapshot of WrestleStat's D1 team rankings.

The first snapshot of each season seeds every team's starting rating, so all
D1 teams are ranked from day one. After that, dual results move the ratings,
and the latest snapshot is shown next to your rankings for comparison.

Setup (once): open WrestleStat's team rankings page in your browser, copy the
address, and save it:
    echo "PASTE_URL_HERE" > data/wrestlestat/rankings_url.txt
Then:
    python -m teams.wrestlestat

Runs at most once per day, identifies itself, and respects robots.txt.
"""
import sys
import urllib.robotparser
from datetime import date
from io import StringIO
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests

from teams.data import season_for
from teams.names import normalize

ROOT = Path(__file__).resolve().parents[1]
SNAP_DIR = ROOT / "data" / "wrestlestat"
URL_FILE = SNAP_DIR / "rankings_url.txt"
USER_AGENT = "wrestling-data-pipeline student project (github.com/andersonowenk-bit/wrestling-data-pipeline)"
TOP, BOTTOM = 1700, 1300  # starting ratings for the No. 1 and last-ranked team


def allowed(url: str) -> bool:
    parts = urlparse(url)
    rp = urllib.robotparser.RobotFileParser(f"{parts.scheme}://{parts.netloc}/robots.txt")
    try:
        rp.read()
    except Exception:
        return True
    return rp.can_fetch(USER_AGENT, url)


def parse_rankings(html: str) -> pd.DataFrame:
    """Find the table with a team or school column and a rank column."""
    for t in pd.read_html(StringIO(html)):
        cols = {c: str(c).lower() for c in t.columns}
        team_col = next((c for c, l in cols.items() if "team" in l or "school" in l), None)
        if team_col is None:
            continue
        rank_col = next((c for c, l in cols.items() if "rank" in l or l in ("#", "rk")), t.columns[0])
        df = pd.DataFrame({
            "rank": pd.to_numeric(t[rank_col].astype(str).str.extract(r"(\d+)")[0], errors="coerce"),
            "team": t[team_col].astype(str),
        }).dropna()
        df["team"] = (df["team"].str.replace(r"\s*\(.*?\)\s*$", "", regex=True)
                      .str.replace(r"^#?\d+\s+", "", regex=True).map(normalize))
        if len(df) >= 10:
            df["rank"] = df["rank"].astype(int)
            return df.sort_values("rank").drop_duplicates("team").reset_index(drop=True)
    raise ValueError("Couldn't find a team rankings table on that page. Check the URL.")


def snapshots() -> dict:
    """{date: DataFrame} for every saved snapshot."""
    out = {}
    for path in sorted(SNAP_DIR.glob("*.csv")):
        out[date.fromisoformat(path.stem)] = pd.read_csv(path)
    return out


def season_priors() -> dict:
    """{season: (date, {team: starting rating})} from the first snapshot of each season."""
    priors = {}
    for d, df in snapshots().items():
        season = season_for(d)
        if season in priors:
            continue
        n = max(len(df) - 1, 1)
        priors[season] = (d, {r.team: TOP - (r.rank - 1) * (TOP - BOTTOM) / n for r in df.itertuples()})
    return priors


def latest_ranks() -> dict:
    snaps = snapshots()
    if not snaps:
        return {}
    df = snaps[max(snaps)]
    return dict(zip(df.team, df["rank"]))


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else (URL_FILE.read_text().strip() if URL_FILE.exists() else "")
    if not url:
        print(__doc__)
        return
    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    out = SNAP_DIR / f"{date.today().isoformat()}.csv"
    if out.exists():
        print(f"Already saved today's snapshot: {out.name}")
        return
    if not allowed(url):
        print("robots.txt asks automated tools not to fetch this page, so nothing was downloaded.")
        return
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    df = parse_rankings(resp.text)
    df.to_csv(out, index=False)
    print(f"Saved {len(df)} teams to {out.relative_to(ROOT)}. No. 1: {df.iloc[0].team}")


if __name__ == "__main__":
    main()
