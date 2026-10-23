# Roadmap

## Phase 1: Data (2 to 3 weeks)
- [ ] Pick a source and check its terms of service and robots.txt
- [ ] Record the source in data/README.md
- [ ] Collect NCAA D1 dual and tournament results for 3 to 5 seasons
- [ ] Save CSVs to data/raw/ in the standard format
- [ ] Load into DuckDB with `make ingest`

## Phase 2: Clean and model (1 to 2 weeks)
- [ ] Add name variations to dbt/seeds/name_aliases.csv
- [ ] Confirm weight class changes show up in marts.wrestlers
- [ ] Make sure forfeits are flagged
- [ ] All dbt tests pass

## Phase 3: Ratings (2 weeks)
- [ ] Tune K and season regression
- [ ] Load official rankings
- [ ] Find the biggest disagreements and write them up

## Phase 4: Win probability (2 to 3 weeks)
- [ ] Hold out the latest season
- [ ] Beat the Elo-only baseline (or explain why not)
- [ ] Check calibration plot

## Phase 5: Dashboard and writeup
- [ ] Deploy to Streamlit Community Cloud
- [ ] Add screenshot to README
- [ ] Finish reports/findings.md
- [ ] Post about it on LinkedIn
