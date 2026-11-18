# Preseason priors

One file per season. Each team's starting rating is the average of two rank-based ratings:

- `ncaa_place`: the team's place at the previous season's NCAA Championships (team scores).
  Blank means the team didn't score, and it is treated as the last place.
- `poll_rank`: the team's rank in the NWCA Division I preseason coaches poll. Teams receiving
  votes outside the top 25 are ranked 26 and down by points. Blank means no votes, and the team
  is treated as no better than the first rank below the vote-getters, or its NCAA place if lower.

A rank turns into a rating on a straight line from 1700 (No. 1) to 1300 (last place).

## 2026-27 sources

- 2026 NCAA Division I Championships final team scores (NCAA.com, March 21, 2026), 70 teams
- NWCA Division I Men's Wrestling Coaches Poll, preseason, October 28, 2026 (top 25 plus 16 teams receiving votes)
