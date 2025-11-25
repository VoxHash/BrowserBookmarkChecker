"""PyQt6 GUI main window."""

import sys
from pathlib import Path
from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
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
    QHBoxLayout,
)

from bookmark_checker.core.exporters import export_dedupe_report_csv, export_netscape_html
from bookmark_checker.core.merge import merge_collections
from bookmark_checker.core.parsers import parse_many


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()
        self.setWindowTitle("BrowserBookmarkChecker")
        self.setMinimumSize(1000, 640)

        # Data
        self.current_collection = None
        self.current_report: List[dict] = []

        # Setup UI
        self._setup_ui()
        self._setup_style()

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

        self.btn_import = QPushButton("Import Files")
        self.btn_import.clicked.connect(self._import_files)
        top_layout.addWidget(self.btn_import)

        self.btn_merge = QPushButton("Find & Merge")
        self.btn_merge.clicked.connect(self._find_and_merge)
        self.btn_merge.setEnabled(False)
        top_layout.addWidget(self.btn_merge)

        self.btn_export = QPushButton("Export Merged")
        self.btn_export.clicked.connect(self._export_merged)
        self.btn_export.setEnabled(False)
        top_layout.addWidget(self.btn_export)

        top_layout.addStretch()

        # Similarity slider
        similarity_label = QLabel("Similarity:")
        top_layout.addWidget(similarity_label)

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
        self.table.setHorizontalHeaderLabels(["Title", "URL (canonical)", "Folder", "Source", "Count"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Bottom status
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        bottom_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        bottom_layout.addWidget(self.status_label)

        layout.addWidget(bottom_widget)

    def _setup_style(self) -> None:
        """Set up dark Fusion style."""
        self.setStyleSheet("""
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
        """)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        """Handle drop event."""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
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

    def _process_files(self, files: List[str]) -> None:
        """Process imported files."""
        self.status_label.setText("Parsing files...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate

        try:
            self.current_collection = parse_many(files)
            if len(self.current_collection.bookmarks) == 0:
                QMessageBox.warning(
                    self,
                    "No Bookmarks Found",
                    f"No bookmarks were found in the selected files.\n\nFiles: {', '.join(files)}",
                )
                self.status_label.setText("No bookmarks found in files")
                self.btn_merge.setEnabled(False)
            else:
                self.status_label.setText(
                    f"Loaded {len(self.current_collection.bookmarks)} bookmarks from {len(files)} file(s)"
                )
                self.btn_merge.setEnabled(True)
                # Show bookmarks in table immediately
                self._populate_table_from_collection()
        except Exception as e:
            import traceback
            error_msg = f"Failed to parse files:\n{str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Error", error_msg)
            self.status_label.setText("Error loading files")
            self.btn_merge.setEnabled(False)
        finally:
            self.progress_bar.setVisible(False)

    def _find_and_merge(self) -> None:
        """Find duplicates and merge."""
        if not self.current_collection:
            return

        self.status_label.setText("Merging and deduplicating...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        try:
            similarity = self.similarity_slider.value()
            merged, report = merge_collections(
                self.current_collection, similarity_threshold=similarity, enable_fuzzy=True
            )

            self.current_report = report
            self._populate_table(report)

            self.status_label.setText(
                f"Merged to {len(merged.bookmarks)} unique bookmarks ({len(report)} groups)"
            )
            self.btn_export.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to merge:\n{e}")
            self.status_label.setText("Error during merge")
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

    def _populate_table(self, report: List[dict]) -> None:
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
        if not self.current_collection or not self.current_report:
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Merged Bookmarks",
            "merged_bookmarks.html",
            "HTML Files (*.html);;All Files (*)",
        )

        if not output_path:
            return

        self.status_label.setText("Exporting...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        try:
            # Re-merge to get merged collection
            similarity = self.similarity_slider.value()
            merged, _ = merge_collections(
                self.current_collection, similarity_threshold=similarity, enable_fuzzy=True
            )

            # Export HTML
            export_netscape_html(merged, output_path)

            # Export CSV
            csv_path = Path(output_path).with_suffix("").with_name(
                f"{Path(output_path).stem}_dedupe_report.csv"
            )
            export_dedupe_report_csv(self.current_report, str(csv_path))

            self.status_label.setText(f"Exported to {output_path} and {csv_path}")
            QMessageBox.information(self, "Success", f"Exported successfully!\n\n{output_path}\n{csv_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export:\n{e}")
            self.status_label.setText("Error during export")
        finally:
            self.progress_bar.setVisible(False)


def launch_gui() -> None:
    """Launch the GUI application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set dark palette
    from PyQt6.QtGui import QPalette, QColor

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

