"""Phase 1: load match CSVs into DuckDB as raw.matches and raw.official_rankings.

Uses data/raw/ if it has CSVs, otherwise falls back to data/sample/.
Run: python -m ingest.load_csv
"""
import duckdb

from config import DB_PATH, RAW_DIR, SAMPLE_DIR


def pick_source():
    real = [p for p in RAW_DIR.glob("*.csv") if p.name != "official_rankings.csv"]
    if real:
        return str(RAW_DIR / "*.csv"), RAW_DIR / "official_rankings.csv", "raw"
    return (str(SAMPLE_DIR / "matches_sample.csv"),
            SAMPLE_DIR / "official_rankings_sample.csv", "sample")


def main():
    matches_glob, rankings_path, label = pick_source()
    con = duckdb.connect(str(DB_PATH))
    con.execute("create schema if not exists raw")
    con.execute(f"""
        create or replace table raw.matches as
        select * from read_csv_auto('{matches_glob}', union_by_name = true)
    """)
    if rankings_path.exists():
        con.execute(f"""
            create or replace table raw.official_rankings as
            select * from read_csv_auto('{rankings_path}')
        """)
    n = con.execute("select count(*) from raw.matches").fetchone()[0]
    print(f"Loaded {n} matches from {label} data into {DB_PATH}")
    con.close()


if __name__ == "__main__":
    main()
