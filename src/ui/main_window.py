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
    CONNECTION_STATES,
    APP_TITLE,
    WINDOW_SIZE,
    DEFAULT_MESSAGES,
)
from .connection_config_widget import ConnectionConfigWidget
from .status_log_widget import StatusLogWidget
from ..utils.system_theme import get_system_color_scheme # Importar a nova função
from .theme_selector import ThemeSelectorWidget


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

        self.add_status_message(DEFAULT_MESSAGES["INIT"])
        self.add_status_message(DEFAULT_MESSAGES["CHECKING_CONFIG"])

        self.load_ipsec_config()
        
        # Iniciar um timer para verificar periodicamente o status da conexão
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.refresh_connection_status_if_needed)
        self.status_timer.start(5000)  # Atualizar a cada 5 segundos
        
        # Adicionar controle de tempo para evitar chamadas muito frequentes
        import time
        self._last_refresh_time = time.time()

        # Criar o seletor de tema e adicionar à interface
        self.theme_selector = ThemeSelectorWidget()
        # Conectar o sinal de mudança de tema
        self.theme_selector.theme_changed.connect(self.handle_theme_change)
        
        # Adicionar o seletor de tema ao layout principal
        layout.addWidget(self.theme_selector)
        
        # Iniciar um timer para verificar periodicamente o tema do sistema (quando em modo automático)
        self.theme_timer = QTimer()
        self.theme_timer.timeout.connect(self.update_theme)
        self.theme_timer.start(10000)  # Verificar a cada 10 segundos
        self.current_app_theme = get_system_color_scheme() # Armazenar o tema atual do app
        
        # Definir o tema inicial como automático
        self.current_manual_theme = None
        self.theme_selector.set_selected_theme("auto")

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

        # Evitar atualizações muito frequentes
        import time
        current_time = time.time()
        # Verificar se o atributo existe, senão inicializar
        if not hasattr(self, '_last_refresh_time'):
            self._last_refresh_time = current_time - 2  # Definir um valor antigo para permitir a primeira atualização
            
        if current_time - self._last_refresh_time < 1:  # No mínimo 1 segundo entre atualizações
            return
        self._last_refresh_time = current_time

        status, is_connected = self.connection_manager.get_connection_status(
            self.current_conn_name
        )
        self.config_widget.update_status(status, is_connected)

        # Verificar se houve mudança no estado de conexão
        if is_connected and not self.is_connected:
            # Mudança para conectado
            self.is_connected = True
            self.log_manager.set_connection_status(True)
            self.log_manager.create_log_file(self.current_conn_name)
            self.add_status_message(
                f"Connected to {self.current_conn_name}. Log file created.",
                show_in_ui=True,
            )
        elif not is_connected and self.is_connected:
            # Mudança para desconectado
            self.is_connected = False
            self.log_manager.set_connection_status(False)
            self.log_manager.delete_log_file()
            self.add_status_message(
                f"Disconnected from {self.current_conn_name}.", show_in_ui=True
            )

    def toggle_connection(self, is_checked: bool):
        """Alterna a conexão IPsec entre ON/OFF."""
        if not self.current_conn_name or self.current_conn_name in [
            "No configurations found",
            "Not installed",
            CONNECTION_STATES["ERROR"],
        ]:
            QMessageBox.critical(
                self, "Error", "No IPsec configuration available to connect."
            )
            # Resetar o toggle switch para o estado anterior se houver um erro
            QTimer.singleShot(100, lambda: self.config_widget.update_status(CONNECTION_STATES["DISCONNECTED"], False))
            return

        if is_checked:
            # Verificar se já está conectando ou conectado para evitar ações duplicadas
            current_status, _ = self.connection_manager.get_connection_status(
                self.current_conn_name
            )
            if current_status == CONNECTION_STATES["CONNECTING"]:
                # Já está tentando conectar, não fazer nada
                return
            elif current_status == CONNECTION_STATES["CONNECTED"]:
                # Se já está conectado, atualizar o status para refletir o estado correto
                QTimer.singleShot(100, lambda: self.config_widget.update_status(CONNECTION_STATES["CONNECTED"], True))
                return

            self.config_widget.update_status(CONNECTION_STATES["CONNECTING"], False)
            self.connect_vpn()
        else:
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
        self.add_status_message(message, show_in_ui=True)
        
        if success:
            # Aguardar um tempo menor e verificar o status mais vezes para feedback mais rápido
            # Atualizar status após a tentativa de conexão
            QTimer.singleShot(1500, self.refresh_connection_status)  # Verificar após 1.5 segundos
            QTimer.singleShot(4000, self.refresh_connection_status)  # Verificar novamente após 4 segundos
        else:
            # Em caso de falha, restaurar o estado do toggle para DISCONNECTED
            # Usar uma chamada adiada para evitar conflitos durante a transição
            QTimer.singleShot(100, lambda: self.config_widget.update_status(CONNECTION_STATES["DISCONNECTED"], False))

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
        self.add_status_message(message, show_in_ui=True)
        
        if success:
            # Verificar status com um intervalo adequado
            QTimer.singleShot(1500, self.refresh_connection_status)  # Verificar após 1.5 segundos
            QTimer.singleShot(4000, self.refresh_connection_status)  # Verificar novamente após 4 segundos
        else:
            # Em caso de falha, atualizar o status para refletir o estado real
            # Usar uma chamada adiada para evitar conflitos durante a transição
            QTimer.singleShot(100, self.refresh_connection_status)

    def clear_logs(self):
        """Limpa o display de logs."""
        self.status_log_widget.clear_display()



    def add_status_message(self, message: str, show_in_ui: bool = True):
        """Adiciona uma mensagem ao display de status e ao arquivo de log."""
        # Adiciona mensagem ao sistema de log (o log_manager cuida do timestamp)
        self.log_manager.add_log_message(message)

        if show_in_ui:
            self.status_log_widget.add_message(message)

    def refresh_connection_status_if_needed(self):
        """Atualiza o status da conexão se não estiver em estado de transição."""
        if not self.current_conn_name:
            return
            
        # Evitar atualizações muito frequentes
        import time
        current_time = time.time()
        # Verificar se o atributo existe, senão inicializar
        if not hasattr(self, '_last_refresh_time'):
            self._last_refresh_time = current_time - 2  # Definir um valor antigo para permitir a primeira atualização
            
        if current_time - self._last_refresh_time < 1:  # No mínimo 1 segundo entre atualizações
            return
        self._last_refresh_time = current_time
            
        # Obter o status atual da conexão
        status, is_connected = self.connection_manager.get_connection_status(
            self.current_conn_name
        )
        
        # Atualizar apenas se não estiver em estado de transição (CONNECTING/DISCONNECTING)
        # Levando em consideração os status retornados em português também
        if status not in [CONNECTION_STATES["CONNECTING"], CONNECTION_STATES["DISCONNECTING"], "Conectando"]:
            # Só atualizar o widget de status, mas não executar ações de logging/mensagem
            # que já são tratadas em connect_vpn/disconnect_vpn
            self.config_widget.update_status(status, is_connected)

    def center_window(self):
        """Centraliza a janela na tela."""
        window_geometry = self.frameGeometry()
        center_point = self.screen().availableGeometry().center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    def update_theme(self):
        """Verifica o tema do sistema e aplica o stylesheet correspondente.
        Este método é chamado periodicamente quando o modo automático está ativo."""
        # Apenas atualizar automaticamente se estiver no modo automático
        if self.theme_selector.get_selected_theme() != "auto":
            return
            
        current_system_theme = get_system_color_scheme()
        if current_system_theme != self.current_app_theme:
            self.current_app_theme = current_system_theme
            self.apply_theme(current_system_theme)

    def handle_theme_change(self, theme: str):
        """Lida com a mudança de tema selecionada pelo usuário no dropdown."""
        if theme == "auto":
            # Voltar ao modo automático
            self.current_app_theme = get_system_color_scheme()
            self.apply_theme(self.current_app_theme)
            self.add_status_message("Tema alterado para automático (segue o tema do sistema)", show_in_ui=True)
        elif theme == "dark":
            self.apply_theme("Dark")
            self.add_status_message("Tema alterado para escuro", show_in_ui=True)
        elif theme == "light":
            self.apply_theme("Light")
            self.add_status_message("Tema alterado para claro", show_in_ui=True)
            
        # Atualizar a referência do tema atual para o manual
        if theme != "auto":
            self.current_manual_theme = theme.capitalize() if theme != "auto" else None
        else:
            self.current_manual_theme = None

    def apply_theme(self, theme: str):
        """Aplica o tema especificado."""
        app = QApplication.instance()
        if app:
            script_dir = os.path.dirname(os.path.realpath(__file__))
            if theme.lower() == "dark":
                style_path = os.path.join(script_dir, "..", "assets", "styles", "dark_theme.qss")
            else:
                style_path = os.path.join(script_dir, "..", "assets", "styles", "light_theme.qss")
            
            if os.path.exists(style_path):
                with open(style_path, "r") as f:
                    app.setStyleSheet(f.read())
            else:
                print(f"WARNING: Stylesheet not found: {style_path}")
