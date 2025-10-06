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
            
        # Primeiro, verificar autenticação antes de abrir a GUI
        app = QApplication(sys.argv)
        
        # Testar a autenticação antes de exibir a GUI
        test_gui = VpnGui()
        
        # Verificar se o helper foi iniciado e está respondendo corretamente
        if not test_gui.helper_process or not test_gui._is_helper_authenticated():
            # A autenticação falhou ou o helper não responde
            test_gui.close()
            # A mensagem de erro já foi exibida por start_helper_process
            return  # Sair sem abrir a GUI principal
        
        # Se a autenticação for bem-sucedida, continuar com a GUI normal
        gui = test_gui  # Reutilizar a instância que já passou pela autenticação
        
        # Conecta o sinal aboutToQuit ao método de limpeza da GUI
        app.aboutToQuit.connect(gui.cleanup)
        
        gui.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()
