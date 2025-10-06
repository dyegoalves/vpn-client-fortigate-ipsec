import os
import sys

def is_dev_environment():
    """Verifica se está no ambiente de desenvolvimento."""
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    lib_dir = os.path.dirname(current_script_dir)
    project_dir = os.path.dirname(lib_dir)
    bin_dir = os.path.join(project_dir, "bin")
    dev_script_path = os.path.join(bin_dir, "vpn-gui.py")
    return os.path.exists(dev_script_path)

def get_dev_script_path():
    """Obtém o caminho do script no ambiente de desenvolvimento."""
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    lib_dir = os.path.dirname(current_script_dir)
    project_dir = os.path.dirname(lib_dir)
    bin_dir = os.path.join(project_dir, "bin")
    return os.path.join(bin_dir, "vpn-gui.py")

def get_installed_script_path():
    """Obtém o caminho do script no ambiente instalado."""
    return "/usr/lib/vpn-client-fortigate/vpn-gui.py"

def get_helper_exec_path():
    """Obtém o caminho do script para execução (usado no wrapper)."""
    return "/usr/bin/vpn-gui"

def get_auth_helper_path():
    """Obtém o caminho do script para autenticação (usado com pkexec)."""
    if is_dev_environment():
        return get_dev_script_path()
    else:
        return get_installed_script_path()

def get_python_path():
    """Obtém o caminho do Python para o ambiente instalado."""
    return "/usr/lib/vpn-client-fortigate"

def is_fully_installed():
    """Verifica se o aplicativo está completamente instalado no sistema."""
    return os.path.exists("/usr/bin/vpn-gui") and os.path.exists("/usr/lib/vpn-client-fortigate/vpn-gui.py")