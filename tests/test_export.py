import json
import tempfile
import unittest
from pathlib import Path

from src.export import ReviewedDatasetExporter


class TestReviewedDatasetExporter(unittest.TestCase):
    def test_export_filters_and_writes(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            reviewed_path = tmp_path / "reviewed_manifest.jsonl"
            records = [
                {
                    "id": "eg_0000",
                    "text": "مرحبا",
                    "audio_path": "data/processed/audio/eg_0000.wav",
                    "quality": 5,
                    "review_notes": "good",
                    "duration": 2.4,
                    "sample_rate": 24000,
                    "reviewed_at": "2026-05-07 00:00:00",
                },
                {
                    "id": "eg_0001",
                    "text": "ازيك",
                    "audio_path": "data/processed/audio/eg_0001.wav",
                    "quality": 2,
                    "review_notes": "bad",
                    "duration": 2.1,
                    "sample_rate": 24000,
                    "reviewed_at": "2026-05-07 00:01:00",
                },
            ]
            with open(reviewed_path, "w", encoding="utf-8") as f:
                for record in records:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")

            exporter = ReviewedDatasetExporter(str(reviewed_path))
            result = exporter.export(min_quality_score=3)

            self.assertEqual(result["count"], 1)
            jsonl_file = Path(result["jsonl_path"])
            tsv_file = Path(result["tsv_path"])
            self.assertTrue(jsonl_file.exists())
            self.assertTrue(tsv_file.exists())

            with open(jsonl_file, encoding="utf-8") as f:
                lines = [json.loads(line) for line in f if line.strip()]
            self.assertEqual(len(lines), 1)
            self.assertEqual(lines[0]["id"], "eg_0000")

            with open(tsv_file, encoding="utf-8") as f:
                rows = [line.strip().split("\t") for line in f if line.strip()]
            self.assertEqual(rows[0], ["audio_path", "text"])
            self.assertEqual(rows[1][0], "data/processed/audio/eg_0000.wav")
            self.assertEqual(rows[1][1], "مرحبا")


if __name__ == "__main__":
    unittest.main()
