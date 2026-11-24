"""Check a batch of dual results, then save the good ones to data/duals/.

The daily results agent writes what it found to a JSON file and runs this.
Nothing reaches the ratings unless every check passes, so a typo, a made-up
team name or a half-finished dual gets rejected instead of moving rankings.

Each item in the JSON list looks like:
  {"date": "2026-11-21", "home": "Lehigh", "away": "Cornell",
   "home_score": 17, "away_score": 17, "neutral": "", "winner": "Cornell",
   "event": "", "source": "https://..."}

Run: python -m teams.ingest results.json [--dry-run]
"""
import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

from teams.data import DUALS_DIR, season_for
from teams.fetch import existing_keys, save
from teams.names import NON_D1, SCHOOL_NAMES, normalize

SOURCES_DIR = DUALS_DIR.parent / "sources"
MAX_TEAM_SCORE = 60  # 10 weights x 6 points for a forfeit/fall is the ceiling


def known_team(team: str) -> bool:
    return team in SCHOOL_NAMES or team.lower() in NON_D1


def check(d: dict, today: date) -> str | None:
    """Return why a dual is rejected, or None if it is good."""
    for key in ("date", "home", "away", "home_score", "away_score"):
        if d.get(key) in (None, ""):
            return f"missing {key}"
    try:
        day = date.fromisoformat(str(d["date"]))
    except ValueError:
        return f"bad date {d['date']!r}"
    if day > today:
        return "date is in the future"
    if season_for(day) != season_for(today):
        return f"not in the current season ({season_for(today)})"
    home, away = normalize(str(d["home"])), normalize(str(d["away"]))
    if home == away:
        return "home and away are the same team"
    for team in (home, away):
        if not known_team(team):
            return f"unknown team {team!r} (add it to team_aliases.csv, school_names.csv or non_d1.txt)"
    try:
        hs, as_ = int(d["home_score"]), int(d["away_score"])
    except (TypeError, ValueError):
        return "scores must be whole numbers"
    if not (0 <= hs <= MAX_TEAM_SCORE and 0 <= as_ <= MAX_TEAM_SCORE):
        return f"score {hs}-{as_} is out of range"
    if hs == as_:
        winner = normalize(str(d.get("winner") or ""))
        if winner not in (home, away):
            return "tied dual needs a winner on criteria"
    if not str(d.get("source", "")).startswith("http"):
        return "missing source link"
    return None


def log_sources(duals: list[dict]) -> None:
    """Keep the link each dual came from, so any result can be checked later."""
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    for d in duals:
        path = SOURCES_DIR / f"{season_for(date.fromisoformat(d['date']))}.csv"
        new_file = not path.exists()
        with open(path, "a", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            if new_file:
                w.writerow(["date", "home", "away", "source"])
            w.writerow([d["date"], d["home"], d["away"], d["source"]])


def ingest(items: list[dict], today: date | None = None, dry_run: bool = False) -> dict:
    today = today or date.today()
    seen = existing_keys()
    good, dupes, rejected = [], [], []
    for d in items:
        reason = check(d, today)
        if reason:
            rejected.append((d, reason))
            continue
        d = {**d, "home": normalize(str(d["home"])), "away": normalize(str(d["away"])),
             "home_score": int(d["home_score"]), "away_score": int(d["away_score"]),
             "winner": normalize(str(d["winner"])) if d.get("winner") else ""}
        key = (d["date"], d["home"], d["away"])
        if key in seen:
            dupes.append(d)
            continue
        seen.add(key)
        good.append(d)
    if good and not dry_run:
        save(good)
        log_sources(good)
    return {"added": good, "already_on_file": dupes, "rejected": rejected}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Check and save a batch of dual results")
    p.add_argument("path", type=Path)
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args(argv)
    result = ingest(json.loads(a.path.read_text()), dry_run=a.dry_run)
    verb = "Would add" if a.dry_run else "Added"
    print(f"{verb} {len(result['added'])}, already on file {len(result['already_on_file'])}, "
          f"rejected {len(result['rejected'])}")
    for d in result["added"]:
        print(f"  + {d['date']} {d['home']} {d['home_score']}, {d['away']} {d['away_score']}")
    for d, reason in result["rejected"]:
        print(f"  x {d.get('date')} {d.get('home')} vs {d.get('away')}: {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
