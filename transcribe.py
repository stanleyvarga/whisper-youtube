#!/usr/bin/env python3
"""
Whisper Audio Transcriber Script
Optimized for M1 MacBook Pro with high-quality English transcription
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path

try:
    import whisper
    from tqdm import tqdm
except ImportError:
    print("Error: Required packages not installed. Please run: pip install -r requirements.txt")
    sys.exit(1)


def sanitize_filename(filename):
    """
    Sanitize filename by converting to lowercase, replacing spaces with hyphens,
    and removing all characters except letters, numbers, and hyphens.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Convert to lowercase
    sanitized = filename.lower()
    
    # Replace spaces and underscores with hyphens
    sanitized = re.sub(r'[\s_]+', '-', sanitized)
    
    # Remove all characters except letters, numbers, and hyphens
    sanitized = re.sub(r'[^a-z0-9\-]', '', sanitized)
    
    # Remove multiple consecutive hyphens
    sanitized = re.sub(r'-+', '-', sanitized)
    
    # Remove leading/trailing hyphens
    sanitized = sanitized.strip('-')
    
    return sanitized


def get_device():
    """
    Detect and return the best available device for inference.
    Returns device type ('cuda' or 'cpu') and device name.
    
    Returns:
        tuple: (device, device_name) where device is 'cuda' or 'cpu'
    """
    try:
        import torch
        if torch.cuda.is_available():
            device = "cuda"
            try:
                device_name = torch.cuda.get_device_name(0)
            except Exception:
                device_name = "GPU (unknown)"
            return device, device_name
        return "cpu", "CPU"
    except Exception:
        return "cpu", "CPU"


def get_audio_duration(audio_file_path):
    """Get audio file duration in seconds"""
    try:
        import librosa
        # Use the updated API parameter name
        duration = librosa.get_duration(path=audio_file_path)
        return duration
    except ImportError:
        # Fallback: estimate based on file size (rough approximation)
        file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
        # Rough estimate: 1MB ≈ 1 minute for compressed audio
        return file_size_mb * 60
    except Exception as e:
        print(f"Warning: Could not get audio duration ({e}). Proceeding without duration info.")
        return None


