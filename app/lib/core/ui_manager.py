from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from ..ui.widgets import ToggleSwitch

class UIManager:
    """Classe para gerenciar a interface do usuário."""
    
    def __init__(self, parent, icon_path):
        self.parent = parent
        self.icon_path = icon_path
        self.toggle_switch = None
        self.status_label = None
        
    def init_ui(self):
        """Inicializa a interface do usuário."""
        self.parent.setWindowTitle("VPN Client FortiGate - IPsec")
        self.parent.setWindowIcon(QIcon(self.icon_path))
        self.parent.setGeometry(600, 300, 500, 220)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)
        
        self.toggle_switch = ToggleSwitch()
        self.toggle_switch.toggled.connect(self.parent.handle_toggle)
        
        self.status_label = QLabel("Verificando status...")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        main_layout.addWidget(self.toggle_switch, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        footer_label = QLabel("VPN Client FortiGate - IPsec v0.1.0 | © 2025 DYSATECH | Open Source")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: #777; font-size: 9px; font-weight: normal;")
        main_layout.addWidget(footer_label)
        
        self.parent.setLayout(main_layout)
        
        return main_layout

    def update_status(self, connected):
        """Atualiza a interface com base no status da conexão."""
        if self.toggle_switch:
            self.toggle_switch.blockSignals(True)
            self.toggle_switch.setChecked(connected)
            self.toggle_switch.setEnabled(True)
            self.toggle_switch.blockSignals(False)
        
        if self.status_label:
            self.status_label.setText("VPN Conectada" if connected else "VPN Desconectada")
            style = "color: {}; font-size: 14px; font-weight: bold;".format(
                '#4CAF50' if connected else '#F44336'
            )
            self.status_label.setStyleSheet(style)

    def set_toggle_state(self, enabled):
        """Define o estado do toggle switch."""
        if self.toggle_switch:
            self.toggle_switch.setEnabled(enabled)