# Quick Start Guide - Updated Features

## 🎯 What Changed?

Your transcribe script now has **two major improvements**:

1. **Subtitle Caching Fixed** ✅
   - Always returns the correct video's subtitles
   - No more getting old cached files from other videos
   
2. **Smart Fallback Transcription** ✨
   - If a video has no subtitles, it automatically transcribes it
   - Uses fast `faster-whisper` implementation
   - Completes in seconds

---

## 📖 How to Use

### Simple: Download Subtitles
```bash
./transcribe.sh --subtitles "https://www.youtube.com/watch?v=VIDEO_ID"
```
**What happens**: Downloads subtitles if available, or transcribes if not

### With Clipboard Copy
```bash
./transcribe.sh --subtitles "https://www.youtube.com/watch?v=VIDEO_ID" --copy
```
**What happens**: Same as above, plus copies the result to your clipboard

### Multiple Videos
```bash
./transcribe.sh --subtitles "URL1" "URL2" "URL3" --copy
```
**What happens**: Each video processed independently. Some might have subtitles, others will be transcribed - all automatic!

---

## 📺 Example Outputs

### When Video HAS Subtitles
```
📥 Downloading subtitles from YouTube: https://...
Video ID: dQw4w9WgXcQ
🔄 Starting subtitle download...
✅ Found file with video ID: Rick Astley - Never Gonna Give You Up...
✅ Subtitle download complete
✅ Converted subtitles to plain text

============================================================
📝 SUBTITLES DOWNLOAD COMPLETE
============================================================
[♪♪♪] ♪ We're no strangers to love ♪ ♪ You know the rules...
```

### When Video has NO Subtitles
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
✅ Download complete
🔄 Using faster-whisper implementation with model 'base'...
⏱️  Processing time: 0m 12s
🚀 Processing speed: 21.0x real-time

============================================================
📝 TRANSCRIPTION COMPLETE (from video, no subtitles)
============================================================
It's your man Alex and in this video I'm going to be showing you guys...
🎵 Playing completion sound
```

---

## ⚡ Performance

| Task | Time | Speed |
|------|------|-------|
| Download Subtitles | Instant | - |
| Transcribe 4m video | 12 seconds | 21x real-time |
| Total for no-subtitle video | ~30 seconds | ⚡ |

---

## 🎁 What You Get

### For Videos WITH Subtitles
- ✅ Correct subtitles (not old cached files)
- ✅ Named with video ID to avoid confusion
- ✅ Saved as both `.vtt` and `.txt` files
- ✅ Works with `--copy` flag

### For Videos WITHOUT Subtitles (New!)
- ✨ Automatic transcription
- ✨ Same output format as subtitles
- ✨ Fast transcription (21x speed)
- ✨ Works with `--copy` flag
- ✨ Cleans up temporary files automatically
- ✨ Beautiful modal warning message

---

## 🔍 How It Works (Technical)

### Subtitle Download Flow
```
User runs command
    ↓
Take snapshot of existing files
    ↓
Try to download subtitles
    ↓
├─ If found: Use new files + return success ✅
└─ If not found: Check if error is "no subtitles"
    ↓
    └─ Download audio → Transcribe → Save ✨
```

### Smart File Detection
- **Before**: Random "most recent file" = wrong video
- **After**: Track files before/after = guaranteed correct video

### Cache Prevention
- Video ID included in filename
- Files tracked by timestamp comparison
- yt-dlp cache disabled
- Force overwrites enabled

---

## 🛠️ Customization

To adjust the transcription settings, edit `transcribe.py` around line 935:

```python
# Change model if needed (default: "base")
model_size="base",  # tiny, base, small, medium, large, large-v3

# Keep audio files if desired (default: cleanup)
cleanup=True,  # Set to False to keep MP3

# Change implementation if needed (default: faster)
implementation="faster",  # Options: faster, whisper
```

---

## 🐛 Troubleshooting

### Issue: "Still getting wrong subtitles"
**Fix**: Subtitles are now tracked by video ID in filename. Old files in `txt/` directory shouldn't interfere anymore.

### Issue: "Transcription is slow"
**Solution**: Already optimized! Uses `faster-whisper` with `base` model for maximum speed.

### Issue: "Want higher quality transcription"
**Fix**: Change `model_size="base"` to `model_size="small"` or `"medium"` in transcribe.py (will be slower)

---

## 📚 See Also

- `CACHE_FIX_EXPLANATION.md` - Deep dive on the caching fix
- `SUBTITLE_FALLBACK_FEATURE.md` - Complete feature documentation
- `IMPROVEMENTS_SUMMARY.md` - Full technical summary

---

## ✅ Verified Working

- ✅ Subtitle downloads correct video
- ✅ Fallback transcription triggered when needed
- ✅ Clipboard copy works for both modes
- ✅ Completion sound plays
- ✅ Auto cleanup of audio files
- ✅ Multiple URLs processed correctly
- ✅ All error messages clear and helpful

---

## 🚀 Ready to Go!

Just use your existing commands - they now work better:

```bash
# This just works now!
./transcribe.sh --subtitles "ANY_YOUTUBE_URL" --copy
```

No more thinking about whether the video has subtitles. The script handles it automatically! 🎉

