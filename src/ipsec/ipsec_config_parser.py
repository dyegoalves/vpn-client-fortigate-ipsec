import os
import re
from typing import List, Optional, Tuple

from ..config.app_config import IPSEC_CONFIG_PATHS, IPSEC_D_PATH


class IPsecConfigParser:
    """
    Responsável por parsear arquivos de configuração IPsec e extrair detalhes de conexão.
    """

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
        # Regex para capturar chave, valor e opcionalmente ignorar comentários na mesma linha
        pattern = r"^\s*([a-zA-Z0-9_-]+)\s*=\s*(.*?)(?:\s*#.*)?$"
        for line in section_content.splitlines():
            # Ignora linhas que são apenas comentários ou vazias
            if not line.strip() or line.strip().startswith("#"):
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

    def find_connection_file(self, conn_name: str) -> Optional[str]:
        """
        Encontra o arquivo de configuração que contém uma conexão específica.
        """
        for config_file in self._get_all_config_files():
            if self._connection_exists_in_file(conn_name, config_file):
                return config_file
        return None

    def get_connection_details_from_file(
        self, config_file: str, conn_name: str
    ) -> dict:
        """
        Extrai detalhes de uma conexão IPsec de um arquivo de configuração.
        """
        details = {}
        try:
            with open(config_file, "r") as f:
                content = f.read()
            # Regex para capturar a seção da conexão, incluindo linhas com 'left', 'right', etc.
            # e parando antes da próxima declaração 'conn' ou do final do arquivo.
            pattern = rf"^\s*conn\s+{re.escape(conn_name)}\s*\n((?:\s*[^\n]*\n)*?)(?=\n\s*conn\s+|\Z)"
            matches = re.search(pattern, content, re.DOTALL | re.MULTILINE)
            if matches:
                conn_section = matches.group(1)
                details = self._parse_key_value_pairs_from_section(conn_section)
                details["config_file"] = config_file
                details["conn_name"] = conn_name
            else:
                details["error"] = (
                    f"Conexão '{conn_name}' não encontrada no arquivo '{config_file}'."
                )
        except FileNotFoundError:
            details["error"] = (
                f"Erro: Arquivo de configuração '{config_file}' não encontrado."
            )
        except Exception as e:
            details["error"] = (
                f"Erro ao ler detalhes da conexão do arquivo '{config_file}': {str(e)}"
            )
        return details

    def get_server_address_from_details(self, connection_details: dict) -> str:
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
