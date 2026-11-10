   1 # Subtitle language via `--language`
   2 
   3 **Date:** 2026-11-10  
   4 **Status:** Approved design
   5 
   6 ## Problem
   7 
   8 `--txt` / `--subtitles` already download YouTube captions and convert VTT → TXT, but `download_youtube_subtitles` hardcodes `--sub-lang en`. Non-English videos (e.g. Czech `cs`) need a manual yt-dlp invocation. Existing `--language` only affects Whisper transcription and subtitle-fallback transcription.
   9 
  10 ## Goal
  11 
  12 Make this work easily:
  13 
  14 ```bash
  15 ./transcribe.sh --txt "https://www.youtube.com/watch?v=umnTAiMUodk" --language cs
  16 ```
  17 
  18 Default remains `en`. No new flags.
  19 
  20 ## Non-goals
  21 
  22 - SRT download/conversion (keep VTT → TXT)
  23 - Multi-language fallback lists (`cs,en`)
  24 - Changes to `transcribe.sh` argument passthrough (already forwards `--language` / `--txt`)
  25 
  26 ## Design
  27 
  28 ### Data flow
  29 
  30 1. User runs `--txt` or `--subtitles` with optional `--language LANG` (default `en`).
  31 2. `download_youtube_subtitles(url, output_dir, language=LANG)` calls yt-dlp with `--sub-lang LANG`, `--write-sub`, `--write-auto-sub`, `--sub-format vtt`, `--skip-download`.
  32 3. On success: convert `.vtt` → `.txt` (existing logic). `--txt` deletes the `.vtt`.
  33 4. On no captions: existing fallback downloads audio and runs Whisper with the same `args.language`.
  34 
  35 ### Code changes
  36 
  37 | File | Change |
  38 |------|--------|
  39 | `transcribe.py` | Add `language="en"` param to `download_youtube_subtitles`; use it in `--sub-lang`; pass `args.language` at call site; update `--language` help text |
  40 | `README.md` | Document that `--language` applies to subtitle download; add non-English `--txt` example |
  41 
  42 File discovery already matches any `*.vtt` (including `*.cs.vtt`); no change required there.
  43 
  44 ### Success criteria
  45 
  46 - `./transcribe.sh --txt "<czech video URL>" --language cs` writes a `.txt` under `txt/` without keeping `.vtt`.
  47 - `./transcribe.sh --txt "<english video URL>"` still defaults to English captions.
  48 - Subtitle fallback transcription continues to honor `--language`.