def transcribe_audio(audio_file_path, model_size="large-v3", cleanup=False, use_gpu=True):
    """
    Transcribe audio file using Whisper model
    
    Args:
        audio_file_path (str): Path to the audio file
        model_size (str): Whisper model size (large-v3 for best quality)
        cleanup (bool): Whether to remove audio files after successful transcription
        use_gpu (bool): Whether to use GPU acceleration if available (default: True)
    
    Returns:
        tuple: (transcribed_text, files_to_cleanup)
    """
    # Detect available device
    device, device_name = get_device()
    if not use_gpu or device == "cpu":
        device = "cpu"
        device_name = "CPU (forced)" if use_gpu else "CPU"
    
    print(f"🔄 Loading Whisper model '{model_size}' on {device_name}...")
    
    # Sanitize the filename for easier handling
    original_path = Path(audio_file_path)
    sanitized_name = sanitize_filename(original_path.stem) + original_path.suffix
    sanitized_path = original_path.parent / sanitized_name
    
    # Rename file if the sanitized name is different
    if sanitized_path != original_path:
        print(f"🔄 Renaming file: {original_path.name} → {sanitized_name}")
        try:
            os.rename(audio_file_path, str(sanitized_path))
            audio_file_path = str(sanitized_path)
            print(f"✅ File renamed successfully")
        except Exception as e:
            print(f"⚠️  Could not rename file: {e}")
            print("Proceeding with original filename...")
    
    # Check if file needs conversion (WebM with .mp3 extension)
    files_to_cleanup = []
    actual_audio_path = audio_file_path
    
    # Add the current audio file to cleanup list if cleanup is requested
    if cleanup:
        files_to_cleanup.append(audio_file_path)
    
    try:
        # Check file format
        import subprocess
        result = subprocess.run(['file', audio_file_path], capture_output=True, text=True)
        if 'WebM' in result.stdout and audio_file_path.endswith('.mp3'):
            print(f"🔄 Detected WebM file with .mp3 extension. Converting to proper MP3...")
            
            # Create converted file path
            converted_path = audio_file_path.replace('.mp3', '_converted.mp3')
            
            # Convert using ffmpeg
            convert_cmd = [
                'ffmpeg', '-i', audio_file_path, 
                '-acodec', 'mp3', converted_path, '-y'
            ]
            subprocess.run(convert_cmd, capture_output=True, check=True)
            
            actual_audio_path = converted_path
            files_to_cleanup.append(converted_path)  # Add converted file to cleanup
            
            if cleanup:
                files_to_cleanup.append(audio_file_path)  # Add original file to cleanup
                
            print(f"✅ Conversion complete: {converted_path}")
            
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"⚠️  Could not check/convert file format: {e}")
        print("Proceeding with original file...")
    
    # Initialize Whisper model
    model = whisper.load_model(model_size)
    
    # Move model to GPU if available
    if device == "cuda":
        try:
            import torch
            model = model.to(device)
            print(f"✅ Model loaded on GPU: {device_name}")
        except Exception as e:
            print(f"⚠️  Could not load model on GPU: {e}")
            print(f"✅ Model loaded on CPU")
            device = "cpu"
            device_name = "CPU (fallback)"
    else:
        print(f"✅ Model loaded on CPU")
    
    # Get audio duration for progress estimation
    duration = get_audio_duration(actual_audio_path)
    if duration:
        duration_str = f"{int(duration//60)}m {int(duration%60)}s"
        print(f"📏 Audio duration: {duration_str}")
    
    print(f"🎵 Transcribing: {actual_audio_path}")
    print("⏳ This may take a few minutes depending on audio length...")
    print("📊 Progress will be shown below:")
    print("-" * 50)
    
    start_time = time.time()
    
    # Set fp16 based on device (GPU can use fp16 for better performance)
    use_fp16 = (device == "cuda")
    
    # Transcribe the audio with optimized settings
    result = model.transcribe(
        audio_file_path,
        language="en",  # English only for better accuracy
        fp16=use_fp16,     # Enable fp16 on GPU, use fp32 on CPU
        verbose=True,    # Enable verbose output for progress
        word_timestamps=False,  # Disable word timestamps for speed
        temperature=0.0,  # Use deterministic sampling for consistency
        compression_ratio_threshold=2.4,  # Skip audio that's likely not speech
        logprob_threshold=-1.0,  # Skip segments with low confidence
        no_speech_threshold=0.6  # Skip segments likely to be silence
    )
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print("-" * 50)
    print(f"✅ Detected language: {result['language']}")
    print(f"⏱️  Processing time: {int(processing_time//60)}m {int(processing_time%60)}s")
    
    if duration:
        speed_ratio = duration / processing_time
        print(f"🚀 Processing speed: {speed_ratio:.1f}x real-time")
    
    return result["text"].strip(), files_to_cleanup


