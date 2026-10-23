"""Turn the many ways a school gets written into one team name."""
import csv
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"


def _aliases() -> dict:
    path = DATA / "team_aliases.csv"
    if not path.exists():
        return {}
    with open(path) as f:
        return {r["alias"].strip().lower(): r["team"].strip() for r in csv.DictReader(f)}


def _non_d1() -> set:
    path = DATA / "non_d1.txt"
    if not path.exists():
        return set()
    return {line.strip().lower() for line in path.read_text().splitlines() if line.strip()}


ALIASES = _aliases()
NON_D1 = _non_d1()


def normalize(name: str) -> str:
    """'Hofstra University' -> 'Hofstra', 'University of Iowa' -> 'Iowa'."""
    raw = " ".join(name.split())
    if raw.lower() in ALIASES:
        return ALIASES[raw.lower()]
    short = raw
    for prefix in ("University of ", "The "):
        if short.startswith(prefix):
            short = short[len(prefix):]
    for suffix in (" University", " College"):
        if short.endswith(suffix):
            short = short[: -len(suffix)]
    return ALIASES.get(short.lower(), short)


def is_d1(team: str) -> bool:
    return team.lower() not in NON_D1
