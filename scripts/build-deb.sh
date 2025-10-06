#!/bin/bash

# Script para criar pacote .deb do VPN Client FortiGate - IPsec
# Seguindo padrões FHS para software desktop Linux
# Desenvolvido por: DYSATECH
# Versão: 0.1.0

set -e  # Sair se ocorrer um erro

# Variáveis
APP_NAME="vpn-client-fortigate"
VERSION=$(cat docs/VERSION 2>/dev/null | grep -o "v[0-9.]*" | head -n1 | tr -d 'v' || echo "0.1.0")
BUILD_DIR="build"
PACKAGE_NAME="${APP_NAME}_${VERSION}_amd64"
PACKAGE_DIR="${BUILD_DIR}/${PACKAGE_NAME}"
CURRENT_DIR=$(pwd)

echo "Iniciando criação do pacote .deb para ${APP_NAME} versão ${VERSION}"

# Limpar builds anteriores
rm -rf "$BUILD_DIR"
mkdir -p "$PACKAGE_DIR/DEBIAN"
mkdir -p "$PACKAGE_DIR/usr/lib/${APP_NAME}"
mkdir -p "$PACKAGE_DIR/usr/bin"
mkdir -p "$PACKAGE_DIR/usr/share/applications"
mkdir -p "$PACKAGE_DIR/usr/share/pixmaps"
mkdir -p "$PACKAGE_DIR/usr/share/doc/${APP_NAME}"
mkdir -p "$PACKAGE_DIR/usr/share/polkit-1/actions"

echo "Criando estrutura de diretórios..."

# Copiar arquivos do aplicativo
cp -r app/lib/* "$PACKAGE_DIR/usr/lib/${APP_NAME}/"
cp app/bin/vpn-gui.py "$PACKAGE_DIR/usr/lib/${APP_NAME}/"
cp app/bin/vpn_start.sh "$PACKAGE_DIR/usr/lib/${APP_NAME}/"
chmod +x "$PACKAGE_DIR/usr/lib/${APP_NAME}/vpn-gui.py"
chmod +x "$PACKAGE_DIR/usr/lib/${APP_NAME}/vpn_start.sh"

# Criar scripts de inicialização em /usr/bin
cat > "$PACKAGE_DIR/usr/bin/vpn-gui" << EOF
#!/bin/sh
export PYTHONPATH="/usr/lib/${APP_NAME}:\$PYTHONPATH"
exec python3 /usr/lib/${APP_NAME}/vpn-gui.py "\$@"
EOF
chmod +x "$PACKAGE_DIR/usr/bin/vpn-gui"

cat > "$PACKAGE_DIR/usr/bin/vpn-start" << EOF
#!/bin/sh
export PYTHONPATH="/usr/lib/${APP_NAME}:\$PYTHONPATH"
exec python3 /usr/lib/${APP_NAME}/vpn_start.sh "\$@"
EOF
chmod +x "$PACKAGE_DIR/usr/bin/vpn-start"

# Copiar ícone
cp app/share/pixmaps/vpn.png "$PACKAGE_DIR/usr/share/pixmaps/vpn-client-icon.png"

# Copiar arquivo .desktop
cp app/share/applications/vpn-gui.desktop "$PACKAGE_DIR/usr/share/applications/"

# Copiar documentação
cp docs/DOCUMENTATION.md "$PACKAGE_DIR/usr/share/doc/${APP_NAME}/DOCUMENTATION.md"
cp docs/VERSION "$PACKAGE_DIR/usr/share/doc/${APP_NAME}/VERSION"
cp README.md "$PACKAGE_DIR/usr/share/doc/${APP_NAME}/README.md"
cp CHANGELOG.md "$PACKAGE_DIR/usr/share/doc/${APP_NAME}/CHANGELOG.md"

# Copiar arquivo de política do PolicyKit
cp app/share/polkit-1/actions/br.com.dysatech.vpn-client-fortigate.policy "$PACKAGE_DIR/usr/share/polkit-1/actions/br.com.dysatech.vpn-client-fortigate.policy"

# Criar controle de pacote
cat > "$PACKAGE_DIR/DEBIAN/control" << EOF
Package: ${APP_NAME}
Version: ${VERSION}
Section: net
Priority: optional
Architecture: amd64
Depends: python3, python3-pyqt5, policykit-1
Maintainer: DYSATECH <support@dysatech.com.br>
Description: VPN Client FortiGate - IPsec
 Cliente VPN gráfico para conexão com servidores FortiGate usando IPsec/IKEv2.
 Este pacote inclui uma interface gráfica para gerenciar conexões VPN.
 .
 O cliente permite iniciar, parar e monitorar conexões VPN FortiGate com
 uma interface intuitiva.
EOF

echo "Arquivos copiados com sucesso!"

# Criar controle de pacote (DEBIAN/control)
cat > "${PACKAGE_DIR}/DEBIAN/control" << EOF
Package: ${APP_NAME}
Version: ${VERSION}
Section: net
Priority: optional
Architecture: amd64
Depends: python3, python3-pyqt5, policykit-1
Maintainer: DYSATECH <dyegoalves@dysatech.com.br>
Description: VPN Client FortiGate - IPsec
 Cliente VPN gráfico para conexão com servidores FortiGate usando IPsec/IKEv2.
 Este pacote inclui uma interface gráfica para gerenciar conexões VPN.
 .
 O cliente permite iniciar, parar e monitorar conexões VPN FortiGate com
 uma interface intuitiva.
EOF

# Criar script de pós-instalação (DEBIAN/postinst)
cat > "${PACKAGE_DIR}/DEBIAN/postinst" << 'EOF'
#!/bin/bash
# Script de pós-instalação

set -e

# Atualizar o cache de desktop
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database ~/.local/share/applications/ 2>/dev/null || true
    update-desktop-database /usr/share/applications/ 2>/dev/null || true
fi

# Atualizar cache de ícones
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache /usr/share/icons/hicolor/ 2>/dev/null || true
fi

# Verificar se PyQt5 está instalado
if ! python3 -c "import PyQt5" &> /dev/null; then
    echo "AVISO: PyQt5 não está instalado. Execute: pip3 install PyQt5"
fi

echo "Instalação concluída! Você pode agora usar o VPN Client FortiGate - IPsec."
EOF

# Ajustar permissões ANTES de criar o pacote
chmod 755 "${PACKAGE_DIR}/DEBIAN"
chmod 755 "${PACKAGE_DIR}/DEBIAN/postinst"
find "$PACKAGE_DIR/usr/share/doc/${APP_NAME}" -type f -exec chmod 644 {} \;

# Ajustar permissões para outros arquivos
find "$PACKAGE_DIR/usr/share/applications" -type f -exec chmod 644 {} \;

# Criar pacote .deb
echo "Criando pacote .deb..."
cd "$BUILD_DIR"
dpkg-deb --build --root-owner-group "$PACKAGE_NAME"
cd "$CURRENT_DIR"

echo "Empacotamento concluído!"
echo "Pacote .deb criado em: ${BUILD_DIR}/${PACKAGE_NAME}.deb"

echo ""
echo "Para instalar o pacote:"
echo "  sudo dpkg -i ${BUILD_DIR}/${PACKAGE_NAME}.deb"