# D1 Wrestling Team Rankings

Elo ratings for NCAA Division I wrestling teams, built from dual meet results. I enter results by hand and GitHub Actions re-ranks the teams after every change. Built by a D1 wrestler at Sacred Heart University.

**Live dashboard:** [wrestling-data-pipeline-kka2nqqhuvsszmtkgbh4y5.streamlit.app](https://wrestling-data-pipeline-kka2nqqhuvsszmtkgbh4y5.streamlit.app)

## Status

Every D1 dual of the 2026-27 season through November 16 is on file, entered by hand from public box scores. Pulling results in automatically is not built. The WrestleStat comparison is written but not switched on yet, which is why that column is blank.

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

After each dual, the winner takes points from the loser. How many depends on two things: how surprising the result was (beating a higher-rated team is worth more) and the margin (a 30-6 win moves ratings more than 18-16, damped for heavy favorites so blowouts of weak teams don't inflate a rating). The home team gets a 25-point edge in the prediction, so road wins count a little more. Between seasons, ratings keep two thirds of their distance from average, since rosters turn over.

Teams don't all start equal. Each season's starting rating comes from two things, averaged: where the team placed at last season's NCAA Championships, and where it sat in the NWCA preseason coaches poll. Each of those is turned into a rating on a straight line from 1700 for No. 1 down to 1300 for last place, and teams that didn't score at NCAAs or get poll votes start at the bottom. That starting point is blended evenly with last season's carryover where there is one. From then on only dual results move the ratings, so early in the season the table leans on last year, and as duals pile up it becomes this model's own view. The inputs and sources are in `data/priors/`.

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

Rankings are only as complete as the results on file. The 2025-26 file only has Sacred Heart's duals, from the team's public schedule, so last season's carryover covers just those teams. 2026-27 results come from FloWrestling's weekly D1 box scores, checked against PodiumPursuit's D1 scores page, with home sites from each school's schedule. Full school names shown in the tables come from `data/school_names.csv`. Automatic dual results plug into `teams/fetch.py` once permission to use a source is in place.

## License

MIT. See [LICENSE](LICENSE).
