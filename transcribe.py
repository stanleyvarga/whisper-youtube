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
    try:
        from faster_whisper import WhisperModel
        FASTER_WHISPER_AVAILABLE = True
    except ImportError:
        FASTER_WHISPER_AVAILABLE = False
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


def transcribe_audio(audio_file_path, model_size="large-v3", cleanup=False, implementation="whisper"):
    """
    Transcribe audio file using Whisper model
    
    Args:
        audio_file_path (str): Path to the audio file
        model_size (str): Whisper model size (large-v3 for best quality)
        cleanup (bool): Whether to remove audio files after successful transcription
        implementation (str): Either 'whisper' or 'faster' to choose the implementation
    
    Returns:
        tuple: (transcribed_text, files_to_cleanup)
    """
    # Validate implementation choice
    if implementation == "faster" and not FASTER_WHISPER_AVAILABLE:
        print("⚠️  faster-whisper not available. Falling back to default whisper implementation.")
        implementation = "whisper"
    
    impl_name = "faster-whisper" if implementation == "faster" else "whisper"
    print(f"🔄 Using {impl_name} implementation with model '{model_size}'...")
    
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
    
    # Initialize Whisper model based on implementation
    if implementation == "faster":
        print(f"⚡ Using faster-whisper with model '{model_size}'...")
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
    else:
        model = whisper.load_model(model_size)
    
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
    
    # Transcribe the audio based on implementation
    if implementation == "faster":
        # Use faster-whisper implementation
        segments, info = model.transcribe(
            actual_audio_path,
            language="en",
            beam_size=5,
            word_timestamps=False,
            temperature=0.0
        )
        
        # Collect the transcription text
        transcription_parts = []
        for segment in segments:
            transcription_parts.append(segment.text)
        result_text = " ".join(transcription_parts).strip()
        
        detected_language = info.language
        
    else:
        # Use default whisper implementation
        result = model.transcribe(
            actual_audio_path,
            language="en",  # English only for better accuracy
            fp16=False,     # Use fp32 for better compatibility
            verbose=True,    # Enable verbose output for progress
            word_timestamps=False,  # Disable word timestamps for speed
            temperature=0.0,  # Use deterministic sampling for consistency
            compression_ratio_threshold=2.4,  # Skip audio that's likely not speech
            logprob_threshold=-1.0,  # Skip segments with low confidence
            no_speech_threshold=0.6  # Skip segments likely to be silence
        )
        result_text = result["text"].strip()
        detected_language = result['language']
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Format processing time
    processing_time_str = f"{int(processing_time//60)}m {int(processing_time%60)}s"
    
    print("-" * 50)
    print(f"✅ Detected language: {detected_language}")
    print(f"⏱️  Processing time: {processing_time_str}")
    
    speed_ratio = None
    speed_ratio_str = None
    if duration:
        speed_ratio = duration / processing_time
        speed_ratio_str = f"{speed_ratio:.1f}x"
        print(f"🚀 Processing speed: {speed_ratio_str} real-time")
    
    # Prepare benchmark data
    benchmark_data = {
        'timestamp': None,  # Will be set in main()
        'implementation': impl_name,
        'model': model_size,
        'audio_duration': f"{int(duration//60)}m {int(duration%60)}s" if duration else None,
        'processing_time': processing_time_str,
        'speed_ratio': speed_ratio_str,
        'detected_language': detected_language,
        'processing_time_seconds': processing_time
    }
    
    return result_text, files_to_cleanup, benchmark_data


def format_benchmark_header(benchmark_data):
    """
    Format benchmark data as a header comment for the transcript
    
    Args:
        benchmark_data (dict): Dictionary containing benchmark information
    
    Returns:
        str: Formatted benchmark header
    """
    from datetime import datetime
    
    header = "# " + "="*60 + "\n"
    header += "# TRANSCRIPTION BENCHMARK DATA\n"
    header += "# " + "="*60 + "\n"
    header += f"# Generated: {benchmark_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}\n"
    header += f"# Implementation: {benchmark_data.get('implementation', 'unknown')}\n"
    header += f"# Model: {benchmark_data.get('model', 'unknown')}\n"
    
    if benchmark_data.get('audio_duration'):
        header += f"# Audio Duration: {benchmark_data['audio_duration']}\n"
    
    if benchmark_data.get('processing_time'):
        header += f"# Processing Time: {benchmark_data['processing_time']}\n"
    
    if benchmark_data.get('speed_ratio'):
        header += f"# Speed: {benchmark_data['speed_ratio']}x real-time\n"
    
    if benchmark_data.get('detected_language'):
        header += f"# Detected Language: {benchmark_data['detected_language']}\n"
    
    header += "# " + "="*60 + "\n\n"
    
    return header


