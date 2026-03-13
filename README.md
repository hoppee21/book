# TXT to EPUB Converter

## Overview
This project provides a PyQt5 desktop interface to convert plain text files (`*.txt`) into EPUB ebooks. It supports metadata editing, optional cover images, and regex-based chapter splitting.

## Highlights
- Improved and grouped UI sections for metadata, file selection, and chapter detection.
- Stronger conversion validation with clear error dialogs.
- Safer chapter parsing with regex validation and helpful failure messages.
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

Leave the chapter pattern empty to create a single chapter for the full text.
