# Changelog

Todas as alterações notáveis no projeto VPN Client FortiGate - IPsec serão documentadas neste arquivo.

## [v0.1.0] - 2025-10-06

### Adicionado
- Interface gráfica para gerenciamento de conexão VPN FortiGate
- Função de conexão e desconexão com toggle switch
- Verificação automática de status da VPN
- Implementação de desconexão automática ao fechar a aplicação
- Aumento do tamanho da janela da interface
- Arquivo de versão e documentação da empresa desenvolvedora
- Notificações de sistema para indicar status da VPN
- Nome do aplicativo atualizado para refletir a tecnologia IPsec
- Informações de rodapé atualizadas incluindo a tecnologia IPsec

## [v0.1.1] - 2025-10-06

### Modificado
- Refatoração da classe VpnGui para seguir o princípio de responsabilidade única (SRP)
- Criação de módulos auxiliares para melhorar a organização (HelperCommunication, UIManager, AnimationManager)
- Melhoria na estrutura de importação para funcionar corretamente em diferentes ambientes
- Correção de problemas de autenticação no ambiente instalado
- Adição de arquivo de política do PolicyKit para permitir execução com privilégios
- Atualização do script de build para incluir o arquivo de política no pacote
- Melhoria na organização do código com separação de responsabilidades
- Correção de erros de permissão ao encerrar o processo helper
- Atualização da documentação para refletir a nova arquitetura modular