#!/usr/bin/env python3
"""
Ponto de entrada principal para a GUI do cliente VPN.
Este script serve como interface para executar o módulo app.lib.core.main.
"""

import sys
import os

# Adiciona o diretório lib ao path para permitir importações
# Para ambiente de desenvolvimento
dev_path = os.path.join(os.path.dirname(__file__), '../lib')
if os.path.exists(dev_path):
    sys.path.insert(0, dev_path)
else:
    # Se não estiver no ambiente de desenvolvimento, tentar importar como módulo instalado
    sys.path.insert(0, '/usr/lib/vpn-client-fortigate')

# Importa e executa o módulo principal
if __name__ == "__main__":
    # Importa main dentro do bloco if para evitar problemas com imports relativos
    try:
        from core.main import main
    except ImportError:
        # Se estiver instalado no sistema, importar como módulo do sistema
        from vpn_client_fortigate.core.main import main
    main()