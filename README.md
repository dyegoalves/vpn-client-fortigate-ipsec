# VPN Client FortiGate - IPsec

Cliente gráfico para gerenciamento de conexão VPN FortiGate usando IPsec/IKEv2.

<img src="./app/share/pixmaps/vpn.png" width="128">

## Descrição

O **VPN Client FortiGate - IPsec** é um cliente VPN gráfico desenvolvido pela DYSATECH para facilitar a conexão com servidores FortiGate usando a tecnologia IPsec/IKEv2.

## Funcionalidades

- Interface gráfica intuitiva com toggle switch
- Indicadores visuais de status em tempo real
- Desconexão automática ao fechar o aplicativo
- Controle refinado da conexão VPN
- Notificações de sistema

## Estrutura do Projeto

O projeto segue os padrões FHS (Filesystem Hierarchy Standard) para software desktop Linux:

- `app/` - Estrutura organizada do aplicativo (ambiente de desenvolvimento)
  - `bin/` - Scripts executáveis de desenvolvimento
  - `lib/` - Código-fonte e bibliotecas (com subdiretório `modules/`)
  - `share/` - Recursos compartilhados (ícones, arquivos .desktop)
- `docs/` - Documentação do projeto
- `scripts/` - Scripts de build e utilitários
- `uninstall.sh` - Script de desinstalação

## Desenvolvimento

Para executar diretamente do código-fonte:

```bash
cd app/bin
python3 vpn-gui.py
```

## Empacotamento

O pacote .deb instala os arquivos da seguinte forma:
- Código-fonte em `/usr/lib/vpn-client-fortigate/`
- Executáveis em `/usr/bin/` (vpn-gui, vpn-start)
- Ícones em `/usr/share/pixmaps/`
- Arquivo .desktop em `/usr/share/applications/`
- Documentação em `/usr/share/doc/vpn-client-fortigate/`

## Desinstalação

Execute o script de desinstalação como root:

```bash
sudo ./uninstall.sh
```

## Execução

Após a instalação do pacote .deb, execute:

```bash
vpn-gui
```

## Dependências

- Python 3.6+
- PyQt5
- StrongSwan
- pkexec (PolicyKit)

## Documentação

Para instruções detalhadas de configuração, instalação e uso, consulte a [documentação completa](docs/DOCUMENTATION.md).

---

**VPN Client FortiGate - IPsec v0.1.0**
Desenvolvido por: DYSATECH
© 2025 DYSATECH - Open Source
