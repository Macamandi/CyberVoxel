#!/bin/bash

echo "🍦 INICIANDO INSTALAÇÃO DO CYBERVOXEL..."

# 1. Pega o diretório atual
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "📂 Diretório detectado: $DIR"

# 2. Cria ambiente virtual Python (VENV) se não existir
if [ ! -d "$DIR/venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv "$DIR/venv"
fi

# 3. Instala dependências
echo "⬇️  Instalando bibliotecas (Ursina)..."
"$DIR/venv/bin/pip" install -r "$DIR/requirements.txt"

# 4. Cria o arquivo .desktop para o Menu do Linux
echo "🖥️  Criando atalho no Menu..."
ICON_PATH="$DIR/CyberVoxelLogo.png"

# Conteúdo do atalho
cat > ~/.local/share/applications/CyberVoxel.desktop << EOL
[Desktop Entry]
Version=1.0
Type=Application
Name=CyberVoxel
Comment=Editor de Voxel para Cyberdecks
Exec="$DIR/venv/bin/python" "$DIR/CyberVoxel.py"
Icon=$ICON_PATH
Path=$DIR
Terminal=false
Categories=Graphics;3DGraphics;
StartupNotify=false
EOL

# 5. Permissões finais
chmod +x "$DIR/CyberVoxel.py"
chmod +x ~/.local/share/applications/CyberVoxel.desktop

echo "✅ SUCESSO! CyberVoxel instalado."
echo "👉 Procure por 'CyberVoxel' no seu menu de aplicativos."
