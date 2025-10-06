import os
from .paths import is_dev_environment, get_dev_script_path, get_installed_script_path, get_auth_helper_path

# --- Configurações Globais ---
VPN_NAME = "fortigate-vpn"


def get_helper_path():
    """Obtém o caminho do helper para execução normal."""
    if is_dev_environment():
        return get_dev_script_path()
    else:
        # Modo instalado - caminho do wrapper shell
        return "/usr/bin/vpn-gui"

# O caminho do helper será resolvido dinamicamente quando necessário
# Não armazenamos em uma variável global para permitir resolução em tempo de execução

# Definir caminho do ícone dependendo do ambiente
# No ambiente instalado, o ícone está em /usr/share/pixmaps/
installed_icon_path = "/usr/share/pixmaps/vpn-client-icon.png"

if os.path.exists(installed_icon_path):
    # Modo instalado - ícone no sistema
    ICON_PATH = installed_icon_path
else:
    # Modo desenvolvimento - tentar encontrar o ícone no diretório do projeto
    # O ícone está em app/lib/assets/img/
    dev_icon_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "assets",
        "img",
        "vpn.png",
    )

    if os.path.exists(dev_icon_path):
        # Modo desenvolvimento - ícone no diretório local
        ICON_PATH = dev_icon_path
    else:
        # Último recurso - ícone padrão do sistema
        ICON_PATH = "vpn-client-icon"
