from pathlib import Path
import tempfile
import unittest

from check_records import validate


class RecordQualityCheckerTests(unittest.TestCase):
    def test_synthetic_example_flags_missing_value(self) -> None:
        path = Path(__file__).resolve().parents[1] / "synthetic-records" / "input.csv"
        result = validate(path)
        self.assertFalse(result["ok"])
        self.assertEqual(result["records_checked"], 3)
        self.assertTrue(any(
            issue.get("record_id") == "SYN-003"
            and issue.get("issue") == "water_depth_in is missing"
            for issue in result["issues"]
        ))

    def test_valid_record_passes(self) -> None:
        content = (
            "record_id,asset_reference,source_type,observed_at,"
            "water_depth_in,quality_status,provenance\n"
            "SYN-100,FIELD-Z01,meter_reading,2026-07-01T08:00:00Z,"
            "0.20,verified,synthetic\n"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as handle:
            handle.write(content)
            path = Path(handle.name)
        try:
            result = validate(path)
            self.assertTrue(result["ok"])
            self.assertEqual(result["issues"], [])
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
