# Gestión del servidor LLaMA
import os
import signal
import logging
import psutil
import subprocess
import time

def check_server_running(port):
    """Verifica si un proceso llama-server está corriendo en el puerto especificado."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.name() == "llama-server" or (proc.cmdline() and "llama-server" in " ".join(proc.cmdline())):
                if f"--port {port}" in " ".join(proc.cmdline()):
                    logging.getLogger(__name__).info(f"Found existing server running on port {port} with PID {proc.pid}")
                    return proc.pid
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    logging.getLogger(__name__).debug(f"No server found running on port {port}")
    return None

def kill_server(pid):
    """Intenta matar el proceso del servidor con SIGTERM y luego SIGKILL si es necesario."""
    try:
        # Método simple: Usar psutil directamente
        logging.getLogger(__name__).info(f"Intentando terminar proceso con PID {pid}")
        proc = psutil.Process(pid)
        proc.terminate()
        
        # Esperar a que termine
        try:
            proc.wait(timeout=2)
            logging.getLogger(__name__).info("Servidor detenido correctamente")
            return True
        except psutil.TimeoutExpired:
            logging.getLogger(__name__).warning("El servidor no terminó con terminate(), enviando kill()")
            proc.kill()
            return True
    except Exception as e:
        logging.getLogger(__name__).error(f"Error al detener el servidor: {e}")
        # Intentar con os.kill como último recurso
        try:
            os.kill(pid, signal.SIGKILL)
            logging.getLogger(__name__).info("Servidor terminado con SIGKILL")
            return True
        except Exception as e2:
            logging.getLogger(__name__).error(f"No se pudo detener el servidor: {e2}")
            return False

def run_server(cmd, bin_dir):
    try:
        process = subprocess.Popen(cmd, shell=True, cwd=bin_dir, preexec_fn=os.setsid)
        logging.getLogger(__name__).info(f"Server started with PID {process.pid}")
        return process
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to start server: {e}")
        return None
