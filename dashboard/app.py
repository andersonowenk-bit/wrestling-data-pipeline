"""Streamlit dashboard: match-up predictor and ratings by weight class.
Run: streamlit run dashboard/app.py
"""
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import duckdb
import joblib
import pandas as pd
import streamlit as st

from config import ARTIFACTS_DIR, DB_PATH, RAW_DIR
from models.features import FEATURES

st.set_page_config(page_title="D1 Wrestling Ratings", layout="wide")

RED, GREEN, NAVY = "#C8102E", "#00843D", "#14284B"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Barlow:wght@400;500;600&display=swap');
html, body, [class*="css"], .stMarkdown, p, td, th, label {{ font-family: 'Barlow', sans-serif; }}
#MainMenu, footer, header [data-testid="stToolbar"] {{ visibility: hidden; }}
.block-container {{ padding-top: 1.5rem; max-width: 1100px; }}
h1, h2, h3 {{ font-family: 'Barlow Condensed', sans-serif; letter-spacing: 0.01em; }}
.masthead {{ background: {NAVY}; color: #fff; padding: 1.4rem 1.6rem 1.2rem; border-radius: 4px;
  border-bottom: 6px solid {RED}; box-shadow: inset 0 -6px 0 {GREEN}; margin-bottom: 1.8rem; }}
