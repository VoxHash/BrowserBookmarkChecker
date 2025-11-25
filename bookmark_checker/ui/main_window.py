"""PyQt6 GUI main window."""

import sys
from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QDragEnterEvent, QDropEvent, QIcon, QPalette
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from bookmark_checker.core.exporters import export_dedupe_report_csv, export_netscape_html
from bookmark_checker.core.merge import merge_collections
from bookmark_checker.core.parsers import parse_many
from bookmark_checker.i18n.translations import get_translation


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()
        self.setMinimumSize(1000, 640)

        # Data
        from bookmark_checker.core.models import BookmarkCollection

        self.current_collection: BookmarkCollection | None = None
        self.current_report: list[dict[str, Any]] = []
        self.current_language = "en"

        # Set window icon
        icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.svg"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Setup UI
        self._setup_ui()
        self._setup_style()
        self._update_ui_texts()

        # Enable drag and drop
        self.setAcceptDrops(True)

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Top bar
        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)

        # Language selector
        self.lang_label = QLabel()
        top_layout.addWidget(self.lang_label)
        self.language_combo = QComboBox()
        self.language_combo.addItems(
            [
                "English",
                "Русский",
                "Português",
                "Español",
                "Eesti",
                "Français",
                "Deutsch",
                "日本語",
                "中文",
                "한국어",
                "Bahasa Indonesia",
            ]
        )
        self.language_combo.setCurrentIndex(0)
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        top_layout.addWidget(self.language_combo)
        top_layout.addSpacing(10)

        self.btn_import = QPushButton()
        self.btn_import.clicked.connect(self._import_files)
        top_layout.addWidget(self.btn_import)

        self.btn_merge = QPushButton()
        self.btn_merge.clicked.connect(self._find_and_merge)
        self.btn_merge.setEnabled(False)
        top_layout.addWidget(self.btn_merge)

        self.btn_export = QPushButton()
        self.btn_export.clicked.connect(self._export_merged)
        self.btn_export.setEnabled(False)
        top_layout.addWidget(self.btn_export)

        top_layout.addStretch()

        # Similarity slider
        self.similarity_label = QLabel()
        top_layout.addWidget(self.similarity_label)

        self.similarity_slider = QSlider(Qt.Orientation.Horizontal)
        self.similarity_slider.setMinimum(0)
        self.similarity_slider.setMaximum(100)
        self.similarity_slider.setValue(85)
        self.similarity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.similarity_slider.setTickInterval(10)
        self.similarity_slider.setMinimumWidth(200)
        top_layout.addWidget(self.similarity_slider)

        self.similarity_label_value = QLabel("85")
        self.similarity_slider.valueChanged.connect(
            lambda v: self.similarity_label_value.setText(str(v))
        )
        top_layout.addWidget(self.similarity_label_value)

        self.fuzzy_checkbox = None  # Will be added if needed

        layout.addWidget(top_bar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        header = self.table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Bottom status
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        bottom_layout.addWidget(self.progress_bar)

        self.status_label = QLabel()
        bottom_layout.addWidget(self.status_label)

        layout.addWidget(bottom_widget)

    def _update_ui_texts(self) -> None:
        """Update all UI texts based on current language."""
        lang_codes = ["en", "ru", "pt", "es", "et", "fr", "de", "ja", "zh", "ko", "id"]
        lang = lang_codes[self.language_combo.currentIndex()]

        self.setWindowTitle(get_translation(lang, "app_title", "BrowserBookmarkChecker"))
        self.lang_label.setText(get_translation(lang, "language", "Language") + ":")
        self.btn_import.setText(get_translation(lang, "import_files", "Import Files"))
        self.btn_merge.setText(get_translation(lang, "find_merge", "Find & Merge"))
        self.btn_export.setText(get_translation(lang, "export_merged", "Export Merged"))
        self.similarity_label.setText(get_translation(lang, "similarity", "Similarity") + ":")

        # Update table headers
        self.table.setHorizontalHeaderLabels(
            [
                get_translation(lang, "title", "Title"),
                get_translation(lang, "url_canonical", "URL (canonical)"),
                get_translation(lang, "folder", "Folder"),
                get_translation(lang, "source", "Source"),
                get_translation(lang, "count", "Count"),
            ]
        )

        # Update status if it's the default "Ready" message
        if (
            self.status_label.text()
            in [
                get_translation(old_lang, "ready", "Ready")
                for old_lang in lang_codes
                if old_lang != lang
            ]
            or self.status_label.text() == "Ready"
        ):
            self.status_label.setText(get_translation(lang, "ready", "Ready"))

        self.current_language = lang

    def _on_language_changed(self, index: int) -> None:
        """Handle language change."""
        self._update_ui_texts()

    def _setup_style(self) -> None:
        """Set up dark Fusion style."""
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
            }
            QPushButton:disabled {
                background-color: #2b2b2b;
                color: #666666;
            }
            QTableWidget {
                background-color: #1e1e1e;
                gridline-color: #3c3c3c;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #3c3c3c;
                padding: 5px;
                border: none;
            }
            QSlider::groove:horizontal {
                background: #3c3c3c;
                height: 5px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #5c5c5c;
                width: 15px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QLabel {
                color: #ffffff;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4caf50;
            }
        """
        )

    def dragEnterEvent(self, event: QDragEnterEvent | None) -> None:
        """Handle drag enter event."""
        if event is None:
            return
        mime_data = event.mimeData()
        if mime_data and mime_data.hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent | None) -> None:
        """Handle drop event."""
        if event is None:
            return
        mime_data = event.mimeData()
        if mime_data:
            files = [url.toLocalFile() for url in mime_data.urls()]
            self._process_files(files)

    def _import_files(self) -> None:
        """Open file dialog to import bookmark files."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Import Bookmark Files",
            "",
            "Bookmark Files (*.html *.json);;All Files (*)",
        )
        if files:
            self._process_files(files)

    def _process_files(self, files: list[str]) -> None:
        """Process imported files."""
        self.status_label.setText(
            get_translation(self.current_language, "parsing_files", "Parsing files...")
        )
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate

        try:
            collection = parse_many(files)
            self.current_collection = collection
            if len(collection.bookmarks) == 0:
                QMessageBox.warning(
                    self,
                    get_translation(self.current_language, "error", "Error"),
                    f"No bookmarks were found in the selected files.\n\nFiles: {', '.join(files)}",
                )
                self.status_label.setText(
                    get_translation(
                        self.current_language, "no_bookmarks_found", "No bookmarks found in files"
                    )
                )
                self.btn_merge.setEnabled(False)
            else:
                loaded_msg = get_translation(
                    self.current_language,
                    "loaded_bookmarks",
                    "Loaded {count} bookmarks from {files} file(s)",
                )
                self.status_label.setText(
                    loaded_msg.format(count=len(collection.bookmarks), files=len(files))
                )
                self.btn_merge.setEnabled(True)
                # Show bookmarks in table immediately
                self._populate_table_from_collection()
        except Exception as e:
            import traceback

            error_msg = f"Failed to parse files:\n{str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(
                self, get_translation(self.current_language, "error", "Error"), error_msg
            )
            self.status_label.setText(
                get_translation(self.current_language, "error_loading_files", "Error loading files")
            )
            self.btn_merge.setEnabled(False)
        finally:
            self.progress_bar.setVisible(False)

    def _find_and_merge(self) -> None:
        """Find duplicates and merge."""
        if not self.current_collection:
            return

        self.status_label.setText(
            get_translation(self.current_language, "merging", "Merging and deduplicating...")
        )
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        try:
            similarity = self.similarity_slider.value()
            merged, report = merge_collections(
                self.current_collection, similarity_threshold=similarity, enable_fuzzy=True
            )

            self.current_report = report
            self._populate_table(report)

            merged_msg = get_translation(
                self.current_language,
                "merged_to",
                "Merged to {count} unique bookmarks ({groups} groups)",
            )
            self.status_label.setText(
                merged_msg.format(count=len(merged.bookmarks), groups=len(report))
            )
            self.btn_export.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(
                self,
                get_translation(self.current_language, "error", "Error"),
                f"Failed to merge:\n{e}",
            )
            self.status_label.setText(
                get_translation(self.current_language, "error_during_merge", "Error during merge")
            )
        finally:
            self.progress_bar.setVisible(False)

    def _populate_table_from_collection(self) -> None:
        """Populate table with raw bookmarks from collection."""
        if not self.current_collection:
            return

        bookmarks = self.current_collection.bookmarks
        self.table.setRowCount(len(bookmarks))

        for row, bookmark in enumerate(bookmarks):
            self.table.setItem(row, 0, QTableWidgetItem(bookmark.title))
            # Show canonical URL if available, otherwise regular URL
            url_display = bookmark.canonical_url or bookmark.url
            self.table.setItem(row, 1, QTableWidgetItem(url_display))
            self.table.setItem(row, 2, QTableWidgetItem(bookmark.folder_path))
            self.table.setItem(row, 3, QTableWidgetItem(bookmark.source_file))
            self.table.setItem(row, 4, QTableWidgetItem("1"))  # Count is 1 for raw bookmarks

    def _populate_table(self, report: list[dict[str, Any]]) -> None:
        """Populate table with dedupe report."""
        self.table.setRowCount(len(report))

        for row, item in enumerate(report):
            self.table.setItem(row, 0, QTableWidgetItem(item["title"]))
            self.table.setItem(row, 1, QTableWidgetItem(item["canonical_url"]))
            folders_str = " | ".join(item["folders"][:3])  # Show first 3
            self.table.setItem(row, 2, QTableWidgetItem(folders_str))
            sources_str = " | ".join(item["sources"])
            self.table.setItem(row, 3, QTableWidgetItem(sources_str))
            self.table.setItem(row, 4, QTableWidgetItem(str(item["count"])))

    def _export_merged(self) -> None:
        """Export merged bookmarks."""
        collection = self.current_collection
        if not collection or not self.current_report:
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Merged Bookmarks",
            "merged_bookmarks.html",
            "HTML Files (*.html);;All Files (*)",
        )

        if not output_path:
            return

        self.status_label.setText(
            get_translation(self.current_language, "exporting", "Exporting...")
        )
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        try:
            # Re-merge to get merged collection
            similarity = self.similarity_slider.value()
            merged, _ = merge_collections(
                collection, similarity_threshold=similarity, enable_fuzzy=True
            )

            # Export HTML
            export_netscape_html(merged, output_path)

            # Export CSV
            csv_path = (
                Path(output_path)
                .with_suffix("")
                .with_name(f"{Path(output_path).stem}_dedupe_report.csv")
            )
            export_dedupe_report_csv(self.current_report, str(csv_path))

            exported_to_msg = get_translation(
                self.current_language,
                "exported_to",
                "Exported to {path1} and {path2}",
            )
            self.status_label.setText(exported_to_msg.format(path1=output_path, path2=csv_path))
            exported_msg = get_translation(
                self.current_language, "exported_successfully", "Exported successfully!"
            )
            QMessageBox.information(
                self,
                get_translation(self.current_language, "success", "Success"),
                f"{exported_msg}\n\n{output_path}\n{csv_path}",
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                get_translation(self.current_language, "error", "Error"),
                f"Failed to export:\n{e}",
            )
            self.status_label.setText(
                get_translation(self.current_language, "error_during_export", "Error during export")
            )
        finally:
            self.progress_bar.setVisible(False)


def launch_gui() -> None:
    """Launch the GUI application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set application icon
    icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.svg"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Set dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(43, 43, 43))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(60, 60, 60))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(60, 60, 60))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
