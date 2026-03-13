import os
import sys
from uuid import uuid4

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QPixmap, QPainter
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGraphicsDropShadowEffect,
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
        self.setWindowIcon(self._create_icon())  # Replaces default OS window icon
        self._init_ui()
        self._apply_stylesheet()

    def _create_icon(self):
        """Creates a modern, programmatic app icon to replace the default OS window icon."""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background rounded rect
        painter.setBrush(QColor("#3498db"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(8, 8, 48, 48, 12, 12)

        # Draw decorative white lines (representing text in a book)
        painter.setBrush(QColor("#ffffff"))
        painter.drawRoundedRect(18, 22, 28, 5, 2, 2)
        painter.drawRoundedRect(18, 33, 28, 5, 2, 2)
        painter.drawRoundedRect(18, 44, 18, 5, 2, 2)

        painter.end()
        return QIcon(pixmap)

    def _init_ui(self):
        self.setWindowTitle("TXT to EPUB Converter")
        self.resize(680, 580)

        # Main Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # Header
        header_label = QLabel("Create Your EPUB")
        header_label.setObjectName("headerLabel")
        layout.addWidget(header_label)

        # Form Groups (Cards)
        layout.addWidget(self._build_metadata_group())
        layout.addWidget(self._build_file_group())
        layout.addWidget(self._build_chapter_group())

        layout.addStretch()  # Pushes actions to the bottom
        layout.addLayout(self._build_actions())

        self.setLayout(layout)

    def _add_shadow(self, widget):
        """Adds a subtle drop shadow to create a modern 'Card' UI effect."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 15))
        widget.setGraphicsEffect(shadow)

    def _build_metadata_group(self):
        group = QGroupBox("Book Metadata")
        self._add_shadow(group)

        form = QFormLayout()
        form.setContentsMargins(20, 25, 20, 20)
        form.setSpacing(12)

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
        self._add_shadow(group)

        wrapper = QVBoxLayout()
        wrapper.setContentsMargins(20, 25, 20, 20)
        wrapper.setSpacing(15)

        # Text file selection row
        txt_layout = QHBoxLayout()
        self.txt_button = QPushButton("Browse Text File...")
        self.txt_button.setCursor(Qt.PointingHandCursor)
        self.txt_button.clicked.connect(self.open_text_file)

        self.txt_path_label = QLabel("No text file selected")
        self.txt_path_label.setObjectName("pathLabel")

        txt_layout.addWidget(self.txt_button)
        txt_layout.addWidget(self.txt_path_label, 1)

        # Cover image selection row
        cover_layout = QHBoxLayout()
        self.cover_button = QPushButton("Browse Cover Image...")
        self.cover_button.setCursor(Qt.PointingHandCursor)
        self.cover_button.clicked.connect(self.open_cover_image)

        self.cover_path_label = QLabel("No cover image selected")
        self.cover_path_label.setObjectName("pathLabel")

        cover_layout.addWidget(self.cover_button)
        cover_layout.addWidget(self.cover_path_label, 1)

        wrapper.addLayout(txt_layout)
        wrapper.addLayout(cover_layout)
        group.setLayout(wrapper)
        return group

    def _build_chapter_group(self):
        group = QGroupBox("Chapter Detection")
        self._add_shadow(group)

        wrapper = QVBoxLayout()
        wrapper.setContentsMargins(20, 25, 20, 20)
        wrapper.setSpacing(8)

        self.chapter_input = QLineEdit(self)
        self.chapter_input.setPlaceholderText(r"Optional regex, e.g. (===\s*.*?\s*===)")

        hint = QLabel("Leave empty to create a single chapter from the full text.")
        hint.setObjectName("hintLabel")

        wrapper.addWidget(self.chapter_input)
        wrapper.addWidget(hint)
        group.setLayout(wrapper)
        return group

    def _build_actions(self):
        actions = QHBoxLayout()
        actions.setSpacing(15)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("statusLabel")
        actions.addWidget(self.status_label, 1)

        self.clear_button = QPushButton("Reset")
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.clear_button.clicked.connect(self.reset_form)
        actions.addWidget(self.clear_button)

        self.quit_button = QPushButton("Quit")
        self.quit_button.setObjectName("dangerBtn")
        self.quit_button.setCursor(Qt.PointingHandCursor)
        self.quit_button.clicked.connect(self.close)
        actions.addWidget(self.quit_button)

        self.convert_button = QPushButton("Convert to EPUB")
        self.convert_button.setObjectName("primaryBtn")
        self.convert_button.setCursor(Qt.PointingHandCursor)
        self.convert_button.setDefault(True)
        self.convert_button.clicked.connect(self.convert)
        actions.addWidget(self.convert_button)

        return actions

    def _apply_stylesheet(self):
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                font-size: 10pt;
                color: #2c3e50;
                background-color: #f4f6f9;
            }

            QLabel#headerLabel {
                font-size: 18pt;
                font-weight: bold;
                color: #2c3e50;
            }

            QGroupBox {
                font-size: 11pt;
                font-weight: bold;
                border: 1px solid #e1e5eb;
                border-radius: 8px;
                margin-top: 14px;
                background-color: #ffffff;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                padding: 0 5px;
                color: #34495e;
            }

            /* Dedicated LineEdit Styling */
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px 10px;
                background-color: #ffffff;
                selection-background-color: #3498db;
                color: #2c3e50;
            }

            QLineEdit:focus {
                border: 1px solid #3498db;
                background-color: #fdfefe;
            }

            /* Dedicated ComboBox Styling */
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px 10px;
                padding-right: 35px; /* Room for the beautiful dropdown arrow */
                background-color: #ffffff;
                selection-background-color: #3498db;
                color: #2c3e50;
            }

            QComboBox:focus {
                border: 1px solid #3498db;
                background-color: #fdfefe;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 32px;
                border-left: 1px solid #e1e5eb;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
                background-color: #f8f9fa;
            }

            QComboBox::drop-down:hover {
                background-color: #ecf0f1;
            }

            QComboBox::down-arrow {
                /* Modern sharp SVG Chevron embedded via Base64 */
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjMmMzZTUwIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBvbHlsaW5lIHBvaW50cz0iNiA5IDEyIDE1IDE4IDkiPjwvcG9seWxpbmU+PC9zdmc+);
                width: 14px;
                height: 14px;
            }

            /* Dropdown List Items */
            QComboBox QAbstractItemView {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #ffffff;
                selection-background-color: #3498db;
                selection-color: #ffffff;
                outline: none; /* remove focus border */
                padding: 4px;
            }

            QComboBox QAbstractItemView::item {
                padding: 8px;
                border-radius: 4px;
                min-height: 24px;
            }

            QComboBox QAbstractItemView::item:hover {
                background-color: #f4f6f9;
                color: #2c3e50;
            }

            /* Standard Buttons (Browse, Reset) */
            QPushButton {
                background-color: #ffffff;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: 500;
            }

            QPushButton:hover {
                background-color: #ecf0f1;
                border-color: #95a5a6;
            }

            QPushButton:pressed {
                background-color: #bdc3c7;
            }

            /* Primary Action Button (Convert) */
            QPushButton#primaryBtn {
                background-color: #3498db;
                color: #ffffff;
                border: none;
                font-size: 10pt;
                font-weight: bold;
                padding: 10px 24px;
            }

            QPushButton#primaryBtn:hover {
                background-color: #2980b9;
            }

            QPushButton#primaryBtn:pressed {
                background-color: #1f618d;
            }

            /* Danger Button (Quit) */
            QPushButton#dangerBtn {
                background-color: #e74c3c;
                color: #ffffff;
                border: none;
                font-weight: bold;
                padding: 10px 20px;
            }

            QPushButton#dangerBtn:hover {
                background-color: #c0392b;
            }

            QPushButton#dangerBtn:pressed {
                background-color: #922b21;
            }

            /* Path Labels (File locations) */
            QLabel#pathLabel {
                background-color: #ecf0f1;
                border: 1px solid #e1e5eb;
                border-radius: 5px;
                padding: 8px;
                color: #7f8c8d;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
            }

            QLabel#statusLabel {
                color: #27ae60;
                font-weight: bold;
                font-size: 11pt;
            }

            QLabel#hintLabel {
                color: #95a5a6;
                font-size: 9pt;
                font-style: italic;
            }
        """)

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
            self.status_label.setStyleSheet("color: #27ae60;")

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
            self.status_label.setStyleSheet("color: #27ae60;")

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
        self.status_label.setStyleSheet("color: #27ae60;")

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
            self.status_label.setStyleSheet("color: #e74c3c;")  # Danger red
            QMessageBox.critical(self, "Conversion Error", str(exc))
            return

        self.status_label.setText(f"Success: {epub_path}")
        self.status_label.setStyleSheet("color: #27ae60;")  # Success green

        QMessageBox.information(
            self,
            "Success",
            f"EPUB created successfully.\n\nSaved to:\n{epub_path}",
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Fusion style establishes a very clean cross-platform baseline
    # to layer the custom stylesheet on without native OS interference.
    app.setStyle("Fusion")

    ex = App()
    ex.show()
    sys.exit(app.exec_())