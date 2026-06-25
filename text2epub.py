import html
import re
from pathlib import Path
from typing import List, Optional, Tuple

SUPPORTED_TEXT_ENCODINGS = (
    "utf-8-sig",
    "utf-16",
    "gb18030",
    "big5",
    "latin-1",
)

SUPPORTED_COVER_EXTENSIONS = {".jpg", ".jpeg", ".png"}
CHAPTER_TITLE_STRIP_CHARS = " \t\r\n=#*-_"
MIN_AUTO_CHAPTER_MATCHES = 2
AUTO_CHAPTER_PATTERNS = (
    r"^[ \t]*(?P<title>第[零〇一二三四五六七八九十百千万两0-9]+章[ \t　]*[^\r\n]{0,80})[ \t]*$",
    r"^[ \t]*(?P<title>Chapter[ \t]+[0-9]+[^\r\n]{0,80})[ \t]*$",
    r"^[ \t]*(?P<title>(?:序章|楔子|尾声|后记|番外)[^\r\n]{0,80})[ \t]*$",
)
DEFAULT_EPUB_STYLESHEET = """
body {
    font-family: serif;
    line-height: 1.65;
    margin: 5%;
}
p {
    margin: 0 0 1em;
}
h1 {
    font-size: 1.35em;
    margin: 0 0 1.2em;
}
""".strip()


class ConversionError(Exception):
    """Raised when TXT to EPUB conversion fails."""


def _text_to_html_paragraphs(text: str) -> str:
    paragraphs = re.split(r"\n\s*\n+", text.strip())
    html_paragraphs = []

    for paragraph in paragraphs:
        lines = [html.escape(line.rstrip()) for line in paragraph.splitlines()]
        body = "<br/>".join(line for line in lines if line)
        if body:
            html_paragraphs.append(f"<p>{body}</p>")

    return "\n".join(html_paragraphs) or "<p></p>"


def _read_text_file(txt_path: Path) -> str:
    last_decode_error: Optional[UnicodeError] = None

    for encoding in SUPPORTED_TEXT_ENCODINGS:
        try:
            return txt_path.read_text(encoding=encoding)
        except UnicodeError as exc:
            last_decode_error = exc
        except OSError as exc:
            raise ConversionError(f"Unable to read text file: {exc}") from exc

    raise ConversionError(
        "Unable to decode text file. Tried: "
        + ", ".join(SUPPORTED_TEXT_ENCODINGS)
        + f". Last error: {last_decode_error}"
    )


def _load_epub_module():
    try:
        from ebooklib import epub
    except ImportError as exc:
        raise ConversionError(
            "Missing dependency: ebooklib. Install it with `python3 -m pip install -r requirements.txt`."
        ) from exc

    return epub


def _clean_chapter_title(raw_title: str, fallback: str) -> str:
    title = raw_title.strip().strip(CHAPTER_TITLE_STRIP_CHARS).strip()
    return title or fallback


def _title_from_match(match: re.Match, fallback: str) -> str:
    raw_title = match.groupdict().get("title")
    if raw_title is None and match.lastindex:
        raw_title = match.group(1)
    if not raw_title:
        raw_title = match.group(0)
    return _clean_chapter_title(raw_title, fallback)


def _detect_chapter_pattern(content: str) -> Optional[str]:
    for pattern in AUTO_CHAPTER_PATTERNS:
        matches = list(re.finditer(pattern, content, re.MULTILINE))
        if len(matches) >= MIN_AUTO_CHAPTER_MATCHES:
            return pattern
    return None


