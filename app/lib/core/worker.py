from PyQt5.QtCore import QThread, pyqtSignal

# ==============================================================================
# WORKER THREAD PARA COMUNICAÇÃO NÃO-BLOQUEANTE
# ==============================================================================
class VpnWorker(QThread):
    """Executa comandos da VPN em segundo plano para não congelar a GUI."""
    result_ready = pyqtSignal(str)

    def __init__(self, helper_process, command):
        super().__init__()
        self.helper_process = helper_process
        self.command = command

    def run(self):
        """Envia um comando para o processo helper e aguarda a resposta."""
        if not self.helper_process or self.helper_process.poll() is not None:
            self.result_ready.emit("ERROR: Helper not running.")
            return
        try:
            self.helper_process.stdin.write(self.command + '\n')
            self.helper_process.stdin.flush()
            # Lê a resposta do helper
            response = self.helper_process.stdout.readline().strip()
            self.result_ready.emit(response)
        except (IOError, BrokenPipeError):
            self.result_ready.emit("ERROR: Communication with helper failed.")
