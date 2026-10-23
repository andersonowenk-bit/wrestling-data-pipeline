"""Team Elo for dual meets.

A win moves a rating more when it was unexpected and when the margin was big.
The margin effect is damped for heavy favorites so blowouts of weak teams
don't inflate a rating.
"""
import math
from dataclasses import dataclass, field

BASE = 1500
K = 30
HOME_EDGE = 25          # Elo points for wrestling on your own mat
SEASON_CARRYOVER = 0.67  # keep two thirds of last season's distance from average


@dataclass
class TeamElo:
    ratings: dict = field(default_factory=dict)

    def get(self, team: str) -> float:
        return self.ratings.get(team, BASE)

    @staticmethod
    def expected(r_a: float, r_b: float) -> float:
        return 1 / (1 + 10 ** ((r_b - r_a) / 400))

    def win_probability(self, team: str, opponent: str, home: str | None = None) -> float:
        edge = HOME_EDGE if home == team else -HOME_EDGE if home == opponent else 0
        return self.expected(self.get(team) + edge, self.get(opponent))

    def update(self, home: str, away: str, home_score: int, away_score: int, neutral: bool = False,
               winner: str | None = None) -> float:
        """Apply one dual. Returns the rating change for the home team."""
        r_home = self.get(home) + (0 if neutral else HOME_EDGE)
        r_away = self.get(away)
        exp_home = self.expected(r_home, r_away)
        if home_score != away_score:
            actual = 1.0 if home_score > away_score else 0.0
        else:
            actual = 1.0 if winner == home else 0.0 if winner == away else 0.5
        margin = abs(home_score - away_score)
        winner_gap = (r_home - r_away) if actual >= 0.5 else (r_away - r_home)
        mult = math.log(margin + 1) * (2.2 / (winner_gap * 0.001 + 2.2)) if margin else 1.0
        change = K * max(mult, 0.5) * (actual - exp_home)
        self.ratings[home] = self.get(home) + change
        self.ratings[away] = self.get(away) - change
        return change

    def new_season(self):
        for t, r in self.ratings.items():
            self.ratings[t] = BASE + (r - BASE) * SEASON_CARRYOVER
