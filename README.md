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
   python3 -m venv venv
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
- `--youtube`: YouTube URL to download audio and transcribe
- `--subtitles`: YouTube URL to download subtitles directly (fast, no transcription needed)
- `--implementation`: Choose implementation (`whisper` or `faster`, default: `whisper`)
  - `whisper`: Default OpenAI Whisper implementation
  - `faster`: faster-whisper (typically 2-4x faster, optimized for CPU)
- `--benchmark`: Include benchmark data header in transcript output (optional)
- `--compare-models`: Show model comparison information

## Implementation Comparison

### Two Implementations Available

The script supports two Whisper implementations:

1. **`whisper`** (default): OpenAI's official Whisper implementation
   - Full-featured with extensive configuration options
   - Verbose progress output
   - Slightly slower but more compatible

2. **`faster`**: faster-whisper implementation using CTranslate2
   - Typically 2-4x faster on CPU
   - Optimized performance
   - Lower memory usage
   - Same model accuracy

### Usage Examples

```bash
# Use default OpenAI Whisper
python transcribe.py --audio audio.mp3

# Use faster-whisper for speed
python transcribe.py --audio audio.mp3 --implementation faster

# Download YouTube subtitles (instant, no transcription)
python transcribe.py --subtitles "https://youtube.com/watch?v=VIDEO_ID"

# Include benchmark data in the output
python transcribe.py --audio audio.mp3 --benchmark

# Use faster-whisper with benchmarking
python transcribe.py --audio audio.mp3 --implementation faster --benchmark

# Compare both implementations with benchmarking
python transcribe.py --audio audio.mp3 --implementation whisper --benchmark
python transcribe.py --audio audio.mp3 --implementation faster --benchmark
```

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
4. Optionally include benchmark data as a header (use `--benchmark` flag)

**File Organization:**
- Audio files: Keep in your current directory or specify full path
- Transcripts: Automatically saved to `txt/` folder
- Example: `audio/podcast.mp3` → `txt/podcast.txt`

**Benchmark Headers (Optional):**

Use the `--benchmark` flag to include detailed benchmark metadata at the top of each transcript file:
- Generation timestamp
- Implementation used (whisper or faster-whisper)
- Model size
- Audio duration
- Processing time
- Real-time speed (e.g., 2.5x real-time)
- Detected language

Example with `--benchmark`:
```
# ============================================================
# TRANSCRIPTION BENCHMARK DATA
# ============================================================
# Generated: 2024-01-15 14:30:45
# Implementation: faster-whisper
# Model: large-v3
# Audio Duration: 5m 23s
# Processing Time: 2m 5s
# Speed: 2.58x real-time
# Detected Language: en
# ============================================================

[Your transcription text here...]
```

Without `--benchmark`:
```
[Your transcription text here...]
```

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
