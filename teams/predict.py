"""Win probability for an upcoming dual.

  python -m teams.predict "Sacred Heart" Hofstra --home Hofstra
"""
import argparse

from teams.data import load_duals
from teams.names import normalize
from teams.rank import run_elo


def main():
    p = argparse.ArgumentParser()
    p.add_argument("team")
    p.add_argument("opponent")
    p.add_argument("--home", default=None, help="which team is at home; leave out for neutral")
    a = p.parse_args()
    team, opp = normalize(a.team), normalize(a.opponent)
    home = normalize(a.home) if a.home else None
    elo, _ = run_elo(load_duals())
    prob = elo.win_probability(team, opp, home)
    site = f"at {home}" if home else "on a neutral mat"
    print(f"{team} ({elo.get(team):.0f}) vs {opp} ({elo.get(opp):.0f}), {site}")
    print(f"{team} win probability: {prob:.0%}")
    for t in (team, opp):
        if t not in elo.ratings:
            print(f"Note: no duals on file for {t}, so it starts at an average rating.")


if __name__ == "__main__":
    main()
