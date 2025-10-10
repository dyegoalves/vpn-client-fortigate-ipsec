"""
VPN IPsec Client Application - Main Module

This module contains the main application class and UI components for managing IPsec VPN connections.
"""

import sys
import os
from typing import List, Optional, Tuple
import subprocess
from datetime import datetime

# Define a plataforma Qt para xcb para melhor compatibilidade com o ambiente Deepin
os.environ['QT_QPA_PLATFORM'] = 'xcb'

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, 
                               QTextEdit, QGroupBox, QMessageBox, QStatusBar, QGridLayout)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPalette, QColor


# Constantes de configuração
APP_TITLE = 'VPN IPsec Client v3 - Deepin Integration'
WINDOW_SIZE = (800, 700)

# Estilos CSS
TOGGLE_STYLE_ON = "QPushButton { background-color: green; color: white; font-weight: bold; border-radius: 10px; min-width: 60px; }"
TOGGLE_STYLE_OFF = "QPushButton { background-color: red; color: white; font-weight: bold; border-radius: 10px; min-width: 60px; }"

# Estados de conexão
CONNECTION_STATES = {
    'CONNECTED': 'Connected',
    'DISCONNECTED': 'Disconnected',
    'CONNECTING': 'Connecting...',
    'DISCONNECTING': 'Disconnecting...',
    'NOT_CONFIGURED': 'Not Configured',
    'NO_CONFIG': 'No config',
    'UNAVAILABLE': 'Unavailable',
    'ERROR': 'Error'
}

# Mensagens padrão
DEFAULT_MESSAGES = {
    'INIT': 'VPN IPsec Client v3 initialized.',
    'CHECKING_CONFIG': 'Checking for existing IPsec configurations...',
    'NO_IPSEC': 'IPsec is not installed on this system.',
    'NO_CONFIGS': 'No IPsec configurations found in system files.',
    'READY': 'VPN IPsec Client ready'
}

# Caminhos de configuração IPsec
IPSEC_CONFIG_PATHS = ['/etc/ipsec.conf']
IPSEC_D_PATH = '/etc/ipsec.d/'

