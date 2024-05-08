import os
import re

from ebooklib import epub


def txt_to_epub(txt_path, epub_path, cover_image_path=None, chapter_pattern=None, book_id='id123456',
                book_title='Sample Book', book_language='zh', author_name='Author Name'):
    try:
        # Read the text file using UTF-8 encoding
        with open(txt_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except IOError:
        print(f"Error: File {txt_path} cannot be opened.")
        return

    # Create a new EPUB book
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier(book_id)
    book.set_title(book_title)
    book.set_language(book_language)

    # Add author
    book.add_author(author_name)

    # Initialize the spine (needed for the book structure)
    spine = ['nav']

    # Add cover
    if cover_image_path:
        try:
            file_type = os.path.splitext(cover_image_path)[1]
            cover_image_data = open(cover_image_path, 'rb').read()
            book.set_cover(f"cover{file_type}", cover_image_data)
        except IOError:
            print(f"Error: Cover image {cover_image_path} cannot be opened.")
            return

    if chapter_pattern:
        chapters = re.split(chapter_pattern, content)
        for i in range(1, len(chapters), 2):
            title = chapters[i].strip('=').strip()
            text = chapters[i] + '\n' + chapters[i + 1].strip()

            # Create an EPUB HTML document
            chapter_file = epub.EpubHtml(title=title, file_name=f'chap_{i // 2 + 1}.xhtml', lang=book.language)
            chapter_file.content = '<html><head></head><body><p>' + text.replace('\n', '<br/>') + '</p></body></html>'

            book.add_item(chapter_file)

            spine.append(chapter_file)

            book.toc.append(epub.Link(chapter_file.file_name, title, f'chap_{i // 2 + 1}'))
    else:
        chapter_file = epub.EpubHtml(title='Full Text', file_name='full_text.xhtml', lang=book.language)
        chapter_file.content = '<html><head></head><body><p>' + content.replace('\n', '<br/>') + '</p></body></html>'
        book.add_item(chapter_file)
        spine.append(chapter_file)
        book.toc.append(epub.Link(chapter_file.file_name, 'Full Text', 'full_text'))

    # Define the EPUB spine
    book.spine = spine

    # Add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    try:
        # Write the EPUB file
        epub.write_epub(epub_path, book, {})
    except Exception as e:
        print(f"Error writing EPUB file: {str(e)}")

# Using a specific pattern
# txt_to_epub('books/《我的老婆是执政官》.txt', 'books/《我的老婆是执政官》.epub', "books/cover1.png", r'(===\s*.*?\s*===)')
