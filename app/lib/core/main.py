#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication

# ==============================================================================
# PONTO DE ENTRADA PRINCIPAL
# ==============================================================================
def main():
    """Função principal que decide se executa a GUI ou o modo helper."""
    # Se o script for chamado com '--run-as-helper', ele executa a lógica do helper.
    # Isso é usado quando o pkexec chama o script como root.
    if "--run-as-helper" in sys.argv:
        # Importação local para evitar dependências desnecessárias no modo helper
        # Usar import absoluto ou relativo dependendo do contexto
        try:
            from ..system.helper import run_helper_mode
        except ImportError:
            # Quando rodando em modo desenvolvimento com PYTHONPATH apropriado
            from system.helper import run_helper_mode
        run_helper_mode()
    else:
        # Caso contrário, inicia a aplicação GUI.
        # Importações locais para evitar carregar a GUI no modo helper.
        try:
            from .app_window import VpnGui
        except ImportError:
            # Quando rodando em modo desenvolvimento com PYTHONPATH apropriado
            from core.app_window import VpnGui
            
        app = QApplication(sys.argv)
        gui = VpnGui()
        
        # Conecta o sinal aboutToQuit ao método de limpeza da GUI
        app.aboutToQuit.connect(gui.cleanup)
        
        gui.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()
