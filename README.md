# D1 Wrestling Team Rankings

Elo ratings for NCAA Division I wrestling teams, built from dual meet results and updated automatically through the season. Built by a D1 wrestler at Sacred Heart University.

## Current rankings

<!-- RANKINGS:START -->
Updated October 31, 2026. 2026-27 season, 1 D1 duals rated so far.

| Rank | Team | Rating | Record | Last 5 | Week | WrestleStat |
|---:|---|---:|---|---|---|---:|
| 1 | Bellarmine | 1534 | 0-0 |  | same |  |
| 2 | Binghamton | 1528 | 0-0 |  | same |  |
| 3 | VMI | 1520 | 0-0 |  | up 1 |  |
| 4 | Franklin & Marshall | 1517 | 0-0 |  | up 1 |  |
| 5 | Morgan State | 1515 | 0-0 |  | up 1 |  |
| 6 | Brown | 1509 | 0-0 |  | up 1 |  |
| 7 | Duke | 1506 | 0-0 |  | up 1 |  |
| 8 | Hofstra | 1496 | 0-1 | L | down 5 |  |
| 9 | Davidson | 1488 | 0-0 |  | same |  |
| 10 | Presbyterian | 1460 | 0-0 |  | same |  |
| 11 | Sacred Heart | 1427 | 1-0 | W | same |  |
<!-- RANKINGS:END -->

The table above is rewritten by GitHub Actions every time a result is added, and once a day during the season.

## How the ratings work

Every team starts at 1500. After each dual, the winner takes points from the loser. How many depends on two things: how surprising the result was (beating a higher-rated team is worth more) and the margin (a 30-6 win moves ratings more than 18-16, damped for heavy favorites so blowouts of weak teams don't inflate a rating). The home team gets a 25-point edge in the prediction, so road wins count a little more. Between seasons, ratings keep two thirds of their distance from average, since rosters turn over.

Each season starts from WrestleStat's preseason team order: the first snapshot of the season sets every D1 team's starting rating (No. 1 at 1700 down to the last team at 1300), blended evenly with last season's carryover. From then on only dual results move the ratings, so the table becomes this model's own view as the season goes. The WrestleStat column shows their current rank for comparison, and the places where the two disagree are the interesting part.

Duals against non-D1 opponents (listed in `data/non_d1.txt`) are kept in the data but left out of the ratings.

## Add a result

~~~bash
python -m teams.add --home Hofstra --away "Sacred Heart" --score 21-15 --date 2026-10-31
~~~

The score is always home first. For a neutral site add `--neutral`. For a tied dual decided on criteria add `--winner "Team"`. You can also edit `data/duals/<season>.csv` directly, including from the GitHub app on a phone, and the rankings update on their own.

## WrestleStat snapshots

Paste the address of WrestleStat's team rankings page into `data/wrestlestat/rankings_url.txt`, then run `python -m teams.wrestlestat`. GitHub Actions also saves a snapshot once a day. The scraper identifies itself, respects robots.txt, and never fetches more than once a day. Team rankings data courtesy of [WrestleStat](https://www.wrestlestat.com).

## Predict a dual

~~~bash
python -m teams.predict "Sacred Heart" Hofstra --home Hofstra
~~~

## Project layout

~~~
teams/             Elo engine, ranking, adding results, predictions, fetching
data/duals/        one CSV of dual results per season (the source of truth)
data/wrestlestat/  daily snapshots of WrestleStat's team rankings
data/              team name aliases and the non-D1 list
rankings/          generated rankings and rating history
dashboard/         Streamlit dashboard
.github/           tests and the automatic ranking update
~~~

## Data and limitations

Rankings are only as complete as the results on file. The 2025-26 file starts with Sacred Heart's duals from the team's public schedule. The preseason snapshot puts all D1 teams on the board, but ratings only move when duals are on file. Automatic dual results plug into `teams/fetch.py` once permission to use a source is in place.
