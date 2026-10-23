from ratings.elo import EloSystem


def test_new_wrestlers_start_at_base():
    assert EloSystem(base=1500).get("anyone") == 1500


def test_equal_ratings_are_a_coin_flip():
    assert EloSystem.expected(1500, 1500) == 0.5


def test_winner_gains_what_loser_loses():
    elo = EloSystem()
    elo.update("a", "b")
    assert elo.get("a") + elo.get("b") == 3000
    assert elo.get("a") > 1500 > elo.get("b")


def test_fall_moves_ratings_more_than_decision():
    dec, fall = EloSystem(), EloSystem()
    dec.update("a", "b", "DEC")
    fall.update("a", "b", "FALL")
    assert fall.get("a") > dec.get("a")


def test_upset_moves_ratings_more_than_expected_win():
    elo = EloSystem(ratings={"fav": 1700, "dog": 1300})
    _, _, expected_win = elo.update("fav", "dog")
    elo = EloSystem(ratings={"fav": 1700, "dog": 1300})
    _, _, upset = elo.update("dog", "fav")
    assert upset > expected_win


def test_new_season_regresses_toward_base():
    elo = EloSystem(ratings={"a": 1700})
    elo.new_season(0.5)
    assert elo.get("a") == 1600
