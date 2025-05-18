# LLaMA-Server-GUI

Interfaz gráfica en GTK para gestionar servidores LLaMA en Linux, con soporte para modelos GGUF.

## Captura de pantalla
Aquí puedes ver cómo se ve la interfaz de LLaMA Server GUI al iniciarla:

<div align="center">
  <img src="assets/screenshot.gif" alt="Captura de pantalla de LLaMA Server GUI">
</div>

## Requisitos y dependencias / Requirements and dependencies

### Español

#### Paquetes del sistema (Ubuntu/Debian)
Antes de instalar las dependencias de Python, asegúrate de tener instalados los siguientes paquetes del sistema:

```bash
sudo apt update
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 libgirepository1.0-dev libcairo2-dev
```

#### Dependencias de Python
Se recomienda usar un entorno virtual para aislar las dependencias del proyecto:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

El archivo `requirements.txt` contiene:
```
psutil
```

### English

#### System packages (Ubuntu/Debian)
Before installing Python dependencies, make sure you have the following system packages installed:

```bash
sudo apt update
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 libgirepository1.0-dev libcairo2-dev
```

#### Python dependencies
It is recommended to use a virtual environment to isolate project dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

The `requirements.txt` file contains:
```
psutil
```

## Ejecución / Running

### Español
Con las dependencias instaladas y el entorno virtual activado, ejecuta la aplicación con:

```bash
python3 gtk_llama_gui.py
```

### English
With all dependencies installed and the virtual environment activated, run the application with:

```bash
python3 gtk_llama_gui.py
```