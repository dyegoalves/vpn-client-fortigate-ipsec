"""
Main Window Module

This module contains the main application class (VPNIPSecClientApp) and all UI components
for managing IPsec VPN connections.
"""

import os
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QMessageBox,
    QStatusBar,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPalette, QColor, QIcon

# Import from other modules
from ..ipsec.ipsec_manager import IPsecManager
from ..loggers.app_loggers import AppLoggers
from ..config.app_config import (
    APP_TITLE,
    WINDOW_SIZE,
    TOGGLE_STYLE_ON,
    TOGGLE_STYLE_OFF,
    TOGGLE_STYLE_CONNECTING,
    CONNECTION_STATES,
    DEFAULT_MESSAGES,
)
from .connection_config_widget import ConnectionConfigWidget
from .status_log_widget import StatusLogWidget


class MainWindow(QMainWindow):
    """
    GUI application for managing IPsec VPN connections.
    """

    def __init__(self):
        super().__init__()
        self.connection_manager = IPsecManager()
        self.log_manager = AppLoggers()
        self.is_connected = False
        self.current_conn_name = None
        self.initUI()

    def initUI(self):
        """Initializes the user interface."""
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(*WINDOW_SIZE)

        # Set window icon
        script_dir = os.path.dirname(os.path.realpath(__file__))
        # Navigate up to src/ then to assets/
        icon_path = os.path.join(script_dir, "..", "assets", "icon.svg")
        icon = QIcon(icon_path)
        if icon.isNull():
            print(f"WARNING: Failed to load application icon from: {icon_path}")
        self.setWindowIcon(icon)

        self.center_window()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # ... (The rest of the UI setup is the same as before)
        title_label = QLabel("Cliente VPN IPsec Fortigate")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        self.config_widget = ConnectionConfigWidget(self.connection_manager)
        self.config_widget.connection_changed.connect(self.on_connection_changed)
        self.config_widget.toggle_requested.connect(self.toggle_connection)
        layout.addWidget(self.config_widget)

        self.status_log_widget = StatusLogWidget()
        self.status_log_widget.clear_logs_requested.connect(self.clear_logs)
        layout.addWidget(self.status_log_widget)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(DEFAULT_MESSAGES["READY"])

        self.add_status_message(DEFAULT_MESSAGES["INIT"])
        self.add_status_message(DEFAULT_MESSAGES["CHECKING_CONFIG"])

        self.load_ipsec_config()
        self.apply_system_theme()

    # ... (All other methods from VPNIPSecClientApp are the same)
    def load_ipsec_config(self):
        """Carrega a configuração IPsec do sistema."""
        try:
            connections = self.connection_manager.load_connections()

            if connections:
                self.config_widget.set_connections(connections)
                first_conn = self.config_widget.get_selected_connection()
                self.current_conn_name = first_conn
                config_file_path, server_addr, conn_details = (
                    self.connection_manager.get_connection_details(first_conn)
                )
                self.config_widget.update_connection_details(
                    first_conn, config_file_path, server_addr, conn_details
                )
                self.refresh_connection_status()
                self.add_status_message(f"Loaded IPsec configuration: {first_conn}")
            else:
                self.config_widget.set_connections([])
                self.config_widget.set_error_state("No configurations found")
                self.add_status_message(DEFAULT_MESSAGES["NO_CONFIGS"])

        except Exception as e:
            self.add_status_message(f"Error loading IPsec configuration: {str(e)}")
            self.config_widget.set_error_state(CONNECTION_STATES["ERROR"])

    def on_connection_changed(self, conn_name):
        """Atualiza a interface quando a conexão selecionada muda."""
        if conn_name:
            self.current_conn_name = conn_name
            config_file_path, server_addr, conn_details = (
                self.connection_manager.get_connection_details(conn_name)
            )
            self.config_widget.update_connection_details(
                conn_name, config_file_path, server_addr, conn_details
            )
            self.refresh_connection_status()

    def refresh_connection_status(self):
        """Atualiza o status da conexão atual."""
        if not self.current_conn_name or self.current_conn_name in [
            "No configurations found",
            "Not installed",
            CONNECTION_STATES["ERROR"],
        ]:
            return

        status, is_connected = self.connection_manager.get_connection_status(
            self.current_conn_name
        )
        self.config_widget.update_status(status, is_connected)

        if is_connected and not self.is_connected:
            self.is_connected = True
            self.log_manager.set_connection_status(True)
            self.log_manager.create_log_file(self.current_conn_name)
            self.add_status_message(
                f"Connected to {self.current_conn_name}. Log file created.",
                show_in_ui=True,
            )
        elif not is_connected and self.is_connected:
            self.is_connected = False
            self.log_manager.set_connection_status(False)
            self.log_manager.delete_log_file()
            self.add_status_message(
                f"Disconnected from {self.current_conn_name}.", show_in_ui=True
            )

    def toggle_connection(self):
        """Alterna a conexão IPsec entre ON/OFF."""
        if not self.current_conn_name or self.current_conn_name in [
            "No configurations found",
            "Not installed",
            CONNECTION_STATES["ERROR"],
        ]:
            QMessageBox.critical(
                self, "Error", "No IPsec configuration available to connect."
            )
            return

        if self.config_widget.toggle_switch.isChecked():
            self.config_widget.update_status(CONNECTION_STATES["CONNECTING"], True)
            self.connect_vpn()
        else:
            self.config_widget.update_status(CONNECTION_STATES["DISCONNECTING"], False)
            self.disconnect_vpn()

    def connect_vpn(self):
        """Conecta ao servidor VPN usando IPsec."""
        if not self.current_conn_name:
            return
        self.add_status_message(
            f"Initiating IPsec connection: {self.current_conn_name}..."
        )
        success, message = self.connection_manager.connect_connection(
            self.current_conn_name
        )
        if success:
            QTimer.singleShot(2000, self.refresh_connection_status)
        else:
            self.add_status_message(message, show_in_ui=True)
            self.config_widget.update_status(CONNECTION_STATES["DISCONNECTED"], False)

    def disconnect_vpn(self):
        """Desconecta do servidor VPN usando IPsec."""
        if not self.current_conn_name:
            return
        self.add_status_message(
            f"Disconnecting IPsec connection: {self.current_conn_name}...",
            show_in_ui=True,
        )
        success, message = self.connection_manager.disconnect_connection(
            self.current_conn_name
        )
        if success:
            self.status_bar.showMessage(CONNECTION_STATES["DISCONNECTED"])
            self.config_widget.update_status(CONNECTION_STATES["DISCONNECTED"], False)
        else:
            self.add_status_message(message, show_in_ui=True)

    def clear_logs(self):
        """Limpa o display de logs."""
        self.status_log_widget.clear_display()

    def apply_system_theme(self):
        """Detecta e aplica o tema do sistema (claro/escuro) para o aplicativo."""
        system_palette = self.style().standardPalette()
        window_color = system_palette.color(QPalette.ColorRole.Window)
        luminance = (
            0.299 * window_color.red()
            + 0.587 * window_color.green()
            + 0.114 * window_color.blue()
        ) / 255
        if luminance < 0.5:
            self.set_dark_theme()

    def set_dark_theme(self):
        """Aplica um tema escuro ao aplicativo."""
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(40, 40, 40))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(65, 105, 225))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(240, 240, 240))
        dark_palette.setColor(
            QPalette.ColorRole.Disabled, QPalette.ColorRole.Text, QColor(120, 120, 120)
        )
        dark_palette.setColor(
            QPalette.ColorRole.Disabled,
            QPalette.ColorRole.ButtonText,
            QColor(120, 120, 120),
        )
        dark_palette.setColor(
            QPalette.ColorRole.Disabled,
            QPalette.ColorRole.WindowText,
            QColor(120, 120, 120),
        )
        self.setPalette(dark_palette)
        app = QApplication.instance()
        if app:
            app.setPalette(dark_palette)

    def add_status_message(self, message: str, show_in_ui: bool = True):
        """Adiciona uma mensagem ao display de status e ao arquivo de log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"

        # Adiciona mensagem ao sistema de log
        self.log_manager.add_log_message(formatted_message)

        if show_in_ui:
            self.status_log_widget.add_message(message)

    def center_window(self):
        """Centraliza a janela na tela."""
        window_geometry = self.frameGeometry()
        center_point = self.screen().availableGeometry().center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
