from src.config import Config
from src.export import ReviewedDatasetExporter
from pathlib import Path
import logging
import argparse

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export reviewed samples to training-ready dataset files.")
    parser.add_argument(
        "--reviewed",
        default="data/processed/reviewed_manifest.jsonl",
        help="Path to the reviewed manifest JSONL file.",
    )
    parser.add_argument(
        "--min-quality",
        type=int,
        default=None,
        help="Minimum quality score to include in the export.",
    )
    args = parser.parse_args()

    config = Config()
    min_quality = args.min_quality
    if min_quality is None:
        min_quality = config.cfg.get("review", {}).get("min_quality_score", 3)

    exporter = ReviewedDatasetExporter(reviewed_manifest_path=args.reviewed)
    result = exporter.export(min_quality_score=min_quality)

    logger.info("Training-ready export complete: %s", result)
    logger.info("Use the TSV file for read-along STT pipelines or the JSONL file for richer metadata.")