def save_transcription(text, output_path):
    """Save transcription to text file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Transcription saved to: {output_path}")


def cleanup_files(files_to_cleanup):
    """Remove files after successful transcription"""
    if not files_to_cleanup:
        return
    
    print(f"\n🧹 Cleaning up {len(files_to_cleanup)} file(s)...")
    for file_path in files_to_cleanup:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"✅ Removed: {file_path}")
            else:
                print(f"⚠️  File not found: {file_path}")
        except Exception as e:
            print(f"❌ Failed to remove {file_path}: {e}")


def play_completion_sound():
    """
    Play a completion sound from the utils/effects folder.
    Looks for audio files starting with [use] and plays the first one found.
    """
    effects_dir = Path("utils/effects")
    
    if not effects_dir.exists():
        print("🎵 No effects folder found, skipping completion sound")
        return
    
    # Look for audio files starting with [use]
    use_files = []
    for file_path in effects_dir.iterdir():
        if file_path.is_file() and file_path.name.startswith("[use]"):
            # Check if it's an audio file
            if file_path.suffix.lower() in ['.mp3', '.wav', '.m4a', '.aac', '.ogg']:
                use_files.append(file_path)
    
    if not use_files:
        print("🎵 No audio files starting with [use] found, skipping completion sound")
        return
    
    # Use the first [use] file found
    sound_file = use_files[0]
    print(f"🎵 Playing completion sound: {sound_file.name}")
    
    try:
        # Try different methods to play the sound
        import subprocess
        import platform
        
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            # Use afplay (built-in macOS audio player)
            subprocess.run(['afplay', str(sound_file)], check=True)
        elif system == "linux":
            # Try common Linux audio players
            players = ['paplay', 'aplay', 'mpg123', 'mpv']
            for player in players:
                try:
                    subprocess.run([player, str(sound_file)], check=True, capture_output=True)
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            else:
                print("⚠️  No suitable audio player found on Linux")
        elif system == "windows":
            # Use Windows Media Player
            subprocess.run(['start', str(sound_file)], shell=True, check=True)
        else:
            print(f"⚠️  Unsupported operating system: {system}")
            
    except Exception as e:
        print(f"⚠️  Could not play completion sound: {e}")
        print("🎵 Completion sound failed, but transcription was successful!")


def download_youtube_audio(url, output_dir="audio"):
    """
    Download audio from YouTube video using yt-dlp
    
    Args:
        url (str): YouTube video URL
        output_dir (str): Directory to save the audio file
        
    Returns:
        str: Path to the downloaded audio file
    """
    import subprocess
    import tempfile
    
    print(f"📥 Downloading audio from YouTube: {url}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Use yt-dlp to download audio in best quality
    cmd = [
        'yt-dlp',
        '--extract-audio',
        '--audio-format', 'mp3',
        '--audio-quality', '0',  # Best quality
        '--output', f'{output_dir}/%(title)s.%(ext)s',
        '--no-playlist',  # Only download single video, not playlist
        url
    ]
    
    try:
        print("🔄 Starting download...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Find the downloaded file - use the most reliable method
        downloaded_file = None
        
        # Method 1: Look for .mp3 files in output directory (most reliable)
        import glob
        mp3_files = glob.glob(f"{output_dir}/*.mp3")
        if mp3_files:
            # Get the most recently modified file
            downloaded_file = max(mp3_files, key=os.path.getmtime)
        
        # Method 2: Try to parse from yt-dlp output as backup
        if not downloaded_file:
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if '.mp3' in line and 'has already been downloaded' in line:
                    # Extract filename from the line
                    # Format: [download] audio/filename.mp3 has already been downloaded
                    parts = line.split()
                    for part in parts:
                        if '.mp3' in part and os.path.exists(part):
                            downloaded_file = part
                            break
                    if downloaded_file:
                        break
                elif '.mp3' in line and '[download]' in line:
                    # Extract filename from download line
                    parts = line.split()
                    for part in parts:
                        if '.mp3' in part and os.path.exists(part):
                            downloaded_file = part
                            break
                    if downloaded_file:
                        break
        
        if downloaded_file and os.path.exists(downloaded_file):
            print(f"✅ Download complete: {os.path.basename(downloaded_file)}")
            return downloaded_file
        else:
            raise Exception("Could not locate downloaded file")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Download failed: {e}")
        print(f"Error output: {e.stderr}")
        raise Exception(f"YouTube download failed: {e.stderr}")
    except Exception as e:
        print(f"❌ Download error: {e}")
        raise


def show_model_comparison():
    """Display model comparison information"""
    print("🎯 WHISPER MODEL COMPARISON")
    print("=" * 50)
    print("Model     | Speed    | Accuracy | Memory | Best For")
    print("-" * 50)
    print("tiny      | Very Fast| Basic    | ~1GB   | Quick tests")
    print("base      | Fast     | Fair     | ~1GB   | General use")
    print("small     | Medium   | Good     | ~2GB   | Balanced")
    print("medium    | Slow     | Very Good| ~5GB   | High quality")
    print("large     | Very Slow| Excellent| ~10GB  | Best accuracy")
    print("large-v2  | Very Slow| Excellent+| ~10GB | Improved accuracy")
    print("large-v3  | Very Slow| Best     | ~10GB  | Highest accuracy")
    print("=" * 50)
    print("\n📊 ACCURACY DIFFERENCES:")
    print("• tiny:    ~15-25% word error rate")
    print("• base:    ~10-15% word error rate")
    print("• small:   ~8-12% word error rate")
    print("• medium:  ~5-8% word error rate")
    print("• large:   ~3-6% word error rate")
    print("• large-v2: ~2-5% word error rate")
    print("• large-v3: ~2-4% word error rate")
    print("\n⚡ SPEED ON M1 MACBOOK PRO:")
    print("• tiny:    ~10-20x real-time")
    print("• base:    ~8-15x real-time")
    print("• small:   ~5-10x real-time")
    print("• medium:  ~2-4x real-time")
    print("• large:   ~1-2x real-time")
    print("• large-v2: ~0.8-1.5x real-time")
    print("• large-v3: ~0.5-1x real-time")
    print("\n💡 RECOMMENDATIONS:")
    print("• For testing: tiny")
    print("• For general use: base or small")
    print("• For high quality: medium")
    print("• For best accuracy: large-v3")
    print("\n📖 See MODEL_COMPARISON.md for detailed information")


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio files using OpenAI's Whisper model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python transcribe.py --audio audio.mp3
  python transcribe.py --audio /path/to/recording.wav
  python transcribe.py --audio podcast.m4a --model medium
  python transcribe.py --audio audio.mp3 --output custom.txt
  python transcribe.py --audio audio.mp3 --cleanup
  python transcribe.py --audio audio.mp3 --gpu
  python transcribe.py --audio audio.mp3 --cpu
  python transcribe.py --youtube "https://youtube.com/watch?v=VIDEO_ID" --model small --cleanup
  python transcribe.py --compare-models

Note: Audio files are automatically renamed to lowercase with hyphens instead of spaces.
Special characters, emojis, and punctuation are removed for easier handling.
YouTube videos are downloaded in best quality MP3 format automatically.
        """
    )
    
    parser.add_argument(
        "--audio",
        help="Path to the audio file to transcribe"
    )
    
    parser.add_argument(
        "--model",
        default="large-v3",
        choices=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"],
        help="Whisper model size (default: large-v3 for best quality)"
    )
    
    parser.add_argument(
        "--output",
        help="Output file path (default: same as input with .txt extension)"
    )
    
    parser.add_argument(
        "--compare-models",
        action="store_true",
        help="Show model comparison information"
    )
    
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove audio files after successful transcription (including converted files)"
    )
    
    parser.add_argument(
        "--youtube",
        help="YouTube video URL to download and transcribe (downloads audio automatically)"
    )
    
    parser.add_argument(
        "--gpu",
        action="store_true",
        default=True,
        help="Use GPU acceleration if available (default: enabled)"
    )
    
    parser.add_argument(
        "--cpu",
        action="store_true",
        help="Force CPU usage even if GPU is available"
    )
    
    args = parser.parse_args()
    
    # Show model comparison if requested
    if args.compare_models:
        show_model_comparison()
        return
    
    # Handle YouTube download if URL provided
    if args.youtube:
        if args.audio:
            print("Error: Cannot specify both --audio and --youtube. Choose one.")
            sys.exit(1)
        
        try:
            # Download audio from YouTube
            audio_path_str = download_youtube_audio(args.youtube)
            audio_path = Path(audio_path_str)
            print(f"📁 Downloaded audio: {audio_path}")
        except Exception as e:
            print(f"Error downloading YouTube audio: {e}")
            sys.exit(1)
    else:
        # Validate input file
        if not args.audio:
            print("Error: Must specify either --audio or --youtube")
            sys.exit(1)
            
        audio_path = Path(args.audio)
        if not audio_path.exists():
            print(f"Error: Audio file '{args.audio}' not found.")
            sys.exit(1)
        
        if not audio_path.is_file():
            print(f"Error: '{args.audio}' is not a file.")
            sys.exit(1)
    
    # Create txt folder if it doesn't exist
    txt_folder = Path("txt")
    txt_folder.mkdir(exist_ok=True)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        # Save to txt folder with sanitized filename
        sanitized_name = sanitize_filename(audio_path.stem) + '.txt'
        output_path = txt_folder / sanitized_name
    
    try:
        # Determine GPU usage preference
        use_gpu = not args.cpu  # Use GPU unless --cpu flag is set
        
        # Transcribe the audio
        transcription, files_to_cleanup = transcribe_audio(
            str(audio_path), 
            args.model, 
            args.cleanup,
            use_gpu=use_gpu
        )
        
        if not transcription:
            print("Warning: No transcription generated. The audio might be too short or contain no speech.")
            return
        
        # Display transcription
        print("\n" + "="*60)
        print("📝 TRANSCRIPTION COMPLETE")
        print("="*60)
        print(transcription)
        print("="*60)
        
        # Save to file
        save_transcription(transcription, str(output_path))
        
        # Play completion sound
        play_completion_sound()
        
        # Clean up files if requested
        if args.cleanup:
            cleanup_files(files_to_cleanup)
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
