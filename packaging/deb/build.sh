#!/bin/bash

# Script para criar um pacote .deb para a aplicação VPN IPsec Client

set -e  # Sair se qualquer comando falhar

# Definir variáveis
APP_NAME="vpn-ipsec-client"
APP_VERSION="0.3.0"
APP_MAINTAINER="VPN IPsec Client Team"
APP_DESCRIPTION="Cliente VPN IPsec para Linux com interface gráfica. Uma aplicação para gerenciar conexões VPN IPsec com uma interface gráfica amigável e integrada ao ambiente Linux."
DEBIAN_PACKAGE_NAME="${APP_NAME}_${APP_VERSION}_amd64.deb"
BUILD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$BUILD_DIR")")"
TEMP_DIR=$(mktemp -d)

echo "Iniciando processo de empacotamento para .deb..."
echo "Pacote: $DEBIAN_PACKAGE_NAME"
echo "Diretório temporário: $TEMP_DIR"

# Verificar se está rodando no Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "Este script só pode ser executado no Linux"
    exit 1
fi

# Verificar se dpkg-deb está instalado
if ! command -v dpkg-deb >/dev/null 2>&1; then
    echo "dpkg-deb é necessário mas não está instalado. Abortando."
    echo "Instale com: sudo apt install dpkg-dev"
    exit 1
fi

echo "Criando estrutura do pacote Debian em $TEMP_DIR..."

# Diretórios principais
mkdir -p "$TEMP_DIR/DEBIAN"
mkdir -p "$TEMP_DIR/usr/bin"
mkdir -p "$TEMP_DIR/usr/lib/$APP_NAME"
mkdir -p "$TEMP_DIR/usr/share/applications"
mkdir -p "$TEMP_DIR/usr/share/icons/hicolor/scalable/apps"

# Criar arquivo control
cat > "$TEMP_DIR/DEBIAN/control" << EOF
Package: $APP_NAME
Version: $APP_VERSION
Section: net
Priority: optional
Architecture: amd64
Depends: python3, python3-pip, python3-pyside6, python3-configparser, python3-cryptography, strongswan, libstrongswan-extra-plugins
Maintainer: $APP_MAINTAINER
Description: $APP_DESCRIPTION
EOF

echo "Criando scripts de manutenção do pacote (postinst, postrm)..."
# Script post-instalação para atualizar o cache de ícones
cat > "$TEMP_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/sh
set -e
if [ "$1" = "configure" ]; then
    echo "Atualizando cache de ícones..."
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
    fi
fi
exit 0
EOF

# Script post-remoção para atualizar o cache de ícones
cat > "$TEMP_DIR/DEBIAN/postrm" << 'EOF'
#!/bin/sh
set -e
if [ "$1" = "remove" ]; then
    echo "Atualizando cache de ícones..."
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
    fi
fi
exit 0
EOF

# Dar permissão de execução para os scripts
chmod 755 "$TEMP_DIR/DEBIAN/postinst"
chmod 755 "$TEMP_DIR/DEBIAN/postrm"

echo "Copiando arquivos da aplicação..."
# Copiar arquivos principais
cp -r "$PROJECT_ROOT/src" "$TEMP_DIR/usr/lib/$APP_NAME/"
cp "$PROJECT_ROOT/main.py" "$TEMP_DIR/usr/lib/$APP_NAME/"
cp "$PROJECT_ROOT/requirements.txt" "$TEMP_DIR/usr/lib/$APP_NAME/" 2>/dev/null || echo "requirements.txt não encontrado"

# Criar script de inicialização
cat > "$TEMP_DIR/usr/bin/$APP_NAME" << 'EOF'
#!/bin/bash
# VPN IPsec Client launcher script

# Caminho para o diretório da aplicação
APP_DIR="/usr/lib/vpn-ipsec-client"

# Verificar se o diretório da aplicação existe
if [ ! -d "$APP_DIR" ]; then
    echo "Erro: Diretório da aplicação não encontrado em $APP_DIR"
    exit 1
fi

# Executar a aplicação
cd "$APP_DIR"
python3 main.py "$@"
EOF

chmod +x "$TEMP_DIR/usr/bin/$APP_NAME"

# Criar atalho da aplicação
cat > "$TEMP_DIR/usr/share/applications/$APP_NAME.desktop" << EOF
[Desktop Entry]
Name=VPN IPsec Client
Exec=$APP_NAME
Type=Application
Icon=/usr/share/icons/hicolor/scalable/apps/$APP_NAME.svg
Categories=Network;
Terminal=false
Comment=Cliente VPN IPsec para Linux
EOF

# Copiar ícone ou criar fallback
if [ -f "$PROJECT_ROOT/src/assets/icon.svg" ]; then
    cp "$PROJECT_ROOT/src/assets/icon.svg" "$TEMP_DIR/usr/share/icons/hicolor/scalable/apps/$APP_NAME.svg"
else
    # Criar ícone temporário como fallback
    cat > "$TEMP_DIR/usr/share/icons/hicolor/scalable/apps/$APP_NAME.svg" << 'SVGEOF'
<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 100 100">
  <rect width="100" height="100" fill="#3498db"/>
  <text x="50" y="55" font-family="Arial" font-size="40" fill="white" text-anchor="middle">VPN</text>
</svg>
SVGEOF
fi

# Ajustar permissões
chmod 644 "$TEMP_DIR/usr/share/applications/$APP_NAME.desktop"
chmod 644 "$TEMP_DIR/usr/share/icons/hicolor/scalable/apps/$APP_NAME.svg"

echo "Estrutura do pacote criada com sucesso. Arquivos:"
find "$TEMP_DIR" -type f | sort

echo "Criando pacote .deb..."
dpkg-deb --build --root-owner-group "$TEMP_DIR" "$BUILD_DIR/$DEBIAN_PACKAGE_NAME"

echo "Pacote .deb criado com sucesso: $BUILD_DIR/$DEBIAN_PACKAGE_NAME"
echo "Tamanho: $(du -h "$BUILD_DIR/$DEBIAN_PACKAGE_NAME" | cut -f1)"

# Limpar diretório temporário
rm -rf "$TEMP_DIR"

echo "Processo de empacotamento .deb concluído com sucesso!"
echo ""
echo "Para instalar o pacote, use:"
echo "  sudo dpkg -i $BUILD_DIR/$DEBIAN_PACKAGE_NAME"
echo ""
echo "Para resolver dependências após a instalação:"
echo "  sudo apt-get install -f"