# D1 Wrestling Team Rankings

Elo ratings for NCAA Division I wrestling teams, built from dual meet results and updated automatically through the season. Built by a D1 wrestler at Sacred Heart University.

## Current rankings

<!-- RANKINGS:START -->
Updated through duals on February 21, 2026. 10 D1 duals rated.

| Rank | Team | Rating | Record | Last 5 | Week |
|---:|---|---:|---|---|---|
| 1 | Bellarmine | 1551 | 1-0 | W | same |
| 2 | Binghamton | 1542 | 1-0 | W | same |
| 3 | Hofstra | 1531 | 1-0 | W | same |
| 4 | VMI | 1529 | 1-0 | W | same |
| 5 | Franklin & Marshall | 1525 | 1-0 | W | same |
| 6 | Morgan State | 1522 | 1-0 | W | same |
| 7 | Brown | 1513 | 1-0 | W | new |
| 8 | Duke | 1510 | 1-0 | W | down 1 |
| 9 | Davidson | 1483 | 0-1 | L | down 1 |
| 10 | Presbyterian | 1440 | 0-1 | L | down 1 |
| 11 | Sacred Heart | 1354 | 2-8 | WLLLL | down 1 |
<!-- RANKINGS:END -->

The table above is rewritten by GitHub Actions every time a result is added, and once a day during the season.

## How the ratings work

Every team starts at 1500. After each dual, the winner takes points from the loser. How many depends on two things: how surprising the result was (beating a higher-rated team is worth more) and the margin (a 30-6 win moves ratings more than 18-16, damped for heavy favorites so blowouts of weak teams don't inflate a rating). The home team gets a 25-point edge in the prediction, so road wins count a little more. Between seasons, ratings keep two thirds of their distance from average, since rosters turn over.

Duals against non-D1 opponents (listed in `data/non_d1.txt`) are kept in the data but left out of the ratings.

## Add a result

~~~bash
python -m teams.add --home Hofstra --away "Sacred Heart" --score 21-15 --date 2026-10-31
~~~

The score is always home first. For a neutral site add `--neutral`. For a tied dual decided on criteria add `--winner "Team"`. You can also edit `data/duals/<season>.csv` directly, including from the GitHub app on a phone, and the rankings update on their own.

## Predict a dual

~~~bash
python -m teams.predict "Sacred Heart" Hofstra --home Hofstra
~~~

## Project layout

~~~
teams/         Elo engine, ranking, adding results, predictions, fetching
data/duals/    one CSV of dual results per season (the source of truth)
data/          team name aliases and the non-D1 list
rankings/      generated rankings and rating history
dashboard/     Streamlit dashboard
.github/       tests and the automatic ranking update
~~~

## Data and limitations

Rankings are only as complete as the results on file. The 2025-26 file starts with Sacred Heart's duals from the team's public schedule. Full coverage of all D1 teams needs a reliable source for every dual; automatic sources plug into `teams/fetch.py` once permission to use them is in place.
