# TXT to EPUB Converter

## Overview
This application provides a graphical user interface to convert text files (`*.txt`) into EPUB format, suitable for e-readers. It supports custom book metadata, optional cover images, and chapter division based on a user-defined regex pattern.

## Features
- **File Conversion:** Convert any plain text file into an EPUB ebook.
- **Metadata Customization:** Set the title, author, language, and a unique book ID for the EPUB.
- **Chapter Detection:** Automatically divide the book into chapters based on a regex pattern.
- **Cover Image:** Add a cover image to the EPUB from PNG, JPG, or JPEG files.
- **Language Selection:** Choose the book's language from a predefined list including English, Chinese, Spanish, French, and German.

## Requirements
- Python 3.6 or higher
- PyQt5
- ebooklib

To install the necessary Python packages, run:
```bash
pip install PyQt5 ebooklib
