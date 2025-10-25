#!/bin/bash
# Activation script for Whisper Audio Transcriber
# This script activates the virtual environment and runs the transcription script

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run setup first:"
    echo "python3.13 -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if transcribe.py exists
if [ ! -f "transcribe.py" ]; then
    echo "Error: transcribe.py not found in current directory"
    exit 1
fi

# Check if any of the arguments are special commands
if [[ "$*" == *"--help"* ]] || [[ "$*" == *"-h"* ]] || [[ "$*" == *"--compare-models"* ]] || [[ "$*" == *"--audio"* ]] || [[ "$*" == *"--youtube"* ]]; then
    # Run the transcription script with all arguments passed through
    python transcribe.py "$@"
else
    # If no special commands, assume first argument is an audio file path
    # and add --audio parameter, properly handling all arguments
    python transcribe.py --audio "$1" "${@:2}"
fi
