"""Train the win probability model and evaluate it honestly on a held-out season.

Holdout = the most recent season. Compares the model to a plain Elo baseline.
Saves the model to models/artifacts/ and a calibration plot to reports/figures/.
Run: python -m models.train
"""
import json

import duckdb
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from config import ARTIFACTS_DIR, DB_PATH, FIGURES_DIR
from models.features import FEATURES, build
from ratings.elo import EloSystem


def metrics(y, p):
    return {"accuracy": round(accuracy_score(y, p > 0.5), 4),
            "brier": round(brier_score_loss(y, p), 4),
            "log_loss": round(log_loss(y, p), 4)}


def main():
    con = duckdb.connect(str(DB_PATH), read_only=True)
    history = con.execute("select * from ratings.elo_history").df()
    con.close()

    df = build(history)
    holdout = df["season"].max()
    train, test = df[df["season"] < holdout], df[df["season"] == holdout]

    model = make_pipeline(StandardScaler(), LogisticRegression())
    model.fit(train[FEATURES], train["target"])
    p_model = model.predict_proba(test[FEATURES])[:, 1]
    p_elo = EloSystem.expected(test["rating_a_pre"], test["rating_b_pre"])

    results = {"holdout_season": int(holdout), "test_matches": len(test),
               "model": metrics(test["target"], p_model),
               "elo_baseline": metrics(test["target"], p_elo)}
    print(json.dumps(results, indent=2))

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, ARTIFACTS_DIR / "win_prob.joblib")
    (FIGURES_DIR.parent / "model_metrics.json").write_text(json.dumps(results, indent=2))

    # Calibration: when the model says 70%, does A actually win about 70% of the time?
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(5, 5))
    for name, p in [("Model", p_model), ("Elo only", p_elo)]:
        frac, mean = calibration_curve(test["target"], p, n_bins=10)
        ax.plot(mean, frac, marker="o", label=name)
    ax.plot([0, 1], [0, 1], "--", color="gray", label="Perfect")
    ax.set_xlabel("Predicted win probability")
    ax.set_ylabel("Actual win rate")
    ax.set_title(f"Calibration on {holdout} season")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "calibration.png", dpi=150)
    print(f"Saved model and calibration plot")


if __name__ == "__main__":
    main()
