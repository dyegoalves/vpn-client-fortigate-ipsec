import os

# --- Configurações Globais ---
VPN_NAME = "fortigate-vpn"


# Função para obter o caminho do helper dinamicamente
def get_helper_path():
    # Caminho do script vpn-gui.py em desenvolvimento
    # Vamos construir o caminho de forma mais robusta
    current_script_dir = os.path.dirname(os.path.abspath(__file__))  # app/lib/config/
    lib_dir = os.path.dirname(current_script_dir)  # app/lib/
    project_dir = os.path.dirname(lib_dir)  # app/
    bin_dir = os.path.join(project_dir, "bin")  # app/bin/
    dev_script_path = os.path.join(bin_dir, "vpn-gui.py")  # app/bin/vpn-gui.py
    
    # Verificar se o script existe no ambiente de desenvolvimento
    if os.path.exists(dev_script_path):
        return dev_script_path
    else:
        # Modo instalado
        return "/usr/bin/vpn-gui"

# Função para obter o caminho do script Python para autenticação via pkexec
def get_auth_helper_path():
    # Caminho do script vpn-gui.py em desenvolvimento
    current_script_dir = os.path.dirname(os.path.abspath(__file__))  # app/lib/config/
    lib_dir = os.path.dirname(current_script_dir)  # app/lib/
    project_dir = os.path.dirname(lib_dir)  # app/
    bin_dir = os.path.join(project_dir, "bin")  # app/bin/
    dev_script_path = os.path.join(bin_dir, "vpn-gui.py")  # app/bin/vpn-gui.py
    
    # Verificar se o script existe no ambiente de desenvolvimento
    if os.path.exists(dev_script_path):
        return dev_script_path
    else:
        # Modo instalado - usar o script Python diretamente em vez do wrapper shell
        return "/usr/lib/vpn-client-fortigate/vpn-gui.py"


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
