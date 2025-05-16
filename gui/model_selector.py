# Selector y gestión de modelos GGUF
import os
from core.utils import find_models
from gi.repository import Gtk
import logging

def update_model_list(entry, model_choice):
    models_dir = entry.get_text()
    if models_dir and os.path.isdir(models_dir):
        models = find_models(models_dir)
        model_store = Gtk.StringList()
        for model in models:
            model_store.append(os.path.basename(model))
        model_choice.set_model(model_store)
        model_choice.set_selected(0)
        logging.getLogger(__name__).info(f"Updated model list with {len(models)} models")
    else:
        model_choice.set_model(Gtk.StringList())
        logging.getLogger(__name__).warning("Invalid or empty models directory, cleared model list")
