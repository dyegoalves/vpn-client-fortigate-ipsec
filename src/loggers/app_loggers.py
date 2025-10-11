"""
Módulo Loggers

Este módulo contém a classe Loggers que gerencia a criação e manutenção
de arquivos de log da aplicação VPN IPsec.
"""

import os
from datetime import datetime

from ..config.app_config import LOGS_DIR


class AppLoggers:
    """
    Classe responsável por gerenciar os logs da aplicação.
    """

    def __init__(self):
        self.log_file_path = None
        self.is_connected = False

        # Garante que o diretório de logs exista
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)

    def set_connection_status(self, is_connected: bool):
        """
        Define o status de conexão e atualiza o comportamento de logging.
        """
        self.is_connected = is_connected

    def create_log_file(self, connection_name: str):
        """
        Cria um novo arquivo de log para a conexão atual.
        """
        if not connection_name:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{connection_name}_{timestamp}.log"
        self.log_file_path = os.path.join(LOGS_DIR, filename)

        initial_content = (
            f"VPN IPsec Log - Connection: {connection_name}\n"
            f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            + "-" * 50
            + "\n"
        )

        if not self._write_to_log_file(initial_content):
            self.log_file_path = None

    def delete_log_file(self):
        """
        Fecha e registra o fim do arquivo de log quando a conexão é encerrada.
        """
        if self.log_file_path and os.path.exists(self.log_file_path):
            final_content = (
                "-" * 50
                + "\n"
                + f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

            self._write_to_log_file(final_content)
        self.log_file_path = None

    def _write_to_log_file(self, content: str) -> bool:
        """
        Escreve conteúdo no arquivo de log se estiver conectado.
        """
        if self.is_connected and self.log_file_path:
            try:
                with open(self.log_file_path, "a", encoding="utf-8") as log_file:
                    log_file.write(content)
                return True
            except Exception:
                return False
        return False

    def add_log_message(self, message: str) -> bool:
        """
        Adiciona uma mensagem ao arquivo de log com timestamp.
        """
        if not self.is_connected:
            return False

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"

        return self._write_to_log_file(formatted_message + "\n")

    def get_log_file_path(self) -> str:
        """
        Retorna o caminho do arquivo de log atual.
        """
        return self.log_file_path
