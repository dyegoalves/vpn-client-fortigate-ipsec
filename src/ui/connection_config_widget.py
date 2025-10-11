from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QGridLayout,
    QGroupBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..config.app_config import (
    TOGGLE_STYLE_ON,
    TOGGLE_STYLE_OFF,
    TOGGLE_STYLE_CONNECTING,
    CONNECTION_STATES,
)


class ConnectionConfigWidget(QGroupBox):
    connection_changed = Signal(str)
    toggle_requested = Signal()

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

        config_layout.addWidget(QLabel("Status:"), 7, 0)
        self.status_label = QLabel(CONNECTION_STATES["NOT_CONFIGURED"])
        config_layout.addWidget(self.status_label, 7, 1)

        self.toggle_switch = QPushButton("OFF")
        self.toggle_switch.setCheckable(True)
        self.toggle_switch.clicked.connect(self.toggle_requested.emit)
        self.toggle_switch.setStyleSheet(TOGGLE_STYLE_OFF)
        config_layout.addWidget(self.toggle_switch, 7, 2)

        self.setLayout(config_layout)

    def _on_connection_changed(self, conn_name):
        self.connection_changed.emit(conn_name)

    def update_connection_details(
        self, conn_name, config_file_path, server_addr, conn_details
    ):
        self.conn_name_label.setText(conn_name)
        self.server_address_label.setText(server_addr)
        self.config_file_label.setText(config_file_path)
        # Procurar por diferentes possíveis campos de autenticação
        auth_type = conn_details.get("authby") or conn_details.get("leftauth") or conn_details.get("rightauth") or "--"
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
        self.toggle_switch.setChecked(is_connected)
        self.toggle_switch.setText("ON" if is_connected else "OFF")
        if (
            status == CONNECTION_STATES["CONNECTING"]
            or status == CONNECTION_STATES["DISCONNECTING"]
        ):
            self.toggle_switch.setStyleSheet(TOGGLE_STYLE_CONNECTING)
        else:
            self.toggle_switch.setStyleSheet(
                TOGGLE_STYLE_ON if is_connected else TOGGLE_STYLE_OFF
            )

    def set_error_state(self, message):
        self.conn_selector.clear()
        self.conn_name_label.setText(CONNECTION_STATES["ERROR"])
        self.server_address_label.setText("N/A")
        self.config_file_label.setText("N/A")
        self.auth_type_label.setText("N/A")
        self.protocols_label.setText("N/A")
        self.rightsubnet_label.setText("N/A")
        self.status_label.setText(CONNECTION_STATES["ERROR"])
        self.toggle_switch.setChecked(False)
        self.toggle_switch.setText("OFF")
        self.toggle_switch.setStyleSheet(TOGGLE_STYLE_OFF)
