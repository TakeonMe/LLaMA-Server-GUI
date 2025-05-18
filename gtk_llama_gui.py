#!/usr/bin/env python3
# Comprobación de dependencias de sistema para PyGObject/GTK
try:
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Gdk', '4.0')
    from gi.repository import Gtk, Gdk
except (ImportError, NameError) as e:
    print("""
[ERROR] No se encontró PyGObject (gi) ni las bibliotecas de GTK necesarias.

Por favor, instala los siguientes paquetes del sistema antes de ejecutar esta aplicación:

    sudo apt update
    sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 libgirepository1.0-dev libcairo2-dev

Luego, vuelve a ejecutar la aplicación dentro de tu entorno virtual si lo usas.
""")
    exit(1)

from gui.main_window import create_main_window
import logging
logger = logging.getLogger(__name__)

def on_activate(app):
    # Crear la ventana principal
    window = create_main_window(app)
    
    # Mostrar la ventana
    window.present()

def main():
    logger.info("Starting LLaMA Server GUI application")
    app = Gtk.Application(application_id="com.llama.llamaserver")
    app.connect("activate", on_activate)
    app.run()

if __name__ == "__main__":
    main()