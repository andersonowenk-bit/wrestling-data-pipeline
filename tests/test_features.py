import pandas as pd

from models.features import build


def sample_history():
    return pd.DataFrame([
        {"match_id": "m1", "season": 2024, "match_date": "2024-01-01", "weight_class": 157,
         "wrestler_a_id": "a", "wrestler_b_id": "b", "rating_a_pre": 1500, "rating_b_pre": 1500,
         "a_won": True, "result_type": "DEC"},
        {"match_id": "m2", "season": 2024, "match_date": "2024-01-08", "weight_class": 157,
         "wrestler_a_id": "a", "wrestler_b_id": "b", "rating_a_pre": 1516, "rating_b_pre": 1484,
         "a_won": False, "result_type": "DEC"},
    ])


def test_first_match_has_neutral_features():
    df = build(sample_history()).set_index("match_id")
    assert df.loc["m1", "h2h_diff"] == 0
    assert df.loc["m1", "form_diff"] == 0


def test_features_only_use_the_past():
    df = build(sample_history()).set_index("match_id")
    # Before m2, A had beaten B once
    assert df.loc["m2", "h2h_diff"] == 1
    assert df.loc["m2", "form_diff"] == 1.0
    assert df.loc["m2", "rating_diff"] == 32
