# Whisper Audio Transcriber

A high-quality audio transcription script using OpenAI's Whisper model, optimized for M1 MacBook Pro.

## Features

- **High Quality**: Uses `large-v3` model for best transcription accuracy
- **M1 Optimized**: Optimized for Apple Silicon performance
- **English Focused**: Configured specifically for English audio for improved accuracy
- **Multiple Formats**: Supports MP3, WAV, M4A, FLAC, and other common audio formats
- **Progress Indicators**: Real-time progress bars and processing metrics
- **Model Comparison**: Built-in model comparison tool to help choose the right model
- **Easy to Use**: Simple command-line interface with helpful emojis and status updates

## Installation

### Prerequisites

- Python 3.8 or higher
- macOS with M1/M2 chip (optimized for Apple Silicon)

### Setup

1. **Clone or download this repository**
   ```bash
   cd /path/to/transcribe
   ```

2. **Create virtual environment with Python 3.13** (required for compatibility)
   ```bash
   python3.13 -m venv venv
   ```

3. **Activate virtual environment and install dependencies**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Make the script executable** (optional)
   ```bash
   chmod +x transcribe.py
   ```

### GPU Acceleration (Optional - AMD/NVIDIA)

For GPU acceleration on supported hardware:

**For AMD GPUs (Linux/ROCm):**
1. Install ROCm 5.7+ following [AMD's official guide](https://rocm.docs.amd.com/)
2. Install PyTorch with ROCm support:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7
   ```
3. Verify GPU detection:
   ```python
   import torch
   print(torch.cuda.is_available())  # Should return True
   print(torch.cuda.get_device_name(0))  # Should display your GPU model
   ```

**For NVIDIA GPUs (CUDA):**
1. Install PyTorch with CUDA support:
   ```bash
   pip install torch torchvision torchaudio
   ```
2. GPU acceleration will be automatically detected

GPU acceleration provides 5-10x speedup on supported hardware.

## Usage

### Basic Usage

**Option 1: Using the activation script (recommended)**
```bash
./transcribe.sh audio_file.mp3
```

**Option 2: Manual activation**
```bash
# Activate virtual environment first
source venv/bin/activate

# Then run the script
python transcribe.py --audio audio_file.mp3
```

### Examples

```bash
# Using the activation script (recommended)
./transcribe.sh podcast.mp3
./transcribe.sh recording.wav
./transcribe.sh audio.m4a --model medium
./transcribe.sh audio.mp3 --output my_transcript.txt

# Compare different models
./transcribe.sh --compare-models

# Or manually activate virtual environment first
source venv/bin/activate
python transcribe.py --audio podcast.mp3
python transcribe.py --audio recording.wav
python transcribe.py --audio audio.m4a --model medium
python transcribe.py --audio audio.mp3 --output my_transcript.txt
```

### Command Line Options

- `--audio`: Path to the audio file to transcribe (required)
- `--model`: Whisper model size (default: `large-v3`)
  - Available models: `tiny`, `base`, `small`, `medium`, `large`, `large-v2`, `large-v3`
  - Larger models = better quality but slower processing
- `--output`: Custom output file path (default: saves to `txt/` folder)
- `--gpu`: Use GPU acceleration if available (default: enabled)
- `--cpu`: Force CPU usage even if GPU is available
- `--compare-models`: Show model comparison information

## Model Information

### Recommended Models

- **`large-v3`** (default): Best quality, slower processing
- **`medium`**: Good balance of quality and speed
- **`small`**: Faster processing, decent quality
- **`base`**: Fastest, basic quality

### Performance on M1 MacBook Pro

| Model | Speed | Quality | Memory Usage |
|-------|-------|---------|--------------|
| `large-v3` | Slow | Excellent | ~6GB |
| `medium` | Medium | Good | ~3GB |
| `small` | Fast | Fair | ~1GB |
| `base` | Very Fast | Basic | ~500MB |

## Progress Indicators

The script provides comprehensive progress feedback:

- **🔄 Model Loading**: Shows progress when downloading/loading the Whisper model
- **📏 Audio Analysis**: Displays audio duration and file information
- **📊 Real-time Processing**: Shows detailed progress during transcription
- **⏱️ Performance Metrics**: Displays processing time and speed (e.g., "2.5x real-time")
- **✅ Completion Status**: Clear indicators when each step is complete
- **📝 Results**: Formatted transcription output with emojis and clear sections

## Output

The script will:
1. Display the transcription in the terminal with progress indicators
2. Save the transcription to a `.txt` file in the `txt/` folder (created automatically)
3. Show processing statistics and performance metrics

**File Organization:**
- Audio files: Keep in your current directory or specify full path
- Transcripts: Automatically saved to `txt/` folder
- Example: `audio/podcast.mp3` → `txt/podcast.txt`

## Troubleshooting

### Common Issues

1. **"faster-whisper not installed"**
   ```bash
   pip install faster-whisper
   ```

2. **Out of memory errors**
   - Try a smaller model: `--model medium` or `--model small`
   - Close other applications to free up RAM

3. **Slow performance**
   - Ensure you're using `faster-whisper` (not `openai-whisper`)
   - Consider using a smaller model for faster processing

4. **Audio format not supported**
   - Convert to MP3 or WAV using ffmpeg:
   ```bash
   ffmpeg -i input.m4a output.mp3
   ```

### Installation Issues

If you encounter issues with PyTorch installation on M1:

```bash
# Install PyTorch with M1 support
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

## Tips for Best Results

1. **Audio Quality**: Higher quality audio files produce better transcriptions
2. **Background Noise**: Minimize background noise for clearer results
3. **Speaking Clarity**: Clear, well-paced speech improves accuracy
4. **File Length**: Very long files may take considerable time to process

## License

This script uses OpenAI's Whisper model. Please refer to OpenAI's licensing terms for commercial use.
