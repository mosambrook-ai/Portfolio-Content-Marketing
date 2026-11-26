"""Refresh the keyword data from the original workbook (requires openpyxl)."""

import json
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "assets/downloads/Cold_Feet_Editions_Keyword_Map.xlsx"
SHEETS = {
    "Keyword database": ("keywords", "term cluster volume difficulty intent cpc source page role priority"),
    "Keyword mapping": ("mapping", "cluster page status primary supporting destination priority rationale"),
    "Content opportunities": ("opportunities", "page keyword title format links priority"),
    "SEO action plan": ("actions", "order action implementation priority status measure"),
}


def main():
    workbook = load_workbook(WORKBOOK, data_only=True, read_only=True)
    data = {}
    for sheet, (key, fields) in SHEETS.items():
        data[key] = [
            dict(zip(fields.split(), row))
            for row in workbook[sheet].iter_rows(min_row=5, values_only=True)
            if row[0] is not None
        ]
    terms = data["keywords"]
    known = [term["difficulty"] for term in terms if term["difficulty"] is not None]
    summary = dict(workbook["Executive summary"].iter_rows(min_row=5, max_col=2, values_only=True))
    assert len({term["term"] for term in terms}) == summary["Recovered keywords"]
    assert sum(term["volume"] for term in terms if term["volume"] is not None) == summary["Combined monthly volume"]
    assert len(known) == summary["Known difficulty scores"]
    assert abs(sum(known) / len(known) - summary["Mean known KD"]) < 1e-10
    (ROOT / "_data/keyword-research.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
