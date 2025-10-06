"""
VPN Client FortiGate - IPsec
Pacote para gerenciamento de conexão VPN FortiGate usando IPsec/IKEv2.

Este pacote contém os módulos principais para a interface gráfica e
a comunicação com o serviço de VPN.
"""
__version__ = "0.1.0"
__author__ = "DYSATECH"

# Importar os submódulos para facilitar o acesso
from . import core
from . import ui
from . import system
from . import config