import sys
import subprocess
from PyQt5.QtWidgets import QMessageBox

def authenticate_and_start_helper():
    """
    Tenta autenticar usando pkexec e iniciar o processo helper.
    Retorna o processo se for bem-sucedido, caso contrário, None.
    """
    # Importar dentro da função para evitar problemas de importação circular
    # Usar import absoluto ou relativo dependendo do contexto
    try:
        # Tenta import relativo primeiro
        from ..config.paths import get_auth_helper_path
    except (ImportError, ValueError):
        # Quando rodando em modo desenvolvimento com PYTHONPATH apropriado
        from config.paths import get_auth_helper_path
    
    HELPER_PATH = get_auth_helper_path()
    
    try:
        command = ["pkexec", sys.executable, HELPER_PATH, "--run-as-helper"]
        helper_process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        # Se o processo terminar imediatamente, a autenticação falhou
        if helper_process.poll() is not None:
            error_output = helper_process.stderr.read()
            raise Exception(f"Falha ao iniciar o helper com pkexec. Erro: {error_output.strip()}")

        # Testa a comunicação com o helper
        helper_process.stdin.write("status\n")
        helper_process.stdin.flush()
        response = helper_process.stdout.readline().strip()

        if not response:
            raise Exception("Falha na comunicação com o processo helper.")

        return helper_process

    except Exception as e:
        QMessageBox.critical(None, "Erro de Autenticação",
                             "Falha na autenticação.\n"
                             "Forneça credenciais válidas de administrador.\n\n"
                             "O aplicativo precisa de privilégios elevados para gerenciar\n"
                             "conexões de rede e o serviço IPsec.\n\n"
                             f"Erro: {str(e)}")
        return None