"""Parse NCAA Championship result PDFs into the standard match CSV format.

Step 1, look at the raw text so you can see the format:
    python -m ingest.parse_ncaa_pdf dump data/raw/pdfs/2025_ncaa.pdf

Step 2, parse every PDF in data/raw/pdfs/ into data/raw/ncaa_<season>.csv:
    python -m ingest.parse_ncaa_pdf parse

Name each PDF by season, like 2025_ncaa.pdf, so the season is known.
Lines that don't match a result pattern are skipped and counted.
"""
import re
import sys
from pathlib import Path

import pandas as pd

from config import RAW_DIR

PDF_DIR = RAW_DIR / "pdfs"

RESULT = re.compile(
    r"^(?:(?P<round>[^()]+?)\s+-\s+)?(?P<winner>[A-Z][\w.'\- ]+?)\s+\((?P<w_team>[^)]+)\)\s*(?:\d+-\d+\s+)?"
    r"won\s+(?:by\s+|in\s+)?(?P<how>[\w\- ]+?)\s+over\s+"
    r"(?P<loser>[A-Z][\w.'\- ]+?)\s+\((?P<l_team>[^)]+)\)\s*(?:\d+-\d+\s+)?"
    r"\((?P<code>[A-Za-z.\-]+(?:\s?-\s?\d+)?)\s*(?P<detail>[^)]*)\)"
)
WEIGHT_HEADER = re.compile(r"\b(125|133|141|149|157|165|174|184|197|285|HWT)\b")

CODE_MAP = {
    "DEC": "DEC", "SV": "DEC", "TB": "DEC", "UTB": "DEC",
    "MD": "MD", "TF": "TF", "FALL": "FALL",
    "FOR": "FOR", "FF": "FOR", "MFF": "FOR", "M FOR": "FOR",
    "INJ": "INJ", "DQ": "DQ",
}


def normalize_code(code: str) -> str:
    c = code.upper().replace(".", "").strip()
    c = re.sub(r"-?\s*\d+$", "", c).strip()
    return CODE_MAP.get(c, CODE_MAP.get(c.split()[0] if c else "", "DEC"))


def parse_score(detail: str):
    m = re.search(r"(\d+)-(\d+)", detail or "")
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def parse_text(text: str, season: int, event: str = "NCAA Championships"):
    rows, skipped = [], 0
    weight = None
    for raw in text.splitlines():
        line = " ".join(raw.split())
        if not line:
            continue
        m = RESULT.match(line)
        if not m:
            header = WEIGHT_HEADER.search(line)
            if header and len(line) < 40:
                weight = 285 if header.group(1) == "HWT" else int(header.group(1))
            elif " over " in line:
                skipped += 1
            continue
        sw, sl = parse_score(m.group("detail"))
        rows.append({
            "season": season, "match_date": f"{season}-03-20", "event": event,
            "event_type": "tournament", "weight_class": weight,
            "wrestler_a": m.group("winner").strip(), "team_a": m.group("w_team").strip(),
            "wrestler_b": m.group("loser").strip(), "team_b": m.group("l_team").strip(),
            "winner": m.group("winner").strip(), "result_type": normalize_code(m.group("code")),
            "score_a": sw, "score_b": sl,
        })
    return rows, skipped


def pdf_text(path: Path) -> str:
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def dump(path: str, lines: int = 80):
    print("\n".join(pdf_text(Path(path)).splitlines()[:lines]))


def parse_all():
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found. Put files like 2025_ncaa.pdf in {PDF_DIR}")
        return
    for path in pdfs:
        season = int(re.match(r"(\d{4})", path.stem).group(1))
        rows, skipped = parse_text(pdf_text(path), season)
        out = RAW_DIR / f"ncaa_{season}.csv"
        pd.DataFrame(rows).to_csv(out, index=False)
        missing = sum(r["weight_class"] is None for r in rows)
        print(f"{path.name}: {len(rows)} matches parsed, {skipped} lines skipped, "
              f"{missing} missing weight class -> {out.name}")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "dump":
        dump(sys.argv[2])
    elif len(sys.argv) >= 2 and sys.argv[1] == "parse":
        parse_all()
    else:
        print(__doc__)
