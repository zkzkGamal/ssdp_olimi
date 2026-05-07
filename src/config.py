import yaml
from pathlib import Path
from dataclasses import dataclass
import logging

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Config:
    def __init__(self, config_path="configs/default.yaml"):
        config_path = Path(config_path)
        if not config_path.exists():
            logger.error("Configuration file not found: %s", config_path)
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, encoding="utf-8") as f:
                self.cfg = yaml.safe_load(f) or {}
        except yaml.YAMLError as exc:
            logger.error("Failed to parse YAML config at %s: %s", config_path, exc)
            raise
        except Exception as exc:
            logger.error("Unable to load configuration from %s: %s", config_path, exc)
            raise

        logger.info("Configuration loaded from %s", config_path)

    @property
    def output_dir(self):
        return Path(self.cfg["paths"]["output_dir"])

    @property
    def audio_dir(self):
        return self.output_dir / "audio"