.masthead h1 {{ color: #fff; font-size: 2.6rem; font-weight: 700; margin: 0; line-height: 1; padding: 0; }}
.masthead p {{ color: #C9D1DB; margin: .45rem 0 0; font-size: 1rem; }}
.note {{ color: #F2C94C; }}
.card {{ display: grid; grid-template-columns: 1fr auto 1fr; gap: 1.5rem; align-items: center;
  background: #fff; border: 1px solid #C9D1DB; border-radius: 4px; padding: 1.6rem; }}
.corner {{ border-left: 8px solid var(--c); padding-left: 1rem; }}
.corner.right {{ border-left: none; border-right: 8px solid var(--c); padding: 0 1rem 0 0; text-align: right; }}
.corner .name {{ font-family: 'Barlow Condensed', sans-serif; font-size: 2.1rem; font-weight: 700; line-height: 1.05; }}
.corner .meta {{ color: #4A5563; font-size: .98rem; margin-top: .2rem; }}
.odds {{ text-align: center; min-width: 220px; }}
.odds .pct {{ font-family: 'Barlow Condensed', sans-serif; font-size: 3.4rem; font-weight: 700; line-height: 1; }}
.odds .vs {{ color: #4A5563; font-size: .95rem; margin: .3rem 0 .7rem; }}
.split {{ display: flex; height: 14px; border-radius: 2px; overflow: hidden; }}
.h2h {{ color: #4A5563; margin: .8rem 0 0; font-size: .98rem; }}
table.rk {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #C9D1DB; }}
table.rk th {{ text-align: left; font-weight: 600; color: #4A5563; padding: .55rem .8rem; border-bottom: 2px solid {NAVY}; }}
table.rk td {{ padding: .5rem .8rem; border-bottom: 1px solid #E4E8EE; }}
table.rk td.num {{ font-family: 'Barlow Condensed', sans-serif; font-size: 1.15rem; font-weight: 600; }}
table.rk td.rank {{ font-family: 'Barlow Condensed', sans-serif; font-size: 1.15rem; color: #4A5563; width: 3rem; }}
.dot {{ display: inline-block; width: 1.25rem; height: 1.25rem; line-height: 1.25rem; margin-right: 3px;
  text-align: center; color: #fff; font-size: .72rem; font-weight: 600; border-radius: 2px; }}
.mix {{ display: flex; height: 30px; border-radius: 2px; overflow: hidden; margin: .4rem 0 .3rem; }}
.mix div {{ color: #fff; font-size: .85rem; padding-left: .5rem; line-height: 30px; white-space: nowrap; overflow: hidden; }}
@media (max-width: 760px) {{ .card {{ grid-template-columns: 1fr; }} .corner.right {{ text-align: left;
  border-right: none; border-left: 8px solid var(--c); padding: 0 0 0 1rem; }} }}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load():
    con = duckdb.connect(str(DB_PATH), read_only=True)
    ratings = con.execute("select * from ratings.elo_current").df()
    history = con.execute("select * from ratings.elo_history").df()
    results = con.execute("select * from marts.results").df()
    con.close()
    return ratings, history, results


@st.cache_resource
def load_model():
    path = ARTIFACTS_DIR / "win_prob.joblib"
    return joblib.load(path) if path.exists() else None


@st.cache_data
def records(results: pd.DataFrame) -> pd.DataFrame:
    r = results.sort_values("match_date")
    long = pd.concat([
        r[["match_date", "winner_id"]].rename(columns={"winner_id": "wrestler_id"}).assign(won=True),
        r[["match_date", "loser_id"]].rename(columns={"loser_id": "wrestler_id"}).assign(won=False),
    ]).sort_values("match_date")
    g = long.groupby("wrestler_id")["won"]
    return pd.DataFrame({"wins": g.sum(), "losses": g.count() - g.sum(),
                         "last5": g.apply(lambda s: list(s.tail(5)))})


ratings, history, results = load()
model = load_model()
ratings = ratings.join(records(results), on="wrestler_id")
using_sample = not any(p for p in RAW_DIR.glob("*.csv") if p.name != "official_rankings.csv")

seasons = f"{int(history.season.min())} to {int(history.season.max())}"
note = '<br><span class="note">Showing synthetic sample data. Real results load from data/raw/.</span>' if using_sample else ""
st.markdown(f"""<div class="masthead"><h1>D1 Wrestling Ratings</h1>
<p>Elo ratings and match predictions from {len(history):,} bouts, {seasons}.{note}</p></div>""",
            unsafe_allow_html=True)

weights = sorted(ratings["current_weight_class"].unique())
weight = st.radio("Weight class", weights, index=weights.index(157) if 157 in weights else 0,
                  horizontal=True, format_func=lambda w: "HWT" if w == 285 else str(w))
field = ratings[ratings["current_weight_class"] == weight].sort_values("rating", ascending=False)
names = field["wrestler_name"].tolist()

st.markdown('<h2 style="margin-top:1rem">Match-up</h2>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
red = c1.selectbox("Red", names, index=0)
green = c2.selectbox("Green", names, index=1 if len(names) > 1 else 0)


def last_form(wid):
    rows = history[(history.wrestler_a_id == wid) | (history.wrestler_b_id == wid)].tail(5)
    wins = ((rows.wrestler_a_id == wid) & rows.a_won) | ((rows.wrestler_b_id == wid) & ~rows.a_won)
    return wins.mean() if len(rows) else 0.5


def corner(row, color, side=""):
    return (f'<div class="corner {side}" style="--c:{color}"><div class="name">{escape(row.wrestler_name)}</div>'
            f'<div class="meta">{escape(row.current_team)}</div>'
            f'<div class="meta">{int(row.wins)}-{int(row.losses)} &nbsp; Rating {row.rating:.0f}</div></div>')


if red == green:
    st.info("Pick two different wrestlers to see a prediction.")
elif model is None:
    st.warning("No trained model found. Run make model, then refresh.")
else:
    a = field[field.wrestler_name == red].iloc[0]
    b = field[field.wrestler_name == green].iloc[0]
    meet = history[((history.wrestler_a_id == a.wrestler_id) & (history.wrestler_b_id == b.wrestler_id)) |
                   ((history.wrestler_a_id == b.wrestler_id) & (history.wrestler_b_id == a.wrestler_id))]
    a_wins = int((((meet.wrestler_a_id == a.wrestler_id) & meet.a_won) |
                  ((meet.wrestler_b_id == a.wrestler_id) & ~meet.a_won)).sum())
    b_wins = len(meet) - a_wins
    x = pd.DataFrame([{"rating_diff": a.rating - b.rating,
                       "form_diff": last_form(a.wrestler_id) - last_form(b.wrestler_id),
                       "h2h_diff": a_wins - b_wins}])[FEATURES]
    p = float(model.predict_proba(x)[0, 1])
    times = f"{len(meet)} time{'s' if len(meet) != 1 else ''}"
    if not len(meet):
        h2h = "They haven't wrestled each other."
    elif a_wins > b_wins:
        h2h = f"They've wrestled {times}. {red.split()[-1]} leads {a_wins}-{b_wins}."
    elif b_wins > a_wins:
        h2h = f"They've wrestled {times}. {green.split()[-1]} leads {b_wins}-{a_wins}."
    else:
        h2h = f"They've split {times}, {a_wins}-{b_wins}."
    st.markdown(f"""<div class="card">{corner(a, RED)}
<div class="odds"><div class="pct"><span style="color:{RED}">{p:.0%}</span> <span style="color:#C9D1DB">/</span> <span style="color:{GREEN}">{1-p:.0%}</span></div>
<div class="vs">Win probability</div>
<div class="split"><div style="width:{p*100:.1f}%;background:{RED}"></div><div style="width:{(1-p)*100:.1f}%;background:{GREEN}"></div></div>
<div class="h2h">{escape(h2h)}</div></div>
{corner(b, GREEN, "right")}</div>""", unsafe_allow_html=True)

label = "HWT" if weight == 285 else f"{weight} lbs"
st.markdown(f'<h2 style="margin-top:2.2rem">Top 20 at {label}</h2>', unsafe_allow_html=True)


def dots(last5):
    if not isinstance(last5, list):
        return ""
    return "".join(f'<span class="dot" style="background:{GREEN if w else RED}">{"W" if w else "L"}</span>'
                   for w in last5)


rows_html = "".join(
    f'<tr><td class="rank">{i}</td><td>{escape(r.wrestler_name)}</td><td>{escape(r.current_team)}</td>'
    f'<td class="num">{r.rating:.0f}</td><td>{int(r.wins)}-{int(r.losses)}</td><td>{dots(r.last5)}</td></tr>'
    for i, r in enumerate(field.head(20).itertuples(), 1))
st.markdown(f"""<table class="rk"><thead><tr><th></th><th>Wrestler</th><th>Team</th><th>Rating</th>
<th>Record</th><th>Last 5</th></tr></thead><tbody>{rows_html}</tbody></table>""", unsafe_allow_html=True)

bouts = results[(results.weight_class == weight) & ~results.is_forfeit]
mix = bouts["result_type"].value_counts(normalize=True)
parts = [("DEC", "Decision", "#5B6B82"), ("MD", "Major", NAVY), ("TF", "Tech fall", GREEN), ("FALL", "Fall", RED)]
bar = "".join(f'<div style="width:{mix.get(k, 0)*100:.1f}%;background:{c}">{n} {mix.get(k, 0):.0%}</div>'
              for k, n, c in parts if mix.get(k, 0) > 0)
st.markdown(f"""<h2 style="margin-top:2.2rem">How bouts end at {label}</h2>
<div class="mix">{bar}</div><p style="color:#4A5563">{len(bouts):,} bouts, forfeits excluded.</p>""",
            unsafe_allow_html=True)
