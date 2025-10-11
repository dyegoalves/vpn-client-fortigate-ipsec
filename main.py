"""
VPN IPsec Client Application - Main Entry Point

This module initializes and runs the Qt application.
"""

import sys
import os

# Adiciona o diretório pai (src) ao sys.path para permitir importações relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow


def main() -> None:
    """
    Main entry point for the Qt application.

    Initializes the QApplication, sets the system style, and shows the main window.
    """
    app = QApplication(sys.argv)

    # Set the application style to match the system theme (important for Deepin)
    app.setStyle("Fusion")

    # Create and show the main application window
    ex = MainWindow()
    ex.show()

    # Execute the application's main loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
