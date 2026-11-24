from datetime import date

import pytest

from teams import fetch, ingest

TODAY = date(2026, 11, 23)
SRC = "https://example.com/box-score"


def dual(**kw):
    base = {"date": "2026-11-21", "home": "Lehigh", "away": "Cornell",
            "home_score": 21, "away_score": 13, "source": SRC}
    return {**base, **kw}


@pytest.fixture
def tmp_data(tmp_path, monkeypatch):
    duals, sources = tmp_path / "duals", tmp_path / "sources"
    duals.mkdir()
    monkeypatch.setattr(fetch, "DUALS_DIR", duals)
    monkeypatch.setattr(ingest, "SOURCES_DIR", sources)
    return duals, sources


@pytest.mark.parametrize("kw, reason", [
    ({"date": "2026-11-30"}, "future"),
    ({"date": "2025-12-01"}, "current season"),
    ({"home": "Hogwarts"}, "unknown team"),
    ({"away": "Lehigh"}, "same team"),
    ({"home_score": 75}, "out of range"),
    ({"home_score": "abc"}, "whole numbers"),
    ({"home_score": 17, "away_score": 17}, "winner"),
    ({"source": ""}, "source"),
    ({"away": ""}, "missing away"),
])
def test_bad_results_are_rejected(kw, reason):
    assert reason in ingest.check(dual(**kw), TODAY)


def test_good_result_passes_and_names_are_cleaned():
    assert ingest.check(dual(home="Lehigh University"), TODAY) is None


def test_tie_with_criteria_winner_passes():
    assert ingest.check(dual(home_score=17, away_score=17, winner="Cornell University"), TODAY) is None


def test_saves_once_and_logs_source(tmp_data):
    duals, sources = tmp_data
    first = ingest.ingest([dual(), dual()], today=TODAY)
    assert len(first["added"]) == 1 and len(first["already_on_file"]) == 1
    second = ingest.ingest([dual(home="Lehigh University")], today=TODAY)
    assert second["added"] == [] and len(second["already_on_file"]) == 1
    assert (duals / "2026-27.csv").read_text().count("Lehigh") == 1
    assert SRC in (sources / "2026-27.csv").read_text()


def test_dry_run_writes_nothing(tmp_data):
    duals, sources = tmp_data
    result = ingest.ingest([dual()], today=TODAY, dry_run=True)
    assert len(result["added"]) == 1
    assert not any(duals.iterdir()) and not sources.exists()
