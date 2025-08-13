# src/consolidate.py

"""
Consolidates transcription JSONs into a CSV per year.

"""

import json
from pathlib import Path
import pandas as pd


def consolidate_json_to_csv(year, transcription_dir_pattern, csv_output_dir):
    in_dir = Path(transcription_dir_pattern.format(year=year))
    out_dir = Path(csv_output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{year}_consolidated.csv"

    files = sorted(in_dir.glob("*.json"))
    print(f"Consolidating {len(files)} JSON files for {year}: {out_path}")

    records = []

    for file in files:
        parts = file.stem.split("_")
        yymmdd, issue, number = parts[0], parts[2], parts[3]
        meta = {
            "date": f"{year}-{yymmdd[2:4]}-{yymmdd[4:6]}",
            "issue": issue,
            "number": number,
        }

        try:
            raw = file.read_text(encoding="utf-8").strip()
            data = json.loads(raw)
            translation = data.get("english_translation", "N/A")

        # the tables of contents contain "....." patterns, where the model often gets stuck infinitely
        # sometimes this results in parse errors
        except json.JSONDecodeError as e:
            print(f"Skip {file.name}: JSON parse error: {e}")
            continue

        records.append(
            {
                "date": meta["date"],
                "issue": meta["issue"],
                "number": meta["number"],
                "translation": translation,
            }
        )

    df = pd.DataFrame.from_records(
        records, columns=["date", "issue", "number", "translation"]
    )

    # tends to get laggy for 1960 and later since ~1.5k issues are published per year
    # most searchable format for now
    df.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"Finished consolidating year {year}")
