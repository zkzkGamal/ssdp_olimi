import torch
import soundfile as sf
from pathlib import Path
import json
import time
from tqdm import tqdm
from huggingface_hub import snapshot_download

from tts_model.chatterbox.mtl_tts import ChatterboxMultilingualTTS, SUPPORTED_LANGUAGES

from src.config import Config
import logging

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class EgyptianTTSPipeline:
    def __init__(self, config: Config = None):
        self.config = config or Config()

        self.output_dir = self.config.output_dir
        self.audio_dir = self.config.audio_dir
        self.audio_dir.mkdir(parents=True, exist_ok=True)

        self.manifest_path = self.output_dir / "manifest.jsonl"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None

        logger.info("Pipeline initialized. Output directory: %s", self.output_dir)
        logger.info("Device: %s", self.device)

    def load_model(self):
        if self.model is not None:
            return

        logger.info("Downloading and loading Chatterbox Egyptian model (%s)...", self.config.cfg.get("tts", {}).get("model_id", "oddadmix/chatterbox-egyptian-v0"))
        try:
            ckpt_dir = snapshot_download(
                repo_id=self.config.cfg.get("tts", {}).get("model_id", "oddadmix/chatterbox-egyptian-v0"),
                repo_type="model",
                revision="main",
            )
        except Exception as exc:
            logger.error("Failed to download model checkpoint: %s", exc, exc_info=True)
            raise

        try:
            self.model = ChatterboxMultilingualTTS.from_checkpoint(str(ckpt_dir) + "/", self.device)
            if hasattr(self.model, "to"):
                self.model.to(self.device)
        except Exception as exc:
            logger.error("Failed to initialize model from checkpoint %s: %s", ckpt_dir, exc, exc_info=True)
            raise

        logger.info("✅ Model loaded successfully on %s", self.device)
        logger.info("Supported languages: %s", SUPPORTED_LANGUAGES if "SUPPORTED_LANGUAGES" in globals() else "Unknown")

    def synthesize(self, text: str, sample_id: str, speaker_id: str = "speaker_01"):
        """Synthesize one sample"""
        if not text or not text.strip():
            logger.error("Cannot synthesize empty text for sample_id: %s", sample_id)
            raise ValueError("Prompt text cannot be empty.")

        self.load_model()

        try:
            wav = self.model.generate(
                text=text,
                language_id=self.config.cfg.get("tts", {}).get("language", "ar"),
                exaggeration=self.config.cfg.get("tts", {}).get("exaggeration", 0.65),
                cfg_weight=self.config.cfg.get("tts", {}).get("cfg_weight", 0.7),
                temperature=self.config.cfg.get("tts", {}).get("temperature", 0.85),
            )
        except Exception as exc:
            logger.error("Generation failed for sample %s: %s", sample_id, exc, exc_info=True)
            raise

        audio_path = self.audio_dir / f"{sample_id}.wav"
        try:
            audio_np = wav.squeeze().cpu().numpy()
            sr = getattr(self.model, "sr", 24000)
            sf.write(str(audio_path), audio_np, sr)
        except Exception as exc:
            logger.error("Failed to save audio for sample %s at %s: %s", sample_id, audio_path, exc, exc_info=True)
            raise

        return {
            "id": sample_id,
            "text": text,
            "audio_path": str(audio_path.relative_to(self.output_dir.parent)),
            "speaker_id": speaker_id,
            "duration": len(audio_np) / sr,
            "sample_rate": sr,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model_used": self.config.cfg.get("tts", {}).get("model_id", "oddadmix/chatterbox-egyptian-v0"),
        }

    def load_existing_ids(self) -> set:
        if not self.manifest_path.exists():
            return set()

        existing_ids = set()
        try:
            with open(self.manifest_path, encoding="utf-8") as f:
                for line_number, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                    try:
                        existing_ids.add(json.loads(line)["id"])
                    except (json.JSONDecodeError, KeyError) as exc:
                        logger.warning(
                            "Skipping invalid manifest entry at %s:%s: %s",
                            self.manifest_path,
                            line_number,
                            exc,
                        )
        except Exception as exc:
            logger.error("Failed to read existing manifest %s: %s", self.manifest_path, exc, exc_info=True)
        return existing_ids

    def run_batch(self, prompts: list):
        """Run synthesis on all prompts with resumability"""
        existing = self.load_existing_ids()
        new_count = 0

        for i, text in tqdm(enumerate(prompts), total=len(prompts), desc="Synthesizing"):
            sample_id = f"eg_{i:04d}"
            if sample_id in existing:
                continue

            try:
                entry = self.synthesize(text, sample_id)
                self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.manifest_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                new_count += 1
                if new_count % 10 == 0:
                    time.sleep(0.5)
            except Exception as exc:
                logger.error("❌ Error on %s: %s", sample_id, exc, exc_info=True)
                time.sleep(3)

        logger.info("✅ Synthesis completed! Generated %d new samples.", new_count)
