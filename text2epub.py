import re

from ebooklib import epub


def txt_to_epub(txt_path, epub_path, cover_image_path=None):
    # Read the text file using UTF-8 encoding
    with open(txt_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Split the text into chapters based on the "===<title>===" pattern
    chapters = re.split(r'(===\s*.*?\s*===)', content)  # Keep the delimiters in the result

    # Create a new EPUB book
    book = epub.EpubBook()

    # Set metadata
    # Set metadata
    book.set_identifier('id1234567')
    book.set_title('高天之上')  # Example Book in Chinese
    book.set_language('zh')

    # Add author
    book.add_author('阴天神隐')  # Author Name in Chinese

    # Initialize the spine (needed for the book structure)
    spine = ['nav']  # Include navigation at the start of the spine

    # Add cover image
    if cover_image_path:
        book.set_cover("cover.png", open(cover_image_path, 'rb').read())

        # Process chapters
        for i in range(1, len(chapters), 2):
            title = chapters[i].strip().strip('=').strip()
            text = chapters[i] + '\n' + chapters[i + 1].strip()

            # Create an EPUB HTML document for each chapter
            chapter_file = epub.EpubHtml(title=title, file_name=f'chap_{i // 2 + 1}.xhtml', lang='zh')
            chapter_file.content = '<html><head></head><body><p>' + text.replace('\n', '<br/>') + '</p></body></html>'

            # Add chapter to the book
            book.add_item(chapter_file)

            # Append chapter to the spine
            spine.append(chapter_file)

            # Add chapter to the table of contents
            book.toc.append(epub.Link(chapter_file.file_name, title, f'chap_{i // 2 + 1}'))

        # Define the EPUB spine and table of contents
        book.spine = spine

        # Add default NCX and Nav file
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Write the EPUB file
        epub.write_epub(epub_path, book, {})


# Usage
txt_to_epub('books/《高天之上》.txt', 'books/《高天之上》.epub', "books/cover.png")
