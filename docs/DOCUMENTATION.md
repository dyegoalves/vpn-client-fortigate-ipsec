# Documentação do VPN Client FortiGate - IPsec

## sSobre o Projeto

O **VPN Client FortiGate - IPsec** é um cliente VPN gráfico desenvolvido pela DYSATECH para facilitar a conexão com servidores FortiGate usando a tecnologia IPsec/IKEv2.

**Versão:** v0.1.0
**Desenvolvido por:** DYSATECH
**Tecnologia:** IPsec/IKEv2 com StrongSwan  | Python3 | PyQt5

## Estrutura do Projeto

- `vpn-gui.py`: Interface gráfica principal (Frontend)
- `app/lib/vpn-client/`: Código-fonte da aplicação
  - `core/`: Componentes principais
    - `main.py`: Ponto de entrada principal
    - `app_window.py`: Lógica da interface gráfica
    - `worker.py`: Thread para operações em segundo plano
  - `ui/`: Componentes de interface
    - `widgets.py`: Componentes de interface personalizados
  - `system/`: Componentes de sistema
    - `helper.py`: Lógica executada com privilégios elevados
  - `config/`: Configurações
    - `config.py`: Configurações globais
- `vpn_start.sh`: Script de linha de comando (Backend)
- `README.md`: Documentação abreviada
- `docs/`: Pasta com documentação detalhada
  - `DOCUMENTATION.md`: Documentação completa
  - `VERSION`: Informações de versão
- `assets/`: Pasta com recursos
  - `img/vpn.png`: Ícone da aplicação
  - `atalho/vpn-gui.desktop`: Arquivo de atalho para o sistema
- `CHANGELOG.md`: Histórico de alterações
- `build-deb.sh`: Script de empacotamento

## Backend - Gerenciamento da VPN

### Componentes

- **StrongSwan**: Daemon IPsec para gerenciamento das conexões VPN
- **IPsec/IKEv2**: Protocolo de segurança para tunelamento
- **Script vpn_start.sh**: Interface de linha de comando para operações da VPN

### Pré-requisitos do Sistema

Antes de instalar o cliente, é essencial que os pré-requisitos do sistema estejam atendidos.

#### Sistema Operacional

- Distribuição Linux (Debian/Ubuntu recomendado)
- Kernel atualizado com suporte a módulos IPsec
- Acesso como administrador (sudo)

#### Recursos do Sistema

- Memória RAM: mínimo de 512MB livres
- Armazenamento: 50MB livres para instalação
- Conexão de rede ativa antes da configuração

#### Dependências do Sistema

- Python 3.6+
- StrongSwan 5.x+
- StrongSwan PKI
- PyQt5

### Configuração do IPsec/StrongSwan (Obrigatório)

Esta configuração é obrigatória e deve ser feita antes da instalação do cliente.

#### 1. Instalar o StrongSwan

Instale o StrongSwan e os utilitários necessários:s

```bash
sudo apt update
sudo apt install strongswan strongswan-pki
```

#### 2. Configurar o IPsec

Edite o arquivo de configuração do IPsec:

```bash
sudo nano /etc/ipsec.conf
```

Adicione a configuração da conexão VPN (ajuste conforme sua rede). A seguir, duas opções de configuração:

**Opção 1 - Acesso a Múltiplas Redes (Recomendado para seu caso):**
Esta configuração permite acesso às redes 192.168.126.x, 192.168.127.x e 10.10.14.x pela VPN, enquanto outros tráfegos (como navegação na internet) continuam usando a conexão padrão:

```conf
# ipsec.conf - strongSwan IPsec configuration file

config setup
    charondebug="ike 2, knl 2, cfg 2, mgr 2"

conn fortigate-vpn
    keyexchange=ikev2
    ike=aes256-sha256-ecp256
    esp=aes256-sha256
    left=%defaultroute
    leftid="seu_identificador"
    leftauth=eap-mschapv2
    eap_identity="seu_usuario"
    leftsourceip=%config
    right=endereco_servidor_vpn
    rightid=%any
    rightauth=psk
    rightsubnet=192.168.126.0/24,192.168.127.0/24,10.10.14.0/24
    auto=add
```

**Opção 2 - Acesso Total (Padrão, roteia todo tráfego pela VPN):**
Esta configuração roteia todo o tráfego pela VPN, útil para ambientes com políticas de segurança mais rígidas:

