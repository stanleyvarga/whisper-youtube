#!/bin/bash
# Activation script for Whisper Audio Transcriber
# Resolves symlinks so this works when installed via ~/.dotfiles/bin or ~/bin

resolve_script_dir() {
    local source="${BASH_SOURCE[0]}"
    while [ -L "$source" ]; do
        local dir
        dir="$(cd -P "$(dirname "$source")" && pwd)"
        source="$(readlink "$source")"
        [[ "$source" != /* ]] && source="$dir/$source"
    done
    cd -P "$(dirname "$source")" && pwd
}

PROJECT_DIR="$(resolve_script_dir)"

# GUI apps and minimal shells often omit Homebrew; Whisper needs ffmpeg on PATH
for brew_bin in /opt/homebrew/bin /usr/local/bin; do
    if [ -d "$brew_bin" ] && [[ ":$PATH:" != *":$brew_bin:"* ]]; then
        PATH="$brew_bin:$PATH"
    fi
done
export PATH

if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "Error: Virtual environment not found at $PROJECT_DIR/venv"
    echo "Run setup first:"
    echo "  cd $PROJECT_DIR"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/transcribe.py" ]; then
    echo "Error: transcribe.py not found in $PROJECT_DIR"
    exit 1
fi

# shellcheck source=/dev/null
source "$PROJECT_DIR/venv/bin/activate"

if [[ "$*" == *"--help"* ]] || [[ "$*" == *"-h"* ]] || [[ "$*" == *"--compare-models"* ]] || [[ "$*" == *"--audio"* ]] || [[ "$*" == *"--youtube"* ]] || [[ "$*" == *"--subtitles"* ]] || [[ "$*" == *"--txt"* ]]; then
    exec python "$PROJECT_DIR/transcribe.py" "$@"
else
    exec python "$PROJECT_DIR/transcribe.py" --audio "$1" "${@:2}"
fi
