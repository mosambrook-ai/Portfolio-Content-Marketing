"""Export the ten strategy worksheets to JSON (requires openpyxl)."""

import json
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
SHEETS = {
    "Strategy": ("strategy", "area decision evidence"),
    "Personas": ("personas", "name motivation barrier content channels search share"),
    "Pillars": ("pillars", "name share objective formats example"),
    "Audience matrix": ("matrix", "pillar romantic writer reader gifter"),
    "Journey": ("journey", "stage touchpoint action kpi"),
    "Content concepts": ("concepts", "name channel pillar audience objective cta keyword"),
    "December calendar": ("calendar", "date theme channel concept pillar audience cta keyword status"),
    "Repurposing": ("repurposing", "asset tiktok pinterest journal email product"),
    "Asset tracker": ("assets", "name state action status"),
    "KPI tracker": ("kpis", "period channel metric baseline target actual source action"),
}


def main():
    workbook = load_workbook(ROOT / "assets/downloads/Cold_Feet_Editions_Content_Strategy.xlsx",
                             data_only=True, read_only=True)
    if set(workbook.sheetnames) != SHEETS.keys():
        raise ValueError("The workbook no longer matches the strategy sheet list.")
    data = {}
    for sheet, (key, fields) in SHEETS.items():
        data[key] = [
            dict(zip(fields.split(), (v.date().isoformat() if isinstance(v, datetime) else v for v in row)))
            for row in workbook[sheet].iter_rows(min_row=4, values_only=True)
            if row and row[0] is not None and not str(row[0]).startswith("Scale:")
        ]
    (ROOT / "_data/content-strategy.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
