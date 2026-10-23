from teams.wrestlestat import parse_rankings

ROWS = "".join(f"<tr><td>{i}</td><td>Team {chr(64 + i)} ({i}-0)</td><td>{i * 3}</td></tr>" for i in range(1, 13))
HTML = f"""<html><body>
<table><tr><th>Menu</th></tr><tr><td>Home</td></tr></table>
<table><thead><tr><th>Rank</th><th>Team</th><th>Points</th></tr></thead><tbody>{ROWS}</tbody></table>
</body></html>"""


def test_finds_rankings_table_and_cleans_names():
    df = parse_rankings(HTML)
    assert len(df) == 12
    assert df.iloc[0].team == "Team A"
    assert df.iloc[0]["rank"] == 1
    assert df.iloc[-1].team == "Team L"
