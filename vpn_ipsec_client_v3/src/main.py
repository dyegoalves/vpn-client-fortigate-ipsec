import sys
import os
# Define a plataforma Qt para xcb para melhor compatibilidade com o ambiente Deepin
os.environ['QT_QPA_PLATFORM'] = 'xcb'

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QTextEdit, QGroupBox, QMessageBox, QStatusBar)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor


class VPNIPSecClientApp(QMainWindow):
    """
    A GUI application for managing IPsec VPN connections on Linux using Qt with Deepin integration.
    """
    
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        """Initialize the user interface."""
        self.setWindowTitle('VPN IPsec Client v3 - Deepin Integration')
        self.setGeometry(100, 100, 700, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel('VPN IPsec Client v3')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Connection settings group
        settings_group = QGroupBox('Connection Settings')
        settings_layout = QVBoxLayout()
        
        # Server address
        server_layout = QHBoxLayout()
        server_label = QLabel('Server Address:')
        self.server_input = QLineEdit()
        self.server_input.setText('vpn.example.com')
        server_layout.addWidget(server_label)
        server_layout.addWidget(self.server_input)
        settings_layout.addLayout(server_layout)
        
        # Username
        username_layout = QHBoxLayout()
        username_label = QLabel('Username:')
        self.username_input = QLineEdit()
        self.username_input.setText('user@example.com')
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        settings_layout.addLayout(username_layout)
        
        # Password
        password_layout = QHBoxLayout()
        password_label = QLabel('Password:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        settings_layout.addLayout(password_layout)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Status log
        status_group = QGroupBox('Connection Status')
        status_layout = QVBoxLayout()
        
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        status_layout.addWidget(self.status_display)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton('Connect')
        self.connect_btn.clicked.connect(self.connect_vpn)
        
        self.disconnect_btn = QPushButton('Disconnect')
        self.disconnect_btn.clicked.connect(self.disconnect_vpn)
        self.disconnect_btn.setEnabled(False)
        
        self.status_btn = QPushButton('Check Status')
        self.status_btn.clicked.connect(self.check_status)
        
        buttons_layout.addWidget(self.connect_btn)
        buttons_layout.addWidget(self.disconnect_btn)
        buttons_layout.addWidget(self.status_btn)
        
        layout.addLayout(buttons_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('Disconnected')
        
        # Add initial messages
        self.add_status_message('VPN IPsec Client v3 initialized.')
        self.add_status_message('Ready to connect to VPN server.')
        
    def apply_system_theme(self):
        """Detect and apply the system theme (dark/light) to the application."""
        # Get the default system palette
        system_palette = self.style().standardPalette()
        
        # Determine if the system theme is dark or light based on window color
        window_color = system_palette.color(QPalette.ColorRole.Window)
        # Calculate luminance to determine if it's a dark theme
        luminance = (0.299 * window_color.red() + 0.587 * window_color.green() + 0.114 * window_color.blue()) / 255
        
        if luminance < 0.5:
            # Dark theme detected
            self.set_dark_theme()
        else:
            # Light theme (default) - no additional changes needed
            pass
    
    def set_dark_theme(self):
        """Apply a dark theme to the application."""
        dark_palette = QPalette()
        
        # Set dark colors
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
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(65, 105, 225))  # Royal blue
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.ColorRole.Disabled, QPalette.ColorRole.Text, QColor(120, 120, 120))
        dark_palette.setColor(QPalette.ColorRole.Disabled, QPalette.ColorRole.ButtonText, QColor(120, 120, 120))
        dark_palette.setColor(QPalette.ColorRole.Disabled, QPalette.ColorRole.WindowText, QColor(120, 120, 120))
        
        self.setPalette(dark_palette)
        
        # Apply the dark theme to the application
        app = QApplication.instance()
        if app:
            app.setPalette(dark_palette)
        
    def add_status_message(self, message):
        """Add a message to the status display."""
        self.status_display.append(message)
        
    def connect_vpn(self):
        """Connect to the VPN server."""
        server = self.server_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not server or not username or not password:
            QMessageBox.critical(self, 'Error', 'Please fill in all connection details.')
            return
            
        self.add_status_message(f'Connecting to {server} as {username}...')
        
        # Simulate connection process
        # In a real implementation, this would call the VPN connection code
        self.status_bar.showMessage('Connecting...')
        self.status_bar.setStyleSheet("QStatusBar{color: orange;}")
        
        # Update button states
        self.connect_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(True)
        
        # Simulate successful connection after delay
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(2000, self.simulate_connection_success)
        
    def simulate_connection_success(self):
        """Simulate successful connection after delay."""
        self.add_status_message('Connected to VPN successfully!')
        self.status_bar.showMessage('Connected')
        self.status_bar.setStyleSheet("QStatusBar{color: green;}")
        
    def disconnect_vpn(self):
        """Disconnect from the VPN server."""
        self.add_status_message('Disconnecting from VPN...')
        
        # In a real implementation, this would call the VPN disconnection code
        self.status_bar.showMessage('Disconnecting...')
        self.status_bar.setStyleSheet("QStatusBar{color: orange;}")
        
        # Update button states
        self.connect_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(False)
        
        # Simulate successful disconnection after delay
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1000, self.simulate_disconnection)
        
    def simulate_disconnection(self):
        """Simulate successful disconnection after delay."""
        self.add_status_message('Disconnected from VPN.')
        self.status_bar.showMessage('Disconnected')
        self.status_bar.setStyleSheet("QStatusBar{color: red;}")
        
        # Update button states
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        
    def check_status(self):
        """Check the current VPN connection status."""
        current_status = self.status_bar.currentMessage()
        self.add_status_message(f'Current status: {current_status}')
        QMessageBox.information(self, 'VPN Status', f'You are currently: {current_status}')


def main():
    """Main entry point for the Qt application with Deepin integration."""
    app = QApplication(sys.argv)
    
    # Set application style to match system theme (important for Deepin)
    app.setStyle('Fusion')
    
    ex = VPNIPSecClientApp()
    # Apply system theme after the widget is created
    ex.apply_system_theme()
    ex.show()
    
    # Handle app exit
    sys.exit(app.exec())


if __name__ == '__main__':
    main()