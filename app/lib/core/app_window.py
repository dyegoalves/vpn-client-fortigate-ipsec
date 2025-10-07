import sys
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import Qt

# ==============================================================================
# LÓGICA DA GUI PRINCIPAL
# ==============================================================================
class VpnGui(QWidget):
    def __init__(self):
        super().__init__()
        self.helper_process = None
        self.worker = None
        self.helper_comm = None
        self.ui_manager = None
        self.animation_manager = None
        
        # Importar dentro do construtor para evitar problemas de importação
        try:
            from ..config.config import ICON_PATH
            from .worker import VpnWorker
            from .helper_communication import HelperCommunication
            from .ui_manager import UIManager
            from .animation_manager import AnimationManager
        except ImportError:
            # Quando rodando em modo desenvolvimento com PYTHONPATH apropriado
            from config.config import ICON_PATH
            from core.worker import VpnWorker
            from core.helper_communication import HelperCommunication
            from core.ui_manager import UIManager
            from core.animation_manager import AnimationManager
        
        # Inicializar os gerenciadores
        self.ui_manager = UIManager(self, ICON_PATH)
        self.animation_manager = AnimationManager(self, None)  # Será definido após a UI ser inicializada
        
        self.ui_manager.init_ui()
        # Agora que a UI está inicializada, podemos definir o status_label para o animation_manager
        self.animation_manager.status_label = self.ui_manager.status_label
        
        if not self.start_helper_process():
            # Se o helper não iniciar devido a problemas de autenticação,
            # fecha imediatamente a aplicação
            self.close()
        else:
            self.check_status()

    def _is_helper_authenticated(self):
        """Verifica se o helper ainda está autenticado e respondendo."""
        if not self.helper_comm:
            return False
        return self.helper_comm.is_helper_authenticated()

    def start_helper_process(self):
        """Inicia o processo helper com privilégios de root via pkexec."""
        # Importar dentro da função para evitar problemas de importação circular
        # Usar import absoluto ou relativo dependendo do contexto
        try:
            # Tenta import relativo primeiro
            from .auth import authenticate_and_start_helper
        except ImportError:
            # Quando rodando em modo desenvolvimento com PYTHONPATH apropriado
            from core.auth import authenticate_and_start_helper
            
        self.helper_process = authenticate_and_start_helper()
        
        if self.helper_process:
            # Criar o objeto de comunicação com o helper
            try:
                from .helper_communication import HelperCommunication
            except ImportError:
                from core.helper_communication import HelperCommunication
                
            self.helper_comm = HelperCommunication(self.helper_process)
            return True
        
        return False

    def run_command(self, command, on_finish):
        """Inicia o worker para executar um comando em segundo plano."""
        # Verifica se o helper ainda está autenticado antes de executar o comando
        if not self.helper_comm.is_helper_authenticated():
            # Tenta reiniciar o helper com autenticação
            if not self.start_helper_process():
                # Se não conseguir reiniciar, exibe erro e desativa o toggle
                QMessageBox.critical(self, "Erro de Autenticação",
                                     "Autenticação expirada ou revogada.\n"
                                     "Reabra o aplicativo e forneça credenciais válidas de administrador.\n\n"
                                     "O aplicativo precisa de privilégios elevados para gerenciar\n"
                                     "conexões de rede e o serviço IPsec.")
                self.ui_manager.set_toggle_state(False)
                return
        
        try:
            from .worker import VpnWorker
        except ImportError:
            from core.worker import VpnWorker
            
        self.worker = VpnWorker(self.helper_process, command)
        self.worker.result_ready.connect(on_finish)
        self.worker.start()
        
    def on_action_finished(self, response):
        """Callback para quando uma ação (start/stop) termina."""
        connected = "STATUS: connected" in response
        self.ui_manager.update_status(connected)
        self.animation_manager.send_notification(f"A VPN está {'conectada' if connected else 'desconectada'}.")
        self.animation_manager.stop_animation()

    def on_status_check_finished(self, response):
        """Callback para quando a verificação de status termina."""
        connected = "STATUS: connected" in response
        self.ui_manager.update_status(connected)
        
    def on_disconnect_for_stop(self, response):
        """Callback específico para a ação de desconectar."""
        self.ui_manager.update_status(False)
        self.animation_manager.send_notification("A VPN foi desconectada.")
        self.animation_manager.stop_animation()

    def handle_toggle(self, checked):
        """Lida com a mudança de estado do toggle switch."""
        self.ui_manager.set_toggle_state(False)
        self.animation_manager.start_animation()
        
        if checked:
            self.animation_manager.send_notification("Conectando a VPN...")
            self.run_command("start", self.on_action_finished)
        else:
            self.animation_manager.send_notification("Desconectando a VPN...")
            self.run_command("stop", self.on_disconnect_for_stop)

    def check_status(self):
        """Verifica o status atual da VPN."""
        self.run_command("status", self.on_status_check_finished)

    def cleanup(self):
        """Executa a limpeza ao fechar a aplicação."""
        if self.helper_comm:
            self.helper_comm.disconnect_if_connected()
            self.helper_comm.close_connection()
