# Funciones auxiliares (por ejemplo, find_models)
import os
import glob
import logging

def find_models(models_dir):
    models = glob.glob(os.path.join(models_dir, "*.gguf"))
    models.sort()
    logging.getLogger(__name__).info(f"Found {len(models)} GGUF models in {models_dir}")
    return models

