from src.synthesizer import EgyptianTTSPipeline
from src.config import Config
from pathlib import Path

import logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("🚀 Starting Egyptian Synthetic Speech Pipeline (S.S.D.P.)\n")
    
    config = Config()
    pipeline = EgyptianTTSPipeline(config)
    
    prompts_path = Path(config.cfg["paths"]["prompts"])
    
    if not prompts_path.exists():
        logger.info(f"❌ Prompts file not found: {prompts_path}")
        logger.info("Please put your prompts in data/raw/prompts.txt")
        exit(1)
    
    with open(prompts_path, encoding="utf-8") as f:
        prompts = [line.strip() for line in f if line.strip()]
    
    logger.info(f"Loaded {len(prompts)} Egyptian Arabic prompts.")
    logger.info(f"Output directory: {config.output_dir}\n")
    
    pipeline.run_batch(prompts)