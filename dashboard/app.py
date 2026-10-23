"""Phase 5: Streamlit dashboard.
Run: streamlit run dashboard/app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import duckdb
import joblib
import pandas as pd
import streamlit as st

from config import ARTIFACTS_DIR, DB_PATH
from models.features import FEATURES, build

st.set_page_config(page_title="Wrestling Analytics", page_icon="🤼", layout="wide")


@st.cache_data
def load():
    con = duckdb.connect(str(DB_PATH), read_only=True)
    ratings = con.execute("select * from ratings.elo_current").df()
    history = con.execute("select * from ratings.elo_history").df()
    weights = con.execute("select * from marts.weight_classes").df()
    con.close()
    return ratings, history, weights


@st.cache_resource
def load_model():
    path = ARTIFACTS_DIR / "win_prob.joblib"
    return joblib.load(path) if path.exists() else None


ratings, history, weights = load()
model = load_model()

st.title("🤼 NCAA Wrestling Analytics")
st.caption("Elo ratings and win probabilities built from match results.")

tab_rank, tab_weights, tab_h2h = st.tabs(["Top wrestlers", "Weight classes", "Head-to-head"])

with tab_rank:
    wc = st.selectbox("Weight class", sorted(ratings["current_weight_class"].unique()))
    top = ratings[ratings["current_weight_class"] == wc].head(20).reset_index(drop=True)
    top.index += 1
    st.dataframe(top[["wrestler_name", "current_team", "rating", "matches_wrestled"]],
                 width="stretch")

with tab_weights:
    st.subheader("Match volume by weight class")
    pivot = weights.pivot(index="weight_class", columns="season", values="matches")
    st.bar_chart(weights.groupby("weight_class")[["matches", "falls", "forfeits"]].sum())
    st.dataframe(pivot, width="stretch")

with tab_h2h:
    st.subheader("Who wins?")
    names = ratings.set_index("wrestler_name")
    c1, c2 = st.columns(2)
    a = c1.selectbox("Wrestler A", names.index, index=0)
    b = c2.selectbox("Wrestler B", names.index, index=1)
    if a == b:
        st.info("Pick two different wrestlers.")
    elif model is None:
        st.warning("Train the model first: python -m models.train")
    else:
        a_id, b_id = names.loc[a, "wrestler_id"], names.loc[b, "wrestler_id"]
        feats = build(history)
        def last_form(wid):
            rows = feats[(feats.wrestler_a_id == wid) | (feats.wrestler_b_id == wid)].tail(5)
            wins = ((rows.wrestler_a_id == wid) & rows.a_won) | ((rows.wrestler_b_id == wid) & ~rows.a_won)
            return wins.mean() if len(rows) else 0.5
        h2h = history[((history.wrestler_a_id == a_id) & (history.wrestler_b_id == b_id)) |
                      ((history.wrestler_a_id == b_id) & (history.wrestler_b_id == a_id))]
        a_wins = (((h2h.wrestler_a_id == a_id) & h2h.a_won) | ((h2h.wrestler_b_id == a_id) & ~h2h.a_won)).sum()
        x = pd.DataFrame([{
            "rating_diff": names.loc[a, "rating"] - names.loc[b, "rating"],
            "form_diff": last_form(a_id) - last_form(b_id),
            "h2h_diff": a_wins - (len(h2h) - a_wins),
        }])[FEATURES]
        p = model.predict_proba(x)[0, 1]
        st.metric(f"{a} win probability", f"{p:.0%}")
        st.progress(float(p))
        st.caption(f"Ratings: {a} {names.loc[a, 'rating']} vs {b} {names.loc[b, 'rating']}. "
                   f"Head-to-head: {a_wins}-{len(h2h) - a_wins}.")
