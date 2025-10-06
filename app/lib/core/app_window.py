import sys
import subprocess
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer

# Importar usando imports absolutos ou relativos dependendo do contexto
try:
    from ..config.config import ICON_PATH, get_helper_path
    from ..ui.widgets import ToggleSwitch
    from .worker import VpnWorker
except ImportError:
    # Quando rodando em modo desenvolvimento com PYTHONPATH apropriado
    from config.config import ICON_PATH, get_helper_path
    from ui.widgets import ToggleSwitch
    from core.worker import VpnWorker

# Obter o caminho do helper
HELPER_PATH = get_helper_path()

# ==============================================================================
# LÓGICA DA GUI PRINCIPAL
# ==============================================================================
class VpnGui(QWidget):
    def __init__(self):
        super().__init__()
        self.helper_process = None
        self.worker = None
        self.rotation_angle = 0
        self.rotation_timer = None
        
        self.init_ui()
        
        if not self.start_helper_process():
            # Se o helper não iniciar, fecha a aplicação após o erro ser mostrado.
            # Usamos QTimer para garantir que a janela seja criada antes de fechá-la.
            QTimer.singleShot(100, self.close)
        else:
            self.check_status()

    def start_helper_process(self):
        """Inicia o processo helper com privilégios de root via pkexec."""
        try:
            command = ["pkexec", sys.executable, HELPER_PATH, "--run-as-helper"]
            self.helper_process = subprocess.Popen(
                command, 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, 
                text=True, 
                bufsize=1
            )
            # Se o processo terminar imediatamente, houve um erro (ex: senha errada)
            if self.helper_process.poll() is not None:
                error_output = self.helper_process.stderr.read()
                raise Exception(f"Falha ao iniciar o helper com pkexec. Erro: {error_output.strip()}")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Erro de Autenticação",
                                 "A autenticação é necessária para gerenciar a VPN.\n"
                                 "Por favor, insira sua senha quando solicitado para continuar.\n\n"
                                 f"Detalhe do erro: {e}")
            return False

    def run_command(self, command, on_finish):
        """Inicia o worker para executar um comando em segundo plano."""
        self.worker = VpnWorker(self.helper_process, command)
        self.worker.result_ready.connect(on_finish)
        self.worker.start()

    def notify(self, message):
        """Envia uma notificação de desktop."""
        subprocess.run(["notify-send", "Gerenciador de VPN", message, "--icon", ICON_PATH])

    def update_ui_from_status(self, connected):
        """Atualiza a interface com base no status da conexão."""
        self.toggle_switch.blockSignals(True)
        self.toggle_switch.setChecked(connected)
        self.toggle_switch.setEnabled(True)
        self.toggle_switch.blockSignals(False)
        
        self.status_label.setText("VPN Conectada" if connected else "VPN Desconectada")
        style = "color: {}; font-size: 14px; font-weight: bold;".format(
            '#4CAF50' if connected else '#F44336'
        )
        self.status_label.setStyleSheet(style)

    def on_action_finished(self, response):
        """Callback para quando uma ação (start/stop) termina."""
        connected = "STATUS: connected" in response
        self.update_ui_from_status(connected)
        self.notify(f"A VPN está {'conectada' if connected else 'desconectada'}.")
        self.stop_rotation_animation()

    def on_status_check_finished(self, response):
        """Callback para quando a verificação de status termina."""
        connected = "STATUS: connected" in response
        self.update_ui_from_status(connected)
        
    def on_disconnect_for_stop(self, response):
        """Callback específico para a ação de desconectar."""
        self.update_ui_from_status(False)
        self.notify("A VPN foi desconectada.")
        self.stop_rotation_animation()

    def handle_toggle(self, checked):
        """Lida com a mudança de estado do toggle switch."""
        self.toggle_switch.setEnabled(False)
        self.start_rotation_animation()
        
        if checked:
            self.notify("Conectando a VPN...")
            self.run_command("start", self.on_action_finished)
        else:
            self.notify("Desconectando a VPN...")
            self.run_command("stop", self.on_disconnect_for_stop)

    def check_status(self):
        """Verifica o status atual da VPN."""
        self.run_command("status", self.on_status_check_finished)

    def start_rotation_animation(self):
        """Inicia uma animação simples para indicar atividade."""
        self.status_label.setText("Processando...")
        if self.rotation_timer is None:
            self.rotation_timer = QTimer()
            self.rotation_timer.timeout.connect(self.rotate_icon)
        self.rotation_timer.start(50)

    def rotate_icon(self):
        # Em vez de rotacionar, vamos animar o texto
        dots = self.status_label.text().count('.')
        new_dots = (dots + 1) % 4
        self.status_label.setText(f"Processando{'.' * new_dots}")
        
    def stop_rotation_animation(self):
        """Para a animação de atividade."""
        if self.rotation_timer:
            self.rotation_timer.stop()

    def cleanup(self):
        """Executa a limpeza ao fechar a aplicação."""
        if self.helper_process and self.helper_process.poll() is None:
            # Antes de fechar, verificar se a VPN está ativa e desconectá-la
            try:
                # Primeiro verificar o status atual
                self.helper_process.stdin.write("status\n")
                self.helper_process.stdin.flush()
                # Ler resposta de status
                response = self.helper_process.stdout.readline().strip()
                
                # Se estiver conectado, desconectar antes de sair
                if "STATUS: connected" in response:
                    # Enviar comando de desconexão
                    self.helper_process.stdin.write("stop\n")
                    self.helper_process.stdin.flush()
                    # Ler resposta de desconexão
                    self.helper_process.stdout.readline()
                    
            except:
                # Se ocorrer erro ao tentar desconectar, prosseguir com o encerramento
                pass
            finally:
                # Enviar comando de saída e encerrar o processo
                try:
                    self.helper_process.stdin.write("quit\n")
                    self.helper_process.stdin.flush()
                    self.helper_process.terminate()
                    self.helper_process.wait(timeout=2)
                except (subprocess.TimeoutExpired, IOError, BrokenPipeError):
                    if self.helper_process.poll() is None:
                        self.helper_process.kill()
                        self.helper_process.wait()
                except Exception:
                    pass # Ignora outros erros no cleanup

    def init_ui(self):
        """Inicializa a interface do usuário."""
        self.setWindowTitle("VPN Client FortiGate - IPsec")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setGeometry(600, 300, 500, 220)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)
        
        self.toggle_switch = ToggleSwitch()
        self.toggle_switch.toggled.connect(self.handle_toggle)
        
        self.status_label = QLabel("Verificando status...")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        main_layout.addWidget(self.toggle_switch, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        footer_label = QLabel("VPN Client FortiGate - IPsec v0.1.0 | © 2025 DYSATECH | Open Source")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: #777; font-size: 9px; font-weight: normal;")
        main_layout.addWidget(footer_label)
        
        self.setLayout(main_layout)
