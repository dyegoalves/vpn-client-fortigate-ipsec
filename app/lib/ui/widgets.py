from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint, pyqtProperty

# ==============================================================================
# WIDGET TOGGLE SWITCH PERSONALIZADO
# ==============================================================================
class ToggleSwitch(QCheckBox):
    """Um widget de toggle switch com animação suave."""
    def __init__(self, parent=None, width=60, height=28, thumb_radius=12):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.setCursor(Qt.PointingHandCursor)
        self._thumb_radius = thumb_radius
        self._margin = (height - 2 * self._thumb_radius) // 2
        self._anim = QPropertyAnimation(self, b"thumb_position", self)
        self._anim.setDuration(150)
        self.stateChanged.connect(self._start_animation)

    @pyqtProperty(QPoint)
    def thumb_position(self):
        # Invertido: ON (checked) é na esquerda, OFF (unchecked) na direita.
        x = self._margin + self._thumb_radius if self.isChecked() else self.width() - self._thumb_radius - self._margin
        return QPoint(x, self.height() // 2)

    @thumb_position.setter
    def thumb_position(self, pos):
        self.update()

    def _start_animation(self, state):
        self._anim.setEndValue(self.thumb_position)
        self._anim.start()

    def mousePressEvent(self, event):
        """Alterna o estado ao clicar em qualquer lugar do widget."""
        self.toggle()
        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        bg_color = QColor("#4CAF50") if self.isChecked() else QColor("#BDBDBD")
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), self.height() / 2, self.height() / 2)
        painter.setBrush(QBrush(Qt.white))
        current_pos = self._anim.currentValue() or self.thumb_position
        painter.drawEllipse(current_pos, self._thumb_radius, self._thumb_radius)