```conf
# ipsec.conf - strongSwan IPsec configuration file

config setup
    charondebug="ike 2, knl 2, cfg 2, mgr 2"

conn fortigate-vpn
    keyexchange=ikev2
    ike=aes256-sha256-ecp256
    esp=aes256-sha256
    left=%defaultroute
    leftid="seu_identificador"
    leftauth=eap-mschapv2
    eap_identity="seu_usuario"
    leftsourceip=%config
    right=endereco_servidor_vpn
    rightid=%any
    rightauth=psk
    rightsubnet=0.0.0.0/0
    auto=add
```

A Opção 1 é recomendada se você precisa acessar servidores específicos nas redes mencionadas mantendo acesso normal à internet. A Opção 2 deve ser usada se sua política de segurança exige que todo tráfego passe pela VPN.

#### 3. Configurar as credenciais

Edite o arquivo de credenciais da VPN:

```bash
sudo nano /etc/ipsec.secrets
```

Adicione as credenciais (substitua pelos seus dados reais):

```conf
: PSK "sua_chave_psk_secreta"
seu_usuario : EAP "sua_senha_usuario"
```

#### 4. Reiniciar o serviço

Após modificar os arquivos, reinicie o serviço IPsec:

```bash
sudo ipsec restart
```

#### 5. Verificar funcionamento

Teste se tudo está funcionando corretamente:

```bash
sudo ipsec statusall
```

#### Comandos do StrongSwan e IPsec

O StrongSwan fornece uma interface de linha de comando para gerenciar a VPN. Aqui estão os comandos mais importantes:

#### Comandos Básicos Terminal

```bash
# Conectar à VPN
sudo ipsec up fortigate-vpn

# Desconectar da VPN
sudo ipsec down fortigate-vpn

# Reiniciar a conexão
sudo ipsec restart

# Recarregar configurações
sudo ipsec reload
```

#### 6. Logs Esperados para Condições de Sucesso

Quando o IPsec/StrongSwan está configurado corretamente, os seguintes logs indicam funcionamento adequado:

**Exemplo de saída com conexão ESTABELECIDA:**

```bash
sudo ipsec statusall

Status of IKE charon daemon (strongSwan 5.9.13, Linux 6.12.33-amd64-desktop-rolling, x86_64):
  uptime: 58 minutes, since Oct 06 00:31:41 2025
  malloc: sbrk 3289088, mmap 0, used 1610128, free 1678960
  worker threads: 11 of 16 idle, 5/0/0/0 working, job queue: 0/0/0/0, scheduled: 41
  loaded plugins: charon test-vectors ldap pkcs11 tpm aesni aes rc2 sha2 sha1 md5 mgf1 rdrand random nonce x509 revocation constraints pubkey pkcs1 pkcs7 pkcs12 pgp dnskey sshkey pem openssl gcrypt pkcs8 af-alg fips-prf gmp curve25519 agent chapoly xcbc cmac hmac kdf ctr ccm gcm drbg curl attr kernel-netlink resolve socket-default connmark forecast farp stroke updown eap-identity eap-aka eap-md5 eap-gtc eap-mschapv2 eap-radius eap-tls eap-ttls eap-tnc xauth-generic xauth-eap xauth-pam tnc-tnccs dhcp lookip error-notify certexpire led addrblock unity counters
Listening IP addresses:
  192.168.18.32
  2804:3ac0:f7a2:6334:fad7:b18c:e3c6:3070
Connections:
fortigate-vpn:  %any...189.50.211.108  IKEv2
fortigate-vpn:   local:  [senai] uses EAP_MSCHAPV2 authentication with EAP identity 'dyegoalves'
fortigate-vpn:   remote: uses pre-shared key authentication
fortigate-vpn:   child:  dynamic === 0.0.0.0/0 TUNNEL
Security Associations (1 up, 0 connecting):
fortigate-vpn[20]: ESTABLISHED 13 seconds ago, 192.168.18.32[senai]...189.50.211.108[senai.aginet.com.br]
fortigate-vpn[20]: IKEv2 SPIs: c45745fd1fb71ffe_i* 67557dd97d08988c_r, EAP reauthentication in 2 hours
fortigate-vpn[20]: IKE proposal: AES_CBC_256/HMAC_SHA2_256_128/PRF_HMAC_SHA2_256/ECP_256
fortigate-vpn{20}:  INSTALLED, TUNNEL, reqid 1, ESP in UDP SPIs: c84a0ffd_i b552dce1_o
fortigate-vpn{20}:  AES_CBC_256/HMAC_SHA2_256_128, 168 bytes_i (2 pkts, 12s ago), 1890 bytes_o (29 pkts, 1s ago), rekeying in 44 minutes
fortigate-vpn{20}:   192.168.100.1/32 === 0.0.0.0/0
```

