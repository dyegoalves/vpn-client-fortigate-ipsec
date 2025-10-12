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
from src.utils.system_theme import get_system_color_scheme # Importar a nova função


def load_stylesheet(theme: str) -> str:
    """Carrega o stylesheet para o tema especificado."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    style_path = os.path.join(script_dir, "src", "assets", "styles", f"{theme}_theme.qss")
    if os.path.exists(style_path):
        with open(style_path, "r") as f:
            return f.read()
    return ""


def main() -> None:
    """
    Main entry point for the Qt application.

    Initializes the QApplication, sets the system style, and shows the main window.
    """
    app = QApplication(sys.argv)

    # Set the application style to match the system theme (important for Deepin)
    app.setStyle("Fusion")

    # Detectar o tema do sistema e aplicar o stylesheet
    current_theme = get_system_color_scheme()
    if current_theme == "Dark":
        stylesheet = load_stylesheet("dark")
    else:
        stylesheet = load_stylesheet("light")
    app.setStyleSheet(stylesheet)

    # Create and show the main application window
    ex = MainWindow()
    ex.show()

    # Execute the application's main loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
