from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QSpacerItem,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..config.app_config import CONNECTION_STATES
from .toggle_switch_button import ToggleSwitchButton  # Importar o novo widget


class ConnectionConfigWidget(QGroupBox):
    connection_changed = Signal(str)
    toggle_requested = Signal(bool)

    def __init__(self, connection_manager, parent=None):
        super().__init__("Configuração IPsec", parent)
        self.connection_mgr = connection_manager
        self.initUI()

    def initUI(self):
        config_layout = QGridLayout()

        config_layout.addWidget(QLabel("Conexão IPsec:"), 0, 0)
        self.conn_selector = QComboBox()
        self.conn_selector.currentTextChanged.connect(self._on_connection_changed)
        config_layout.addWidget(self.conn_selector, 0, 1, 1, 2)

        config_layout.addWidget(QLabel("Nome da Conexão:"), 1, 0)
        self.conn_name_label = QLabel("--")
        config_layout.addWidget(self.conn_name_label, 1, 1, 1, 2)

        config_layout.addWidget(QLabel("Endereço do Servidor:"), 2, 0)
        self.server_address_label = QLabel("--")
        config_layout.addWidget(self.server_address_label, 2, 1, 1, 2)

        config_layout.addWidget(QLabel("Arquivo de Configuração:"), 3, 0)
        self.config_file_label = QLabel("--")
        config_layout.addWidget(self.config_file_label, 3, 1, 1, 2)

        config_layout.addWidget(QLabel("Tipo de Autenticação:"), 4, 0)
        self.auth_type_label = QLabel("--")
        config_layout.addWidget(self.auth_type_label, 4, 1, 1, 2)

        config_layout.addWidget(QLabel("Protocolos (IKE/ESP):"), 5, 0)
        self.protocols_label = QLabel("--")
        config_layout.addWidget(self.protocols_label, 5, 1, 1, 2)

        config_layout.addWidget(QLabel("Sub-rede Remota:"), 6, 0)
        self.rightsubnet_label = QLabel("--")
        config_layout.addWidget(self.rightsubnet_label, 6, 1, 1, 2)

        # Layout para o título do status para alinhamento
        status_title_layout = QVBoxLayout()
        status_title_layout.setContentsMargins(0, 0, 0, 0)
        status_title_layout.addItem(
            QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )
        status_title_layout.addWidget(QLabel("Status:"))
        status_title_layout.setAlignment(Qt.AlignTop)
        config_layout.addLayout(status_title_layout, 7, 0)

        self.status_label = QLabel(CONNECTION_STATES["NOT_CONFIGURED"])

        # Layout para o status label para alinhar com o toggle
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.addItem(
            QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )
        status_layout.addWidget(self.status_label)
        status_layout.setAlignment(Qt.AlignTop)
        config_layout.addLayout(status_layout, 7, 1)

        self.toggle_switch = ToggleSwitchButton(width=55, height=25)  # Tamanho ajustado
        self.toggle_switch.stateChanged.connect(self._on_toggle_state_changed)

        # Criar um layout vertical para o toggle com margem superior
        toggle_layout = QVBoxLayout()
        toggle_layout.setContentsMargins(0, 0, 0, 0)  # Remover margens do layout
        toggle_layout.addItem(
            QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )
        toggle_layout.addWidget(self.toggle_switch)
        toggle_layout.setAlignment(Qt.AlignTop)  # Alinhar ao topo

        config_layout.addLayout(toggle_layout, 7, 2)

        # Adicionar um QSpacerItem para empurrar os elementos para cima
        config_layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), 8, 0, 1, 3
        )

        self.setLayout(config_layout)

    def _on_connection_changed(self, conn_name):
        self.connection_changed.emit(conn_name)

    def _on_toggle_state_changed(self, state):
        """Lida com a mudança de estado do toggle switch, mas só emite o sinal
        se não estiver em um estado de transição."""
        # Somente emitir o sinal se não estiver em estado de transição
        if not hasattr(
            self.toggle_switch, "_current_state"
        ) or self.toggle_switch._current_state not in ["CONNECTING", "DISCONNECTING"]:
            self.toggle_requested.emit(state)

    def update_connection_details(
        self, conn_name, config_file_path, server_addr, conn_details
    ):
        self.conn_name_label.setText(conn_name)
        self.server_address_label.setText(server_addr)
        self.config_file_label.setText(config_file_path)
        # Procurar por diferentes possíveis campos de autenticação
        auth_type = (
            conn_details.get("authby")
            or conn_details.get("leftauth")
            or conn_details.get("rightauth")
            or "--"
        )
        self.auth_type_label.setText(auth_type)
        protocols = f"{conn_details.get('ike', '--')}/{conn_details.get('esp', '--')}"
        self.protocols_label.setText(protocols)
        self.rightsubnet_label.setText(conn_details.get("rightsubnet", "--"))

    def set_connections(self, connections):
        self.conn_selector.clear()
        if connections:
            self.conn_selector.addItems(connections)
        else:
            self.conn_selector.addItem("No configurations found")

    def get_selected_connection(self):
        return self.conn_selector.currentText()

    def update_status(self, status, is_connected):
        self.status_label.setText(status)
        # O ToggleSwitch gerencia seu próprio estado e estilo
        if status == CONNECTION_STATES["CONNECTED"] or status == "Conectado":
            self.toggle_switch.setConnectionState("CONNECTED")
        elif status == CONNECTION_STATES["DISCONNECTED"] or status == "Desconectado":
            self.toggle_switch.setConnectionState("DISCONNECTED")
        elif (
            CONNECTION_STATES["CONNECTING"] in status or status == "Conectando"
        ):  # Adicionando suporte para o status retornado pelo IPsec Commander
            self.toggle_switch.setConnectionState("CONNECTING")
        elif status == "Não configurado":
            self.toggle_switch.setConnectionState(
                "DISCONNECTED"
            )  # Tratar como desconectado se não estiver configurado
        else:
            self.toggle_switch.setConnectionState("DISCONNECTED")  # Estado padrão

    def set_error_state(self, message):
        self.conn_selector.clear()
        self.conn_name_label.setText(CONNECTION_STATES["ERROR"])
        self.server_address_label.setText("N/A")
        self.config_file_label.setText("N/A")
        self.auth_type_label.setText("N/A")
        self.protocols_label.setText("N/A")
        self.rightsubnet_label.setText("N/A")
        self.status_label.setText(CONNECTION_STATES["ERROR"])
        self.toggle_switch.setConnectionState(
            "DISCONNECTED"
        )  # Em caso de erro, o switch deve estar desligado
