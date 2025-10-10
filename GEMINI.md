# Projeto: VPN IPsec Client para Linux

## REGRAS

* Responda sempre em PT-BR
* Seja um programador python com foco software desktop no linux
* Faca um sempre plano TODO para se direcionar

## Descrição

Este projeto implementa um cliente VPN IPsec com interface gráfica para sistemas Linux, com foco especial em integração com o ambiente desktop Deepin. O aplicativo permite gerenciar conexões IPsec VPN com um toggle switch intuitivo que mostra o status da conexão.

## Arquitetura

- **Tecnologia Principal**: PySide6 para a interface gráfica
- **Linguagem**: Python 3.6+
- **Framework**: Qt com integração Deepin
- **Estrutura**: Separação clara entre lógica de negócios (IPsecManager) e interface (VPNIPSecClientApp)

## Funcionalidades

- Interface gráfica com toggle switch para conexão/desconexão
- Leitura automática de configurações IPsec de `/etc/ipsec.conf` e `/etc/ipsec.d/*.conf`
- Exibição de informações detalhadas das conexões
- Sistema de logging que salva arquivos apenas quando conectado
- Integração com tema do sistema (modo claro/escuro)
- Compatibilidade com ambiente Deepin

## Componentes Principais

- `IPsecManager`: Gerencia todas as operações IPsec (leitura de configurações, status, conexão/desconexão)
- `VPNIPSecClientApp`: Interface gráfica principal com PySide6
- Sistema de logging que opera conforme o estado de conexão

## Requisitos

- Python 3.6+
- PySide6
- Sistema Linux com IPsec (StrongSwan ou LibreSwan)
- Permissões administrativas para gerenciamento de rede

## Status

Projeto completo com todas as funcionalidades implementadas e testadas.
