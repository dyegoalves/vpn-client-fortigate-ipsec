import os
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer


class StatusLogWidget(QWidget):
    clear_logs_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # Layout principal vertical
        main_layout = QVBoxLayout()
        
        # Criar layout horizontal para o título e o botão de limpar logs
        title_layout = QHBoxLayout()
        
        # Título do grupo
        title_label = QLabel("Status da Conexão e Logs")
        font = QFont()
        font.setBold(True)
        title_label.setFont(font)
        
        # Botão de limpar logs
        clear_logs_btn = QPushButton()
        icon_path = os.path.join(
            os.path.dirname(__file__), "..", "assets", "clear_log_icon.svg"
        )
        pixmap = QPixmap(18, 18)  # Tamanho do pixmap igual ao tamanho do botão
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        svg_renderer = QSvgRenderer(icon_path)
        svg_renderer.render(painter)
        painter.end()
        clear_logs_btn.setIcon(QIcon(pixmap))
        clear_logs_btn.clicked.connect(self.clear_logs_requested.emit)
        clear_logs_btn.setStyleSheet(
            "QPushButton {"
            "  background-color: rgba(255, 200, 200, 180);"
            "  border: 1px solid #ff6666;"
            "  border-radius: 4px;"
            "  color: #cc0000;"
            "  font-size: 15px;"
            "  padding: 4px;"
            "  min-width: 18px;"
            "  max-width: 18px;"
            "  min-height: 18px;"
            "  max-height: 18px;"
            "  margin: 0 0 0 10px;"  # Espaçamento à esquerda
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
        clear_logs_btn.setIconSize(clear_logs_btn.size())
        clear_logs_btn.setFixedSize(18, 18)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()  # Adiciona um espaçamento expansível
        title_layout.addWidget(clear_logs_btn)
        
        # Adiciona o layout do título ao layout principal
        main_layout.addLayout(title_layout)
        
        # Área de exibição de logs com borda para simular o grupo
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setMaximumHeight(150)
        self.status_display.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        # Adiciona um pequeno espaçamento à direita para evitar sobreposição do scrollbar
        self.status_display.setViewportMargins(0, 0, 10, 0)

        main_layout.addWidget(self.status_display)
        
        # Define o layout principal para o widget
        self.setLayout(main_layout)

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
