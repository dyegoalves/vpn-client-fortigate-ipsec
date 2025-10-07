import subprocess

class HelperCommunication:
    """Classe para gerenciar a comunicação com o processo helper."""
    
    def __init__(self, helper_process):
        self.helper_process = helper_process
        # Importar dentro do construtor para evitar problemas de importação
        try:
            from ..config.paths import get_auth_helper_path
            self.helper_path = get_auth_helper_path()
        except (ImportError, ValueError):
            from config.paths import get_auth_helper_path
            self.helper_path = get_auth_helper_path()

    def send_command(self, command):
        """Envia um comando para o helper e retorna a resposta."""
        if not self.is_helper_running():
            return None
            
        try:
            self.helper_process.stdin.write(f"{command}\n")
            self.helper_process.stdin.flush()
            response = self.helper_process.stdout.readline().strip()
            return response
        except (IOError, BrokenPipeError):
            return None

    def is_helper_running(self):
        """Verifica se o helper ainda está em execução."""
        return self.helper_process and self.helper_process.poll() is None

    def is_helper_authenticated(self):
        """Verifica se o helper está autenticado e respondendo."""
        if not self.is_helper_running():
            return False
            
        try:
            # Envia um comando de teste para verificar se o helper ainda está ativo
            response = self.send_command("status")
            # Se tivermos uma resposta válida, o helper ainda está autenticado
            return response is not None
        except (IOError, BrokenPipeError, AttributeError):
            return False

    def disconnect_if_connected(self):
        """Desconecta a VPN se estiver conectada."""
        if not self.is_helper_authenticated():
            return False
            
        # Verificar o status atual
        response = self.send_command("status")
        
        # Se estiver conectado, desconectar antes de sair
        if response and "STATUS: connected" in response:
            # Enviar comando de desconexão
            self.send_command("stop")
            return True
        return False

    def close_connection(self):
        """Fecha a conexão com o helper."""
        if self.is_helper_running():
            try:
                self.send_command("quit")
                self.helper_process.stdin.close()
                self.helper_process.stdout.close()
            except (IOError, BrokenPipeError):
                pass