# Subtitle Caching Fix - Explanation

## Problem

When downloading subtitles from YouTube, the script was returning subtitles from previously downloaded videos instead of the correct video specified in the command.

**Example Issue:**
- Running: `./transcribe.sh --subtitles "https://www.youtube.com/watch?v=HTjXVJ_XU5s" --copy`
- Expected: Subtitles from video with ID `HTjXVJ_XU5s`
- Actual: Subtitles from a different video about "flatbread" (an old cached file)

## Root Causes

The original code had several issues:

1. **Poor File Detection**: The fallback logic was using `glob.glob()` to find "the most recently modified .vtt file" in the entire `txt/` directory, which could pick up old files from previous downloads.

2. **No Initial Snapshot**: The code didn't track which files existed before the download, making it impossible to distinguish newly created files from old ones.

3. **No Error Handling for Missing Subtitles**: If a video had no subtitles, the code would still try to find "the most recent file" and return an old cached file instead of properly reporting the error.

4. **No Video ID Enforcement**: While video IDs were included in filenames, the fallback detection wasn't specifically looking for them.

## The Fix

### 1. **File Tracking (Lines 481-482)**
   - Create a snapshot of existing files BEFORE downloading
   - Compare files before/after to identify newly created files
   ```python
   files_before_download = set(glob.glob(f"{output_dir}/*"))
   ```

### 2. **Better Error Detection (Lines 507-509)**
   - Check for specific error messages from yt-dlp
   - Detect when subtitles genuinely aren't available
   ```python
   if 'There are no subtitles' in output_combined or ('has no' in output_combined and 'subtitle' in output_combined):
   ```

### 3. **Improved File Detection Logic (Lines 552-573)**
   - **Priority 1**: Look for newly created files (files that didn't exist before)
   - **Priority 2**: Look for files with the specific video ID in the filename
   - **No Priority 3**: Don't fall back to "most recent file" from old cache

### 4. **yt-dlp Options**
   - Added `--force-overwrites`: Ensures files are actually downloaded, not reused
   - Added `--no-cache-dir`: Prevents yt-dlp from using its own cache
   - Added `--no-part`: Prevents incomplete .part files

## How It Works Now

1. Before downloading, the script creates a list of all existing files in `txt/`
2. It runs yt-dlp to download the subtitles with the specific video ID in the filename
3. After download, it checks for newly created files
4. If new files exist, it uses them (guaranteed to be the correct video)
5. If no new files but video ID found in filename, use those
6. If no subtitles at all, report error instead of returning wrong file

## Testing

### Test Case 1: Video with Subtitles ✅
```bash
./transcribe.sh --subtitles "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --copy
```
Result: Downloads and returns correct subtitles for Rick Astley video

### Test Case 2: Video without Subtitles ✅
```bash
./transcribe.sh --subtitles "https://www.youtube.com/watch?v=HTjXVJ_XU5s" --copy
```
Result: Shows clear error message instead of returning old cached subtitles

## Files Modified

- `transcribe.py`: Updated `download_youtube_subtitles()` function with:
  - File tracking before/after download
  - Better error detection
  - Improved file selection logic
  - Added video ID in debug output

## Benefits

1. **Correctness**: Always returns subtitles for the requested video
2. **Transparency**: Clear error messages when subtitles unavailable
3. **No Cache Pollution**: New downloads always override old cache
4. **Future-Proof**: Even if many old files exist, new downloads are correctly identified

