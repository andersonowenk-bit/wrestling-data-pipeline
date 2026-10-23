import pandas as pd

from teams.add import season_for
from teams.elo import BASE, TeamElo
from teams.names import normalize
from teams.rank import build_table
from datetime import date


def test_names_normalize():
    assert normalize("Hofstra University") == "Hofstra"
    assert normalize("University of Iowa") == "Iowa"
    assert normalize("Virginia Military Institute") == "VMI"
    assert normalize("Franklin and Marshall College") == "Franklin & Marshall"


def test_ratings_are_zero_sum():
    elo = TeamElo()
    elo.update("A", "B", 25, 10)
    assert round(elo.get("A") + elo.get("B")) == 2 * BASE
    assert elo.get("A") > BASE > elo.get("B")


def test_bigger_margin_moves_more():
    close, blowout = TeamElo(), TeamElo()
    close.update("A", "B", 18, 16, neutral=True)
    blowout.update("A", "B", 40, 0, neutral=True)
    assert blowout.get("A") > close.get("A")


def test_home_edge_means_road_win_counts_more():
    road, home = TeamElo(), TeamElo()
    road.update("B", "A", 10, 20)
    home.update("A", "B", 20, 10)
    assert road.get("A") > home.get("A")


def test_tied_dual_uses_criteria_winner():
    elo = TeamElo()
    elo.update("A", "B", 17, 17, neutral=True, winner="B")
    assert elo.get("B") > elo.get("A")


def test_season_label():
    assert season_for(date(2026, 10, 31)) == "2026-27"
    assert season_for(date(2027, 2, 14)) == "2026-27"


def test_rank_table():
    duals = pd.DataFrame([
        {"date": pd.Timestamp("2026-11-01"), "home": "A", "away": "B", "home_score": 30, "away_score": 6,
         "neutral": False, "winner": "", "event": "", "season": "2026-27"},
        {"date": pd.Timestamp("2026-11-10"), "home": "B", "away": "C", "home_score": 20, "away_score": 15,
         "neutral": False, "winner": "", "event": "", "season": "2026-27"},
    ])
    import teams.rank as rank
    rank.season_priors = lambda: {}
    rank.latest_ranks = lambda: {}
    table, _ = build_table(duals)
    assert table.iloc[0].team == "A"
    assert table.set_index("team").loc["B", "wins"] == 1