```bash
sudo ipsec status fortigate-vpn 

Security Associations (1 up, 0 connecting):
fortigate-vpn[24]: ESTABLISHED 4 minutes ago, 192.168.18.32[senai]...189.50.211.108[senai.aginet.com.br]
fortigate-vpn{24}:  INSTALLED, TUNNEL, reqid 1, ESP in UDP SPIs: c6d8a947_i b552dce5_o
fortigate-vpn{24}:   192.168.100.1/32 === 0.0.0.0/0
```

Neste exemplo, observe os indicadores de SUCESSO:

* **fortigate-vpn[24]: ESTABLISHED 9 seconds ago, 192.168.18.32[senai]...189.50.211.108[senai.aginet.com.br]**

- "Security Associations (1 up, 0 connecting)": 1 associação ativa
- "fortigate-vpn[20]: ESTABLISHED 13 seconds ago": conexão estabelecida há 13 segundos
- "192.168.18.32[senai]...189.50.211.108[senai.aginet.com.br]": IPs local e remoto corretos
- "fortigate-vpn{20}:  INSTALLED, TUNNEL": túnel IPsec instalado e ativo
- "bytes_i" e "bytes_o": tráfego sendo contado em ambas direções (entrada e saída)

### Instalação do Cliente Backend

O backend do cliente é baseado no StrongSwan e não requer instalação adicional além do script vpn_start.sh que já faz parte do repositório. O script pode ser executado diretamente:

```bash
bash vpn_start.sh
```



---



## Frontend - GUI (Interface Gráfica)

### Componentes

- **PyQt5**: Framework para interface gráfica
- **vpn-gui.py**: Código-fonte principal da interface gráfica
- **Elementos da interface**: Toggle Switch, Indicadores de Status e Animações

### Execução

Execute o cliente com interface gráfica:

```bash
cd /caminho/do/projeto
python3 vpn-gui.py
```

Ou execute diretamente o módulo:

```bash
cd /caminho/do/projeto
python3 -m src.main
```

A aplicação solicitará permissões de administrador para gerenciar a conexão VPN.

### Elementos da Interface

- **Janela Principal:** "VPN Client FortiGate - IPsec"
- **Toggle Switch:** Conecta/desconecta a VPN com um clique
- **Indicador de Status:** Mostra se a VPN está conectada ou desconectada
- **Rodapé:** Informações da versão e empresa ("VPN Client FortiGate - IPsec v0.1.0 | © 2025 DYSATECH | Open Source")

### Funcionalidades da GUI

- Conectar/desconectar VPN com um clique
- Atualização visual do status em tempo real
- Animações durante processos de conexão/desconexão
- Notificações de sistema
- Desconexão automática ao fechar a aplicação

### Instalação do Cliente Frontend

#### Passo 1: Instalar PyQt5

Instale a biblioteca gráfica:

```bash
pip3 install PyQt5
```

#### Passo 2: Obter o Cliente

Clone o repositório do projeto:

```bash
git clone https://github.com/seu_usuario/vpn-client-fortigate.git
cd vpn-client-fortigate
```

## Atalho no Sistema

### Criar atalho no menu de aplicações

Ou use o arquivo .desktop pronto ou crie manualmente:

**Opção 1: Usando o arquivo .desktop pronto (recomendado):**

1. Torne o script executável:
   ```bash
   chmod +x /home/dyegoalves/vpn/vpn-gui.py
   ```

2. Copie o arquivo .desktop fornecido para o diretório de aplicações:
   ```bash
   cp /home/dyegoalves/vpn/assets/atalho/vpn-gui.desktop ~/.local/share/applications/
   ```

3. Copie o ícone para o diretório de ícones do sistema:
   ```bash
   mkdir -p ~/.local/share/icons/hicolor/256x256/apps/
   cp /home/dyegoalves/vpn/assets/img/vpn.png ~/.local/share/icons/hicolor/256x256/apps/vpn-client-icon.png
   ```

4. Atualize o cache de aplicativos:
   ```bash
   update-desktop-database ~/.local/share/applications/
   ```

**Opção 2: Criando o arquivo .desktop manualmente:**

1. Torne o script executável:
   ```bash
   chmod +x /home/dyegoalves/vpn/vpn-gui.py
   ```

