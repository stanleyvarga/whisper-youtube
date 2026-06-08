# Subtitle Download Fallback Feature

## Overview

The transcribe script now intelligently handles videos that don't have subtitles by automatically transcribing them instead using the faster-whisper implementation.

## What Changed

### Smart Fallback Logic

When you run:
```bash
./transcribe.sh --subtitles "https://www.youtube.com/watch?v=VIDEO_ID" --copy
```

The script will:

1. **First**: Try to download subtitles from the video
2. **If successful**: Return the subtitles as before ✅
3. **If no subtitles found**: Automatically transcribe the video instead ✨

### Key Features

#### 1. **Automatic Detection**
- Detects when a video has no subtitles
- Shows a friendly warning message with a nice modal-style box
- Transitions seamlessly to transcription

#### 2. **Faster Transcription by Default**
- Uses `faster-whisper` implementation (much faster than regular whisper)
- Uses `base` model for speed (you can adjust in code if needed)
- Automatically cleans up the downloaded audio after transcription

#### 3. **Same Output Format**
- Saves transcription to `.txt` file in the same directory as subtitles
- Works with `--copy` flag (copies to clipboard)
- Shows preview of the result
- Plays completion sound

## Usage Examples

### Example 1: Video WITH Subtitles
```bash
./transcribe.sh --subtitles "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```
✅ **Result**: Downloads subtitles normally

### Example 2: Video WITHOUT Subtitles
```bash
./transcribe.sh --subtitles "https://www.youtube.com/watch?v=HTjXVJ_XU5s" --copy
```
✅ **Result**: 
- Shows "NO SUBTITLES AVAILABLE" warning
- Downloads the audio
- Transcribes it using faster-whisper
- Copies the transcription to clipboard

### Example 3: Multiple Videos
```bash
./transcribe.sh --subtitles "URL1" "URL2" "URL3"
```
- Each URL is processed independently
- Some might have subtitles, others might be transcribed
- All handled automatically!

## Output Examples

### When Subtitles are Found
```
📥 Downloading subtitles from YouTube: https://...
Video ID: dQw4w9WgXcQ
🔄 Starting subtitle download...
✅ Found file with video ID: Rick Astley - Never Gonna Give You Up...
✅ Subtitle download complete: ...
✅ Converted subtitles to plain text: ...
```

### When No Subtitles (Fallback to Transcription)
```
📥 Downloading subtitles from YouTube: https://...
Video ID: HTjXVJ_XU5s
🔄 Starting subtitle download...
❌ The video has no subtitles available!

============================================================
⚠️  NO SUBTITLES AVAILABLE
============================================================
The video has no subtitles, but we can transcribe it instead!
🔄 Downloading video and transcribing with faster-whisper...
============================================================

📥 Downloading audio from YouTube: https://...
✅ Download complete: ...
🔄 Using faster-whisper implementation with model 'base'...
⏱️  Processing time: 0m 12s
🚀 Processing speed: 21.0x real-time
📋 Copied transcription to clipboard (4033 characters)

============================================================
📝 TRANSCRIPTION COMPLETE (from video, no subtitles)
============================================================
```

## Technical Details

### Implementation Changes

**File**: `transcribe.py`
**Function**: Error handling in `main()` function (lines 916-971)

#### What Happens:
1. Catches the "no subtitles" exception
2. Checks if error message contains "no subtitles"
3. If yes, downloads the audio using `download_youtube_audio()`
4. Transcribes using `transcribe_audio()` with:
   - `implementation="faster"` (faster-whisper)
   - `model_size="base"` (balanced speed/quality)
   - `cleanup=True` (removes audio after transcription)
5. Saves and optionally copies to clipboard
6. Shows completion with modal-style formatting

### Performance

- **Average speed**: 21x real-time (much faster than regular whisper)
- **Model used**: `base` (lightweight but accurate)
- **Cleanup**: Audio file automatically deleted after transcription
- **Time for 4:21 video**: ~12 seconds ⚡

## Configuration

To adjust the fallback transcription behavior, modify these lines in `transcribe.py`:

```python
# Change model size if needed
model_size="base",  # Options: tiny, base, small, medium, large, large-v3

# Change to False if you want to keep the audio files
cleanup=True,

# Change implementation if desired
implementation="faster",  # Options: faster, whisper
```

## Edge Cases Handled

1. ✅ Video has subtitles → Returns subtitles
2. ✅ Video has no subtitles → Transcribes automatically
3. ✅ Multiple URLs, mixed subtitles/no-subtitles → Each handled appropriately
4. ✅ `--copy` flag works with both subtitles and transcriptions
5. ✅ Transcription saves to same directory as subtitles would
6. ✅ Completion sound plays regardless of subtitle/transcription mode

## Benefits

- **No Manual Intervention**: Automatic fallback, no user prompts needed
- **Consistent Experience**: Same output format for both subtitles and transcriptions
- **Fast**: Uses faster-whisper for quick results
- **Clean**: Automatically removes temporary audio files
- **Informative**: Clear visual feedback about what's happening

