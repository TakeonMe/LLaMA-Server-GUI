# Lectura y escritura de configuración
import os
import logging
import json

# Guardar la configuración siempre en ~/.llama-server-gui/.llama-server-config.json
CONFIG_FILE = os.path.expanduser("~/.llama-server-gui/.llama-server-config.json")

DEFAULT_CONFIG = {
    "models_dir": "",
    "bin_base": "",
    "ngl": "40",
    "port": "8080",
    "prompt": "",
    "temp": "0.8",
    "top_k": "40",
    "top_p": "0.9",
    "repeat_penalty": "1.1",
    "threads": str(int(os.cpu_count() / 2 or 4)),
    "ctx_size": "4096",
    "max_tokens": "512",
    "language": "en",  # Idioma por defecto: inglés
    "theme": "system"  # Tema por defecto: sistema
}

def save_config(models_dir, bin_base, ngl, port, prompt, temp, top_k, top_p, repeat_penalty, threads, ctx_size, max_tokens, language="es", theme="system"):
    config = {
        "models_dir": models_dir,
        "bin_base": bin_base,
        "ngl": ngl,
        "port": port,
        "prompt": prompt,
        "temp": temp,
        "top_k": top_k,
        "top_p": top_p,
        "repeat_penalty": repeat_penalty,
        "threads": threads,
        "ctx_size": ctx_size,
        "max_tokens": max_tokens,
        "language": language,
        "theme": theme
    }
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        logging.getLogger(__name__).info(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to save configuration to {CONFIG_FILE}: {e}")

def load_config():
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                user_config = json.load(f)
                config.update(user_config)
            logging.getLogger(__name__).info(f"Loaded configuration from {CONFIG_FILE}")
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to load configuration from {CONFIG_FILE}: {e}")
    else:
        logging.getLogger(__name__).info("Using default configuration")
    return config