2. Crie o arquivo `.desktop` em `~/.local/share/applications/`:
   ```ini
   [Desktop Entry]
   Version=1.0
   Type=Application
   Name=VPN Client FortiGate - IPsec
   Comment=Cliente VPN para FortiGate usando IPsec
   Exec=/home/dyegoalves/vpn/vpn-gui.py
   Icon=vpn-client-icon
   Terminal=false
   Categories=Network;
   StartupNotify=true
   ```

3. Copie o ícone para o diretório de ícones do sistema:
   ```bash
   mkdir -p ~/.local/share/icons/hicolor/256x256/apps/
   cp /home/dyegoalves/vpn/assets/img/vpn.png ~/.local/share/icons/hicolor/256x256/apps/vpn-client-icon.png
   ```

4. Atualize o cache de aplicativos:
   ```bash
   update-desktop-database ~/.local/share/applications/
   ```

### Criar atalho na área de trabalho

Para criar um atalho diretamente na área de trabalho:

1. Copie o arquivo .desktop fornecido para a pasta da área de trabalho:
   ```bash
   cp /home/dyegoalves/vpn/assets/atalho/vpn-gui.desktop ~/Área\\ de\\ Trabalho/
   # ou em inglês:
   cp /home/dyegoalves/vpn/assets/atalho/vpn-gui.desktop ~/Desktop/
   ```

2. Torne o atalho confiável (necessário em muitos sistemas):
   ```bash
   chmod +x ~/Área\\ de\\ Trabalho/vpn-gui.desktop
   # ou em inglês:
   chmod +x ~/Desktop/vpn-gui.desktop
   ```

### Instruções Específicas para Deepin Linux

No Deepin Linux, após seguir as etapas acima, o atalho deve aparecer no menu de aplicações. Em alguns casos, pode ser necessário reiniciar a sessão ou o sistema para que o ícone apareça corretamente.

Caso o ícone não apareça no menu, você pode tentar atualizar o cache de ícones:
```bash
gtk-update-icon-cache
```

Se ainda não funcionar, verifique se o serviço de gerenciamento de arquivos do Deepin está reconhecendo o novo arquivo .desktop.

### Problemas Comuns

**Pergunta:** Por que o cliente solicita senha de administrador?
**Resposta:** O cliente precisa de permissões elevadas para gerenciar conexões de rede e o serviço IPsec.

**Pergunta:** O que significa "fortigate-vpn[20]: ESTABLISHED"?
**Resposta:** Indica que a conexão VPN foi estabelecida com sucesso.

**Pergunta:** A interface não responde ao clicar no toggle?
**Resposta:** Verifique se o serviço IPsec está em execução e se as configurações estão corretas.

**Pergunta:** O script de linha de comando funciona mas a GUI não?
**Resposta:** Verifique se o PyQt5 está instalado corretamente e se o usuário tem permissão para exibir interfaces gráficas.

## Empacotamento para Distribuições Linux

O projeto inclui scripts para facilitar o empacotamento e instalação em distribuições Linux.

### Scripts de Empacotamento e Instalação

O projeto inclui os seguintes scripts:

- `build-deb.sh`: Gera pacote .deb para distribuição

### Como empacotar o projeto

Execute o script de empacotamento:

```bash
./build-deb.sh
```

O script irá:

1. Criar uma estrutura de pacote adequada
2. Gerar um pacote .deb instalável com `dpkg`

Após a execução, você encontrará o pacote em `build/vpn-client-fortigate_*.deb`.

### Como instalar

**Usando o pacote .deb gerado:**

```bash
sudo dpkg -i build/vpn-client-fortigate_*.deb
```

### Como desinstalar

**Se instalado com o pacote .deb:**
```bash
sudo dpkg -r vpn-client-fortigate
```

---

Desenvolvido por: DYSATECH
© 2025 DYSATECH - Open Source

## Modo Desenvolvimento

Para executar o projeto em modo desenvolvimento:

```bash
cd /caminho/do/projeto
python3 vpn-gui.py
```

Ou diretamente com o módulo:

```bash
cd /caminho/do/projeto
python3 -m src.main
```

## Dependências

O cliente VPN requer as seguintes dependências:

- Python 3.6+
- PyQt5
- StrongSwan
- pkexec (PolicyKit)

Para instalar as dependências em sistemas Debian/Ubuntu:

```bash
sudo apt update
sudo apt install python3-pyqt5 strongswan policykit-1
```

## Controle de Versão

A versão atual do software está definida no arquivo `docs/VERSION`. Use esse arquivo para rastrear qual versão está instalada em seu sistema.