def _extract_chapters(content: str, chapter_pattern: str) -> List[Tuple[str, str]]:
    try:
        compiled = re.compile(chapter_pattern, re.MULTILINE)
    except re.error as exc:
        raise ConversionError(f"Invalid chapter pattern: {exc}") from exc

    matches = list(compiled.finditer(content))
    if not matches:
        raise ConversionError(
            "Chapter pattern did not produce chapters. Try a different regex or leave it empty."
        )

    if any(match.start() == match.end() for match in matches):
        raise ConversionError("Chapter pattern matched empty text. Please use a more specific regex.")

    chapters: List[Tuple[str, str]] = []

    preface = content[: matches[0].start()].strip()
    if preface:
        chapters.append(("Preface", preface))

    for index, match in enumerate(matches, start=1):
        next_match = matches[index] if index < len(matches) else None
        body_start = match.end()
        body_end = next_match.start() if next_match else len(content)

        title = _title_from_match(match, f"Chapter {index}")
        body = content[body_start:body_end].strip()
        if not body:
            continue
        chapters.append((title, body))

    if not chapters:
        raise ConversionError("No non-empty chapters were found with the current pattern.")

    return chapters


def _build_chapters(content: str, chapter_pattern: Optional[str] = None) -> List[Tuple[str, str]]:
    effective_pattern = chapter_pattern or _detect_chapter_pattern(content)
    if effective_pattern:
        return _extract_chapters(content, effective_pattern)
    return [("Full Text", content.strip())]


def _chapter_content(title: str, body: str) -> str:
    safe_title = html.escape(title)
    return f"<h1>{safe_title}</h1>\n{_text_to_html_paragraphs(body)}"


def txt_to_epub(
    txt_path: str,
    epub_path: str,
    cover_image_path: Optional[str] = None,
    chapter_pattern: Optional[str] = None,
    book_id: str = "id123456",
    book_title: str = "Sample Book",
    book_language: str = "en",
    author_name: str = "Author Name",
) -> None:
    epub = _load_epub_module()
    txt_file = Path(txt_path).expanduser()
    epub_file = Path(epub_path).expanduser()

    if not txt_file.is_file():
        raise ConversionError(f"Text file not found: {txt_file}")

    content = _read_text_file(txt_file)

    if not content.strip():
        raise ConversionError("The text file is empty.")

    book = epub.EpubBook()
    book.set_identifier(book_id.strip() or "id123456")
    book.set_title(book_title.strip() or "Untitled Book")
    book.set_language((book_language or "en").strip() or "en")
    book.add_author(author_name.strip() or "Unknown Author")

    spine = ["nav"]
    toc = []

    if cover_image_path:
        cover_file = Path(cover_image_path).expanduser()
        if not cover_file.is_file():
            raise ConversionError(f"Cover image not found: {cover_file}")

        file_type = cover_file.suffix.lower()
        if file_type not in SUPPORTED_COVER_EXTENSIONS:
            raise ConversionError(
                "Unsupported cover image type. Please use a PNG or JPEG image."
            )

        try:
            cover_image_data = cover_file.read_bytes()
            book.set_cover(f"cover{file_type}", cover_image_data)
        except OSError as exc:
            raise ConversionError(f"Unable to read cover image: {exc}") from exc

    stylesheet = epub.EpubItem(
        uid="book_style",
        file_name="style/book.css",
        media_type="text/css",
        content=DEFAULT_EPUB_STYLESHEET,
    )
    book.add_item(stylesheet)

    chapters = _build_chapters(content, chapter_pattern)
    for index, (title, body) in enumerate(chapters, start=1):
        item_id = "full_text" if len(chapters) == 1 else f"chap_{index}"
        file_name = "full_text.xhtml" if item_id == "full_text" else f"{item_id}.xhtml"
        chapter_file = epub.EpubHtml(
            title=title,
            file_name=file_name,
            lang=(book_language or "en"),
        )
        chapter_file.content = _chapter_content(title, body)
        chapter_file.add_item(stylesheet)
        book.add_item(chapter_file)
        spine.append(chapter_file)
        toc.append(epub.Link(chapter_file.file_name, title, item_id))

    book.toc = tuple(toc)
    book.spine = spine
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    try:
        epub_file.parent.mkdir(parents=True, exist_ok=True)
        epub.write_epub(str(epub_file), book, {})
    except Exception as exc:  # ebooklib raises generic exceptions
        raise ConversionError(f"Error writing EPUB file: {exc}") from exc
