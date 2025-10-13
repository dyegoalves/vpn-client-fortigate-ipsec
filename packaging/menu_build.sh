#!/bin/bash

# Script principal para empacotamento da aplicação VPN IPsec Client
# Este script coordena os diferentes métodos de empacotamento com um menu interativo.

# --- Funções de Build ---

PROJECT_ROOT="/home/dyegoalves/projects/vpn-ipsec-fortigate-client-linux"

# Cria o pacote AppImage
build_appimage() {
    cd "$PROJECT_ROOT"
    echo "================================="
    echo "Criando AppImage..."
    echo "================================="
    if [ -f "packaging/appimage/build.sh" ]; then
        (cd "packaging/appimage" && ./build.sh)
        echo "---------------------------------"
        echo "AppImage criado com sucesso!"
        echo "---------------------------------"
    else
        echo "Erro: Script 'packaging/appimage/build.sh' não encontrado."
    fi
    echo ""
    read -p "Pressione Enter para voltar ao menu..."
}

# Cria o pacote Deb
build_deb() {
    cd "$PROJECT_ROOT"
    echo "================================="
    echo "Criando pacote Deb..."
    echo "================================="
    echo "Diretório atual antes da verificação: $(pwd)"
    echo "PROJECT_ROOT: $PROJECT_ROOT"
    if [ -f "packaging/deb/build.sh" ]; then
        (cd "packaging/deb" && ./build.sh)
        echo "---------------------------------"
        echo "Pacote Deb criado com sucesso!"
        echo "---------------------------------"
    else
        echo "Erro: Script 'packaging/deb/build.sh' não encontrado."
    fi
    echo ""
    read -p "Pressione Enter para voltar ao menu..."
}

# Cria todos os pacotes
build_all() {
    echo "================================="
    echo "Criando todos os pacotes..."
    echo "================================="
    build_appimage
    build_deb
    echo "---------------------------------"
    echo "Todos os pacotes foram criados!"
    echo "---------------------------------"
    echo ""
    read -p "Pressione Enter para voltar ao menu..."
}

# --- Menu Principal ---

# Exibe o menu de opções
show_menu() {
    clear
    echo "============================================="
    echo "  Menu de Empacotamento - VPN IPsec Client"
    echo "============================================="
    echo "  Selecione o formato do pacote:"
    echo
    echo "  1) AppImage   - Cria um AppImage executável"
    echo "  2) Deb        - Cria um pacote .deb"
    echo "  3) Todos      - Cria todos os pacotes"
    echo
    echo "  4) Sair"
    echo "============================================="
}

# Loop principal do menu
while true; do
    show_menu
    read -p "Digite sua escolha [1-4]: " choice

    case "$choice" in
        1)
            build_appimage
            ;;
        2)
            build_deb
            ;;
        3)
            build_all
            ;;
        4)
            echo "Saindo do script de empacotamento."
            return 1
            ;;
        *)
            echo "Opção inválida: '$choice'. Tente novamente."
            sleep 2
            ;;
    esac
done
