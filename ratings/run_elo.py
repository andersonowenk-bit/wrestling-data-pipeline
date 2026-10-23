"""Run Elo over every non-forfeit match in date order.

Writes two tables to DuckDB:
  ratings.elo_history  pre-match ratings for every bout (used for modeling)
  ratings.elo_current  latest rating for every wrestler
Run: python -m ratings.run_elo
"""
import duckdb
import pandas as pd

from config import DB_PATH, ELO_BASE, ELO_K, ELO_SEASON_REGRESSION
from ratings.elo import EloSystem


def compute(results: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    elo = EloSystem(k=ELO_K, base=ELO_BASE)
    history = []
    season = None
    for row in results.itertuples(index=False):
        if season is not None and row.season != season:
            elo.new_season(ELO_SEASON_REGRESSION)
        season = row.season
        ra, rb = elo.get(row.wrestler_a_id), elo.get(row.wrestler_b_id)
        elo.update(row.winner_id, row.loser_id, row.result_type)
        history.append({
            "match_id": row.match_id, "season": row.season, "match_date": row.match_date,
            "weight_class": row.weight_class, "wrestler_a_id": row.wrestler_a_id,
            "wrestler_b_id": row.wrestler_b_id, "rating_a_pre": ra, "rating_b_pre": rb,
            "a_won": bool(row.a_won), "result_type": row.result_type,
        })
    return pd.DataFrame(history), elo.ratings


def main():
    con = duckdb.connect(str(DB_PATH))
    results = con.execute("""
        select * from marts.results
        where not is_forfeit
        order by match_date, match_id
    """).df()
    history, current = compute(results)
    current_df = pd.DataFrame({"wrestler_id": list(current), "rating": list(current.values())})

    con.execute("create schema if not exists ratings")
    con.register("history_df", history)
    con.register("current_df", current_df)
    con.execute("create or replace table ratings.elo_history as select * from history_df")
    con.execute("""
        create or replace table ratings.elo_current as
        select w.wrestler_id, w.wrestler_name, w.current_team, w.current_weight_class,
               w.matches_wrestled, round(c.rating, 1) as rating
        from current_df c join marts.wrestlers w using (wrestler_id)
        order by rating desc
    """)
    print(f"Rated {len(current_df)} wrestlers across {len(history)} matches")
    con.close()


if __name__ == "__main__":
    main()
