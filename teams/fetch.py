"""Pull new dual results from automatic sources into data/duals/.

Each source is a function that returns a list of duals shaped like:
  {"date": "2026-10-31", "home": "Hofstra", "away": "Sacred Heart",
   "home_score": 21, "away_score": 15, "neutral": "", "winner": "", "event": ""}

Only add a source you have permission to use (for example, a data export or
API access granted by the site owner). Duals already on file are skipped.
Run: python -m teams.fetch
"""
import csv

from teams.add import season_for
from teams.data import COLUMNS, DUALS_DIR
from teams.names import normalize
from datetime import date

SOURCES = []  # add source functions here once you have an approved data source


def existing_keys() -> set:
    keys = set()
    for path in DUALS_DIR.glob("*.csv"):
        with open(path) as f:
            for r in csv.DictReader(f):
                keys.add((r["date"], normalize(r["home"]), normalize(r["away"])))
    return keys


def save(duals: list[dict]) -> int:
    seen, added = existing_keys(), 0
    for d in duals:
        d = {**{c: "" for c in COLUMNS}, **d, "home": normalize(d["home"]), "away": normalize(d["away"])}
        key = (d["date"], d["home"], d["away"])
        if key in seen:
            continue
        path = DUALS_DIR / f"{season_for(date.fromisoformat(d['date']))}.csv"
        new_file = not path.exists()
        with open(path, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore", lineterminator="\n")
            if new_file:
                w.writeheader()
            w.writerow(d)
        seen.add(key)
        added += 1
    return added


def main():
    if not SOURCES:
        print("No automatic sources enabled yet. Add results with python -m teams.add for now.")
        return
    total = sum(save(source()) for source in SOURCES)
    print(f"Added {total} new duals.")


if __name__ == "__main__":
    main()
