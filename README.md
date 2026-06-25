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
python3 -m pip install -r requirements.txt
```

## Run

```bash
python3 converter.py
```

## macOS Setup

On macOS, use the project-local conda environment:

```bash
conda env create --prefix ./.conda --file environment.yml
conda activate ./.conda
python converter.py
```

If the environment already exists, only activate it:

```bash
conda activate ./.conda
python converter.py
```

Alternatively, use a Python virtual environment so the PyQt5 and ebooklib packages stay isolated from the system Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 converter.py
```

The app uses native macOS file dialogs, remembers the most recently selected folder during a session, and lets you choose the output `.epub` path explicitly.

## Chapter Pattern Example
If chapters are delimited like `=== Chapter 1 ===`, `=== Chapter 2 ===`, use:

```regex
(===\s*.*?\s*===)
```

Leave the chapter pattern empty to auto-detect common chapter headings. If no chapters are detected, the converter creates a single chapter for the full text.

Chapter regexes can be written with or without a capture group. For example, this also works for line-based chapter headings:

```regex
^Chapter\s+\d+.*$
```

Chinese headings such as `第一章外乡人` are detected automatically.
