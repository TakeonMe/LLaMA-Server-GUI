# Diálogos personalizados (errores, info, etc.)
from gi.repository import Gtk
import logging

def show_error(window, message):
    dialog = Gtk.MessageDialog(
        transient_for=window,
        modal=True,
        message_type=Gtk.MessageType.ERROR,
        buttons=Gtk.ButtonsType.OK,
        text=f"Error: {message}",  # Incluir todo en el texto principal
    )
    dialog.connect("response", lambda d, r: d.destroy())
    dialog.present()
    logging.getLogger(__name__).error(message)

def show_info_dialog(window, title, message):
    dialog = Gtk.MessageDialog(
        transient_for=window,
        modal=True,
        message_type=Gtk.MessageType.INFO,
        buttons=Gtk.ButtonsType.OK,
        text=f"{title}\n\n{message}",  # Incluir título y mensaje separados por saltos de línea
    )
    dialog.connect("response", lambda d, r: d.destroy())
    dialog.present()
    logging.getLogger(__name__).info(f"{title}: {message}")
