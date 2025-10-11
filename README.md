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

## Instalação e Configuração Obrigatória

Para garantir o funcionamento correto da aplicação, é essencial seguir os passos de configuração abaixo. A instalação das dependências de sistema (StrongSwan) e dos pacotes Python é obrigatória.

1. Clone ou baixe este repositório.
2. Navegue até o diretório do projeto.
3. Instale os pacotes Python necessários:

   ```bash
   pip install --break-system-packages -r requirements.txt  # ou use um ambiente virtual
   ```
4. Instale o StrongSwan e seus plugins (dependências do sistema):

   ```bash
   sudo apt update
   sudo apt install strongswan strongswan-pki strongswan-swanctl libstrongswan-extra-plugins
   ```

## Uso

Para executar a aplicação:

```bash
git clone https://github.com/dyegoalves/vpn-ipsec-fortigate-client-linux.git
cd vpn-ipsec-fortigate-client-linux
python main.py
```

## Configuração de Conexões IPsec

Para que a aplicação possa gerenciar suas conexões VPN, é necessário configurar os arquivos de configuração do IPsec no seu sistema. A aplicação lê automaticamente as configurações de `/etc/ipsec.conf` e de arquivos `.conf` dentro de `/etc/ipsec.d/`.

### Exemplo de `ipsec.conf`

Você pode usar o arquivo `ipsec.conf.example` localizado na pasta `logs_ai` do projeto como base para suas configurações. Este arquivo demonstra uma configuração básica para uma conexão VPN.

```
config setup
    charondebug="ike 2, knl 2, cfg 2, mgr 2"

conn fortigate-vpn  # Nome da conexão, pode ser alterado
    keyexchange=ikev2
    ike=aes256-sha256-ecp256
    esp=aes256-sha256
    left=%defaultroute
    leftid="<SEU_ID_ESQUERDO>" # Ex: "meu_cliente" ou o ID configurado no Fortigate
    leftauth=eap-mschapv2
    leftdns=<DNS_PRIMARIO>,<DNS_SECUNDARIO> # Ex: 8.8.8.8,8.8.4.4
    eap_identity="<SEU_USUARIO_EAP>" # Seu nome de usuário para autenticação EAP
    leftsourceip=%config
    right=<ENDERECO_DO_SERVIDOR_VPN> # Ex: vpn.suaempresa.com.br ou IP do Fortigate
    rightid=%any
    rightauth=psk
    rightsubnet=<SUBNET_REMOTE_1>,<SUBNET_REMOTE_2> # Ex: 192.168.127.0/24,10.10.10.0/24
    auto=add
```

### Passos para Configurar sua Conexão

1. **Crie ou Edite o Arquivo `ipsec.conf`**:

   * Abra o arquivo `/etc/ipsec.conf` com um editor de texto com privilégios de superusuário:
     ```bash
     sudo nano /etc/ipsec.conf
     ```
   * Adicione suas configurações de conexão VPN. Você pode incluir múltiplas seções `conn` para diferentes VPNs. Certifique-se de que o nome da conexão (`conn <nome-da-conexao>`) seja único e descritivo.
   * Alternativamente, você pode criar arquivos de configuração individuais em `/etc/ipsec.d/` (ex: `/etc/ipsec.d/minha_vpn.conf`).
2. **Configure os Segredos (se necessário)**:

   * Se sua conexão VPN usar autenticação por chave pré-compartilhada (PSK) ou EAP com senha, você precisará configurar o arquivo `/etc/ipsec.secrets`.
   * Abra o arquivo com privilégios de superusuário:

     ```bash
     sudo nano /etc/ipsec.secrets
     ```
   * Adicione suas credenciais no formato apropriado. Por exemplo, para PSK e EAP com senha:

     ```
     : PSK "sua_chave_secreta"
     <eap_identity> : EAP "sua_senha"
     ```
   
    
   * **Importante**: Mantenha este arquivo seguro, pois ele contém informações sensíveis.
3. **Verifique a Sintaxe**:

   * Após editar os arquivos, é uma boa prática verificar a sintaxe para evitar erros:
     ```bash
     sudo ipsec rereadall
     sudo ipsec status
     ```
   * Se houver erros, o comando `ipsec rereadall` geralmente indicará onde eles estão.
4. **Reinicie o Serviço IPsec**:

   * Para que as novas configurações sejam carregadas, reinicie o serviço strongSwan:
     ```bash
     sudo systemctl restart strongswan
     ```

Após seguir esses passos, a aplicação cliente VPN IPsec deverá detectar e permitir que você gerencie suas conexões configuradas.

### Configuração

1. A aplicação detecta automaticamente as conexões IPsec disponíveis em `/etc/ipsec.conf` e `/etc/ipsec.d/*.conf`.
2. Selecione a conexão desejada no menu suspenso.
3. Visualize os detalhes da conexão (endereço do servidor, tipo de autenticação, protocolos, etc.).
4. Use o toggle switch ou os botões de conectar/desconectar para controlar a conexão VPN.
5. Monitore o status da conexão e os logs na interface.
6. Acesse logs detalhados através do botão "Ver Logs Detalhados".

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