def save_transcription(text, output_path, benchmark_data=None):
    """
    Save transcription to text file with optional benchmark header
    
    Args:
        text (str): Transcription text
        output_path (str): Path to save the file
        benchmark_data (dict): Optional benchmark data to include as header
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        if benchmark_data:
            header = format_benchmark_header(benchmark_data)
            f.write(header)
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


def download_youtube_subtitles(url, output_dir="txt"):
    """
    Download subtitles from YouTube video using yt-dlp
    
    Args:
        url (str): YouTube video URL
        output_dir (str): Directory to save the subtitle file
        
    Returns:
        str: Path to the downloaded subtitle file
    """
    import subprocess
    
    print(f"📥 Downloading subtitles from YouTube: {url}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Use yt-dlp to download subtitles
    cmd = [
        'yt-dlp',
        '--write-sub',
        '--write-auto-sub',  # Also try auto-generated subtitles if manual aren't available
        '--sub-lang', 'en',  # Prioritize English subtitles
        '--sub-format', 'vtt',  # Use VTT format (we'll convert to plain text)
        '--skip-download',  # Don't download video/audio
        '--output', f'{output_dir}/%(title)s.%(ext)s',
        url
    ]
    
    try:
        print("🔄 Starting subtitle download...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Look for downloaded subtitle files
        import glob
        subtitle_files = glob.glob(f"{output_dir}/*.vtt")
        
        if not subtitle_files:
            # Try to find any subtitle files
            subtitle_files = glob.glob(f"{output_dir}/*.*")
            subtitle_files = [f for f in subtitle_files if Path(f).suffix in ['.vtt', '.srt', '.txt', '.srv1', '.srv2', '.srv3']]
        
        if subtitle_files:
            # Get the most recently modified subtitle file
            downloaded_file = max(subtitle_files, key=os.path.getmtime)
            print(f"✅ Subtitle download complete: {os.path.basename(downloaded_file)}")
            return downloaded_file
        else:
            raise Exception("Could not locate downloaded subtitle file")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Subtitle download failed: {e}")
        print(f"Error output: {e.stderr}")
        raise Exception(f"YouTube subtitle download failed: {e.stderr}")
    except Exception as e:
        print(f"❌ Subtitle download error: {e}")
        raise


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
  python transcribe.py --audio audio.mp3 --benchmark
  python transcribe.py --audio audio.mp3 --implementation faster --benchmark
  python transcribe.py --youtube "https://youtube.com/watch?v=VIDEO_ID" --model small --cleanup
  python transcribe.py --subtitles "https://youtube.com/watch?v=VIDEO_ID"
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
        "--subtitles",
        help="YouTube video URL to download subtitles directly (no transcription needed)"
    )
    
    parser.add_argument(
        "--implementation",
        default="whisper",
        choices=["whisper", "faster"],
        help="Choose implementation: 'whisper' (default OpenAI) or 'faster' (faster-whisper)"
    )
    
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Include benchmark data header in the transcript output"
    )
    
    args = parser.parse_args()
    
    # Show model comparison if requested
    if args.compare_models:
        show_model_comparison()
        return
    
    # Handle YouTube subtitles download if URL provided
    if args.subtitles:
        if args.audio or args.youtube:
            print("Error: Cannot specify --subtitles with --audio or --youtube. Choose one.")
            sys.exit(1)
        
        try:
            # Download subtitles from YouTube
            subtitles_path_str = download_youtube_subtitles(args.subtitles)
            subtitles_path = Path(subtitles_path_str)
            print(f"📁 Downloaded subtitles: {subtitles_path}")
            
            # Convert VTT to plain text if needed
            if subtitles_path.suffix == '.vtt':
                # Simple VTT to text conversion
                with open(subtitles_path, 'r', encoding='utf-8') as f:
                    vtt_content = f.read()
                
                # Simple regex to extract text from VTT
                import re
                # Remove VTT timestamps and metadata
                text_lines = []
                for line in vtt_content.split('\n'):
                    line = line.strip()
                    # Skip metadata and timestamps
                    if line and not line.startswith('WEBVTT') and not '-->' in line and not line.startswith('NOTE'):
                        if not re.match(r'^\d+$', line):  # Skip cue numbers
                            text_lines.append(line)
                
                text_content = '\n'.join(text_lines).strip()
                
                # Save as .txt
                txt_path = subtitles_path.with_suffix('.txt')
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                
                print(f"✅ Converted subtitles to plain text: {txt_path}")
                print("\n" + "="*60)
                print("📝 SUBTITLES DOWNLOAD COMPLETE")
                print("="*60)
                print(text_content[:500] + "..." if len(text_content) > 500 else text_content)
                print("="*60)
                
            return
            
        except Exception as e:
            print(f"Error downloading YouTube subtitles: {e}")
            sys.exit(1)
    
    # Handle YouTube download if URL provided
    elif args.youtube:
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
            print("Error: Must specify either --audio, --youtube, or --subtitles")
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
        # Transcribe the audio
        transcription, files_to_cleanup, benchmark_data = transcribe_audio(
            str(audio_path), 
            args.model, 
            args.cleanup,
            args.implementation
        )
        
        if not transcription:
            print("Warning: No transcription generated. The audio might be too short or contain no speech.")
            return
        
        # Add timestamp to benchmark data if benchmarking is enabled
        if args.benchmark:
            from datetime import datetime
            benchmark_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Display transcription
        print("\n" + "="*60)
        print("📝 TRANSCRIPTION COMPLETE")
        print("="*60)
        print(transcription)
        print("="*60)
        
        # Save to file with optional benchmark data
        benchmark_data_to_save = benchmark_data if args.benchmark else None
        save_transcription(transcription, str(output_path), benchmark_data_to_save)
        
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
