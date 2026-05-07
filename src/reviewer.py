# src/reviewer.py
import gradio as gr
import json
from pathlib import Path
import logging
import time

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class DatasetReviewer:
    def __init__(self, manifest_path="data/processed/manifest.jsonl"):
        self.manifest_path = Path(manifest_path)
        self.reviewed_path = self.manifest_path.parent / "reviewed_manifest.jsonl"
        self.samples = self.load_samples()
        self.current_idx = 0

    def load_samples(self):
        if not self.manifest_path.exists():
            logger.warning("Manifest file does not exist: %s", self.manifest_path)
            return []

        samples = []
        try:
            with open(self.manifest_path, encoding="utf-8") as f:
                for line_number, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                    try:
                        samples.append(json.loads(line))
                    except json.JSONDecodeError as exc:
                        logger.warning(
                            "Skipping invalid JSON at %s:%s: %s",
                            self.manifest_path,
                            line_number,
                            exc,
                        )
        except Exception as exc:
            logger.error("Failed to load manifest from %s: %s", self.manifest_path, exc, exc_info=True)
            return []

        logger.info("Loaded %d samples from manifest for review.", len(samples))
        return samples

    def save_review(self, idx: int, quality: int, notes: str):
        if idx < 0 or idx >= len(self.samples):
            logger.error("Review index out of range: %s", idx)
            return False

        sample = self.samples[idx].copy()
        sample["quality"] = int(quality)
        sample["review_notes"] = notes.strip()
        sample["reviewed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

        try:
            self.reviewed_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.reviewed_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(sample, ensure_ascii=False) + "\n")
            logger.info("Saved review for sample %s", sample.get("id"))
            return True
        except Exception as exc:
            logger.error("Failed to save review for sample %s: %s", sample.get("id"), exc, exc_info=True)
            return False

    def get_current(self):
        if not self.samples:
            return "", "", ""

        sample = self.samples[self.current_idx]
        return sample.get("text", ""), sample.get("audio_path", ""), sample.get("id", "")

    def launch(self):
        with gr.Blocks(title="Olimi AI - Egyptian Data Review") as demo:
            gr.Markdown("# 🇪🇬 Olimi AI - Synthetic Egyptian Speech Review")
            gr.Markdown("Review samples → Rate quality → Add notes")

            with gr.Row():
                with gr.Column(scale=2):
                    text_box = gr.Textbox(label="Egyptian Arabic Text", lines=4, interactive=False)
                with gr.Column(scale=3):
                    audio_player = gr.Audio(label="🔊 Generated Audio", type="filepath")

            with gr.Row():
                sample_info = gr.Textbox(label="Sample ID", interactive=False)
                progress = gr.Textbox(label="Progress", interactive=False)

            quality = gr.Slider(minimum=1, maximum=5, step=1, value=4, label="Quality Score (5 = Excellent)")
            notes = gr.Textbox(label="Review Notes (pronunciation, prosody, noise, artifacts...)", lines=3)

            with gr.Row():
                btn_prev = gr.Button("← Previous")
                btn_save = gr.Button("✅ Save Review & Next", variant="primary", size="large")
                btn_next = gr.Button("Next →")

            def update_ui():
                text, audio, sid = self.get_current()
                prog = f"{self.current_idx + 1} / {len(self.samples)}" if self.samples else "0 / 0"
                return text, audio, sid, prog

            def save_and_next(quality_score, review_notes):
                if self.save_review(self.current_idx, quality_score, review_notes):
                    self.current_idx = min(self.current_idx + 1, len(self.samples) - 1)
                return update_ui()

            def go_previous():
                self.current_idx = max(0, self.current_idx - 1)
                return update_ui()

            btn_save.click(
                save_and_next,
                inputs=[quality, notes],
                outputs=[text_box, audio_player, sample_info, progress],
            )

            btn_next.click(update_ui, outputs=[text_box, audio_player, sample_info, progress])
            btn_prev.click(go_previous, outputs=[text_box, audio_player, sample_info, progress])

            demo.load(update_ui, outputs=[text_box, audio_player, sample_info, progress])

        try:
            demo.launch(share=False, server_name="127.0.0.1", server_port=7860)
        except Exception as exc:
            logger.error("Failed to launch review interface: %s", exc, exc_info=True)

if __name__ == "__main__":
    DatasetReviewer().launch()
