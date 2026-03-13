# TXT to EPUB Converter

## Overview
A modern PyQt5 desktop app that converts plain text files (`*.txt`) into EPUB ebooks. The interface is organized into polished sections for metadata, file selection, and chapter parsing.

## Highlights
- Clean, modern UI styling with grouped cards and a conversion status bar.
- Metadata controls for title, author, language, and unique book ID.
- File pickers for source TXT, optional cover image, and custom EPUB output path.
- Regex-based chapter splitting with safe validation and clear error messages.
- HTML-escaped content generation to avoid malformed chapter output.

## Requirements
- Python 3.8+
- PyQt5
- ebooklib

Install dependencies:

```bash
pip install PyQt5 ebooklib
```

## Run

```bash
python converter.py
```

## Chapter Pattern Example
If chapters are delimited like `=== Chapter 1 ===`, `=== Chapter 2 ===`, use:

```regex
(===\s*.*?\s*===)
```

Leave the chapter pattern empty to create one chapter from the full text.
