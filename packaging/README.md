# Diretório de Empacotamento

Este diretório contém scripts e configurações para diferentes métodos de empacotamento da aplicação VPN IPsec Client.

## Estrutura

```
packaging/
├── menu_build.sh         # Script principal com menu interativo para empacotamento
├── appimage/             # Scripts e configurações para AppImage
│   ├── build.sh          # Script para criar AppImage
│   └── README.md         # Documentação para AppImage
└── debian/               # Scripts e configurações para pacote .deb
    ├── build.sh          # Script para criar pacote .deb
    └── README.md         # Documentação para pacote .deb
```

## Como usar

Para executar qualquer tipo de empacotamento, use o script principal com menu interativo:

```bash
./packaging/menu_build.sh
```

O script apresentará um menu com as seguintes opções:

```
=============================================
  Menu de Empacotamento - VPN IPsec Client
=============================================
  Selecione o formato do pacote:

  1) AppImage   - Cria um AppImage executável
  2) Deb        - Cria um pacote .deb
  3) Todos      - Cria todos os pacotes

  4) Sair
=============================================
Digite sua escolha [1-4]:
```

## Tipos de Empacotamento

### AppImage
- Formato portátil que não requer instalação
- Pode ser executado em qualquer sistema Linux x86_64
- Contém todos os recursos necessários

### Pacote Debian (.deb)
- Formato para distribuições baseadas em Debian/Ubuntu
- Instalação através do sistema de pacotes
- Gerencia dependências automaticamente

### Todos
- Executa todos os tipos de empacotamento em sequência
- Gera tanto o AppImage quanto o pacote .deb