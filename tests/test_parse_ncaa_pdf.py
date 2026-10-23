from ingest.parse_ncaa_pdf import normalize_code, parse_text

SAMPLE = """125
Champ. Round 2 - Luke Lilledahl (Penn State) 25-1 won by decision over Gavin Hoffman (Lock Haven) 20-3 (Dec 4-0)
Champ. Round 1 - Jane Doe (Iowa) 20-2 won by fall over John Roe (Army) 10-9 (Fall 2:31)
184
Champ. Round 2 - C. Starocci (Penn State) won by tech fall over A. Brenot (North Dakota State) (TF 15-0 4:24)
1st Place Match - Vincent Robinson (NC State) won in tie breaker - 1 over Troy Spratley (Oklahoma State) (TB-1 2-1)
some unrelated line
"""


def test_parses_all_result_lines():
    rows, skipped = parse_text(SAMPLE, 2025)
    assert len(rows) == 4
    assert skipped == 0


def test_fields_are_correct():
    first = parse_text(SAMPLE, 2025)[0][0]
    assert first["winner"] == "Luke Lilledahl"
    assert first["team_a"] == "Penn State"
    assert first["wrestler_b"] == "Gavin Hoffman"
    assert first["result_type"] == "DEC"
    assert (first["score_a"], first["score_b"]) == (4, 0)
    assert first["weight_class"] == 125


def test_weight_class_carries_forward():
    rows, _ = parse_text(SAMPLE, 2025)
    assert [r["weight_class"] for r in rows] == [125, 125, 184, 184]


def test_result_codes():
    assert normalize_code("Fall") == "FALL"
    assert normalize_code("TB-1") == "DEC"
    assert normalize_code("SV-1") == "DEC"
    assert normalize_code("MD") == "MD"
    assert normalize_code("M. For.") == "FOR"
