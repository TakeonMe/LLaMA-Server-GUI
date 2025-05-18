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

> ⚠️ **Advertencia:** Esta aplicación requiere que `/usr/bin/python3` sea Python 3.8 o superior. Comprueba tu versión con:
> ```bash
> /usr/bin/python3 --version
> ```
> Si tienes una versión más antigua, actualiza tu sistema antes de instalar.


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

> ⚠️ **Warning:** This application requires `/usr/bin/python3` to be Python 3.8 or newer. Check your version with:
> ```bash
> /usr/bin/python3 --version
> ```
> If you have an older version, please update your system before installing.


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

---

### Instalación automática (install.sh)

Puedes instalar la aplicación y crear un acceso directo en tu escritorio fácilmente ejecutando el script de instalación:

```bash
bash install.sh
```

Esto realizará los siguientes pasos:
- Crea un entorno virtual Python (si no existe)
- Instala todas las dependencias necesarias
- Crea un lanzador de escritorio con icono
- Copia el lanzador a tu escritorio

Al finalizar, verás un acceso directo para iniciar la aplicación con doble clic.

---

### Automatic installation (install.sh)

You can install the application and create a desktop shortcut easily by running the installation script:

```bash
bash install.sh
```

This will:
- Create a Python virtual environment (if it does not exist)
- Install all required dependencies
- Create a desktop launcher with icon
- Copy the launcher to your desktop

At the end, you will have a shortcut to start the application with a double click.