# Diretório para armazenar logs
LOGS_DIR = os.path.expanduser('~/.vpn_ipsec_logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)


class IPsecManager:
    """
    Gerenciador das operações IPsec.
    
    Esta classe encapsula todas as operações relacionadas ao IPsec, incluindo
    leitura de configurações, verificação de status e controle de conexão.
    """
    
    @staticmethod
    def get_ipsec_connections() -> List[str]:
        """
        Retorna uma lista de conexões IPsec encontradas nos arquivos de configuração.
        
        Returns:
            List[str]: Lista de nomes de conexões IPsec
        """
        import subprocess
        import re
        
        # Verifica se IPsec está instalado
        result = subprocess.run(['which', 'ipsec'], capture_output=True, text=True)
        if result.returncode != 0:
            return []
        
        connections = []
        config_files = IPSEC_CONFIG_PATHS.copy()
        
        # Verifica arquivos adicionais em /etc/ipsec.d/
        if os.path.exists(IPSEC_D_PATH):
            for file in os.listdir(IPSEC_D_PATH):
                if file.endswith('.conf') and not file.endswith('~'):
                    config_files.append(f'{IPSEC_D_PATH}{file}')
        
        # Lê os arquivos de configuração para encontrar conexões
        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    content = f.read()
                    # Encontra conexões no formato 'conn <nome>'
                    found_conns = re.findall(r'^\s*conn\s+([^\s#]+)', content, re.MULTILINE)
                    connections.extend([conn.strip() for conn in found_conns if not conn.strip().startswith('#')])
        
        return connections
    
    @staticmethod
    def get_connection_details(conn_name: str) -> Tuple[str, str]:
        """
        Obtém detalhes de uma conexão específica.
        
        Args:
            conn_name: Nome da conexão IPsec
            
        Returns:
            Tuple[str, str]: (caminho_do_arquivo, endereco_do_servidor)
        """
        config_file_path = IPsecManager._find_connection_file(conn_name)
        if not config_file_path:
            return '', 'Server address not found'
        
        server_addr = IPsecManager._get_server_address(config_file_path, conn_name)
        return config_file_path, server_addr

    @staticmethod
    def _find_connection_file(conn_name: str) -> Optional[str]:
        """
        Encontra o arquivo de configuração que contém uma conexão específica.
        
        Args:
            conn_name: Nome da conexão IPsec
            
        Returns:
            Optional[str]: Caminho do arquivo ou None se não encontrado
        """
        # Procura nos arquivos de configuração principais
        for config_file in IPSEC_CONFIG_PATHS:
            if IPsecManager._connection_exists_in_file(conn_name, config_file):
                return config_file
        
        # Se não encontrar nos arquivos principais, verifica em /etc/ipsec.d/
        if os.path.exists(IPSEC_D_PATH):
            for file in os.listdir(IPSEC_D_PATH):
                if file.endswith('.conf') and not file.endswith('~'):
                    config_file = f'{IPSEC_D_PATH}{file}'
                    if IPsecManager._connection_exists_in_file(conn_name, config_file):
                        return config_file
        
        return None

    @staticmethod
    def _connection_exists_in_file(conn_name: str, file_path: str) -> bool:
        """
        Verifica se uma conexão específica existe em um arquivo de configuração.
        
        Args:
            conn_name: Nome da conexão IPsec
            file_path: Caminho do arquivo de configuração
            
        Returns:
            bool: True se a conexão existe no arquivo, False caso contrário
        """
        import re
        
        if not os.path.exists(file_path):
            return False
        
        with open(file_path, 'r') as f:
            content = f.read()
            # Verifica se a conexão existe neste arquivo
            pattern = rf'^\s*conn\s+{re.escape(conn_name)}\s*($|[\s#])'
            return bool(re.search(pattern, content, re.MULTILINE))
    
    @staticmethod
    def _get_server_address(config_file: str, conn_name: str) -> str:
        """
        Extrai o endereço do servidor para uma conexão específica a partir do arquivo de configuração.
        
        Args:
            config_file: Caminho do arquivo de configuração
            conn_name: Nome da conexão IPsec
            
        Returns:
            str: Endereço do servidor ou mensagem de erro
        """
        import re
        try:
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Encontra a seção para esta conexão
            pattern = rf'^\s*conn\s+{re.escape(conn_name)}\s*\n(.*?)(?=\n\s*conn\s+|\Z)'
            matches = re.search(pattern, content, re.DOTALL | re.MULTILINE)
            
            if matches:
                conn_section = matches.group(1)
                # Procura pelo endereço do servidor remoto (right= ou alsoip=), tratando o erro de digitação 'rithg'
                right_match = re.search(r'^\s*(?:right|rithg)\s*=\s*([^\s#]+)', conn_section, re.MULTILINE)
                if right_match:
                    return right_match.group(1)
                
                # Alternativa: procura por alsoip
                alsoip_match = re.search(r'^\s*alsoip\s*=\s*([^\s#]+)', conn_section, re.MULTILINE)
                if alsoip_match:
                    return alsoip_match.group(1)
                
                # Alternativa: procura por rightsubnet
                rightsubnet_match = re.search(r'^\s*rightsubnet\s*=\s*([^\s#]+)', conn_section, re.MULTILINE)
                if rightsubnet_match:
                    # Extrai o endereço IP da sub-rede se necessário
                    subnet = rightsubnet_match.group(1)
                    if '/' in subnet:
                        return subnet.split('/')[0]  # Retorna o endereço de rede
                    return subnet
            
            return 'Server address not found'
        except Exception as e:
            return f'Error: {str(e)}'
    
    @staticmethod
    def connect_connection(conn_name: str) -> Tuple[bool, str]:
        """
        Inicia uma conexão IPsec.
        
        Args:
            conn_name: Nome da conexão IPsec
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        import subprocess
        
        try:
            # Executa o comando ipsec para iniciar a conexão
            result = subprocess.run(['sudo', 'ipsec', 'up', conn_name], capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, f'IPsec connection "{conn_name}" initiated successfully.'
            else:
                return False, f'Failed to initiate connection "{conn_name}": {result.stderr.strip()}'
        except FileNotFoundError:
            return False, 'Error: IPsec command not found. Please ensure IPsec is installed and in PATH.'
        except Exception as e:
            return False, f'Error initiating connection: {str(e)}'
    
    @staticmethod
    def disconnect_connection(conn_name: str) -> Tuple[bool, str]:
        """
        Termina uma conexão IPsec.
        
        Args:
            conn_name: Nome da conexão IPsec
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        import subprocess
        
        try:
            # Executa o comando ipsec para terminar a conexão
            result = subprocess.run(['sudo', 'ipsec', 'down', conn_name], capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, f'IPsec connection "{conn_name}" terminated successfully.'
            else:
                return False, f'Failed to terminate connection "{conn_name}": {result.stderr.strip()}'
        except FileNotFoundError:
            return False, 'Error: IPsec command not found. Please ensure IPsec is installed and in PATH.'
        except Exception as e:
            return False, f'Error terminating connection: {str(e)}'
    
    @staticmethod
    def get_connection_status(conn_name: str) -> Tuple[str, bool]:
        """
        Obtém o status de uma conexão IPsec específica.
        
        Args:
            conn_name: Nome da conexão IPsec
            
        Returns:
            Tuple[str, bool]: (status_text, is_connected)
        """
        import subprocess
        
        try:
            # Executa o comando ipsec para obter o status
            result = subprocess.run(['sudo', 'ipsec', 'status'], capture_output=True, text=True)
            
            if result.returncode == 0:
                status_output = result.stdout
                
                # Verifica se a conexão específica está estabelecida
                if conn_name in status_output and 'ESTABLISHED' in status_output:
                    return 'Connected', True
                elif conn_name in status_output and ('IPSEC SA established' in status_output or 'eroute owner' in status_output):
                    return 'Connected', True
                else:
                    return 'Disconnected', False
            else:
                return 'Disconnected', False
        except FileNotFoundError:
            return 'Disconnected', False
        except Exception:
            return 'Disconnected', False


class VPNIPSecClientApp(QMainWindow):
    """
    Aplicativo GUI para gerenciar conexões IPsec VPN no Linux usando Qt com integração Deepin.
    """
    
    def __init__(self):
        super().__init__()
        self.ipsec_mgr = IPsecManager()
        self.current_conn_name = None
        self.log_file_path = None
        self.is_connected = False
        self.initUI()
        
    def initUI(self):
        """Inicializa a interface do usuário."""
        self.setWindowTitle(APP_TITLE)
        self.setGeometry(100, 100, *WINDOW_SIZE)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Título
        title_label = QLabel('VPN IPsec Client v3')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Informações de Configuração IPsec
        config_group = QGroupBox('Configuração IPsec')
        config_layout = QGridLayout()
        
        # Nome da Conexão
        config_layout.addWidget(QLabel('Nome da Conexão:'), 0, 0)
        self.conn_name_label = QLabel('--')
        config_layout.addWidget(self.conn_name_label, 0, 1)
        
        # Endereço do Servidor
        config_layout.addWidget(QLabel('Endereço do Servidor:'), 1, 0)
        self.server_address_label = QLabel('--')
        config_layout.addWidget(self.server_address_label, 1, 1)
        
        # Status
        config_layout.addWidget(QLabel('Status:'), 2, 0)
        self.status_label = QLabel(CONNECTION_STATES['NOT_CONFIGURED'])
        config_layout.addWidget(self.status_label, 2, 1)
        
        # Toggle Switch
        self.toggle_switch = QPushButton('OFF')
        self.toggle_switch.setCheckable(True)
        self.toggle_switch.clicked.connect(self.toggle_connection)
        self.toggle_switch.setStyleSheet(TOGGLE_STYLE_OFF)
        config_layout.addWidget(self.toggle_switch, 2, 2)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Log de status
        status_group = QGroupBox('Status da Conexão')
        status_layout = QVBoxLayout()
        
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        status_layout.addWidget(self.status_display)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Layout dos botões
        buttons_layout = QHBoxLayout()
        
        self.status_btn = QPushButton('Atualizar Status')
        self.status_btn.clicked.connect(self.refresh_status)
        
        buttons_layout.addWidget(self.status_btn)
        buttons_layout.addStretch()  # Adiciona stretch para alinhar botões
        
        layout.addLayout(buttons_layout)
        
        # Barra de status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(DEFAULT_MESSAGES['READY'])
        
        # Adiciona mensagens iniciais
        self.add_status_message(DEFAULT_MESSAGES['INIT'])
        self.add_status_message(DEFAULT_MESSAGES['CHECKING_CONFIG'])
        
        # Carrega a configuração IPsec existente
        self.load_ipsec_config()
        
        # Aplica o tema do sistema
        self.apply_system_theme()
    
    def load_ipsec_config(self):
        """Carrega a configuração IPsec do sistema."""
        try:
            connections = self.ipsec_mgr.get_ipsec_connections()
            
            if connections:
                # Usa a primeira conexão encontrada
                first_conn = connections[0]
                self.current_conn_name = first_conn
                self.conn_name_label.setText(first_conn)
                
                # Obtém detalhes da conexão
                _, server_addr = self.ipsec_mgr.get_connection_details(first_conn)
                self.server_address_label.setText(server_addr)
                
                # Verifica o status da conexão
                self.refresh_connection_status()
                
                self.add_status_message(f'Loaded IPsec configuration: {first_conn}')
            else:
                self.conn_name_label.setText('No configurations found')
                self.server_address_label.setText('N/A')
                self.status_label.setText(CONNECTION_STATES['NO_CONFIG'])
                self.add_status_message(DEFAULT_MESSAGES['NO_CONFIGS'])
                
        except Exception as e:
            self.add_status_message(f'Error loading IPsec configuration: {str(e)}')
            self.conn_name_label.setText(CONNECTION_STATES['ERROR'])
            self.server_address_label.setText('N/A')
            self.status_label.setText(CONNECTION_STATES['ERROR'])
    
    def refresh_connection_status(self):
        """Atualiza o status da conexão atual."""
        if not self.current_conn_name or self.current_conn_name in ['No configurations found', 'Not installed', CONNECTION_STATES['ERROR']]:
            return
        
        status, is_connected = self.ipsec_mgr.get_connection_status(self.current_conn_name)
        self.status_label.setText(status)
        
        # Verifica se houve mudança de estado para gerenciar o log
        if is_connected and not self.is_connected:
            # Acabou de conectar - criar arquivo de log
            self.is_connected = True
            self.create_log_file()
            self.add_status_message(f'Connected to {self.current_conn_name}. Log file created.', show_in_ui=True)
        elif not is_connected and self.is_connected:
            # Acabou de desconectar - fechar arquivo de log
            self.is_connected = False
            self.delete_log_file()
            self.add_status_message(f'Disconnected from {self.current_conn_name}.', show_in_ui=True)
        
        # Atualiza o toggle switch conforme o estado real
        self.toggle_switch.setChecked(is_connected)
        self.toggle_switch.setText('ON' if is_connected else 'OFF')
        self.toggle_switch.setStyleSheet(
            TOGGLE_STYLE_ON if is_connected else TOGGLE_STYLE_OFF
        )
    
    def toggle_connection(self):
        """Alterna a conexão IPsec entre ON/OFF."""
        if not self.current_conn_name or self.current_conn_name in ['No configurations found', 'Not installed', CONNECTION_STATES['ERROR']]:
            QMessageBox.critical(self, 'Error', 'No IPsec configuration available to connect.')
            return
        
        if self.toggle_switch.isChecked():
            # Liga
            self.toggle_switch.setText('ON')
            self.toggle_switch.setStyleSheet(TOGGLE_STYLE_ON)
            self.status_label.setText(CONNECTION_STATES['CONNECTING'])
            self.connect_vpn()
        else:
            # Desliga
            self.toggle_switch.setText('OFF')
            self.toggle_switch.setStyleSheet(TOGGLE_STYLE_OFF)
            self.status_label.setText(CONNECTION_STATES['DISCONNECTING'])
            self.disconnect_vpn()
    
    def connect_vpn(self):
        """Conecta ao servidor VPN usando IPsec."""
        if not self.current_conn_name:
            return
            
        self.add_status_message(f'Initiating IPsec connection: {self.current_conn_name}...')
        
        success, message = self.ipsec_mgr.connect_connection(self.current_conn_name)
        
        if success:
            # Verifica o status após um momento para atualizar a UI
            QTimer.singleShot(2000, self.refresh_connection_status)
        else:
            self.add_status_message(message, show_in_ui=True)
            # Reseta o toggle switch para o estado OFF
            self.toggle_switch.setChecked(False)
            self.toggle_switch.setText('OFF')
            self.toggle_switch.setStyleSheet(TOGGLE_STYLE_OFF)
    
    def disconnect_vpn(self):
        """Desconecta do servidor VPN usando IPsec."""
        if not self.current_conn_name:
            return
            
        self.add_status_message(f'Disconnecting IPsec connection: {self.current_conn_name}...', show_in_ui=True)
        
        success, message = self.ipsec_mgr.disconnect_connection(self.current_conn_name)
        
        if success:
            # Atualiza a UI imediatamente
            self.status_label.setText(CONNECTION_STATES['DISCONNECTED'])
            self.status_bar.showMessage(CONNECTION_STATES['DISCONNECTED'])
            
            # Atualiza o toggle switch para o estado OFF
            self.toggle_switch.setChecked(False)
            self.toggle_switch.setText('OFF')
            self.toggle_switch.setStyleSheet(TOGGLE_STYLE_OFF)
        else:
            self.add_status_message(message, show_in_ui=True)
    
    def refresh_status(self):
        """Atualiza o status atual da conexão VPN."""
        self.refresh_connection_status()
        current_status = self.status_label.text()
        self.add_status_message(f'Current status: {current_status}')
        QMessageBox.information(self, 'VPN Status', f'Current status: {current_status}')
        
    def apply_system_theme(self):
        """Detecta e aplica o tema do sistema (claro/escuro) para o aplicativo."""
        # Obtém a paleta padrão do sistema
        system_palette = self.style().standardPalette()
        
        # Determina se o tema do sistema é escuro ou claro com base na cor da janela
        window_color = system_palette.color(QPalette.ColorRole.Window)
        # Calcula a luminância para determinar se é um tema escuro
        luminance = (0.299 * window_color.red() + 0.587 * window_color.green() + 0.114 * window_color.blue()) / 255
        
        if luminance < 0.5:
            # Tema escuro detectado
            self.set_dark_theme()
    
    def set_dark_theme(self):
        """Aplica um tema escuro ao aplicativo."""
        dark_palette = QPalette()
        
        # Define cores escuras
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
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(65, 105, 225))  # Azul royal
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.ColorRole.Disabled, QPalette.ColorRole.Text, QColor(120, 120, 120))
        dark_palette.setColor(QPalette.ColorRole.Disabled, QPalette.ColorRole.ButtonText, QColor(120, 120, 120))
        dark_palette.setColor(QPalette.ColorRole.Disabled, QPalette.ColorRole.WindowText, QColor(120, 120, 120))
        
        self.setPalette(dark_palette)
        
        # Aplica o tema escuro ao aplicativo
        app = QApplication.instance()
        if app:
            app.setPalette(dark_palette)
    
    def add_status_message(self, message: str, show_in_ui: bool = True):
        """
        Adiciona uma mensagem ao display de status e ao arquivo de log se estiver conectado.
        
        Args:
            message: Mensagem a ser adicionada
            show_in_ui: Se True, mostra a mensagem na interface (padrão: True)
        """
        # Adiciona timestamp à mensagem
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        # Salva no arquivo de log se estiver conectado
        if self.is_connected and self.log_file_path:
            try:
                with open(self.log_file_path, 'a', encoding='utf-8') as log_file:
                    log_file.write(formatted_message + '\n')
            except Exception:
                # Se não conseguir escrever no arquivo, apenas ignora
                pass
        
        # Exibe na interface se solicitado e não for uma mensagem de status rotineira
        if show_in_ui and not self._is_routine_status_message(message):
            self.status_display.append(formatted_message)
    
    def _is_routine_status_message(self, message: str) -> bool:
        """
        Verifica se a mensagem é de status rotineira que não deve ser exibida na UI.
        
        Args:
            message: Mensagem a ser verificada
            
        Returns:
            bool: True se for uma mensagem de status rotineira, False caso contrário
        """
        routine_messages = [
            'Loaded IPsec configuration',
            'Current status:',
            'Command output:'
        ]
        
        return any(routine_msg in message for routine_msg in routine_messages)
    
    def create_log_file(self):
        """Cria um novo arquivo de log com base na conexão atual."""
        if not self.current_conn_name:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.current_conn_name}_{timestamp}.log"
        self.log_file_path = os.path.join(LOGS_DIR, filename)
        
        # Escreve cabeçalho no arquivo de log
        try:
            with open(self.log_file_path, 'w', encoding='utf-8') as log_file:
                log_file.write(f"VPN IPsec Log - Connection: {self.current_conn_name}\n")
                log_file.write(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                log_file.write("-" * 50 + "\n")
        except Exception:
            # Se não conseguir criar o arquivo, define como None
            self.log_file_path = None
            self.add_status_message("Warning: Could not create log file.", show_in_ui=True)
    
    def delete_log_file(self):
        """Exclui o arquivo de log quando a conexão é encerrada."""
        if self.log_file_path and os.path.exists(self.log_file_path):
            try:
                with open(self.log_file_path, 'a', encoding='utf-8') as log_file:
                    log_file.write("-" * 50 + "\n")
                    log_file.write(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                # Opcional: excluir o arquivo quando desconectado
                # os.remove(self.log_file_path)
            except Exception:
                pass
        self.log_file_path = None


def main() -> None:
    """
    Ponto de entrada principal para o aplicativo Qt com integração Deepin.
    
    Esta função inicializa o QApplication, configura o estilo do sistema
    e exibe a janela principal do aplicativo.
    """
    app = QApplication(sys.argv)
    
    # Define o estilo do aplicativo para combinar com o tema do sistema (importante para Deepin)
    app.setStyle('Fusion')
    
    ex = VPNIPSecClientApp()
    ex.show()
    
    # Manipula a saída do aplicativo
    sys.exit(app.exec())


if __name__ == '__main__':
    main()