#!/bin/bash
# Script para criar um pacote .deb para a aplicação VPN IPsec Client

set -e  # Sair se qualquer comando falhar

# =============================
# Definições principais
# =============================
APP_NAME="vpn-ipsec-client"
APP_VERSION="0.4.0"
APP_MAINTAINER="VPN IPsec Client Team"
APP_DESCRIPTION="Cliente VPN IPsec para Linux com interface gráfica. Gerencia conexões VPN IPsec com uma interface amigável e integrada ao ambiente Linux."
DEBIAN_PACKAGE_NAME="${APP_NAME}_${APP_VERSION}_amd64.deb"

# Diretórios base
BUILD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$BUILD_DIR")")"
TEMP_DIR=$(mktemp -d)

echo "Iniciando empacotamento .deb para $APP_NAME v$APP_VERSION"
echo "Diretório temporário: $TEMP_DIR"

# =============================
# Verificações básicas
# =============================
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "Este script deve ser executado em Linux."
    exit 1
fi

if ! command -v dpkg-deb >/dev/null 2>&1; then
    echo "dpkg-deb não encontrado. Instale com: sudo apt install dpkg-dev"
    exit 1
fi

# =============================
# Estrutura do pacote
# =============================
echo "Criando estrutura do pacote..."
mkdir -p "$TEMP_DIR/DEBIAN"
mkdir -p "$TEMP_DIR/usr/bin"
mkdir -p "$TEMP_DIR/usr/lib/$APP_NAME"
mkdir -p "$TEMP_DIR/usr/share/applications"
mkdir -p "$TEMP_DIR/usr/share/icons/hicolor/scalable/apps"

# =============================
# Arquivo control (corrigido)
# =============================
cat > "$TEMP_DIR/DEBIAN/control" << EOF
Package: $APP_NAME
Version: $APP_VERSION
Section: net
Priority: optional
Architecture: amd64
Depends: python3 (>= 3.8), python3-pip, python3-cryptography, strongswan, libstrongswan-extra-plugins
Maintainer: $APP_MAINTAINER
Description: $APP_DESCRIPTION
EOF

# =============================
# postinst (instala PySide6 via pip)
# =============================
cat > "$TEMP_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/sh
set -e

if [ "$1" = "configure" ]; then
    echo "[+] Instalando dependências Python necessárias..."
    if command -v python3 >/dev/null 2>&1; then
        python3 -m pip install --upgrade pip wheel setuptools >/dev/null 2>&1 || true
        python3 -m pip install --no-cache-dir PySide6 >/dev/null 2>&1 || {
            echo "Aviso: Falha ao instalar PySide6, verifique sua conexão."
        }
    fi

    echo "[+] Atualizando cache de ícones..."
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
    fi
fi
exit 0
EOF

# =============================
# postrm (limpa cache de ícones)
# =============================
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

chmod 755 "$TEMP_DIR/DEBIAN/postinst" "$TEMP_DIR/DEBIAN/postrm"

# =============================
# Copiar arquivos da aplicação
# =============================
echo "Copiando arquivos da aplicação..."
cp -r "$PROJECT_ROOT/src" "$TEMP_DIR/usr/lib/$APP_NAME/" 2>/dev/null || echo "Aviso: diretório src não encontrado."
cp "$PROJECT_ROOT/main.py" "$TEMP_DIR/usr/lib/$APP_NAME/" 2>/dev/null || echo "Aviso: main.py não encontrado."
cp "$PROJECT_ROOT/requirements.txt" "$TEMP_DIR/usr/lib/$APP_NAME/" 2>/dev/null || true

# =============================
# Script de inicialização
# =============================
cat > "$TEMP_DIR/usr/bin/$APP_NAME" << 'EOF'
#!/bin/bash
# VPN IPsec Client launcher

APP_DIR="/usr/lib/vpn-ipsec-client"

if [ ! -d "$APP_DIR" ]; then
    echo "Erro: diretório da aplicação não encontrado em $APP_DIR"
    exit 1
fi

cd "$APP_DIR"
exec python3 main.py "$@"
EOF
chmod +x "$TEMP_DIR/usr/bin/$APP_NAME"

# =============================
# Atalho desktop
# =============================
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
chmod 644 "$TEMP_DIR/usr/share/applications/$APP_NAME.desktop"

# =============================
# Ícone (com fallback)
# =============================
if [ -f "$PROJECT_ROOT/src/assets/icon.svg" ]; then
    cp "$PROJECT_ROOT/src/assets/icon.svg" "$TEMP_DIR/usr/share/icons/hicolor/scalable/apps/$APP_NAME.svg"
else
    cat > "$TEMP_DIR/usr/share/icons/hicolor/scalable/apps/$APP_NAME.svg" << 'SVGEOF'
<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 100 100">
  <rect width="100" height="100" fill="#3498db"/>
  <text x="50" y="55" font-family="Arial" font-size="40" fill="white" text-anchor="middle">VPN</text>
</svg>
SVGEOF
fi
chmod 644 "$TEMP_DIR/usr/share/icons/hicolor/scalable/apps/$APP_NAME.svg"

# =============================
# Criar pacote .deb
# =============================
echo "Criando pacote .deb..."
dpkg-deb --build --root-owner-group "$TEMP_DIR" "$BUILD_DIR/$DEBIAN_PACKAGE_NAME"

echo ""
echo "✅ Pacote criado: $BUILD_DIR/$DEBIAN_PACKAGE_NAME"
du -h "$BUILD_DIR/$DEBIAN_PACKAGE_NAME" | awk '{print "Tamanho:", $1}'

# =============================
# Limpeza
# =============================
rm -rf "$TEMP_DIR"
echo ""
echo "Empacotamento concluído com sucesso!"
echo "Para instalar:"
echo "  sudo dpkg -i $BUILD_DIR/$DEBIAN_PACKAGE_NAME"
echo "Para corrigir dependências, se necessário:"
echo "  sudo apt-get install -f"
