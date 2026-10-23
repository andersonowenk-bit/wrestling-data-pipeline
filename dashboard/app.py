"""Team rankings dashboard. Run: streamlit run dashboard/app.py"""
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import streamlit as st

from teams.data import load_duals
from teams.rank import build_table, movement, run_elo

st.set_page_config(page_title="D1 Wrestling Team Rankings", layout="wide")
RED, GREEN, NAVY = "#C8102E", "#00843D", "#14284B"

st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Barlow:wght@400;500;600&display=swap');
html, body, [class*="css"], .stMarkdown, p, td, th, label {{ font-family: 'Barlow', sans-serif; }}
#MainMenu, footer, header [data-testid="stToolbar"] {{ visibility: hidden; }}
.block-container {{ padding-top: 1.5rem; max-width: 1000px; }}
h1, h2 {{ font-family: 'Barlow Condensed', sans-serif; }}
.masthead {{ background: {NAVY}; color: #fff; padding: 1.4rem 1.6rem 1.2rem; border-radius: 4px;
  border-bottom: 6px solid {RED}; box-shadow: inset 0 -6px 0 {GREEN}; margin-bottom: 1.8rem; }}
.masthead h1 {{ color: #fff; font-size: 2.6rem; font-weight: 700; margin: 0; line-height: 1; padding: 0; }}
.masthead p {{ color: #C9D1DB; margin: .45rem 0 0; }}
.card {{ display: grid; grid-template-columns: 1fr auto 1fr; gap: 1.5rem; align-items: center;
  background: #fff; border: 1px solid #C9D1DB; border-radius: 4px; padding: 1.5rem; }}
.side {{ border-left: 8px solid var(--c); padding-left: 1rem; }}
.side.right {{ border-left: none; border-right: 8px solid var(--c); padding: 0 1rem 0 0; text-align: right; }}
.side .name {{ font-family: 'Barlow Condensed', sans-serif; font-size: 2.1rem; font-weight: 700; line-height: 1.05; }}
.side .meta {{ color: #4A5563; margin-top: .2rem; }}
.odds {{ text-align: center; min-width: 220px; }}
.odds .pct {{ font-family: 'Barlow Condensed', sans-serif; font-size: 3.4rem; font-weight: 700; line-height: 1; }}
.odds .sub {{ color: #4A5563; margin: .3rem 0 .7rem; }}
.split {{ display: flex; height: 14px; border-radius: 2px; overflow: hidden; }}
table.rk {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #C9D1DB; }}
table.rk th {{ text-align: left; font-weight: 600; color: #4A5563; padding: .55rem .8rem; border-bottom: 2px solid {NAVY}; }}
table.rk td {{ padding: .5rem .8rem; border-bottom: 1px solid #E4E8EE; }}
table.rk td.big {{ font-family: 'Barlow Condensed', sans-serif; font-size: 1.15rem; font-weight: 600; }}
.dot {{ display: inline-block; width: 1.25rem; height: 1.25rem; line-height: 1.25rem; margin-right: 3px;
  text-align: center; color: #fff; font-size: .72rem; font-weight: 600; border-radius: 2px; }}
.up {{ color: {GREEN}; }} .down {{ color: {RED}; }} .flat {{ color: #8A94A3; }}
@media (max-width: 760px) {{ .card {{ grid-template-columns: 1fr; }} .side.right {{ text-align: left;
  border-right: none; border-left: 8px solid var(--c); padding: 0 0 0 1rem; }} }}
</style>""", unsafe_allow_html=True)

duals = load_duals()
table, history = build_table(duals)
if table.empty:
    st.info("Nothing to rank yet. Save a WrestleStat snapshot or add a dual, then refresh.")
    st.stop()
elo, _ = run_elo(duals)

season = history.season.max()
played = int((duals.season == season).sum()) if len(duals) else 0
updated = history.date.max().strftime("%B %-d, %Y")
st.markdown(f"""<div class="masthead"><h1>D1 Wrestling Team Rankings</h1>
<p>{season} season. {played} D1 duals rated so far, updated {updated}.</p></div>""", unsafe_allow_html=True)

st.markdown("<h2>Predict a dual</h2>", unsafe_allow_html=True)
teams = table.team.tolist()
c1, c2, c3 = st.columns([2, 2, 1.4])
first = c1.selectbox("Team", teams, index=teams.index("Sacred Heart") if "Sacred Heart" in teams else 0)
second = c2.selectbox("Opponent", teams, index=teams.index("Hofstra") if "Hofstra" in teams else 1)
site = c3.selectbox("Where", [f"At {second}", f"At {first}", "Neutral"])
home = second if site == f"At {second}" else first if site == f"At {first}" else None


def side(team, color, cls=""):
    r = table.set_index("team").loc[team]
    return (f'<div class="side {cls}" style="--c:{color}"><div class="name">{escape(team)}</div>'
            f'<div class="meta">No. {r["rank"]} &nbsp; Rating {r.rating}</div>'
            f'<div class="meta">{r.wins}-{r.losses} this season</div></div>')


if first == second:
    st.info("Pick two different teams.")
else:
    p = elo.win_probability(first, second, home)
    where = f"at {home}" if home else "on a neutral mat"
    st.markdown(f"""<div class="card">{side(first, RED)}
<div class="odds"><div class="pct"><span style="color:{RED}">{p:.0%}</span> <span style="color:#C9D1DB">/</span> <span style="color:{GREEN}">{1-p:.0%}</span></div>
<div class="sub">Win probability {where}</div>
<div class="split"><div style="width:{p*100:.1f}%;background:{RED}"></div><div style="width:{(1-p)*100:.1f}%;background:{GREEN}"></div></div></div>
{side(second, GREEN, "right")}</div>""", unsafe_allow_html=True)

st.markdown('<h2 style="margin-top:2.2rem">Rankings</h2>', unsafe_allow_html=True)


def dots(s):
    return "".join(f'<span class="dot" style="background:{GREEN if c == "W" else RED}">{c}</span>' for c in s)


def move(r):
    m = movement(r)
    cls = "up" if m.startswith("up") else "down" if m.startswith("down") else "flat"
    return f'<span class="{cls}">{m}</span>'


rows = "".join(f'<tr><td class="big">{r["rank"]}</td><td>{escape(r.team)}</td><td class="big">{r.rating}</td>'
               f'<td>{r.wins}-{r.losses}</td><td>{dots(r.last5)}</td><td>{move(r)}</td>'
               f'<td>{"" if pd.isna(r.wrestlestat) else int(r.wrestlestat)}</td></tr>'
               for _, r in table.iterrows())
st.markdown(f"""<table class="rk"><thead><tr><th>Rank</th><th>Team</th><th>Rating</th><th>Record</th>
<th>Last 5</th><th>This week</th><th>WrestleStat</th></tr></thead><tbody>{rows}</tbody></table>""", unsafe_allow_html=True)

st.markdown('<h2 style="margin-top:2.2rem">Rating over time</h2>', unsafe_allow_html=True)
pick = st.multiselect("Teams", teams, default=[t for t in ["Sacred Heart", "Hofstra"] if t in teams])
if pick:
    chart = history[history.team.isin(pick)].pivot_table(index="date", columns="team", values="rating").ffill()
    st.line_chart(chart, color=[RED, GREEN, NAVY, "#5B6B82", "#F2C94C"][:len(pick)])
