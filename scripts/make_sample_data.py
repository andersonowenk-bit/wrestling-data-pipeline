"""Generate SYNTHETIC wrestling results so the pipeline runs end to end
before real data is collected. Every name and result here is made up.

Run: python scripts/make_sample_data.py
"""
import random
import sys
from pathlib import Path
from datetime import date, timedelta

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import SAMPLE_DIR  # noqa: E402

random.seed(7)
np.random.seed(7)

WEIGHTS = [125, 133, 141, 149, 157, 165, 174, 184, 197, 285]
TEAMS = [f"Team {c}" for c in "ABCDEFGHIJKLMNOP"]
FIRST = ["Jake", "Luke", "Mason", "Owen", "Cole", "Tyler", "Ryan", "Nick", "Evan", "Drew",
         "Sam", "Max", "Ben", "Zach", "Kyle", "Noah", "Liam", "Eli", "Gabe", "Jon"]
LAST = ["Miller", "Smith", "Brooks", "Reyes", "Carter", "Hayes", "Kim", "Foster", "Lopez",
        "Price", "Ward", "Bell", "Cruz", "Diaz", "Grant", "Hughes", "Long", "Ross", "Shaw", "West"]
SEASONS = [2021, 2022, 2023, 2024, 2025]


def make_wrestlers():
    names = set()
    rows = []
    for w in WEIGHTS:
        for team in TEAMS:
            while True:
                name = f"{random.choice(FIRST)} {random.choice(LAST)}"
                if name not in names:
                    names.add(name)
                    break
            rows.append({"name": name, "team": team, "weight": w,
                         "skill": np.random.normal(0, 1)})
    return rows


def result_type(p_gap):
    r = random.random() + p_gap * 0.4
    if r > 1.25:
        return "FALL"
    if r > 1.05:
        return "TF"
    if r > 0.85:
        return "MD"
    return "DEC"


def main():
    wrestlers = make_wrestlers()
    rows = []
    for season in SEASONS:
        start = date(season - 1, 11, 1)
        # A few wrestlers move up a weight class each season
        for wr in wrestlers:
            if random.random() < 0.08 and wr["weight"] != 285:
                wr["weight"] = WEIGHTS[WEIGHTS.index(wr["weight"]) + 1]
            wr["skill"] += np.random.normal(0.1, 0.2)
        for week in range(14):
            day = start + timedelta(days=7 * week)
            event_type = "tournament" if week in (5, 13) else "dual"
            event = "Conference Championships" if week == 13 else (
                "Holiday Open" if week == 5 else f"Dual Week {week + 1}")
            for w in WEIGHTS:
                pool = [x for x in wrestlers if x["weight"] == w]
                random.shuffle(pool)
                for a, b in zip(pool[::2], pool[1::2]):
                    if a["team"] == b["team"]:
                        continue
                    p_a = 1 / (1 + np.exp(-(a["skill"] - b["skill"]) * 1.2))
                    a_wins = random.random() < p_a
                    win, lose = (a, b) if a_wins else (b, a)
                    if random.random() < 0.03:
                        rt, sw, sl = "FOR", None, None
                    else:
                        rt = result_type(abs(p_a - 0.5) * 2)
                        sw = {"DEC": random.randint(3, 7), "MD": random.randint(9, 14),
                              "TF": random.randint(15, 20), "FALL": None}[rt]
                        sl = None if sw is None else max(0, sw - {"DEC": random.randint(1, 6),
                                                                  "MD": random.randint(8, 11),
                                                                  "TF": 15}[rt])
                    # Occasional name variation, cleaned later by the dbt alias seed
                    name_a = a["name"].replace("Jon ", "Jonathan ") if random.random() < 0.3 else a["name"]
                    rows.append({
                        "season": season, "match_date": day.isoformat(), "event": event,
                        "event_type": event_type, "weight_class": w,
                        "wrestler_a": name_a, "team_a": a["team"],
                        "wrestler_b": b["name"], "team_b": b["team"],
                        "winner": name_a if a_wins else b["name"], "result_type": rt,
                        "score_a": sw if a_wins else sl, "score_b": sl if a_wins else sw,
                    })
    df = pd.DataFrame(rows)
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(SAMPLE_DIR / "matches_sample.csv", index=False)

    # Fake "official" rankings for the final season: true skill plus noise
    last = [x for x in wrestlers]
    rank_rows = []
    for w in WEIGHTS:
        pool = sorted([x for x in last if x["weight"] == w],
                      key=lambda x: x["skill"] + np.random.normal(0, 0.5), reverse=True)[:10]
        for i, x in enumerate(pool, 1):
            rank_rows.append({"season": SEASONS[-1], "weight_class": w, "rank": i, "wrestler": x["name"]})
    pd.DataFrame(rank_rows).to_csv(SAMPLE_DIR / "official_rankings_sample.csv", index=False)
    # Alias seed so dbt can merge "Jonathan X" back into "Jon X"
    aliases = sorted({n for n in df["wrestler_a"] if n.startswith("Jonathan ")})
    seed = SAMPLE_DIR.parent.parent / "dbt" / "seeds" / "name_aliases.csv"
    pd.DataFrame({"alias": aliases,
                  "canonical_name": [a.replace("Jonathan ", "Jon ") for a in aliases]}
                 ).to_csv(seed, index=False)
    print(f"Wrote {len(df)} synthetic matches and {len(rank_rows)} ranking rows to {SAMPLE_DIR}")


if __name__ == "__main__":
    main()
