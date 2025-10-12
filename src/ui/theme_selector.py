"""
Theme Selector Widget

This module provides a theme selection combobox that allows users to manually
switch between dark and light themes.
"""

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QWidget, QLabel
from PySide6.QtCore import Signal
from PySide6.QtCore import Qt


class ThemeSelectorWidget(QWidget):
    """
    A widget containing a combobox for theme selection.
    """
    theme_changed = Signal(str)  # Signal emitted when theme is changed

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignLeft)  # Alinhar à esquerda
        
        # Create label for the theme selector
        theme_label = QLabel("Tema:")
        
        # Create theme selection combobox
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Auto (System)", "auto")
        self.theme_combo.addItem("Dark", "dark")
        self.theme_combo.addItem("Light", "light")
        
        # Os estilos de padding serão aplicados automaticamente via QSS
        # Definir larguras consistentes com os estilos QSS
        self.theme_combo.setMinimumWidth(150)
        self.theme_combo.setMaximumWidth(300)
        # A altura será definida automaticamente pelo QSS
        # mas podemos definir uma altura mínima para consistência
        self.theme_combo.setMinimumHeight(24)
        
        # Connect the selection change to emit the signal
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        
        # Add the label and combobox to the layout
        layout.addWidget(theme_label)
        layout.addWidget(self.theme_combo)
        layout.addStretch()  # Add stretch to keep the combobox to the left
        
        self.setLayout(layout)

    def set_selected_theme(self, theme: str):
        """Set the selected theme in the combobox."""
        index = self.theme_combo.findData(theme)
        if index != -1:
            self.theme_combo.setCurrentIndex(index)

    def get_selected_theme(self) -> str:
        """Get the currently selected theme."""
        return self.theme_combo.currentData()

    def _on_theme_changed(self, text: str):
        """Handle theme change and emit the signal."""
        theme = self.theme_combo.currentData()
        self.theme_changed.emit(theme)