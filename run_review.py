# run_review.py
from src.reviewer import DatasetReviewer
import logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("🇪🇬 Launching Olimi AI - Synthetic Data Review Tool")
    logger.info("============================================================\n")
    
    reviewer = DatasetReviewer()
    
    if len(reviewer.samples) == 0:
        logger.info("❌ No manifest found. Please run synthesis first.")
        logger.info("   python run_synthesis.py")
    else:
        logger.info(f"✅ Loaded {len(reviewer.samples)} samples for review.\n")
        reviewer.launch()   # This will start Gradio