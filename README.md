# D1 Wrestling Team Rankings

Elo ratings for NCAA Division I wrestling teams, built from dual meet results. I enter results by hand and GitHub Actions re-ranks the teams after every change. Built by a D1 wrestler at Sacred Heart University.

**Live dashboard:** [wrestling-data-pipeline-kka2nqqhuvsszmtkgbh4y5.streamlit.app](https://wrestling-data-pipeline-kka2nqqhuvsszmtkgbh4y5.streamlit.app)

## Status

This is early. Right now the only duals on file are Sacred Heart's, so the only teams rated are the ones Sacred Heart has wrestled. The WrestleStat comparison is written but not switched on yet, which is why that column is blank. Pulling results in automatically is not built.

## Current rankings

<!-- RANKINGS:START -->
Updated November 16, 2026. 2026-27 season, 75 D1 duals rated so far.

| Rank | Team | Rating | Record | Last 5 | Week | WrestleStat |
|---:|---|---:|---|---|---|---:|
| 1 | Iowa State | 1658 | 4-0 | WWWW | up 3 |  |
| 2 | Penn State | 1623 | 2-0 | WW | new |  |
| 3 | West Virginia | 1620 | 3-0 | WWW | up 5 |  |
| 4 | Purdue | 1612 | 3-0 | WWW | down 3 |  |
| 5 | Michigan | 1608 | 2-0 | WW | up 1 |  |
| 6 | Rutgers | 1606 | 3-0 | WWW | down 4 |  |
| 7 | Princeton | 1605 | 3-0 | WWW | new |  |
| 8 | American | 1600 | 3-0 | WWW | down 3 |  |
| 9 | Oklahoma State | 1594 | 2-0 | WW | up 2 |  |
| 10 | Illinois | 1592 | 2-0 | WW | same |  |
| 11 | Pittsburgh | 1591 | 2-0 | WW | new |  |
| 12 | Appalachian State | 1585 | 2-0 | WW | down 9 |  |
| 13 | Army | 1582 | 2-0 | WW | up 1 |  |
| 14 | Stanford | 1571 | 2-0 | WW | new |  |
| 15 | Iowa | 1562 | 1-0 | W | new |  |
| 16 | Virginia Tech | 1552 | 1-0 | W | down 4 |  |
| 17 | South Dakota State | 1549 | 1-0 | W | down 2 |  |
| 18 | Cal Poly | 1545 | 1-0 | W | new |  |
| 19 | SIU Edwardsville | 1544 | 1-0 | W | new |  |
| 20 | Virginia | 1543 | 1-0 | W | down 4 |  |
| 21 | Ohio State | 1538 | 1-0 | W | new |  |
| 22 | NC State | 1536 | 1-0 | W | new |  |
| 23 | Bucknell | 1534 | 2-1 | LWW | up 9 |  |
| 24 | Chattanooga | 1530 | 2-1 | WWL | new |  |
| 25 | Northern Illinois | 1528 | 1-0 | W | new |  |
<!-- RANKINGS:END -->

The table above is rewritten by GitHub Actions every time a result is added, and once a day during the season.

## How the ratings work

Every team starts at 1500. After each dual, the winner takes points from the loser. How many depends on two things: how surprising the result was (beating a higher-rated team is worth more) and the margin (a 30-6 win moves ratings more than 18-16, damped for heavy favorites so blowouts of weak teams don't inflate a rating). The home team gets a 25-point edge in the prediction, so road wins count a little more. Between seasons, ratings keep two thirds of their distance from average, since rosters turn over.

Each season starts from WrestleStat's preseason team order: the first snapshot of the season sets every D1 team's starting rating (No. 1 at 1700 down to the last team at 1300), blended evenly with last season's carryover. From then on only dual results move the ratings, so the table becomes this model's own view as the season goes. The WrestleStat column shows their current rank for comparison, and the places where the two disagree are the interesting part.

Duals against non-D1 opponents (listed in `data/non_d1.txt`) are kept in the data but left out of the ratings.

## Add a result

~~~bash
python -m teams.add --home Hofstra --away "Sacred Heart" --score 35-7 --date 2026-10-31
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

## License

MIT. See [LICENSE](LICENSE).
