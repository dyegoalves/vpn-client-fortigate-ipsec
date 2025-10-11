import subprocess
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
                ["sudo", "ipsec", "up", conn_name], capture_output=True, text=True
            )
            if result.returncode == 0:
                return True, f'IPsec connection "{conn_name}" initiated successfully.'
            else:
                return (
                    False,
                    f'Failed to initiate connection "{conn_name}": {result.stderr.strip()}',
                )
        except FileNotFoundError:
            return (
                False,
                "Error: IPsec command not found. Please ensure IPsec is installed and in PATH.",
            )
        except Exception as e:
            return False, f"Error initiating connection: {str(e)}"

    def disconnect_connection(self, conn_name: str) -> Tuple[bool, str]:
        """
        Termina uma conexão IPsec.
        """
        try:
            result = subprocess.run(
                ["sudo", "ipsec", "down", conn_name], capture_output=True, text=True
            )
            if result.returncode == 0:
                return True, f'IPsec connection "{conn_name}" terminated successfully.'
            else:
                return (
                    False,
                    f'Failed to terminate connection "{conn_name}": {result.stderr.strip()}',
                )
        except FileNotFoundError:
            return (
                False,
                "Error: IPsec command not found. Please ensure IPsec is installed and in PATH.",
            )
        except Exception as e:
            return False, f"Error terminating connection: {str(e)}"

    def get_connection_status(self, conn_name: str) -> Tuple[str, bool]:
        """
        Obtém o status de uma conexão IPsec específica.
        """
        try:
            result = subprocess.run(
                ["sudo", "ipsec", "status"], capture_output=True, text=True
            )
            if result.returncode == 0:
                status_output = result.stdout
                is_connected = False
                status_message = "Disconnected"

                if conn_name in status_output:
                    if (
                        "ESTABLISHED" in status_output
                        or "IPSEC SA established" in status_output
                        or "eroute owner" in status_output
                    ):
                        is_connected = True
                        status_message = "Connected"
                
                return status_message, is_connected
            else:
                return "Disconnected", False
        except FileNotFoundError:
            return "Disconnected", False
        except Exception: # Captura qualquer outra exceção
            return "Disconnected", False
