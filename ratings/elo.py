"""Phase 3: Elo rating system for wrestlers.

Bigger wins (major decision, tech fall, fall) move ratings more than a
regular decision. Forfeits are excluded before they get here.
"""
from dataclasses import dataclass, field

RESULT_MULTIPLIER = {
    "DEC": 1.00,
    "MD": 1.15,
    "TF": 1.30,
    "FALL": 1.40,
    "INJ": 0.75,
    "DQ": 0.75,
}


@dataclass
class EloSystem:
    k: float = 32
    base: float = 1500
    ratings: dict = field(default_factory=dict)

    def get(self, wrestler_id: str) -> float:
        return self.ratings.get(wrestler_id, self.base)

    @staticmethod
    def expected(rating_a: float, rating_b: float) -> float:
        """Probability A beats B."""
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    def update(self, winner_id: str, loser_id: str, result_type: str = "DEC"):
        """Apply one result. Returns (winner_pre, loser_pre, change)."""
        rw, rl = self.get(winner_id), self.get(loser_id)
        mult = RESULT_MULTIPLIER.get(result_type, 1.0)
        change = self.k * mult * (1 - self.expected(rw, rl))
        self.ratings[winner_id] = rw + change
        self.ratings[loser_id] = rl - change
        return rw, rl, change

    def new_season(self, regression: float = 0.25):
        """Pull every rating partway back toward the base between seasons."""
        for wid, r in self.ratings.items():
            self.ratings[wid] = r + (self.base - r) * regression
