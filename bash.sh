#!/usr/bin/env bash
set -euo pipefail

VENV_DIR="venv"
REPO_URL="https://github.com/Oddadmix/lahgtna-chatterbox.git"
CLONE_DIR="lahgtna-chatterbox"
LOCAL_TTS_DIR="tts_model"
PROMPTS_FILE="data/raw/prompts.txt"

echo "=== SSDP Olimi Setup and Run Script ==="

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is not installed. Install Python 3.11+ and retry."
  exit 1
fi

if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating virtual environment in $VENV_DIR..."
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip

echo "Installing Python dependencies..."
python -m pip install -r requirements.txt

if [[ ! -d "$LOCAL_TTS_DIR" ]]; then
  if [[ -d "$CLONE_DIR/src" ]]; then
    echo "Using existing cloned repository at $CLONE_DIR/src..."
    mv "$CLONE_DIR/src" "$LOCAL_TTS_DIR"
  else
    echo "Cloning TTS model repository..."
    git clone "$REPO_URL"
    mv "$CLONE_DIR/src" "$LOCAL_TTS_DIR"
  fi
fi

if [[ ! -f "$PROMPTS_FILE" ]]; then
  echo "Creating sample prompts file at $PROMPTS_FILE..."
  mkdir -p "$(dirname "$PROMPTS_FILE")"
  cat > "$PROMPTS_FILE" <<'EOF'
مرحباً بك في مشروعنا.
هذا مثال لنص تراكب توليد الكلام.
الهدف هو إنتاج بيانات صوتية مصرية عربية.
EOF
fi

echo "Running synthesis pipeline..."
python run_synthesis.py

echo "Synthesis complete."
echo "To launch the review UI, run:"
echo "  source $VENV_DIR/bin/activate && python run_review.py"
echo "If you want to run the review step automatically, rerun with:"
echo "  bash bash.sh --review"
echo "To export reviewed samples after review, rerun with:"
echo "  bash bash.sh --export"
echo "To run both review and export automatically, rerun with:"
echo "  bash bash.sh --review --export"

if [[ "${1:-}" == "--review" ]] || [[ "${2:-}" == "--review" ]]; then
  echo "Launching review UI..."
  python run_review.py
fi

if [[ "${1:-}" == "--export" ]] || [[ "${2:-}" == "--export" ]]; then
  echo "Exporting reviewed dataset..."
  python run_export.py
fi