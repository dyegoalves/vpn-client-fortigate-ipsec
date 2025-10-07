from PyQt5.QtCore import QTimer

class AnimationManager:
    """Classe para gerenciar animações e notificações."""
    
    def __init__(self, parent, status_label):
        self.parent = parent
        self.status_label = status_label
        self.rotation_timer = None

    def start_animation(self):
        """Inicia uma animação simples para indicar atividade."""
        if self.status_label:
            self.status_label.setText("Processando...")
        if self.rotation_timer is None:
            self.rotation_timer = QTimer()
            self.rotation_timer.timeout.connect(self.rotate_icon)
        self.rotation_timer.start(50)

    def rotate_icon(self):
        # Em vez de rotacionar, vamos animar o texto
        if self.status_label:
            dots = self.status_label.text().count('.')
            new_dots = (dots + 1) % 4
            self.status_label.setText(f"Processando{'.' * new_dots}")
        
    def stop_animation(self):
        """Para a animação de atividade."""
        if self.rotation_timer:
            self.rotation_timer.stop()
            if self.status_label:
                self.status_label.setText("Verificando status...")

    def send_notification(self, message):
        """Envia uma notificação de desktop."""
        import subprocess
        from ..config.config import ICON_PATH
        subprocess.run(["notify-send", "Gerenciador de VPN", message, "--icon", ICON_PATH])