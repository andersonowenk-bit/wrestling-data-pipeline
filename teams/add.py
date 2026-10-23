"""Add a dual result, then re-rank.

Score is HOME-AWAY. Examples:
  python -m teams.add --home Hofstra --away "Sacred Heart" --score 21-15 --date 2026-10-31
  python -m teams.add --home Lehigh --away Cornell --score 17-17 --winner Cornell --date 2026-12-05
  python -m teams.add --home Iowa --away "Penn State" --score 12-25 --date 2027-01-30 --neutral
"""
import argparse
import csv
from datetime import date

from teams import rank
from teams.data import COLUMNS, DUALS_DIR
from teams.names import normalize


def season_for(d: date) -> str:
    start = d.year if d.month >= 8 else d.year - 1
    return f"{start}-{str(start + 1)[-2:]}"


def main():
    p = argparse.ArgumentParser(description="Add a dual result")
    p.add_argument("--home", required=True)
    p.add_argument("--away", required=True)
    p.add_argument("--score", required=True, help="home-away, like 21-15")
    p.add_argument("--date", default=date.today().isoformat())
    p.add_argument("--neutral", action="store_true")
    p.add_argument("--winner", default="", help="only needed for tied duals decided on criteria")
    p.add_argument("--event", default="")
    a = p.parse_args()

    home_score, away_score = (int(x) for x in a.score.split("-"))
    d = date.fromisoformat(a.date)
    path = DUALS_DIR / f"{season_for(d)}.csv"
    DUALS_DIR.mkdir(parents=True, exist_ok=True)
    new_file = not path.exists()
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        if new_file:
            w.writeheader()
        w.writerow({"date": d.isoformat(), "home": normalize(a.home), "away": normalize(a.away),
                    "home_score": home_score, "away_score": away_score,
                    "neutral": "yes" if a.neutral else "", "winner": a.winner, "event": a.event})
    print(f"Added to {path.name}: {normalize(a.home)} {home_score}, {normalize(a.away)} {away_score}\n")
    rank.main()


if __name__ == "__main__":
    main()
