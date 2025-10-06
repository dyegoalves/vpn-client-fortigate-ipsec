#!/bin/bash

VPN_NAME="fortigate-vpn"

function start_vpn() {
    echo "Iniciando VPN $VPN_NAME..."
    sudo systemctl start ipsec
    sudo ipsec up $VPN_NAME
    echo "VPN iniciada."
}

function stop_vpn() {
    echo "Parando VPN $VPN_NAME..."
    sudo ipsec down $VPN_NAME
    sudo systemctl stop ipsec
    echo "VPN parada."
}

function status_vpn() {
    echo "Status da VPN $VPN_NAME:"
    systemctl status ipsec --no-pager
    ps aux | grep charon | grep -v grep
}

function menu() {
    while true; do
        clear
        echo "=============================="
        echo "   Gerenciador de VPN"
        echo "=============================="
        echo "1) Iniciar VPN"
        echo "2) Parar VPN"
        echo "3) Ver status da VPN"
        echo "4) Reiniciar VPN"
        echo "5) Sair"
        echo "=============================="
        read -p "Escolha uma opção [1-5]: " option

        case $option in
            1) start_vpn ;;
            2) stop_vpn ;;
            3) status_vpn ;;
            4) stop_vpn; start_vpn ;;
            5) echo "Saindo..."; return 1 ;;
            *) echo "Opção inválida!"; sleep 1 ;;
        esac
        read -p "Pressione Enter para continuar..."
    done
}

menu
