
import sys
import subprocess
from PyQt5.QtWidgets import QMessageBox

try:
    from ..config.config import get_helper_path
except ImportError:
    from config.config import get_helper_path

HELPER_PATH = get_helper_path()

def authenticate_and_start_helper():
    """
    Tenta autenticar usando pkexec e iniciar o processo helper.
    Retorna o processo se for bem-sucedido, caso contrário, None.
    """
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
                             "A autenticação é necessária para gerenciar a VPN.\n"
                             "Por favor, insira sua senha de administrador quando solicitado.\n\n"
                             f"Detalhe do erro: {str(e)}")
        return None
