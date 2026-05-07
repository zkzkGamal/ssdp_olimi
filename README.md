# SSDP Olimi

**SSDP Olimi** is a synthetic speech data generation and review pipeline focused on Egyptian Arabic TTS. It uses the `oddadmix/chatterbox-egyptian-v0` model through a local TTS integration and provides an end-to-end workflow from prompt files to generated audio samples and review UI.

## Project Structure

- `bash.sh` - automation script for environment setup, dependency installation, prompt initialization, synthesis, and optional review launch.
- `run_synthesis.py` - entrypoint for synthetic speech generation.
- `run_review.py` - entrypoint for the Gradio-based review interface.
- `configs/default.yaml` - pipeline configuration file.
- `data/raw/prompts.txt` - source prompts for synthesis.
- `data/processed/` - generated output directory with audio and `manifest.jsonl`.
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

If you want the automation script to run the review step automatically after synthesis, use:

```bash
bash bash.sh --review
```

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
- If no manifest exists, it will instruct you to run `python run_synthesis.py`

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
