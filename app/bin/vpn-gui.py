#!/usr/bin/env python3
"""
Ponto de entrada principal para a GUI do cliente VPN.
Este script serve como interface para executar o módulo app.lib.core.main.
"""

import sys
import os

# Adiciona o diretório lib ao path para permitir importações
# Determina o ambiente e configura o path adequadamente
current_dir = os.path.dirname(os.path.abspath(__file__))
dev_lib_path = os.path.join(current_dir, '../lib')

if os.path.exists(dev_lib_path):
    # Ambiente de desenvolvimento
    sys.path.insert(0, dev_lib_path)
    from core.main import main
else:
    # Ambiente instalado - o código está em /usr/lib/vpn-client-fortigate/
    installed_path = '/usr/lib/vpn-client-fortigate'
    if installed_path not in sys.path:
        sys.path.insert(0, installed_path)
    from core.main import main

# Importa e executa o módulo principal
if __name__ == "__main__":
    main()