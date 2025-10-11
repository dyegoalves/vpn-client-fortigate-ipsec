# Cliente VPN IPsec para Linux

Uma aplicação com interface gráfica para gerenciar conexões VPN IPsec em sistemas Linux, construída com Qt (PySide6). Esta aplicação oferece uma interface intuitiva para conectar, desconectar e monitorar conexões VPN IPsec, com excelente integração com ambientes de desktop Linux como o Deepin.

## Descrição

Este projeto implementa um cliente VPN IPsec com interface gráfica para sistemas Linux, com foco especial em integração com o ambiente desktop Deepin. O aplicativo permite gerenciar conexões IPsec VPN com um toggle switch intuitivo que mostra o status da conexão.

## Funcionalidades

- Interface gráfica com toggle switch para conexão/desconexão
- Leitura automática de configurações IPsec de `/etc/ipsec.conf` e `/etc/ipsec.d/*.conf`
- Exibição de informações detalhadas das conexões (endereço do servidor, tipo de autenticação, protocolos IKE/ESP, sub-rede remota)
- Monitoramento do status da conexão com indicadores visuais (toggle switch vermelho/verde)
- Logs de conexão com saída reduzida na UI e salvamento em arquivo apenas quando conectado
- Funcionalidades de conectar, desconectar e verificar status
- Integração com o tema do sistema (suporte a modo claro/escuro)
- Compatibilidade com o ambiente de desktop Deepin
- Exibição de detalhes de conexão detalhados

## Arquitetura

- **Tecnologia Principal**: PySide6 para a interface gráfica
- **Linguagem**: Python 3.6+
- **Framework**: Qt com integração Deepin
- **Estrutura**: Separação clara entre lógica de negócios (`IPsecManager`) e interface (`VPNIPSecClientApp`)

## Componentes Principais

- `IPsecManager`: Gerencia todas as operações IPsec (leitura de configurações, status, conexão/desconexão)
- `VPNIPSecClientApp`: Interface gráfica principal com PySide6
- Sistema de logging que opera conforme o estado de conexão

## Requisitos

- Python 3.6 ou superior
- PySide6
- Sistema operacional Linux com utilitários IPsec (strongswan ou libreswan)
- Privilégios administrativos para gerenciamento de conexão IPsec

## Instalação

1.  Clone ou baixe este repositório.
2.  Navegue até o diretório do projeto.
3.  Instale os pacotes necessários:

    ```bash
    pip install --break-system-packages -r requirements.txt  # ou use um ambiente virtual
    ```

4.  Instale o StrongSwan e seus plugins (dependências do sistema):

    ```bash
    sudo apt update
    sudo apt install strongswan strongswan-pki strongswan-swanctl libstrongswan-extra-plugins
    ```

## Uso

Para executar a aplicação:

```bash
cd src
python main.py
```

### Configuração

1.  A aplicação detecta automaticamente as conexões IPsec disponíveis em `/etc/ipsec.conf` e `/etc/ipsec.d/*.conf`.
2.  Selecione a conexão desejada no menu suspenso.
3.  Visualize os detalhes da conexão (endereço do servidor, tipo de autenticação, protocolos, etc.).
4.  Use o toggle switch ou os botões de conectar/desconectar para controlar a conexão VPN.
5.  Monitore o status da conexão e os logs na interface.
6.  Acesse logs detalhados através do botão "Ver Logs Detalhados".

## Notas de Implementação

Este é um frontend GUI Qt para um cliente VPN IPsec. O Qt foi escolhido por sua excelente integração com ambientes de desktop Linux, particularmente o Deepin, proporcionando:

- Aparência nativa que corresponde ao tema do sistema
- Melhor integração com os recursos do ambiente de desktop
- Consistência visual aprimorada em diferentes distribuições Linux

A aplicação se integra com comandos IPsec de nível de sistema (`ipsec up/down/status`) para gerenciar conexões e inclui:

- Configuração de sistema adequada para compatibilidade com Deepin (plataforma xcb)
- Detecção automática de tema e suporte a modo escuro
- Toggle switch com codificação de cores (vermelho para desconectado, verde para conectado)
- Registro baseado em arquivo que só salva quando conectado
- Saída de log visual reduzida na interface, conforme solicitado

## Status

Projeto completo com todas as funcionalidades implementadas e testadas.

## Licença

Este projeto é de código aberto e está disponível sob a Licença MIT.
