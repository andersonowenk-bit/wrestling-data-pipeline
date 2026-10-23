"""Template for collecting results from a public website.

BEFORE USING: read the site's terms of service and robots.txt. If either
forbids automated collection, do not scrape it. Find another source or
enter the data by hand. Record what you checked in data/README.md.

Output: one CSV per event in data/raw/ matching the format in data/README.md.
"""
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

from config import RAW_DIR

HEADERS = {"User-Agent": "wrestling-data-pipeline (student project; contact: your-email)"}
DELAY_SECONDS = 3  # be polite: never hammer a site


def fetch(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    time.sleep(DELAY_SECONDS)
    return resp.text


def parse_results(html: str) -> list[dict]:
    """Turn one results page into rows. Customize for your source."""
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    # TODO: find the table or list of bouts and fill in each field below
    # for bout in soup.select("..."):
    #     rows.append({"season": ..., "match_date": ..., "event": ..., "event_type": ...,
    #                  "weight_class": ..., "wrestler_a": ..., "team_a": ...,
    #                  "wrestler_b": ..., "team_b": ..., "winner": ...,
    #                  "result_type": ..., "score_a": ..., "score_b": ...})
    return rows


def save(rows: list[dict], name: str) -> Path:
    path = RAW_DIR / f"{name}.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


if __name__ == "__main__":
    raise SystemExit("Fill in parse_results() for your source first.")
