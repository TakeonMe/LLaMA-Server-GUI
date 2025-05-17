# Selector y gestión de modelos GGUF
import os
from core.utils import find_models
from gi.repository import Gtk, GObject
import logging
import math

# Creamos un modelo personalizado para almacenar tanto el nombre para mostrar como la ruta real
class ModelItem(GObject.GObject):
    def __init__(self, path, display_name):
        super().__init__()
        self.path = path  # Ruta completa al archivo
        self.display_name = display_name  # Nombre con tamaño para mostrar
    
    def get_path(self):
        return self.path
    
    def get_display_name(self):
        return self.display_name

def get_file_size_gb(file_path):
    """Obtiene el tamaño del archivo en GB con un decimal"""
    size_bytes = os.path.getsize(file_path)
    size_gb = size_bytes / (1024 * 1024 * 1024)  # Convertir bytes a GB
    # Redondear a 1 decimal
    if size_gb < 0.1:
        # Para archivos muy pequeños, mostrar en MB
        size_mb = size_bytes / (1024 * 1024)
        return f"{size_mb:.1f} MB"
    return f"{size_gb:.1f} GB"

# Función para obtener el modelo seleccionado (path completo)
def get_selected_model_path(model_choice, models_dir=None):
    """Obtiene la ruta completa del modelo seleccionado
    
    Args:
        model_choice: El widget de selección de modelos
        models_dir: Directorio de modelos (opcional)
    
    Returns:
        La ruta completa al modelo seleccionado o una cadena vacía si no hay selección
    """
    selected = model_choice.get_selected()
    if selected < 0:
        return ""  # No hay selección
    
    model_list = model_choice.get_model()
    if not model_list or model_list.get_n_items() == 0:
        return ""  # Lista vacía
    
    # Verificar si tenemos rutas almacenadas
    if hasattr(model_choice, "model_paths"):
        # Obtener el nombre para mostrar del modelo seleccionado
        display_name = model_list.get_string(selected)
        if display_name in model_choice.model_paths:
            return model_choice.model_paths[display_name]
    
    # Alternativa: reconstruir la ruta basada en el nombre del modelo
    model_text = model_list.get_string(selected)
    # Si el texto tiene formato "nombre (tamaño)", extraer solo el nombre
    if " (" in model_text:
        model_name = model_text.split(" (")[0]
    else:
        model_name = model_text
    
    # Si no se proporcionó el directorio de modelos, no podemos construir la ruta
    if not models_dir:
        return ""
    
    # La ruta completa es el directorio de modelos + nombre del archivo
    return os.path.join(models_dir, model_name)
    
def update_model_list(entry, model_choice):
    models_dir = entry.get_text()
    if models_dir and os.path.isdir(models_dir):
        models = find_models(models_dir)
        model_store = Gtk.StringList()
        
        # Guardar las rutas completas como un atributo del modelo_choice para uso posterior
        if not hasattr(model_choice, "model_paths"):
            model_choice.model_paths = {}
            
        model_choice.model_paths.clear()
        
        for model in models:
            model_name = os.path.basename(model)
            model_size = get_file_size_gb(model)
            display_name = f"({model_size}) - {model_name}"
            model_store.append(display_name)
            # Guardar la relación entre el nombre mostrado y la ruta real
            model_choice.model_paths[display_name] = model
            
        model_choice.set_model(model_store)
        if model_store.get_n_items() > 0:
            model_choice.set_selected(0)
        logging.getLogger(__name__).info(f"Updated model list with {len(models)} models")
    else:
        model_choice.set_model(Gtk.StringList())
        if hasattr(model_choice, "model_paths"):
            model_choice.model_paths.clear()
        logging.getLogger(__name__).warning("Invalid or empty models directory, cleared model list")
