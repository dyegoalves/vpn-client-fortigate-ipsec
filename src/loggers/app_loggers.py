"""
Módulo Loggers

Este módulo contém a classe Loggers que gerencia a criação e manutenção
de arquivos de log da aplicação VPN IPsec.
"""

import os
from datetime import datetime

from ..config.app_config import LOG_FILE_PATH


class AppLoggers:
    """
    Classe responsável por gerenciar os logs da aplicação.
    """

    def __init__(self):
        self.is_connected = False
        # Garante que o diretório do arquivo de log exista
        log_dir = os.path.dirname(LOG_FILE_PATH)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, mode=0o755, exist_ok=True)

    def set_connection_status(self, is_connected: bool):
        """
        Define o status de conexão e atualiza o comportamento de logging.
        """
        self.is_connected = is_connected

    def create_log_file(self, connection_name: str):
        """
        Adiciona registro de início de conexão ao arquivo único de log.
        """
        if not connection_name:
            return

        initial_content = (
            f"\n" + "=" * 50 + f"\n"
            f"VPN IPsec Log - Connection: {connection_name}\n"
            f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            + "=" * 50 + f"\n"
        )

        self._write_to_log_file(initial_content)

    def delete_log_file(self):
        """
        Adiciona registro de fim de conexão ao arquivo único de log.
        """
        final_content = (
            "=" * 50 + f"\n"
            f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Connection ended.\n"
            + "=" * 50 + f"\n"
        )

        self._write_to_log_file(final_content)

    def _write_to_log_file(self, content: str) -> bool:
        """
        Escreve conteúdo no arquivo único de log.
        """
        try:
            with open(LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
                log_file.write(content)
            return True
        except Exception as e:
            print(f"Error writing to log file: {e}")
            return False

    def add_log_message(self, message: str) -> bool:
        """
        Adiciona uma mensagem ao arquivo de log com timestamp.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Removendo duplicação de timestamp adicionado pelo sistema de UI
        if message.startswith('[') and ']' in message[:20]:  # Verificar se a mensagem já contém timestamp
            formatted_message = f"{message}"
        else:
            formatted_message = f"[{timestamp}] {message}"

        return self._write_to_log_file(formatted_message + "\n")

    def get_log_file_path(self) -> str:
        """
        Retorna o caminho do arquivo de log único.
        """
        return LOG_FILE_PATH
