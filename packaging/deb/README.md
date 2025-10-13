# Empacotamento Debian (.deb)

Este diretório contém os scripts e configurações necessários para empacotar a aplicação VPN IPsec Client como um pacote Debian (.deb).

## Estrutura

```
packaging/debian/
├── build.sh    # Script principal para criar o pacote .deb
└── README.md   # Este arquivo
```

## Como criar o pacote .deb

Execute o script de build:

```bash
cd packaging/debian
./build.sh
```

O script irá:
1. Criar uma estrutura de diretórios para o pacote Debian
2. Copiar os arquivos da aplicação para os diretórios apropriados
3. Criar o script de inicialização e o atalho do aplicativo
4. Definir as dependências necessárias no arquivo de controle
5. Gerar o pacote .deb final

O pacote resultante será nomeado `vpn-ipsec-client-<version>_amd64.deb` e salvo no diretório `packaging/debian/`.

## Requisitos

- Linux (baseado em Debian/Ubuntu)
- dpkg-deb
- python3
- python3-pip
- python3-pyside6
- python3-configparser
- python3-cryptography
- strongswan
- libstrongswan-extra-plugins

## Notas

- O script automaticamente lida com permissões e dependências
- O pacote .deb gerado é compatível com sistemas baseados em Debian/Ubuntu
- Todos os arquivos temporários são criados e mantidos dentro do diretório de empacotamento