import os
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QGroupBox,
    QGridLayout,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont




class StatusLogWidget(QGroupBox):
    clear_logs_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("Status da Conexão e Logs", parent)
        self.initUI()

    def initUI(self):
        status_layout = QVBoxLayout()

        log_area_layout = QGridLayout()

        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setMaximumHeight(150)

        log_area_layout.addWidget(self.status_display, 0, 0)

        clear_logs_btn = QPushButton("🗑")
        clear_logs_btn.clicked.connect(self.clear_logs_requested.emit)
        clear_logs_btn.setStyleSheet(
            "QPushButton {"
            "  background-color: rgba(255, 200, 200, 180);"
            "  border: 1px solid #ff6666;"
            "  border-radius: 4px;"
            "  color: #cc0000;"
            "  font-size: 15px;"
            "  padding: 3px;"
            "  min-width: 20px;"
            "  max-width: 20px;"
            "  min-height: 20px;"
            "  max-height: 20px;"
            "  margin: 6px;"
            "}"
            "QPushButton:hover {"
            "  background-color: rgba(255, 150, 150, 200);"
            "  border: 1px solid #ff3333;"
            "  color: #990000;"
            "}"
            "QPushButton:pressed {"
            "  background-color: rgba(255, 100, 100, 220);"
            "}"
        )
        clear_logs_btn.setFixedSize(20, 20)

        log_area_layout.addWidget(clear_logs_btn, 0, 0, Qt.AlignBottom | Qt.AlignRight)

        status_layout.addLayout(log_area_layout)
        self.setLayout(status_layout)

    def add_message(self, message: str):
        if not self._is_routine_status_message(message):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            self.status_display.append(formatted_message)

    def _is_routine_status_message(self, message: str) -> bool:
        """Verifica se a mensagem é de status rotineira."""
        routine_messages = [
            "Loaded IPsec configuration",
            "Current status:",
            "Command output:",
        ]
        return any(routine_msg in message for routine_msg in routine_messages)

    def clear_display(self):
        self.status_display.clear()
