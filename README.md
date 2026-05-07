# SSDP Olimi

**SSDP Olimi** is a comprehensive synthetic speech data generation and review pipeline tailored for Egyptian Arabic TTS. Leveraging the `oddadmix/chatterbox-egyptian-v0` model via a local Chatterbox TTS integration, it delivers an end-to-end workflow from text prompts to high-quality, training-ready audio datasets for STT model fine-tuning.

This pipeline addresses real-world challenges in Arabic dialect processing, including informal speech patterns, dialect-specific vocabulary, and synthetic data quality assurance. It emphasizes reliability, configurability, and human-in-the-loop validation to produce datasets suitable for downstream machine learning tasks.

## Table of Contents

- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Detailed Usage](#detailed-usage)
- [Configuration](#configuration)
- [Adding Prompts](#adding-prompts)
- [Output and Artifacts](#output-and-artifacts)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Pipeline Reliability and Design](#pipeline-reliability-and-design)
- [Quality Limitations and Trade-offs](#quality-limitations-and-trade-offs)
- [Contributing](#contributing)
- [License](#license)

## Project Structure

- `bash.sh` - Automation script for environment setup, dependency installation, prompt initialization, synthesis, and optional review/export.
- `run_synthesis.py` - Entrypoint for synthetic speech generation.
- `run_review.py` - Entrypoint for the Gradio-based review interface.
- `run_export.py` - Export reviewed samples to training-ready dataset files.
- `tests/test_export.py` - Unit test for export pipeline validation.
- `configs/default.yaml` - Pipeline configuration file.
- `data/raw/prompts.txt` - Source prompts for synthesis.
- `data/processed/` - Generated output directory with audio, manifests, and exports.
- `demo/` - Demo assets and example materials for the project.
- `tts_model/` - Local copy of the TTS repository source.
- `requirements.txt` - Python dependency specification.
- `src/` - Core pipeline modules:
  - `config.py` - Configuration management.
  - `synthesizer.py` - TTS synthesis logic.
  - `reviewer.py` - Review UI and data handling.
  - `export.py` - Dataset export utilities.

## Requirements

- **Python**: 3.11+ (tested with Python 3.11 / 3.12)
- **Git**: For cloning dependencies.
- **GPU**: CUDA-capable GPU recommended for TTS acceleration (falls back to CPU if unavailable).
- **Disk Space**: ~5GB for model checkpoints and generated data.
- **Network**: Internet access for model downloads (Hugging Face).

## Quick Start

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd ssdp_olimi
   bash bash.sh
   ```

2. **Review Generated Data**:
   ```bash
   source venv/bin/activate
   python run_review.py
   ```

3. **Export Training Dataset**:
   ```bash
   python run_export.py
   ```

For a fully automated run (synthesis + review + export):
```bash
bash bash.sh --review --export
```

## Detailed Usage

### Synthesis

Run TTS synthesis on prompts:

```bash
source venv/bin/activate
python run_synthesis.py
```

- Reads prompts from `data/raw/prompts.txt`.
- Generates `.wav` files in `data/processed/audio/`.
- Outputs metadata to `data/processed/manifest.jsonl`.
- Supports resumability: skips already-generated samples.

### Review

Launch the interactive review UI:

```bash
python run_review.py
```

- Displays text, audio, and navigation controls.
- Allows quality scoring (1-5) and notes.
- Persists reviews to `data/processed/reviewed_manifest.jsonl`.
- Requires a generated manifest; exits gracefully if none exists.

### Export

Convert reviewed samples to training formats:

```bash
python run_export.py --min-quality 4
```

- Filters samples by quality score (default: 3).
- Outputs `training_manifest.jsonl` (rich metadata) and `training_manifest.tsv` (STT-ready).
- Normalizes audio paths for portability.

### Automation Script

`bash.sh` handles setup and optional steps:

- `bash bash.sh` - Setup and synthesis only.
- `bash bash.sh --review` - Setup, synthesis, and review.
- `bash bash.sh --export` - Setup, synthesis, and export (assumes review exists).
- `bash bash.sh --review --export` - Full pipeline.

## Configuration

The main config file is `configs/default.yaml`. Key sections:

- **Project**:
  - `name`: Dataset identifier.
  - `version`: Pipeline version.

- **Paths**:
  - `prompts`: Input prompt file path.
  - `output_dir`: Base output directory.
  - `audio_dir`: Audio storage path.

- **TTS**:
  - `model_id`: Hugging Face model ID (e.g., `oddadmix/chatterbox-egyptian-v0`).
  - `language`: Language code (e.g., `eg` for Egyptian).
  - `exaggeration`, `cfg_weight`, `temperature`: Synthesis parameters for prosody control.
  - `sample_rate`: Output audio sample rate.

- **Batch**:
  - `max_samples`: Maximum samples to generate (0 for unlimited).
  - `resume`: Enable resumability.

- **Review**:
  - `min_quality_score`: Default quality threshold for export.

Modify `configs/default.yaml` to customize behavior. The pipeline validates config on load.

## Adding Prompts

Edit `data/raw/prompts.txt` with one prompt per line. Prompts should reflect Egyptian Arabic:

```text
ازيك عامل إيه؟ فينك مش باين بقالك فترة كبيرة.
أنا لسه صاحي من النوم وهنزل أروح الشغل حالا.
```

- Use informal, dialect-specific expressions (e.g., `مش`, `بقى`, `أوي`).
- Ensure UTF-8 encoding.
- The pipeline handles empty lines and skips invalid entries.

## Output and Artifacts

All outputs are in `data/processed/`:

- `audio/` - Generated `.wav` files (24kHz, mono).
- `manifest.jsonl` - Synthesis metadata (ID, text, audio_path, duration, etc.).
- `reviewed_manifest.jsonl` - Reviewed samples with quality and notes.
- `training_manifest.jsonl` - Filtered export with normalized paths.
- `training_manifest.tsv` - Tab-separated format for STT pipelines (`audio_path<TAB>text`).

Intermediate artifacts are observable via logs and file timestamps.

## Testing

Run unit tests to validate critical logic:

```bash
python -m unittest tests/test_export.py
```

- Covers export filtering, path normalization, and file writing.
- Add more tests as the pipeline evolves.

## Troubleshooting

### Common Issues

- **Python Version**: Ensure Python 3.11+. Upgrade with `pyenv` or system package manager.
- **GPU/CUDA**: If CUDA errors occur, install compatible PyTorch: `pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121`.
- **Dependencies**: If installation fails, check network/proxy. Use `pip install --no-cache-dir` for retries.
- **Model Download**: Requires Hugging Face access. If blocked, download manually to `tts_model/`.
- **Audio Playback**: Ensure browser supports `.wav`. Check file paths in review UI.
- **Manifest Errors**: Verify `data/raw/prompts.txt` exists and is UTF-8 encoded.
- **Resumability**: If synthesis hangs, check disk space and kill background processes.

### Edge Cases

- **Empty Prompts**: Skipped with warnings.
- **Network Interruptions**: Synthesis resumes from last checkpoint; re-run `run_synthesis.py`.
- **Large Datasets**: Use `batch.max_samples` to limit generation.
- **Quality Filtering**: Adjust `--min-quality` in export for stricter criteria.
- **Path Issues**: Ensure absolute paths in config; export normalizes relative paths.
- **Memory/CPU**: On low-end systems, reduce batch size or use CPU-only PyTorch.

### Logs and Debugging

- Enable verbose logging: `export PYTHONPATH=src && python -c "import logging; logging.basicConfig(level=logging.DEBUG)"`.
- Check `data/processed/` for partial outputs.
- For TTS issues, verify `tts_model/` integrity.

## Pipeline Reliability and Design

- **Configuration Externalization**: All settings in YAML for easy modification.
- **Resumability**: Synthesis skips existing IDs; export re-runs safely.
- **Error Handling**: Graceful failures with informative logs; no silent corruption.
- **Observability**: Logs, manifests, and timestamps track progress.
- **Modularity**: Separate scripts for synthesis, review, and export.
- **Testing**: Unit tests for export; manual validation for UI.

## Quality Limitations and Trade-offs

Synthetic data can mislead STT models due to artifacts. Key limitations:

- **Single Speaker**: All audio from one synthetic voice; lacks diversity.
- **Prosody Issues**: Occasional unnatural intonation or mispronunciation.
- **Dialect Bias**: Prompts may not cover all Egyptian variants.
- **Artifact Contamination**: Noise or clipping in low-quality samples.
- **Manual Review**: Subjective; requires domain expertise.

Mitigations:
- Human review filters poor samples.
- Configurable synthesis parameters for tuning.
- Export thresholds ensure only high-quality data is used.

For production, supplement with real data and automated quality metrics (e.g., WER validation).

## Contributing

- Fork the repository and submit pull requests.
- Follow PEP 8 for Python code.
- Add tests for new features.
- Update README for changes.

## License

This project is licensed under the MIT License. See LICENSE file for details. If no LICENSE exists, consider adding one (e.g., MIT or Apache 2.0).

