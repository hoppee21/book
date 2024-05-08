import os
import sys

from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QFileDialog, QMessageBox, QComboBox)

from text2epub import txt_to_epub


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.language_combo = None
        self.quit_button = None
        self.chapter_input = None
        self.convert_button = None
        self.chapter_label = None
        self.cover_path_label = None
        self.cover_button = None
        self.txt_path_label = None
        self.txt_button = None
        self.id_input = None
        self.language_input = None
        self.language_label = None
        self.author_label = None
        self.author_input = None
        self.title_input = None
        self.title_label = None
        self.id_label = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('TXT to EPUB Converter')
        self.setGeometry(300, 300, 400, 300)

        # Layouts
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        # Title input
        self.title_label = QLabel('Book Title:')
        self.title_input = QLineEdit(self)
        layout.addWidget(self.title_label)
        layout.addWidget(self.title_input)

        # Author input
        self.author_label = QLabel('Author Name:')
        self.author_input = QLineEdit(self)
        layout.addWidget(self.author_label)
        layout.addWidget(self.author_input)

        # Language selection
        self.language_label = QLabel('Book Language:')
        layout.addWidget(self.language_label)

        self.language_combo = QComboBox(self)
        languages = {'en': 'English', 'zh': 'Chinese', 'es': 'Spanish', 'fr': 'French', 'de': 'German'}
        for code, name in languages.items():
            self.language_combo.addItem(name, code)  # The second parameter is the internal data
        layout.addWidget(self.language_combo)

        # Book ID input
        self.id_label = QLabel('Book ID:')
        self.id_input = QLineEdit(self)
        layout.addWidget(self.id_label)
        layout.addWidget(self.id_input)

        # Text file selection
        self.txt_button = QPushButton('Select Text File', self)
        self.txt_button.clicked.connect(self.open_text_file)
        layout.addWidget(self.txt_button)
        self.txt_path_label = QLabel('No file selected')
        layout.addWidget(self.txt_path_label)

        # Cover image selection
        self.cover_button = QPushButton('Select Cover Image (Optional)', self)
        self.cover_button.clicked.connect(self.open_cover_image)
        layout.addWidget(self.cover_button)
        self.cover_path_label = QLabel('No file selected')
        layout.addWidget(self.cover_path_label)

        # Chapter pattern input
        self.chapter_label = QLabel('Chapter Pattern (Optional):')
        self.chapter_input = QLineEdit(self)
        layout.addWidget(self.chapter_label)
        layout.addWidget(self.chapter_input)

        # Convert button
        self.convert_button = QPushButton('Convert to EPUB', self)
        self.convert_button.clicked.connect(self.convert)
        button_layout.addWidget(self.convert_button)

        # Quit button
        self.quit_button = QPushButton('Quit', self)
        self.quit_button.clicked.connect(self.close)
        button_layout.addWidget(self.quit_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def open_text_file(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Select a text file", "", "Text Files (*.txt)", options=options)
        if filename:
            self.txt_path_label.setText(filename)

    def open_cover_image(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Select a cover image", "", "Image Files (*.png *.jpg *.jpeg)",
                                                  options=options)
        if filename:
            self.cover_path_label.setText(filename)

    def convert(self):
        txt_path = self.txt_path_label.text()
        if txt_path == 'No file selected':
            QMessageBox.warning(self, 'Error', 'Please select a text file.')
            return
        epub_path = os.path.splitext(txt_path)[0] + '.epub'
        cover_image_path = self.cover_path_label.text() if self.cover_path_label.text() != 'No file selected' else None
        chapter_pattern = self.chapter_input.text()
        book_id = self.id_input.text()
        book_title = self.title_input.text()
        book_language = self.language_input.text()
        author_name = self.author_input.text()

        try:
            txt_to_epub(txt_path, epub_path, cover_image_path, chapter_pattern, book_id, book_title, book_language,
                        author_name)
            QMessageBox.information(self, 'Success', 'The EPUB has been created successfully!')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'An error occurred: {str(e)}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
