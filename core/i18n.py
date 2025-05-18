# Sistema de internacionalización para LLaMA Server GUI
import os
import json
import logging

# Ruta al archivo de traducciones
LANGUAGE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "translations.json")

# Idiomas disponibles
LANGUAGES = ["es", "en", "pt", "it", "de", "zh", "ja"]

# Idioma por defecto
DEFAULT_LANGUAGE = "en"

# Variable global para almacenar el idioma actual
current_language = DEFAULT_LANGUAGE

# Diccionario para almacenar las traducciones
translations = {}


def load_translations():
    """Carga las traducciones desde el archivo JSON"""
    global translations
    try:
        if os.path.exists(LANGUAGE_FILE):
            with open(LANGUAGE_FILE, "r", encoding="utf-8") as f:
                translations = json.load(f)
            logging.getLogger(__name__).info(f"Traducciones cargadas desde {LANGUAGE_FILE}")
        else:
            logging.getLogger(__name__).warning(f"Archivo de traducciones no encontrado en {LANGUAGE_FILE}")
            translations = {}
    except Exception as e:
        logging.getLogger(__name__).error(f"Error al cargar traducciones: {e}")
        translations = {}


def get_text(key, language=None):
    """Obtiene el texto traducido para la clave dada
    
    Args:
        key: Clave del texto a traducir
        language: Idioma específico (si es None, usa el idioma actual)
    
    Returns:
        El texto traducido o la clave original si no se encuentra traducción
    """
    lang = language or current_language
    
    # Si no hay traducciones cargadas, intentar cargarlas
    if not translations:
        load_translations()
    
    # Si la clave no existe o el idioma no está disponible, devolver la clave original
    if key not in translations or lang not in translations[key]:
        return key
    
    return translations[key][lang]


def set_language(language):
    """Establece el idioma actual
    
    Args:
        language: Código de idioma ("es" o "en")
    
    Returns:
        True si el idioma se cambió correctamente, False en caso contrario
    """
    global current_language
    if language in LANGUAGES:
        current_language = language
        logging.getLogger(__name__).info(f"Idioma cambiado a: {language}")
        return True
    else:
        logging.getLogger(__name__).warning(f"Idioma no soportado: {language}")
        return False


def get_current_language():
    """Obtiene el idioma actual
    
    Returns:
        El código del idioma actual
    """
    return current_language


# Cargar traducciones al importar el módulo
load_translations()
