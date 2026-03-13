import html
import os
import re
from typing import List, Optional, Tuple

from ebooklib import epub


class ConversionError(Exception):
    """Raised when TXT to EPUB conversion fails."""


def _text_to_html_paragraphs(text: str) -> str:
    escaped = html.escape(text)
    return "<p>" + escaped.replace("\n", "<br/>") + "</p>"


def _extract_chapters(content: str, chapter_pattern: str) -> List[Tuple[str, str]]:
    try:
        compiled = re.compile(chapter_pattern)
    except re.error as exc:
        raise ConversionError(f"Invalid chapter pattern: {exc}") from exc

    parts = compiled.split(content)
    if len(parts) < 3:
        raise ConversionError(
            "Chapter pattern did not produce chapters. Try a different regex or leave it empty."
        )

    chapters: List[Tuple[str, str]] = []
    for i in range(1, len(parts), 2):
        title = parts[i].strip("=").strip() or f"Chapter {i // 2 + 1}"
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if not body:
            continue
        chapters.append((title, body))

    if not chapters:
        raise ConversionError("No non-empty chapters were found with the current pattern.")

    return chapters


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
    if not os.path.exists(txt_path):
        raise ConversionError(f"Text file not found: {txt_path}")

    try:
        with open(txt_path, "r", encoding="utf-8") as file:
            content = file.read()
    except OSError as exc:
        raise ConversionError(f"Unable to read text file: {exc}") from exc

    if not content.strip():
        raise ConversionError("The text file is empty.")

    book = epub.EpubBook()
    book.set_identifier(book_id.strip() or "id123456")
    book.set_title(book_title.strip() or "Untitled Book")
    book.set_language(book_language)
    book.add_author(author_name.strip() or "Unknown Author")

    spine = ["nav"]
    toc = []

    if cover_image_path:
        try:
            file_type = os.path.splitext(cover_image_path)[1]
            with open(cover_image_path, "rb") as cover_file:
                cover_image_data = cover_file.read()
            book.set_cover(f"cover{file_type}", cover_image_data)
        except OSError as exc:
            raise ConversionError(f"Unable to read cover image: {exc}") from exc

    if chapter_pattern:
        chapters = _extract_chapters(content, chapter_pattern)
        for index, (title, body) in enumerate(chapters, start=1):
            chapter_file = epub.EpubHtml(
                title=title,
                file_name=f"chap_{index}.xhtml",
                lang=book_language,
            )
            chapter_file.content = f"<html><head></head><body>{_text_to_html_paragraphs(body)}</body></html>"
            book.add_item(chapter_file)
            spine.append(chapter_file)
            toc.append(epub.Link(chapter_file.file_name, title, f"chap_{index}"))
    else:
        chapter_file = epub.EpubHtml(title="Full Text", file_name="full_text.xhtml", lang=book_language)
        chapter_file.content = (
            f"<html><head></head><body>{_text_to_html_paragraphs(content)}</body></html>"
        )
        book.add_item(chapter_file)
        spine.append(chapter_file)
        toc.append(epub.Link(chapter_file.file_name, "Full Text", "full_text"))

    book.toc = tuple(toc)
    book.spine = spine
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    try:
        epub.write_epub(epub_path, book, {})
    except Exception as exc:  # ebooklib raises generic exceptions
        raise ConversionError(f"Error writing EPUB file: {exc}") from exc
