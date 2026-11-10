import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import transcribe


class DownloadYoutubeSubtitlesLanguageTest(unittest.TestCase):
    def test_passes_language_to_yt_dlp_sub_lang(self):
        with tempfile.TemporaryDirectory() as tmp:
            vtt_path = Path(tmp) / "video-[abc123def45].cs.vtt"
            vtt_path.write_text(
                "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nAhoj\n",
                encoding="utf-8",
            )

            mock_result = MagicMock()
            mock_result.stdout = f"Writing video subtitles to: {vtt_path}\n"
            mock_result.stderr = ""

            with patch("subprocess.run", return_value=mock_result) as mock_run:
                path = transcribe.download_youtube_subtitles(
                    "https://www.youtube.com/watch?v=umnTAiMUodk",
                    output_dir=tmp,
                    language="cs",
                )

            self.assertEqual(path, str(vtt_path))
            cmd = mock_run.call_args.args[0]
            self.assertIn("--sub-lang", cmd)
            self.assertEqual(cmd[cmd.index("--sub-lang") + 1], "cs")

    def test_defaults_sub_lang_to_en(self):
        with tempfile.TemporaryDirectory() as tmp:
            vtt_path = Path(tmp) / "video-[abc123def45].en.vtt"
            vtt_path.write_text(
                "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nHi\n",
                encoding="utf-8",
            )

            mock_result = MagicMock()
            mock_result.stdout = f"Writing video subtitles to: {vtt_path}\n"
            mock_result.stderr = ""

            with patch("subprocess.run", return_value=mock_result) as mock_run:
                transcribe.download_youtube_subtitles(
                    "https://www.youtube.com/watch?v=umnTAiMUodk",
                    output_dir=tmp,
                )

            cmd = mock_run.call_args.args[0]
            self.assertEqual(cmd[cmd.index("--sub-lang") + 1], "en")


if __name__ == "__main__":
    unittest.main()
