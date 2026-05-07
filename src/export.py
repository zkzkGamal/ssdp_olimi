import json
import logging
from pathlib import Path
from typing import List

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class ReviewedDatasetExporter:
    def __init__(self, reviewed_manifest_path: str = "data/processed/reviewed_manifest.jsonl"):
        self.reviewed_manifest_path = Path(reviewed_manifest_path)
        self.output_dir = self.reviewed_manifest_path.parent
        self.training_jsonl_path = self.output_dir / "training_manifest.jsonl"
        self.training_tsv_path = self.output_dir / "training_manifest.tsv"

    def load_reviews(self) -> List[dict]:
        if not self.reviewed_manifest_path.exists():
            logger.error("Reviewed manifest not found: %s", self.reviewed_manifest_path)
            raise FileNotFoundError(f"Reviewed manifest not found: {self.reviewed_manifest_path}")

        reviews = []
        with open(self.reviewed_manifest_path, encoding="utf-8") as f:
            for line_number, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    reviews.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    logger.warning(
                        "Skipping invalid JSON at %s:%s: %s",
                        self.reviewed_manifest_path,
                        line_number,
                        exc,
                    )
        logger.info("Loaded %d reviewed samples.", len(reviews))
        return reviews

    def normalize_audio_path(self, audio_path: str) -> str:
        path = Path(audio_path)
        if path.is_absolute():
            return str(path)

        candidates = [
            path,
            self.reviewed_manifest_path.parent / path,
            Path("data") / path,
            Path("data") / self.reviewed_manifest_path.parent.name / path.name,
        ]

        for candidate in candidates:
            if candidate.exists():
                return str(candidate)

        logger.warning("Could not normalize audio path %r. Falling back to %s", audio_path, candidates[-1])
        return str(candidates[-1])

    def filter_reviews(self, reviews: List[dict], min_quality_score: int = 3) -> List[dict]:
        filtered = [
            r for r in reviews
            if isinstance(r.get("quality"), int) and r.get("quality", 0) >= min_quality_score
        ]
        logger.info("Filtered %d / %d samples with quality >= %d.", len(filtered), len(reviews), min_quality_score)
        return filtered

    def export_to_jsonl(self, reviews: List[dict]) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        training_records = []
        for review in reviews:
            training_records.append({
                "id": review.get("id"),
                "audio_path": self.normalize_audio_path(review.get("audio_path", "")),
                "text": review.get("text", ""),
                "duration": review.get("duration"),
                "sample_rate": review.get("sample_rate"),
                "quality": review.get("quality"),
                "review_notes": review.get("review_notes", ""),
                "reviewed_at": review.get("reviewed_at"),
            })

        with open(self.training_jsonl_path, "w", encoding="utf-8") as f:
            for record in training_records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        logger.info("Exported %d records to %s", len(training_records), self.training_jsonl_path)
        return self.training_jsonl_path

    def export_to_tsv(self, reviews: List[dict]) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(self.training_tsv_path, "w", encoding="utf-8") as f:
            f.write("audio_path\ttext\n")
            for review in reviews:
                audio_path = self.normalize_audio_path(review.get("audio_path", ""))
                text = review.get("text", "" ).replace("\t", " ").replace("\n", " ")
                f.write(f"{audio_path}\t{text}\n")

        logger.info("Exported %d records to %s", len(reviews), self.training_tsv_path)
        return self.training_tsv_path

    def export(self, min_quality_score: int = 3) -> dict:
        reviews = self.load_reviews()
        filtered_reviews = self.filter_reviews(reviews, min_quality_score)
        jsonl_path = self.export_to_jsonl(filtered_reviews)
        tsv_path = self.export_to_tsv(filtered_reviews)
        return {
            "jsonl_path": jsonl_path,
            "tsv_path": tsv_path,
            "count": len(filtered_reviews),
        }
