#!/usr/bin/env python3
"""Public-safe synthetic record validator.

This example is intentionally generic and non-production.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import sys
from pathlib import Path

REQUIRED_FIELDS = {
    "record_id",
    "asset_reference",
    "source_type",
    "observed_at",
    "water_depth_in",
    "quality_status",
    "provenance",
}
ALLOWED_SOURCE_TYPES = {"meter_reading", "staff_report"}
ALLOWED_QUALITY = {"verified", "review_required", "missing_value"}


def parse_iso8601(value: str) -> bool:
    try:
        dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate(path: Path) -> dict:
    issues: list[dict] = []
    seen: set[str] = set()

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing_headers = REQUIRED_FIELDS - set(reader.fieldnames or [])
        if missing_headers:
            return {
                "ok": False,
                "issues": [{"issue": f"Missing headers: {sorted(missing_headers)}"}],
            }
        rows = list(reader)

    for row_number, row in enumerate(rows, start=2):
        record_id = row["record_id"].strip()

        if not record_id:
            issues.append({"row": row_number, "issue": "record_id is required"})
        elif record_id in seen:
            issues.append({
                "row": row_number,
                "record_id": record_id,
                "issue": "duplicate record_id",
            })
        seen.add(record_id)

        if row["source_type"] not in ALLOWED_SOURCE_TYPES:
            issues.append({
                "row": row_number,
                "record_id": record_id,
                "issue": "unsupported source_type",
            })

        if row["quality_status"] not in ALLOWED_QUALITY:
            issues.append({
                "row": row_number,
                "record_id": record_id,
                "issue": "unsupported quality_status",
            })

        if not parse_iso8601(row["observed_at"]):
            issues.append({
                "row": row_number,
                "record_id": record_id,
                "issue": "invalid observed_at timestamp",
            })

        value = row["water_depth_in"].strip()
        if not value:
            issues.append({
                "row": row_number,
                "record_id": record_id,
                "issue": "water_depth_in is missing",
            })
        else:
            try:
                float(value)
            except ValueError:
                issues.append({
                    "row": row_number,
                    "record_id": record_id,
                    "issue": "water_depth_in is not numeric",
                })

    return {
        "ok": not issues,
        "records_checked": len(rows),
        "issues": issues,
        "disclaimer": "Public synthetic example only; not production AGRO-AI logic.",
    }


if __name__ == "__main__":
    default = Path(__file__).resolve().parents[1] / "synthetic-records" / "input.csv"
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    print(json.dumps(validate(csv_path), indent=2))
