from PySide6.QtCore import Qt, QTimer, QRectF, QSize, Signal
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel
import sys


class ToggleSwitchButton(QWidget):
    # Sinal para quando o estado muda
    stateChanged = Signal(bool)

    def __init__(
        self,
        width=72,
        height=36,
        on_color="#4cd964",  # Verde para "Conectado"
        off_color="#d9534f",  # Vermelho para "Desconectado"
        connecting_color="#FFA500",
    ):
        super().__init__()
        self.setFixedSize(width, height)
        self._width = width
        self._height = height
        self._on_color = on_color
        self._off_color = off_color
        self._connecting_color = connecting_color

        self._checked = False
        self._thumb_pos = 2.0
        self._target = 2.0
        self._speed = 0.15

        # Simplificar para 3 estados
        self._current_state = "DISCONNECTED"  # Pode ser "CONNECTED", "DISCONNECTED", "CONNECTING"

        self._timer = QTimer()
        self._timer.setInterval(15)
        self._timer.timeout.connect(self._animate)
        self._timer.start()

    def sizeHint(self):
        return QSize(self._width, self._height)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._current_state not in [
            "CONNECTING",
            "DISCONNECTING",
        ]:
            self._checked = not self._checked
            self._target = self._width - self._height + 2 if self._checked else 2
            self.stateChanged.emit(self._checked)
            self.update()
        else:
            super().mousePressEvent(event)

    def setConnectionState(self, state: str):
        """Define o estado de conexão e atualiza a aparência do toggle"""
        self._current_state = state

        if state == "CONNECTED":
            # Conexão estabelecida - toggle deve estar no estado ON
            self._checked = True
            self._target = self._width - self._height + 2
        elif state == "DISCONNECTED":
            # Conexão encerrada - toggle deve estar no estado OFF
            self._checked = False
            self._target = 2
        elif state == "CONNECTING":
            # Iniciando conexão - o thumb se move para posição de "conectado"
            self._target = self._width - self._height + 2
            self._checked = True

        self.update()

    def _animate(self):
        if abs(self._thumb_pos - self._target) < 0.5:
            self._thumb_pos = self._target
        else:
            self._thumb_pos += (self._target - self._thumb_pos) * self._speed
        self.update()

    def paintEvent(self, event):
        thumb_d = self._height - 4
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Determinar cor de fundo com base no estado
        if self._current_state == "CONNECTED" or (
            self._current_state not in ["CONNECTING"] and self._checked
        ):
            color = QColor(self._on_color)  # Verde quando ON ou CONNECTED
        elif self._current_state == "CONNECTING":
            color = QColor(self._connecting_color)  # Laranja durante conexão
        else:
            color = QColor(self._off_color)  # Cinza quando OFF

        # Fundo
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(
            QRectF(0, 0, self._width, self._height), self._height / 2, self._height / 2
        )

        # Bolinha
        painter.setBrush(QColor("#ffffff"))
        painter.setPen(QPen(QColor(180, 180, 180)))
        painter.drawEllipse(QRectF(self._thumb_pos, 2, thumb_d, thumb_d))

        # Adicionar ícones de status se necessário
        if self._current_state in ["CONNECTING", "DISCONNECTING"]:
            # Desenhar indicador de carregamento
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.setBrush(Qt.NoBrush)

            # Desenhar um arco para indicar carregamento
            painter.drawArc(
                self._thumb_pos + 2, 4, thumb_d - 4, thumb_d - 4, 45 * 16, 270 * 16
            )

    def isChecked(self):
        return self._checked
