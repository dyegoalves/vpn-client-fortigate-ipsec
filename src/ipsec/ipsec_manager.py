"""
Módulo ConnectionIPsec

Este módulo contém a classe ConnectionIPsec que gerencia todas as operações
relacionadas às conexões IPsec.
"""

import os
import subprocess
import re
from typing import List, Optional, Tuple

from ..config.app_config import IPSEC_CONFIG_PATHS, IPSEC_D_PATH
from .ipsec_config_parser import IPsecConfigParser
from .ipsec_commander import IPsecCommander


class IPsecManager:
    """
    Gerencia todas as operações relacionadas às conexões IPsec, orquestrando o parsing de configuração e a execução de comandos.
    """

    def __init__(self):
        self.config_parser = IPsecConfigParser()
        self.commander = IPsecCommander()
        self.connections = []
        self.current_connection = None
        self.load_connections()

    def load_connections(self) -> List[str]:
        """
        Carrega as conexões IPsec a partir dos arquivos de configuração.
        """
        result = subprocess.run(["which", "ipsec"], capture_output=True, text=True)
        if result.returncode != 0:
            self.connections = []
            return []

        connections = []
        for config_file in self.config_parser._get_all_config_files():
            connections.extend(
                self.config_parser._parse_connections_from_file(config_file)
            )

        self.connections = connections
        return connections

    def get_connection_details(self, conn_name: str) -> Tuple[str, str, dict]:
        """
        Obtém os detalhes de uma conexão específica.
        """
        config_file_path = self.config_parser.find_connection_file(conn_name)
        if not config_file_path:
            return "", "Server address not found", {}

        connection_details = self.config_parser.get_connection_details_from_file(
            config_file_path, conn_name
        )
        server_addr = self.config_parser.get_server_address_from_details(
            connection_details
        )
        return config_file_path, server_addr, connection_details

    def _get_connection_details(self, config_file: str, conn_name: str) -> dict:
        """
        Extrai detalhes adicionais de uma conexão IPsec do arquivo de configuração.
        """
        details = {}
        try:
            with open(config_file, "r") as f:
                content = f.read()

            pattern = rf"^\s*conn\s+{re.escape(conn_name)}\s*\n(.*?)(?=\n\s*conn\s+|\Z)"
            matches = re.search(pattern, content, re.DOTALL | re.MULTILINE)

            if matches:
                conn_section = matches.group(1)
                details = self._parse_key_value_pairs_from_section(conn_section)

                details["config_file"] = config_file
                details["conn_name"] = conn_name
        except Exception as e:
            details["error"] = f"Error reading connection details: {str(e)}"
        return details

    def _find_connection_file(self, conn_name: str) -> Optional[str]:
        """
        Encontra o arquivo de configuração que contém uma conexão específica.
        """
        for config_file in self._get_all_config_files():
            if self._connection_exists_in_file(conn_name, config_file):
                return config_file
        return None

    def _get_all_config_files(self) -> List[str]:
        """
        Coleta todos os caminhos de arquivos de configuração IPsec relevantes.
        """
        config_files = IPSEC_CONFIG_PATHS.copy()
        if os.path.exists(IPSEC_D_PATH):
            for file in os.listdir(IPSEC_D_PATH):
                if file.endswith(".conf") and not file.endswith("~"):
                    config_files.append(os.path.join(IPSEC_D_PATH, file))
        return config_files

    def _connection_exists_in_file(self, conn_name: str, file_path: str) -> bool:
        """
        Verifica se uma conexão específica existe em um arquivo de configuração.
        """
        if not os.path.exists(file_path):
            return False
        with open(file_path, "r") as f:
            content = f.read()
            pattern = rf"^\s*conn\s+{re.escape(conn_name)}\s*($|[\s#])"
            return bool(re.search(pattern, content, re.MULTILINE))

    def _parse_key_value_pairs_from_section(self, section_content: str) -> dict:
        """
        Extrai todos os pares chave=valor de uma string de conteúdo de seção.
        """
        details = {}
        # Regex para encontrar linhas com chave=valor, ignorando comentários e espaços em branco
        # Captura a chave e o valor até o final da linha ou um comentário
        pattern = r"^\s*([a-zA-Z0-9_-]+)\s*=\s*([^#\n]+)"
        for line in section_content.splitlines():
            # Ignorar linhas de comentário completas
            if re.match(r"^\s*#", line):
                continue

            match = re.search(pattern, line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                details[key] = value
        return details

    def _parse_connections_from_file(self, file_path: str) -> List[str]:
        """
        Extrai os nomes das conexões de um arquivo de configuração IPsec.
        """
        connections = []
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                content = f.read()
                found_conns = re.findall(r"^\s*conn\s+([^\s#]+)", content, re.MULTILINE)
                connections.extend(
                    [
                        conn.strip()
                        for conn in found_conns
                        if not conn.strip().startswith("#")
                    ]
                )
        return connections

    def _get_server_address(self, connection_details: dict) -> str:
        """
        Extrai o endereço do servidor de um dicionário de detalhes da conexão.
        """
        if "right" in connection_details:
            return connection_details["right"]
        if "alsoip" in connection_details:
            return connection_details["alsoip"]
        if "rightsubnet" in connection_details:
            subnet = connection_details["rightsubnet"]
            if "/" in subnet:
                return subnet.split("/")[0]
            return subnet
        return "Server address not found"

    def connect_connection(self, conn_name: str) -> Tuple[bool, str]:
        """
        Inicia uma conexão IPsec.
        """
        try:
            result = subprocess.run(
                ["sudo", "ipsec", "up", conn_name], capture_output=True, text=True
            )
            if result.returncode == 0:
                self.current_connection = conn_name
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
                if self.current_connection == conn_name:
                    self.current_connection = None
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
        except Exception:
            return "Disconnected", False
