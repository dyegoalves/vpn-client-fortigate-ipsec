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
        success, message = self.commander.connect_connection(conn_name)
        if success:
            self.current_connection = conn_name
        return success, message

    def disconnect_connection(self, conn_name: str) -> Tuple[bool, str]:
        """
        Termina uma conexão IPsec.
        """
        success, message = self.commander.disconnect_connection(conn_name)
        if success:
            if self.current_connection == conn_name:
                self.current_connection = None
        return success, message

    def get_connection_status(self, conn_name: str) -> Tuple[str, bool]:
        """
        Obtém o status de uma conexão IPsec específica.
        """
        return self.commander.get_connection_status(conn_name)
