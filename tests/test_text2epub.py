import tempfile
import unittest
from pathlib import Path

from text2epub import (
    _build_chapters,
    _detect_chapter_pattern,
    _extract_chapters,
    _read_text_file,
    _text_to_html_paragraphs,
)


class TextToEpubTests(unittest.TestCase):
    def test_html_paragraphs_escape_content(self):
        html = _text_to_html_paragraphs("One & two\nline <tag>\n\nNext")

        self.assertIn("One &amp; two<br/>line &lt;tag&gt;", html)
        self.assertIn("<p>Next</p>", html)

    def test_extract_chapters_without_capture_group(self):
        content = "intro\nChapter 1 Start\nBody one\nChapter 2 End\nBody two"
        chapters = _extract_chapters(content, r"^Chapter\s+\d+.*$")

        self.assertEqual(
            chapters,
            [
                ("Preface", "intro"),
                ("Chapter 1 Start", "Body one"),
                ("Chapter 2 End", "Body two"),
            ],
        )

    def test_extract_chapters_with_capture_group(self):
        content = "== Alpha ==\nBody one\n== Beta ==\nBody two"
        chapters = _extract_chapters(content, r"^==\s*(.*?)\s*==$")

        self.assertEqual(chapters, [("Alpha", "Body one"), ("Beta", "Body two")])

    def test_extract_chapters_with_named_title_group(self):
        content = "第一章外乡人\nBody one\n第二章“恶作剧”\nBody two"
        chapters = _extract_chapters(content, r"^(?P<title>第[一二三四五六七八九十]+章.*)$")

        self.assertEqual(chapters, [("第一章外乡人", "Body one"), ("第二章“恶作剧”", "Body two")])

    def test_auto_detects_chinese_chapters(self):
        content = "简介\n第一章外乡人\nBody one\n第二章“恶作剧”\nBody two"

        self.assertIsNotNone(_detect_chapter_pattern(content))
        self.assertEqual(
            _build_chapters(content),
            [("Preface", "简介"), ("第一章外乡人", "Body one"), ("第二章“恶作剧”", "Body two")],
        )

    def test_auto_detection_falls_back_to_full_text(self):
        self.assertEqual(_build_chapters("Only one body"), [("Full Text", "Only one body")])

    def test_read_text_file_accepts_gb18030(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            txt_path = Path(tmpdir) / "book.txt"
            txt_path.write_bytes("第一章".encode("gb18030"))

            self.assertEqual(_read_text_file(txt_path), "第一章")


if __name__ == "__main__":
    unittest.main()
