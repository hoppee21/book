import os
import sys
from uuid import uuid4

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from text2epub import ConversionError, txt_to_epub


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.txt_file_path = None
        self.cover_file_path = None
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("TXT to EPUB Converter")
        self.setGeometry(250, 150, 620, 520)

        layout = QVBoxLayout()
        layout.setSpacing(14)

        layout.addWidget(self._build_metadata_group())
        layout.addWidget(self._build_file_group())
        layout.addWidget(self._build_chapter_group())
        layout.addLayout(self._build_actions())

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #2d6a4f; font-weight: 600;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def _build_metadata_group(self):
        group = QGroupBox("Book Metadata")
        form = QFormLayout()

        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("e.g. The Great Novel")
        form.addRow("Title:", self.title_input)

        self.author_input = QLineEdit(self)
        self.author_input.setPlaceholderText("e.g. Jane Doe")
        form.addRow("Author:", self.author_input)

        self.language_combo = QComboBox(self)
        languages = {
            "en": "English",
            "zh": "Chinese",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
        }
        for code, name in languages.items():
            self.language_combo.addItem(f"{name} ({code})", code)
        form.addRow("Language:", self.language_combo)

        self.id_input = QLineEdit(self)
        self.id_input.setText(str(uuid4()))
        self.id_input.setToolTip("Unique identifier for your EPUB.")
        form.addRow("Book ID:", self.id_input)

        group.setLayout(form)
        return group

    def _build_file_group(self):
        group = QGroupBox("Source Files")
        wrapper = QVBoxLayout()

        self.txt_button = QPushButton("Choose Text File (*.txt)", self)
        self.txt_button.clicked.connect(self.open_text_file)
        wrapper.addWidget(self.txt_button)

        self.txt_path_label = QLabel("No text file selected")
        self.txt_path_label.setWordWrap(True)
        wrapper.addWidget(self.txt_path_label)

        self.cover_button = QPushButton("Choose Cover Image (optional)", self)
        self.cover_button.clicked.connect(self.open_cover_image)
        wrapper.addWidget(self.cover_button)

        self.cover_path_label = QLabel("No cover image selected")
        self.cover_path_label.setWordWrap(True)
        wrapper.addWidget(self.cover_path_label)

        group.setLayout(wrapper)
        return group

    def _build_chapter_group(self):
        group = QGroupBox("Chapter Detection")
        wrapper = QVBoxLayout()

        self.chapter_input = QLineEdit(self)
        self.chapter_input.setPlaceholderText(r"Optional regex, e.g. (===\s*.*?\s*===)")

        hint = QLabel(
            "Leave empty to create a single chapter from the full text."
        )
        hint.setStyleSheet("color: #666666;")

        wrapper.addWidget(self.chapter_input)
        wrapper.addWidget(hint)
        group.setLayout(wrapper)
        return group

    def _build_actions(self):
        actions = QHBoxLayout()

        self.convert_button = QPushButton("Convert to EPUB", self)
        self.convert_button.setDefault(True)
        self.convert_button.clicked.connect(self.convert)
        actions.addWidget(self.convert_button)

        self.clear_button = QPushButton("Reset", self)
        self.clear_button.clicked.connect(self.reset_form)
        actions.addWidget(self.clear_button)

        self.quit_button = QPushButton("Quit", self)
        self.quit_button.clicked.connect(self.close)
        actions.addWidget(self.quit_button)

        return actions

    def open_text_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select a text file",
            "",
            "Text Files (*.txt)",
        )
        if filename:
            self.txt_file_path = filename
            self.txt_path_label.setText(filename)
            self.status_label.setText("Text file selected")

    def open_cover_image(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select a cover image",
            "",
            "Image Files (*.png *.jpg *.jpeg)",
        )
        if filename:
            self.cover_file_path = filename
            self.cover_path_label.setText(filename)
            self.status_label.setText("Cover image selected")

    def reset_form(self):
        self.title_input.clear()
        self.author_input.clear()
        self.id_input.setText(str(uuid4()))
        self.language_combo.setCurrentIndex(0)
        self.chapter_input.clear()
        self.txt_file_path = None
        self.cover_file_path = None
        self.txt_path_label.setText("No text file selected")
        self.cover_path_label.setText("No cover image selected")
        self.status_label.setText("Form reset")

    def convert(self):
        if not self.txt_file_path:
            QMessageBox.warning(self, "Missing File", "Please select a text file.")
            return

        if not os.path.isfile(self.txt_file_path):
            QMessageBox.warning(self, "Invalid File", "The selected text file no longer exists.")
            return

        epub_path = os.path.splitext(self.txt_file_path)[0] + ".epub"

        chapter_pattern = self.chapter_input.text().strip() or None
        book_id = self.id_input.text().strip() or str(uuid4())
        book_title = self.title_input.text().strip() or os.path.basename(self.txt_file_path)
        author_name = self.author_input.text().strip() or "Unknown Author"
        book_language = self.language_combo.currentData(Qt.UserRole)

        try:
            txt_to_epub(
                txt_path=self.txt_file_path,
                epub_path=epub_path,
                cover_image_path=self.cover_file_path,
                chapter_pattern=chapter_pattern,
                book_id=book_id,
                book_title=book_title,
                book_language=book_language,
                author_name=author_name,
            )
        except ConversionError as exc:
            self.status_label.setText("Conversion failed")
            QMessageBox.critical(self, "Conversion Error", str(exc))
            return

        self.status_label.setText(f"Success: {epub_path}")
        QMessageBox.information(
            self,
            "Success",
            f"EPUB created successfully.\n\nSaved to:\n{epub_path}",
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
