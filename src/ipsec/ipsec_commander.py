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
                check=False,  # Não levantar exceção automaticamente
            )
            # O comando 'ipsec up' pode retornar 0 mesmo quando o processo de conexão é iniciado
            # ou pode retornar outro código mesmo após iniciar o processo
            if result.returncode == 0 or "connection 'fortigate-vpn' established successfully" in result.stdout or "initiating" in result.stdout:
                return True, f'Conexão IPsec "{conn_name}" iniciada com sucesso. Verifique o status para confirmação.'
            else:
                return False, f'Falha ao iniciar conexão "{conn_name}": {result.stderr.strip() or result.stdout.strip()}'
        except FileNotFoundError:
            return (
                False,
                "Erro: Comando 'ipsec' não encontrado. Verifique se o StrongSwan/LibreSwan está instalado e no PATH.",
            )
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
                check=False,  # Não levantar exceção automaticamente
            )
            # O comando 'ipsec down' pode retornar 0 mesmo quando o processo de desconexão é iniciado
            # ou pode retornar outro código mesmo após iniciar o processo
            if result.returncode == 0 or "deleting IKE_SA" in result.stdout or "connection '" + conn_name + "' closed successfully" in result.stdout:
                return True, f'Conexão IPsec "{conn_name}" terminada com sucesso. Verifique o status para confirmação.'
            else:
                return False, f'Falha ao terminar conexão "{conn_name}": {result.stderr.strip() or result.stdout.strip()}'
        except FileNotFoundError:
            return (
                False,
                "Erro: Comando 'ipsec' não encontrado. Verifique se o StrongSwan/LibreSwan está instalado e no PATH.",
            )
        except Exception as e:
            return False, f"Erro inesperado ao terminar conexão: {str(e)}"

    def get_connection_status(self, conn_name: str) -> Tuple[str, bool]:
        """
        Obtém o status de uma conexão IPsec específica.
        """
        try:
            # Primeiro, verificar se a conexão está ativa ou em processo de conexão
            result = subprocess.run(
                ["sudo", "ipsec", "status"], capture_output=True, text=True, check=False
            )
            
            # Verificar se o comando foi executado com sucesso
            if result.returncode != 0:
                # Se o comando falhou, tentar obter status de configuração
                if self._is_connection_configured(conn_name):
                    return "Desconectado", False
                else:
                    return f"Erro ao obter status: {result.stderr.strip() or result.stdout.strip()}", False
            
            status_output = result.stdout

            # Procurar por diferentes padrões de status para tornar a detecção mais robusta
            # Primeiro, procurar por ESTABLISHED ou conexões ativas
            established_pattern = rf"{re.escape(conn_name)}.*ESTABLISHED"
            if re.search(established_pattern, status_output, re.MULTILINE | re.DOTALL):
                return "Conectado", True
            
            # Em seguida, procurar por CONNECTING ou IKE_AUTH, CHILD_CREATE (em progresso)
            connecting_patterns = [
                rf"{re.escape(conn_name)}.*CONNECTING",
                rf"{re.escape(conn_name)}.*IKE_AUTH",
                rf"{re.escape(conn_name)}.*CHILD_CREATE",
                # Adicionando mais padrões comuns
                rf"{re.escape(conn_name)}.*initiating",
                rf"{re.escape(conn_name)}.*establishing"
            ]
            
            for pattern in connecting_patterns:
                if re.search(pattern, status_output, re.MULTILINE | re.DOTALL):
                    return "Conectando", False

            # Verificar se a conexão simplesmente está listada como configurada (mesmo que não ativa)
            # A saída de "ipsec status" pode não mostrar conexões inativas, então devemos verificar
            # se a conexão está definida em algum arquivo de configuração
            if self._is_connection_configured(conn_name):
                # A conexão está configurada mas não ativa
                return "Desconectado", False
            else:
                # A conexão não está configurada
                return "Não configurado", False
                
        except FileNotFoundError:
            return "Erro: Comando 'ipsec' não encontrado.", False
        except Exception as e:
            # Em caso de erro geral, verificar se a conexão está configurada
            if self._is_connection_configured(conn_name):
                return "Desconectado", False
            else:
                return f"Erro inesperado ao obter status: {str(e)}", False

    def _is_connection_configured(self, conn_name: str) -> bool:
        """
        Verifica se uma conexão está configurada em algum arquivo de configuração do IPsec.
        """
        try:
            # Procurar por definições de conexão em arquivos de configuração
            import os
            
            # Verificar no arquivo principal
            if os.path.exists("/etc/ipsec.conf"):
                with open("/etc/ipsec.conf", "r") as f:
                    content = f.read()
                    if re.search(rf"^\s*conn\s+{re.escape(conn_name)}\b", content, re.MULTILINE | re.IGNORECASE):
                        return True
            
            # Verificar nos arquivos do diretório ipsec.d
            ipsec_d_path = "/etc/ipsec.d/"
            if os.path.exists(ipsec_d_path) and os.path.isdir(ipsec_d_path):
                for file_name in os.listdir(ipsec_d_path):
                    if file_name.endswith(('.conf', '.ipsec', '.cfg')):
                        file_path = os.path.join(ipsec_d_path, file_name)
                        if os.path.isfile(file_path):
                            with open(file_path, "r") as f:
                                content = f.read()
                                if re.search(rf"^\s*conn\s+{re.escape(conn_name)}\b", content, re.MULTILINE | re.IGNORECASE):
                                    return True
            return False
        except Exception:
            # Se houver qualquer erro ao ler os arquivos de configuração, assumir que não está configurada
            return False
