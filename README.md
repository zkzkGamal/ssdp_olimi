# SSDP Olimi

**SSDP Olimi** is a synthetic speech data generation and review pipeline focused on Egyptian Arabic TTS. It uses the `oddadmix/chatterbox-egyptian-v0` model through a local TTS integration and provides an end-to-end workflow from prompt files to generated audio samples and review UI.

## Project Structure

- `bash.sh` - automation script for environment setup, dependency installation, prompt initialization, synthesis, and optional review launch.
- `run_synthesis.py` - entrypoint for synthetic speech generation.
- `run_review.py` - entrypoint for the Gradio-based review interface.
- `run_export.py` - export reviewed samples to training-ready dataset files.
- `tests/test_export.py` - unit test for export pipeline validation.
- `configs/default.yaml` - pipeline configuration file.
- `data/raw/prompts.txt` - source prompts for synthesis.
- `data/processed/` - generated output directory with audio and `manifest.jsonl`.
- `demo/` - demo assets and example material for the project.
- `tts_model/` - local copy of the TTS repository source.
- `requirements.txt` - Python dependency specification.

## Requirements

- Python 3.11+ (tested with Python 3.11 / 3.12)
- `git`
- CUDA-capable GPU if you intend to use the model with CUDA acceleration.

## Setup and Installation

Use the project automation script to prepare the environment and run synthesis.

```bash
bash bash.sh
```

The script performs these tasks:

1. Creates a Python virtual environment in `venv/`
2. Installs dependencies from `requirements.txt`
3. Clones `lahgtna-chatterbox` if needed and prepares `tts_model/`
4. Creates a sample `data/raw/prompts.txt` if none exists
5. Executes `run_synthesis.py`

## Running Review UI

After synthesis finishes, launch the review UI with:

```bash
source venv/bin/activate
python run_review.py
```

Review results are saved to:

```text
data/processed/reviewed_manifest.jsonl
```

If you want the automation script to run the review step automatically after synthesis, use:

```bash
bash bash.sh --review
```

## Export Training Dataset

After review, export training-ready files with:

```bash
source venv/bin/activate
python run_export.py
```

Use a higher threshold if you want only the top-rated samples:

```bash
python run_export.py --min-quality 4
```

## Demo and Example Files

The repository also includes a demo folder with example materials:

- `demo/` - contains demo assets and example content for the project.
- `demo/lahgtna-chatterbox/` - local copy of a demo TTS integration and README information.

## How It Works

### `run_synthesis.py`

- Loads config from `configs/default.yaml`
- Reads prompts from `data/raw/prompts.txt`
- Uses `EgyptianTTSPipeline` from `src/synthesizer.py`
- Downloads the model from Hugging Face
- Generates `.wav` audio files in `data/processed/audio/`
- Writes metadata to `data/processed/manifest.jsonl`

### `run_review.py`

- Loads generated samples from the manifest
- Starts the review UI for manual inspection
- Allows score and notes for each sample
- Saves reviewed data to `data/processed/reviewed_manifest.jsonl`
- If no manifest exists, it will instruct you to run `python run_synthesis.py`

## Case Study Notes

### Prompt generation

Prompts are stored in `data/raw/prompts.txt` and are written in Egyptian Arabic. They use everyday conversational language, dialect-specific vocabulary, and common spoken expressions such as `مش`, `بقى`, `أوي`, `يا ريت`, and `فين`. The intent is to reflect real informal speech patterns that Egyptian STT models should learn.

### TTS model choice

The pipeline uses `oddadmix/chatterbox-egyptian-v0` because it is designed for Egyptian Arabic speech synthesis and is compatible with the local Chatterbox TTS integration in this repo. This choice prioritizes dialect coverage and reproducibility, even though synthetic audio may still have artifacts, unnatural prosody, or occasional pronunciation issues.

### Review approach

The review interface is implemented in `src/reviewer.py` using Gradio. It provides:

- a text display for Egyptian Arabic prompts
- an audio player for generated speech
- a quality score slider (1-5)
- a reviewer notes field for pronunciation, prosody, noise, or artifacts
- next / previous navigation

Review decisions are persisted to `data/processed/reviewed_manifest.jsonl` so that only manually verified examples are retained for downstream use.

### Training-ready output

The reviewed output format is JSON Lines (`.jsonl`), which is easy to consume for training pipelines. Each record includes:

- `id`
- `text`
- `audio_path`
- `speaker_id`
- `duration`
- `sample_rate`
- `generated_at`
- `model_used`
- `quality`
- `review_notes`
- `reviewed_at`

This structure is training-ready because it combines text/audio alignment with review metadata. It can also be converted to standard STT dataset formats such as CSV, TSV, or `wav.scp` + transcript pairs.

### Pipeline reliability and design

- Configuration is externalized in `configs/default.yaml`.
- Synthesis is batched in `src/synthesizer.py` with resumability: the pipeline skips already-generated sample IDs when the manifest exists.
- Intermediate artifacts are observable through logs, `data/processed/manifest.jsonl`, `data/processed/audio/`, and `data/processed/reviewed_manifest.jsonl`.

### Quality limitations and trade-offs

Synthetic data can mislead STT models if it is too uniform or contains artifacts. Current limitations include:

- single-speaker synthetic audio
- occasional unnatural prosody or mispronunciation
- lack of explicit quality filtering other than manual review
- potential dialect bias based on prompt selection and model behavior

This pipeline addresses those issues by requiring human review before samples are marked as training-ready, but it does not yet include automated quality scoring or STT validation.

## Configuration

The main configuration file is `configs/default.yaml`.

Important fields:

- `paths.prompts` - path to the prompt text file
- `paths.output_dir` - base path for generated output
- `paths.audio_dir` - path where generated audio is written
- `tts.model_id` - Hugging Face model ID
- `tts.exaggeration`, `tts.cfg_weight`, `tts.temperature` - model synthesis parameters
- `batch.max_samples` - maximum samples to generate

## Adding Prompts

Edit `data/raw/prompts.txt` with one prompt per line. Example:

```text
مرحباً بك في مشروعنا.
هذا مثال لنص تراكب توليد الكلام.
الهدف هو إنتاج بيانات صوتية مصرية عربية.
```

## Output

Generated data is stored under `data/processed/`:

- `data/processed/audio/` - generated `.wav` files
- `data/processed/manifest.jsonl` - metadata for every generated sample
- `data/processed/reviewed_manifest.jsonl` - manually reviewed samples with quality and notes
- `data/processed/training_manifest.jsonl` - filtered training-ready dataset export
- `data/processed/training_manifest.tsv` - tab-separated training dataset for STT pipelines

## Tests

A small unit test is included for the export logic:

```bash
python -m unittest tests/test_export.py
```

## Troubleshooting

- If `python3` is missing, install it first.
- If dependency installation fails, check your network and GPU/CUDA compatibility.
- If the TTS repository clone fails, verify internet access and Git permissions.
- If the model download fails, ensure Hugging Face access and available disk space.

## Notes

- `bash.sh` is intended to be the primary setup helper.
- The root `tts_model/` folder must be present or created by the script for imports to work.
- `run_review.py` requires a generated manifest file from `run_synthesis.py`.

## License

No explicit license is included in this repository. If you add one, update this README accordingly.
# ssdp_olimi
