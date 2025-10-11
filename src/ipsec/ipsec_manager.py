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
