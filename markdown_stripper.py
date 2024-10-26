import re
import socket
import sqlite3
import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QByteArray, QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class SettingsDialog(QDialog):
    """Dialog for managing application settings"""

    def __init__(self, parent: Optional[QMainWindow] = None) -> None:
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        layout = QVBoxLayout()
        prompt_layout = QHBoxLayout()
        prompt_label = QLabel("Prompt Location:")
        self.prompt_path = QLineEdit()
        self.prompt_path.setText(self.parent.prompt_location)
        self.prompt_path.textChanged.connect(self.check_path)
        self.path_status = QLabel()
        prompt_layout.addWidget(prompt_label)
        prompt_layout.addWidget(self.prompt_path)
        prompt_layout.addWidget(self.path_status)
        layout.addLayout(prompt_layout)
        layout.addWidget(QLabel("Window Settings:"))
        window_info = QTextEdit()
        window_info.setPlainText(
            f"Position: {self.parent.pos().x()}, {self.parent.pos().y()}\n"
            f"Size: {self.parent.size().width()}x{self.parent.size().height()}"
        )
        window_info.setReadOnly(True)
        window_info.setMaximumHeight(100)
        layout.addWidget(window_info)
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(save_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.check_path()

    def check_path(self) -> None:
        """Validate prompt file path and update status indicator"""
        path = Path(self.prompt_path.text())
        is_valid = path.exists() and path.is_file()
        if is_valid:
            self.path_status.setText("✓")
            self.path_status.setStyleSheet("color: green;")
        else:
            self.path_status.setText("✗")
            self.path_status.setStyleSheet("color: red;")
        self.parent.copy_prompt_btn.setEnabled(is_valid)
        if is_valid:
            self.parent.copy_prompt_btn.setToolTip(
                "Copy prompt template to clipboard"
            )
        else:
            self.parent.copy_prompt_btn.setToolTip(
                f"Prompt file not found: {path}"
            )

    def save_settings(self) -> None:
        """Save settings and close dialog"""
        self.parent.prompt_location = self.prompt_path.text()
        self.parent.save_settings()
        self.parent.check_prompt_file()
        self.parent.show_status("Settings saved", "red")
        self.close()


class MarkdownStripper(QMainWindow):
    """Main application window for stripping markdown formatting"""

    def __init__(self) -> None:
        super().__init__()
        self.hostname = socket.gethostname().split(".")[0]
        self.db_path = Path(f"{self.hostname}.settings")
        self.prompt_location = "prompt.txt"
        self.copy_prompt_btn = QPushButton("Copy Prompt")
        self.copy_prompt_btn.clicked.connect(self.copy_prompt)
        self.init_database()
        self.load_settings()
        self.setWindowTitle("Markdown Stripper")
        self.setMinimumSize(600, 500)
        self.load_window_settings()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.copy_prompt_btn)
        self.check_prompt_file()
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Paste markdown text here...")
        layout.addWidget(self.input_text)
        self.process_btn = QPushButton("Process")
        self.process_btn.clicked.connect(self.process_text)
        layout.addWidget(self.process_btn)
        self.output_text = QTextEdit()
        self.output_text.setPlaceholderText("Stripped text will appear here...")
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)
        button_layout = QVBoxLayout()
        self.copy_btn = QPushButton("Copy")
        self.clear_btn = QPushButton("Clear")
        self.exit_btn = QPushButton("Exit")
        button_layout.addWidget(self.copy_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.exit_btn)
        self.copy_btn.clicked.connect(self.copy_text)
        self.clear_btn.clicked.connect(self.clear_text)
        self.exit_btn.clicked.connect(self.close)
        layout.addLayout(button_layout)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_message = QLabel("Ready")
        self.status_bar.addWidget(self.status_message)
        self.create_menu_bar()

    def create_menu_bar(self) -> None:
        """Initialize application menu bar"""
        menubar = self.menuBar()
        options_menu = menubar.addMenu("Options")
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        options_menu.addAction(settings_action)

    def show_settings(self) -> None:
        """Display settings dialog"""
        dialog = SettingsDialog(self)
        dialog.exec()

    def init_database(self) -> None:
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        conn.text_factory = bytes
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS window_settings (
                setting_name TEXT PRIMARY KEY, value BLOB)"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS settings (
                setting_name TEXT PRIMARY KEY, value TEXT)"""
        )
        cursor.execute(
            """INSERT OR IGNORE INTO settings (setting_name, value)
            VALUES (?, ?)""",
            ("prompt_location", "prompt.txt"),
        )
        conn.commit()
        conn.close()

    def save_settings(self) -> None:
        """Save application settings to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT OR REPLACE INTO settings (setting_name, value)
            VALUES (?, ?)""",
            ("prompt_location", self.prompt_location),
        )
        conn.commit()
        conn.close()
        self.save_window_settings()

    def load_settings(self) -> None:
        """Load application settings from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT value FROM settings WHERE setting_name=?",
                ("prompt_location",),
            )
            result = cursor.fetchone()
            if result:
                self.prompt_location = result[0]
            conn.close()
            self.load_window_settings()
        except sqlite3.Error:
            self.prompt_location = "prompt.txt"

    def save_window_settings(self) -> None:
        """Save window geometry to database"""
        geometry_data = self.saveGeometry()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT OR REPLACE INTO window_settings (setting_name, value)
            VALUES (?, ?)""",
            ("geometry", geometry_data.data()),
        )
        conn.commit()
        conn.close()

    def load_window_settings(self) -> None:
        """Load and apply window geometry from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.text_factory = bytes
            cursor = conn.cursor()
            cursor.execute(
                "SELECT value FROM window_settings WHERE setting_name=?",
                ("geometry",),
            )
            result = cursor.fetchone()
            conn.close()
            if result:
                geometry_data = QByteArray(result[0])
                self.restoreGeometry(geometry_data)
            else:
                self.resize(600, 500)
        except (sqlite3.Error, ValueError):
            self.resize(600, 500)

    def moveEvent(self, event) -> None:
        """Handle window move event"""
        super().moveEvent(event)
        self.save_window_settings()

    def resizeEvent(self, event) -> None:
        """Handle window resize event"""
        super().resizeEvent(event)
        self.save_window_settings()

    def strip_markdown(self, text: str) -> str:
        """Remove markdown formatting while preserving content"""
        text = re.sub(r"^(#{1,6}\s*)(.*)", r"\2", text, flags=re.MULTILINE)
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text, flags=re.DOTALL)
        text = re.sub(r"__(.*?)__", r"\1", text, flags=re.DOTALL)
        text = re.sub(r"\*(.*?)\*", r"\1", text, flags=re.DOTALL)
        text = re.sub(r"_(.*?)_", r"\1", text, flags=re.DOTALL)
        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
        text = re.sub(r"```[\s\S]*?```", lambda m: m.group(0)[3:-3], text)
        text = re.sub(r"`([^`]+)`", r"\1", text)
        text = re.sub(r"^[ \t]*[-*+]\s+(.*)", r"- \1", text, flags=re.MULTILINE)
        text = re.sub(
            r"^[ \t]*(\d+\.)\s+(.*)", r"\1 \2", text, flags=re.MULTILINE
        )
        text = re.sub(r"^[ \t]*>\s+(.*)", r"\1", text, flags=re.MULTILINE)
        return text

    def copy_prompt(self) -> None:
        """Copy prompt file contents to clipboard"""
        try:
            with open(self.prompt_location, "r", encoding="utf-8") as file:
                prompt_text = file.read()
            clipboard = QApplication.clipboard()
            clipboard.setText(prompt_text)
            self.show_status("Prompt copied to clipboard", "red")
        except FileNotFoundError:
            self.show_status(f"{self.prompt_location} not found", "red")

    def show_status(self, message: str, color: str) -> None:
        """Display status message with color"""
        self.status_message.setText(message)
        self.status_message.setStyleSheet(f"color: {color};")
        QTimer.singleShot(5000, self.reset_status)

    def reset_status(self) -> None:
        """Reset status message to default"""
        self.status_message.setText("Ready")
        self.status_message.setStyleSheet("color: black;")

    def process_text(self) -> None:
        """Process markdown text and copy result to clipboard"""
        input_text = self.input_text.toPlainText()
        stripped_text = self.strip_markdown(input_text)
        self.output_text.setPlainText(stripped_text)
        clipboard = QApplication.clipboard()
        clipboard.setText(stripped_text)
        self.show_status("Text processed and copied to clipboard", "red")

    def copy_text(self) -> None:
        """Copy output text to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output_text.toPlainText())
        self.show_status("Output text copied to clipboard", "red")

    def clear_text(self) -> None:
        """Clear input and output text"""
        self.input_text.clear()
        self.output_text.clear()
        self.show_status("Text cleared", "red")

    def closeEvent(self, event) -> None:
        """Handle window close event"""
        self.save_window_settings()
        self.save_settings()
        event.accept()

    def check_prompt_file(self) -> None:
        """Check if prompt file exists and enable/disable button accordingly"""
        prompt_path = Path(self.prompt_location)
        self.copy_prompt_btn.setEnabled(
            prompt_path.exists() and prompt_path.is_file()
        )
        if not self.copy_prompt_btn.isEnabled():
            self.copy_prompt_btn.setToolTip(
                f"Prompt file not found: {self.prompt_location}"
            )
        else:
            self.copy_prompt_btn.setToolTip("Copy prompt template to clipboard")


def main() -> None:
    """Application entry point"""
    app = QApplication(sys.argv)
    window = MarkdownStripper()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
