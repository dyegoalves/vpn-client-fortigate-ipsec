# Documentação do VPN Client FortiGate - IPsec

## Arquitetura do Projeto

O projeto segue princípios de design orientado a objetos e responsabilidade única:

- Componentes bem definidos com funções específicas
- Separação clara entre interface e lógica de negócios
- Comunicação segura entre componentes de usuário e sistema

## Estrutura de Diretórios

- `app/` - Código-fonte e recursos do aplicativo
  - `bin/` - Scripts executáveis
  - `lib/` - Código-fonte principal
    - `core/` - Componentes principais (interface, comunicação, workers)
    - `config/` - Configurações e gerenciamento de caminhos
    - `ui/` - Componentes de interface
    - `system/` - Componentes de sistema com privilégios
  - `share/` - Recursos compartilhados (ícones, arquivos .desktop)
- `docs/` - Documentação do projeto
- `scripts/` - Scripts de build e utilitários
- `build/` - Arquivos gerados pelo processo de compilação
- `logs/` - Registros de execução do aplicativo

## Backend - Gerenciamento da VPN

O backend utiliza o StrongSwan para gerenciar as conexões IPsec/IKEv2. Inclui:

- **StrongSwan**: Daemon IPsec para gerenciamento das conexões VPN
- **Script vpn_start.sh**: Interface de linha de comando para operações da VPN

### Pré-requisitos

- Python 3.6+
- StrongSwan 5.x+
- StrongSwan PKI
- PyQt5
- pkexec (PolicyKit)
- Acesso como administrador (sudo)

## Configuração do IPsec

### 1. Instalar dependências

```bash
sudo apt update
sudo apt install strongswan strongswan-pki python3-pyqt5 policykit-1
# plugins depedencias
sudo apt install strongswan-swanctl
sudo apt install libstrongswan-extra-plugins

```

### 2. Configurar IPsec

Edite `sudo nano /etc/ipsec.conf` e adicione a conexão VPN:

```
sudo nano /etc/ipsec.conf
```

**Atenção**: Edite com seus dados, observando os campos entre `<>` e substitua-os.
Além disso, observe que `ike` (fase 1) e `esp` (fase 2) são algoritmos de autenticação que precisam ser compatíveis com o servidor.
As sub-redes configuradas para acesso são: 192.168.127.0/24, 192.168.126.0/24 e 10.10.10.0/24
Para configurar o DNS da Google (8.8.8.8 e 8.8.4.4), adicione as opções leftdns conforme exemplo abaixo.

```bash
config setup
    charondebug="ike 2, knl 2, cfg 2, mgr 2"

conn fortigate-vpn  
    keyexchange=ikev2
    ike=aes256-sha256-ecp256
    esp=aes256-sha256
    left=%defaultroute
    leftid="<SEU_IDENTIFICADOR_AQUI>"
    leftauth=eap-mschapv2
    eap_identity="<SEU_USUARIO_AQUI>"
    leftsourceip=%config
    leftdns=8.8.8.8,8.8.4.4
    right=<IP_DO_SERVIDOR_VPN_AQUI>
    rightid=%any
    rightauth=psk
    rightsubnet=192.168.127.0/24,192.168.126.0/24,10.10.10.0/24
    auto=add
```

### 3. Configurar credenciais

Em `sudo nano /etc/ipsec.secrets`, adicione:

```bash
  sudo nano /etc/ipsec.secrets
```

```bash
: PSK "<SUA_CHAVE_PSK_SECRET_AQUI>"
<SEU_USUARIO_AQUI> : EAP "<SUA_SENNHA_USUARIO_AQUI>"
```

```bash
  sudo chmod 600 /etc/ipsec.secrets
```

> **Observação**: Substitua `<SEU_USUARIO_AQUI>` pelo mesmo nome de usuário usado na configuração do IPsec.

### 4. Reiniciar serviço

```bash
sudo ipsec restart
```

## Comandos úteis do StrongSwan

```bash
# Conectar à VPN
sudo ipsec up fortigate-vpn

# Desconectar da VPN
sudo ipsec down fortigate-vpn

# Ver status
sudo ipsec statusall

# Verificar status de uma conexão específica
sudo ipsec status
```

## Frontend - Interface Gráfica

A interface gráfica é construída com PyQt5 e oferece:

- Toggle switch para conexão/desconexão
- Indicadores visuais de status
- Animações e notificações
- Desconexão automática ao fechar

## Autenticação e Permissões

O aplicativo utiliza PolicyKit para execução de comandos com privilégios:

- Solicita credenciais de administrador via `pkexec`
- Comunica-se com um helper que executa comandos IPsec
- Verifica constantemente se o helper está respondendo

## Empacotamento

O projeto inclui um script para gerar pacotes .deb:

O script `build-deb.sh` automatiza a criação de um pacote .deb seguindo o padrão FHS, com todos os componentes necessários para o funcionamento do aplicativo.

### Como gerar o pacote:

```bash
sudo chmod +x ./scripts/build-deb.sh
./scripts/build-deb.sh
```

### Estrutura do pacote:

- `/usr/lib/vpn-client-fortigate/` - Arquivos principais do aplicativo
- `/usr/bin/` - Atalhos (vpn-gui e vpn-start)
- `/usr/share/applications/` - Arquivo .desktop
- `/usr/share/pixmaps/` - Ícone do aplicativo
- `/usr/share/doc/vpn-client-fortigate/` - Documentação
- `/usr/share/polkit-1/actions/` - Política do PolicyKit

### Dependências:

- `python3`
- `python3-pyqt5`
- `policykit-1`

### Instalação:

```bash
sudo dpkg -i build/vpn-client-fortigate_{versão}_amd64.deb
```

## Desenvolvimento

Para rodar em modo desenvolvimento:

```bash
cd app/bin
python3 vpn-gui.py
```

---

Desenvolvido por: DYSATECH
© 2025 DYSATECH - Open Source
