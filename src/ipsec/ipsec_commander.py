import subprocess
import re
from typing import Tuple


class IPsecCommander:
    """
    Responsável por executar comandos IPsec e interpretar suas saídas.
    """

    def connect_connection(self, conn_name: str) -> Tuple[bool, str]:
        """
        Inicia uma conexão IPsec.
        """
        try:
            result = subprocess.run(
                ["sudo", "ipsec", "up", conn_name],
                capture_output=True,
                text=True,
                check=True,
            )
            return True, f'Conexão IPsec "{conn_name}" iniciada com sucesso.'
        except FileNotFoundError:
            return (
                False,
                "Erro: Comando 'ipsec' não encontrado. Verifique se o StrongSwan/LibreSwan está instalado e no PATH.",
            )
        except subprocess.CalledProcessError as e:
            return False, f'Falha ao iniciar conexão "{conn_name}": {e.stderr.strip()}'
        except Exception as e:
            return False, f"Erro inesperado ao iniciar conexão: {str(e)}"

    def disconnect_connection(self, conn_name: str) -> Tuple[bool, str]:
        """
        Termina uma conexão IPsec.
        """
        try:
            result = subprocess.run(
                ["sudo", "ipsec", "down", conn_name],
                capture_output=True,
                text=True,
                check=True,
            )
            return True, f'Conexão IPsec "{conn_name}" terminada com sucesso.'
        except FileNotFoundError:
            return (
                False,
                "Erro: Comando 'ipsec' não encontrado. Verifique se o StrongSwan/LibreSwan está instalado e no PATH.",
            )
        except subprocess.CalledProcessError as e:
            return False, f'Falha ao terminar conexão "{conn_name}": {e.stderr.strip()}'
        except Exception as e:
            return False, f"Erro inesperado ao terminar conexão: {str(e)}"

    def get_connection_status(self, conn_name: str) -> Tuple[str, bool]:
        """
        Obtém o status de uma conexão IPsec específica.
        """
        try:
            result = subprocess.run(
                ["sudo", "ipsec", "status"], capture_output=True, text=True, check=True
            )
            status_output = result.stdout

            if re.search(
                rf"^{re.escape(conn_name)}\[\d+\]: ESTABLISHED",
                status_output,
                re.MULTILINE,
            ):
                return "Conectado", True
            elif re.search(
                rf"^{re.escape(conn_name)}\[\d+\]: CONNECTING",
                status_output,
                re.MULTILINE,
            ):
                return "Conectando", False
            else:
                return "Desconectado", False
        except FileNotFoundError:
            return "Erro: Comando 'ipsec' não encontrado.", False
        except subprocess.CalledProcessError as e:
            return f"Erro ao obter status: {e.stderr.strip()}", False
        except Exception as e:
            return f"Erro inesperado ao obter status: {str(e)}", False
