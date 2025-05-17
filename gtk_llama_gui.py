#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, Gdk
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