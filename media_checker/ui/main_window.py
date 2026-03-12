"""PyQt6 GUI main window for media duplicate checker."""

import sys
from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt, QThread, pyqtSignal
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

from media_checker.core.dedupe import group_duplicates
from media_checker.core.exporters import (
    export_duplicate_list_txt,
    export_duplicate_report_csv,
    export_duplicate_report_json,
)
from media_checker.core.metadata import extract_all_metadata
from media_checker.core.models import MediaCollection
from media_checker.core.scanner import scan_directory
from media_checker.i18n.translations import get_translation


class ScanThread(QThread):
    """Thread for scanning directory."""

    progress = pyqtSignal(int, int)
    finished = pyqtSignal(MediaCollection)

    def __init__(self, directory: str) -> None:
        """Initialize scan thread."""
        super().__init__()
        self.directory = directory

    def run(self) -> None:
        """Run the scan."""
        collection = scan_directory(self.directory, self.progress.emit)
        self.finished.emit(collection)


class MetadataThread(QThread):
    """Thread for extracting metadata."""

    progress = pyqtSignal(int, int)
    finished = pyqtSignal(MediaCollection)

    def __init__(self, collection: MediaCollection) -> None:
        """Initialize metadata thread."""
        super().__init__()
        self.collection = collection

    def run(self) -> None:
        """Extract metadata for all files."""
        total = len(self.collection.files)
        for idx, media_file in enumerate(self.collection.files):
            extract_all_metadata(media_file, calculate_hash=True)
            self.progress.emit(idx + 1, total)
        self.finished.emit(self.collection)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()
        self.setMinimumSize(1200, 700)

        # Data
        self.current_collection: MediaCollection | None = None
        self.current_report: list[dict[str, Any]] = []
        self.current_language = "en"

        # Threads
        self.scan_thread: ScanThread | None = None
        self.metadata_thread: MetadataThread | None = None

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

        self.btn_select_folder = QPushButton()
        self.btn_select_folder.clicked.connect(self._select_folder)
        self.btn_select_folder.setToolTip("Select a folder to scan for media files")
        top_layout.addWidget(self.btn_select_folder)

        self.btn_analyze = QPushButton()
        self.btn_analyze.clicked.connect(self._analyze_files)
        self.btn_analyze.setEnabled(False)
        self.btn_analyze.setToolTip("Extract metadata from scanned media files")
        top_layout.addWidget(self.btn_analyze)

        self.btn_find_duplicates = QPushButton()
        self.btn_find_duplicates.clicked.connect(self._find_duplicates)
        self.btn_find_duplicates.setEnabled(False)
        self.btn_find_duplicates.setToolTip("Find duplicate media files")
        top_layout.addWidget(self.btn_find_duplicates)

        self.btn_export = QPushButton()
        self.btn_export.clicked.connect(self._export_report)
        self.btn_export.setEnabled(False)
        self.btn_export.setToolTip("Export duplicate report to file")
        top_layout.addWidget(self.btn_export)

        top_layout.addStretch()

        # Duration tolerance slider
        self.tolerance_label = QLabel()
        top_layout.addWidget(self.tolerance_label)

        self.tolerance_slider = QSlider(Qt.Orientation.Horizontal)
        self.tolerance_slider.setMinimum(0)
        self.tolerance_slider.setMaximum(10)
        self.tolerance_slider.setValue(1)
        self.tolerance_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.tolerance_slider.setTickInterval(1)
        self.tolerance_slider.setMinimumWidth(150)
        self.tolerance_slider.setToolTip("Duration tolerance in seconds for duplicate matching")
        self.tolerance_slider.setAccessibleName("Duration tolerance slider")
        top_layout.addWidget(self.tolerance_slider)

        self.tolerance_label_value = QLabel("1.0s")
        self.tolerance_slider.valueChanged.connect(
            lambda v: self.tolerance_label_value.setText(f"{v}.0s")
        )
        top_layout.addWidget(self.tolerance_label_value)

        layout.addWidget(top_bar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        header = self.table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
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

        self.setWindowTitle(get_translation(lang, "app_title", "Media Duplicate Checker"))
        self.lang_label.setText(get_translation(lang, "language", "Language") + ":")
        self.btn_select_folder.setText(
            get_translation(lang, "select_folder", "Select Folder")
        )
        self.btn_analyze.setText(get_translation(lang, "analyze_files", "Analyze Files"))
        self.btn_find_duplicates.setText(
            get_translation(lang, "find_duplicates", "Find Duplicates")
        )
        self.btn_export.setText(get_translation(lang, "export_report", "Export Report"))
        self.tolerance_label.setText(
            get_translation(lang, "duration_tolerance", "Duration Tolerance") + ":"
        )

        # Update table headers
        self.table.setHorizontalHeaderLabels(
            [
                get_translation(lang, "file_path", "File Path"),
                get_translation(lang, "file_type", "Type"),
                get_translation(lang, "size", "Size"),
                get_translation(lang, "duration", "Duration"),
                get_translation(lang, "codec", "Codec"),
                get_translation(lang, "count", "Count"),
                get_translation(lang, "locations", "Locations"),
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
            urls = [url.toLocalFile() for url in mime_data.urls()]
            # Take first directory if dropped
            for url in urls:
                path = Path(url)
                if path.is_dir():
                    self._scan_directory(str(path))
                    return

    def _select_folder(self) -> None:
        """Open folder dialog to select directory."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Scan")
        if folder:
            self._scan_directory(folder)

    def _scan_directory(self, directory: str) -> None:
        """Scan directory for media files."""
        self.status_label.setText(
            get_translation(self.current_language, "scanning", "Scanning directory...")
        )
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.btn_select_folder.setEnabled(False)

        # Create and start scan thread
        self.scan_thread = ScanThread(directory)
        self.scan_thread.progress.connect(self._on_scan_progress)
        self.scan_thread.finished.connect(self._on_scan_finished)
        self.scan_thread.start()

    def _on_scan_progress(self, processed: int, total: int) -> None:
        """Handle scan progress update."""
        if total > 0:
            self.progress_bar.setRange(0, total)
            self.progress_bar.setValue(processed)
            self.status_label.setText(
                get_translation(
                    self.current_language,
                    "scanning_progress",
                    "Scanning: {processed}/{total} files",
                ).format(processed=processed, total=total)
            )

    def _on_scan_finished(self, collection: MediaCollection) -> None:
        """Handle scan completion."""
        self.current_collection = collection
        self.progress_bar.setVisible(False)

        if len(collection.files) == 0:
            QMessageBox.warning(
                self,
                get_translation(self.current_language, "error", "Error"),
                get_translation(
                    self.current_language,
                    "no_media_found",
                    "No media files found in the selected directory.",
                ),
            )
            self.status_label.setText(
                get_translation(
                    self.current_language, "no_media_found", "No media files found"
                )
            )
            self.btn_analyze.setEnabled(False)
        else:
            found_msg = get_translation(
                self.current_language,
                "found_files",
                "Found {count} media files",
            )
            self.status_label.setText(found_msg.format(count=len(collection.files)))
            self.btn_analyze.setEnabled(True)
            # Populate table with basic info
            self._populate_table_from_collection()

        self.btn_select_folder.setEnabled(True)

    def _analyze_files(self) -> None:
        """Extract metadata for all files."""
        if not self.current_collection:
            return

        self.status_label.setText(
            get_translation(
                self.current_language, "extracting_metadata", "Extracting metadata..."
            )
        )
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(self.current_collection.files))
        self.progress_bar.setValue(0)
        self.btn_analyze.setEnabled(False)

        # Create and start metadata thread
        self.metadata_thread = MetadataThread(self.current_collection)
        self.metadata_thread.progress.connect(self._on_metadata_progress)
        self.metadata_thread.finished.connect(self._on_metadata_finished)
        self.metadata_thread.start()

    def _on_metadata_progress(self, processed: int, total: int) -> None:
        """Handle metadata extraction progress."""
        self.progress_bar.setValue(processed)
        self.status_label.setText(
            get_translation(
                self.current_language,
                "extracting_progress",
                "Extracting metadata: {processed}/{total}",
            ).format(processed=processed, total=total)
        )

    def _on_metadata_finished(self, collection: MediaCollection) -> None:
        """Handle metadata extraction completion."""
        self.current_collection = collection
        self.progress_bar.setVisible(False)
        self.status_label.setText(
            get_translation(
                self.current_language,
                "metadata_extracted",
                "Metadata extracted successfully",
            )
        )
        self.btn_analyze.setEnabled(True)
        self.btn_find_duplicates.setEnabled(True)
        self._populate_table_from_collection()

    def _find_duplicates(self) -> None:
        """Find duplicate files."""
        if not self.current_collection:
            return

        self.status_label.setText(
            get_translation(
                self.current_language, "finding_duplicates", "Finding duplicates..."
            )
        )
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        try:
            tolerance = float(self.tolerance_slider.value())
            grouped, report = group_duplicates(
                self.current_collection,
                match_by_hash=True,
                match_by_size_duration=True,
                match_by_thumbnail=True,
                duration_tolerance=tolerance,
            )

            self.current_report = report
            self._populate_table(report)

            if len(report) == 0:
                self.status_label.setText(
                    get_translation(
                        self.current_language,
                        "no_duplicates_found",
                        "No duplicates found",
                    )
                )
            else:
                duplicates_msg = get_translation(
                    self.current_language,
                    "duplicates_found",
                    "Found {count} duplicate groups",
                )
                self.status_label.setText(duplicates_msg.format(count=len(report)))
                self.btn_export.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(
                self,
                get_translation(self.current_language, "error", "Error"),
                f"Failed to find duplicates:\n{e}",
            )
            self.status_label.setText(
                get_translation(
                    self.current_language, "error_finding_duplicates", "Error finding duplicates"
                )
            )
        finally:
            self.progress_bar.setVisible(False)

    def _populate_table_from_collection(self) -> None:
        """Populate table with files from collection."""
        if not self.current_collection:
            return

        files = self.current_collection.files
        self.table.setRowCount(len(files))

        from media_checker.core.utils import format_duration, format_size

        for row, media_file in enumerate(files):
            self.table.setItem(row, 0, QTableWidgetItem(str(media_file.path)))
            self.table.setItem(row, 1, QTableWidgetItem(media_file.file_type))
            self.table.setItem(row, 2, QTableWidgetItem(format_size(media_file.file_size)))
            self.table.setItem(
                row, 3, QTableWidgetItem(format_duration(media_file.duration))
            )
            self.table.setItem(row, 4, QTableWidgetItem(media_file.codec or ""))
            self.table.setItem(row, 5, QTableWidgetItem("1"))
            self.table.setItem(row, 6, QTableWidgetItem(media_file.parent_dir))

    def _populate_table(self, report: list[dict[str, Any]]) -> None:
        """Populate table with duplicate report."""
        self.table.setRowCount(len(report))

        from media_checker.core.utils import format_duration, format_size

        for row, item in enumerate(report):
            # Show first file path
            paths = item["paths"]
            first_path = paths[0] if paths else ""
            self.table.setItem(row, 0, QTableWidgetItem(first_path))
            self.table.setItem(row, 1, QTableWidgetItem(item["file_type"]))
            self.table.setItem(row, 2, QTableWidgetItem(format_size(item["file_size"])))
            duration_str = (
                format_duration(item.get("duration")) if item.get("duration") else "N/A"
            )
            self.table.setItem(row, 3, QTableWidgetItem(duration_str))
            self.table.setItem(row, 4, QTableWidgetItem(item.get("codec") or ""))
            self.table.setItem(row, 5, QTableWidgetItem(str(item["count"])))
            # Show parent directories
            dirs_str = " | ".join(item["parent_dirs"][:3])
            self.table.setItem(row, 6, QTableWidgetItem(dirs_str))

    def _export_report(self) -> None:
        """Export duplicate report."""
        if not self.current_report:
            return

        output_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Duplicate Report",
            "duplicate_report.csv",
            "CSV Files (*.csv);;JSON Files (*.json);;Text Files (*.txt);;All Files (*)",
        )

        if not output_path:
            return

        self.status_label.setText(
            get_translation(self.current_language, "exporting", "Exporting...")
        )
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        try:
            if output_path.endswith(".json"):
                export_duplicate_report_json(self.current_report, output_path)
            elif output_path.endswith(".txt"):
                export_duplicate_list_txt(self.current_report, output_path)
            else:
                export_duplicate_report_csv(self.current_report, output_path)

            exported_msg = get_translation(
                self.current_language, "exported_successfully", "Exported successfully!"
            )
            self.status_label.setText(
                get_translation(
                    self.current_language,
                    "exported_to",
                    "Exported to {path}",
                ).format(path=output_path)
            )
            QMessageBox.information(
                self,
                get_translation(self.current_language, "success", "Success"),
                f"{exported_msg}\n\n{output_path}",
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                get_translation(self.current_language, "error", "Error"),
                f"Failed to export:\n{e}",
            )
            self.status_label.setText(
                get_translation(
                    self.current_language, "error_during_export", "Error during export"
                )
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

