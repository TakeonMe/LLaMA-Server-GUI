#!/bin/bash
# Comprobación de versión mínima de Python (3.8)
PYTHON_VERSION=$(/usr/bin/python3 -c 'import sys; print("{}.{}".format(sys.version_info.major, sys.version_info.minor))')
REQUIRED_VERSION="3.8"
if [[ $(echo -e "$PYTHON_VERSION\n$REQUIRED_VERSION" | sort -V | head -n1) != "$REQUIRED_VERSION" ]]; then
    echo "[ERROR] Se requiere Python 3.8 o superior en /usr/bin/python3. Versión detectada: $PYTHON_VERSION"
    exit 1
fi

# Instalador para LLaMA Server GUI (instalación mínima en ~/.llama-server-gui)
# Comentarios en español

set -e

APPDIR="$HOME/.llama-server-gui"
DESKTOP_FILE="$HOME/.local/share/applications/llama-server-gui.desktop"

# 1. Borrar instalación previa si existe
if [ -d "$APPDIR" ]; then
    echo "[INFO] Eliminando instalación anterior en $APPDIR..."
    rm -rf "$APPDIR"
fi

# 2. Crear directorio de la aplicación
mkdir -p "$APPDIR"

# 3. Copiar solo los archivos y carpetas necesarios
cp gtk_llama_gui.py requirements.txt "$APPDIR/"
cp -r core "$APPDIR/"
cp -r gui "$APPDIR/"
mkdir -p "$APPDIR/assets"
cp assets/llama-server-gui.svg "$APPDIR/assets/"
cp assets/translations.json "$APPDIR/assets/"

# 4. Crear entorno virtual dentro del directorio oculto
cd "$APPDIR"
if [ ! -d "venv" ]; then
    echo "[INFO] Creando entorno virtual Python..."
    python3 -m venv venv
fi

# 5. Activar entorno virtual e instalar dependencias
source venv/bin/activate
if [ -f requirements.txt ]; then
    echo "[INFO] Instalando dependencias de Python..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# 6. Instalar dependencias del sistema (GTK y utilidades)
echo "[INFO] Instalando dependencias del sistema (requiere sudo)..."
sudo apt-get update
sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-gtksource-4

# 7. Crear lanzador de escritorio en local/share/applications
cat > "$DESKTOP_FILE" <<EOL
[Desktop Entry]
Type=Application
Name=LLaMA Server GUI
# Usar el intérprete global de Python en vez del del entorno virtual para evitar problemas de ejecución
Exec=/usr/bin/python3 $APPDIR/gtk_llama_gui.py
Icon=$APPDIR/assets/llama-server-gui.svg
Terminal=false
Categories=Utility;Development;
StartupWMClass=com.llama.llamaserver
EOL
chmod +x "$DESKTOP_FILE"

echo "[OK] Instalación completada. Puedes buscar 'LLaMA Server GUI' en tu menú de aplicaciones."

# Instalador para LLaMA Server GUI
# Comentarios en español

set -e

# 1. Crear entorno virtual (opcional, recomendado)
if [ ! -d "venv" ]; then
    echo "[INFO] Creando entorno virtual Python..."
    python3 -m venv venv
fi

# 2. Activar entorno virtual
source venv/bin/activate

# 3. Instalar dependencias Python
if [ -f requirements.txt ]; then
    echo "[INFO] Instalando dependencias de Python..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# 4. Instalar dependencias del sistema (GTK y utilidades)
echo "[INFO] Instalando dependencias del sistema (requiere sudo)..."
sudo apt-get update
sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-gtksource-4

# 5. Crear lanzador de escritorio
cat > llama-server-gui.desktop <<EOL
[Desktop Entry]
Type=Application
Name=LLaMA Server GUI
Exec=$(pwd)/venv/bin/python3 $(pwd)/gtk_llama_gui.py
Icon=$(pwd)/assets/llama-server-gui.svg
Terminal=false
Categories=Utility;Development;
StartupWMClass=com.llama.llamaserver
EOL
chmod +x llama-server-gui.desktop

# 6. Copiar lanzador al escritorio del usuario
cp llama-server-gui.desktop "$HOME/Escritorio/"

# 7. Mensaje final
echo "[OK] Instalación completada. Puedes ejecutar la aplicación desde el lanzador en tu escritorio."
