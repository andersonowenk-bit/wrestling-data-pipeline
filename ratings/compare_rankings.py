"""Compare Elo rankings to official rankings. Disagreements are the story.

Prints a Spearman correlation per weight class and the biggest gaps, and
saves the full comparison to reports/ranking_comparison.csv.
Run: python -m ratings.compare_rankings
"""
import duckdb
from scipy.stats import spearmanr

from config import DB_PATH, ROOT


def main():
    con = duckdb.connect(str(DB_PATH), read_only=True)
    tables = [t[0] for t in con.execute(
        "select table_name from information_schema.tables where table_schema = 'raw'").fetchall()]
    if "official_rankings" not in tables:
        print("No official rankings loaded. Add data/raw/official_rankings.csv")
        return
    df = con.execute("""
        with elo as (
            select *, row_number() over (partition by current_weight_class order by rating desc) as elo_rank
            from ratings.elo_current
        )
        select o.weight_class, o.wrestler, o.rank as official_rank, e.elo_rank, e.rating
        from raw.official_rankings o
        left join elo e on lower(e.wrestler_name) = lower(o.wrestler)
                       and e.current_weight_class = o.weight_class
        where o.season = (select max(season) from raw.official_rankings)
        order by o.weight_class, o.rank
    """).df()
    con.close()

    df["gap"] = df["elo_rank"] - df["official_rank"]
    print("Spearman correlation (Elo vs official), by weight class:")
    for wc, g in df.dropna().groupby("weight_class"):
        rho, _ = spearmanr(g["official_rank"], g["elo_rank"])
        print(f"  {wc:>3}: {rho:.2f}")
    print("\nBiggest disagreements:")
    print(df.dropna().reindex(df["gap"].abs().sort_values(ascending=False).index)
          .head(10).to_string(index=False))
    out = ROOT / "reports" / "ranking_comparison.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved {out}")


if __name__ == "__main__":
    main()
