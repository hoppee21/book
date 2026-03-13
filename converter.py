import os
import sys
from uuid import uuid4

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
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
        self.output_file_path = None
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("TXT to EPUB Converter")
        self.setGeometry(240, 120, 760, 620)
        self._apply_styles()

        root = QVBoxLayout()
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        root.addWidget(self._build_header())
        root.addWidget(self._build_metadata_group())
        root.addWidget(self._build_file_group())
        root.addWidget(self._build_chapter_group())
        root.addLayout(self._build_actions())

        self.status_label = QLabel("Ready to convert")
        self.status_label.setObjectName("StatusLabel")
        root.addWidget(self.status_label)

        self.setLayout(root)

    def _apply_styles(self):
        self.setStyleSheet(
            """
            QWidget {
                background: #f5f7fb;
                color: #1f2937;
                font-size: 13px;
            }
            QLabel#HeaderTitle {
                font-size: 24px;
                font-weight: 700;
                color: #0f172a;
            }
            QLabel#HeaderSubtitle {
                color: #475569;
                margin-top: 2px;
            }
            QLabel#StatusLabel {
                background: #e8f1ff;
                border: 1px solid #c7dcff;
                border-radius: 8px;
                padding: 10px;
                color: #1e40af;
                font-weight: 600;
            }
            QGroupBox {
                border: 1px solid #d8e1f0;
                border-radius: 10px;
                margin-top: 12px;
                background: #ffffff;
                font-weight: 600;
                padding: 14px 12px 12px 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #334155;
            }
            QLineEdit, QComboBox {
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 8px;
                background: #ffffff;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #60a5fa;
            }
            QPushButton {
                border-radius: 8px;
                border: 1px solid #cbd5e1;
                padding: 8px 12px;
                background: #f8fafc;
            }
            QPushButton:hover {
                background: #eef2ff;
            }
            QPushButton#PrimaryButton {
                background: #2563eb;
                border: 1px solid #1d4ed8;
                color: white;
                font-weight: 700;
                padding: 10px 16px;
            }
            QPushButton#PrimaryButton:hover {
                background: #1d4ed8;
            }
            QLabel#PathLabel {
                color: #475569;
                background: #f8fafc;
                border: 1px dashed #cbd5e1;
                border-radius: 8px;
                padding: 8px;
            }
            """
        )

    def _build_header(self):
        frame = QFrame(self)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("TXT → EPUB Converter")
        title.setObjectName("HeaderTitle")
        subtitle = QLabel("Build polished EPUB files with metadata, cover images, and chapter parsing.")
        subtitle.setObjectName("HeaderSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        frame.setLayout(layout)
        return frame

    def _build_metadata_group(self):
        group = QGroupBox("Book Metadata")
        form = QFormLayout()
        form.setSpacing(10)

        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("e.g. The Great Novel")
        form.addRow("Title", self.title_input)

        self.author_input = QLineEdit(self)
        self.author_input.setPlaceholderText("e.g. Jane Doe")
        form.addRow("Author", self.author_input)

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
        form.addRow("Language", self.language_combo)

        self.id_input = QLineEdit(self)
        self.id_input.setText(str(uuid4()))
        self.id_input.setToolTip("Unique identifier for your EPUB.")
        form.addRow("Book ID", self.id_input)

        group.setLayout(form)
        return group

    def _build_file_group(self):
        group = QGroupBox("Files")
        wrapper = QVBoxLayout()
        wrapper.setSpacing(10)

        txt_row = QHBoxLayout()
        self.txt_button = QPushButton("Browse TXT", self)
        self.txt_button.clicked.connect(self.open_text_file)
        self.txt_path_label = QLabel("No text file selected")
        self.txt_path_label.setObjectName("PathLabel")
        self.txt_path_label.setWordWrap(True)
        txt_row.addWidget(self.txt_button)
        txt_row.addWidget(self.txt_path_label, 1)

        cover_row = QHBoxLayout()
        self.cover_button = QPushButton("Browse Cover", self)
        self.cover_button.clicked.connect(self.open_cover_image)
        self.cover_path_label = QLabel("No cover image selected")
        self.cover_path_label.setObjectName("PathLabel")
        self.cover_path_label.setWordWrap(True)
        cover_row.addWidget(self.cover_button)
        cover_row.addWidget(self.cover_path_label, 1)

        output_row = QHBoxLayout()
        self.output_button = QPushButton("Save EPUB As", self)
        self.output_button.clicked.connect(self.select_output_file)
        self.output_path_label = QLabel("Auto: same folder as source text")
        self.output_path_label.setObjectName("PathLabel")
        self.output_path_label.setWordWrap(True)
        output_row.addWidget(self.output_button)
        output_row.addWidget(self.output_path_label, 1)

        wrapper.addLayout(txt_row)
        wrapper.addLayout(cover_row)
        wrapper.addLayout(output_row)
        group.setLayout(wrapper)
        return group

    def _build_chapter_group(self):
        group = QGroupBox("Chapter Detection")
        wrapper = QVBoxLayout()
        wrapper.setSpacing(8)

        self.chapter_input = QLineEdit(self)
        self.chapter_input.setPlaceholderText(r"Optional regex, e.g. (===\s*.*?\s*===)")

        hint = QLabel("Tip: Leave empty to produce a single chapter from the full text.")
        hint.setStyleSheet("color: #64748b;")

        wrapper.addWidget(self.chapter_input)
        wrapper.addWidget(hint)
        group.setLayout(wrapper)
        return group

    def _build_actions(self):
        actions = QHBoxLayout()
        actions.addStretch(1)

        self.clear_button = QPushButton("Reset", self)
        self.clear_button.clicked.connect(self.reset_form)
        actions.addWidget(self.clear_button)

        self.quit_button = QPushButton("Quit", self)
        self.quit_button.clicked.connect(self.close)
        actions.addWidget(self.quit_button)

        self.convert_button = QPushButton("Convert to EPUB", self)
        self.convert_button.setObjectName("PrimaryButton")
        self.convert_button.setDefault(True)
        self.convert_button.clicked.connect(self.convert)
        actions.addWidget(self.convert_button)

        return actions

    def _set_status(self, message):
        self.status_label.setText(message)

    def open_text_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select a text file", "", "Text Files (*.txt)")
        if filename:
            self.txt_file_path = filename
            self.txt_path_label.setText(filename)
            if not self.output_file_path:
                auto_output = os.path.splitext(filename)[0] + ".epub"
                self.output_path_label.setText(f"Auto: {auto_output}")
            self._set_status("Text file selected")

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
            self._set_status("Cover image selected")

    def select_output_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save EPUB As", "", "EPUB Files (*.epub)")
        if filename:
            if not filename.lower().endswith(".epub"):
                filename += ".epub"
            self.output_file_path = filename
            self.output_path_label.setText(filename)
            self._set_status("Output location selected")

    def reset_form(self):
        self.title_input.clear()
        self.author_input.clear()
        self.id_input.setText(str(uuid4()))
        self.language_combo.setCurrentIndex(0)
        self.chapter_input.clear()
        self.txt_file_path = None
        self.cover_file_path = None
        self.output_file_path = None
        self.txt_path_label.setText("No text file selected")
        self.cover_path_label.setText("No cover image selected")
        self.output_path_label.setText("Auto: same folder as source text")
        self._set_status("Form reset")

    def convert(self):
        if not self.txt_file_path:
            QMessageBox.warning(self, "Missing File", "Please select a text file.")
            return

        if not os.path.isfile(self.txt_file_path):
            QMessageBox.warning(self, "Invalid File", "The selected text file no longer exists.")
            return

        epub_path = self.output_file_path or (os.path.splitext(self.txt_file_path)[0] + ".epub")

        chapter_pattern = self.chapter_input.text().strip() or None
        book_id = self.id_input.text().strip() or str(uuid4())
        book_title = self.title_input.text().strip() or os.path.splitext(os.path.basename(self.txt_file_path))[0]
        author_name = self.author_input.text().strip() or "Unknown Author"
        book_language = self.language_combo.currentData(Qt.UserRole)

        self._set_status("Converting…")
        QApplication.processEvents()

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
            self._set_status("Conversion failed")
            QMessageBox.critical(self, "Conversion Error", str(exc))
            return

        self._set_status(f"Done: {epub_path}")
        QMessageBox.information(self, "Success", f"EPUB created successfully.\n\nSaved to:\n{epub_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
