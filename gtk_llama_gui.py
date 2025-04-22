#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gio, Gdk
import subprocess
import os
import glob
import signal
import json
import psutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

CONFIG_FILE = ".llama-server-config.txt"
server_running = False
process = None

def find_models(models_dir):
    models = glob.glob(os.path.join(models_dir, "*.gguf"))
    logger.info(f"Found {len(models)} GGUF models in {models_dir}")
    return models

def save_config(models_dir, bin_base, ngl, port, prompt, temp, top_k, top_p, repeat_penalty, threads):
    try:
        with open(CONFIG_FILE, "w") as f:
            f.write(f"{models_dir}\n{bin_base}\n{ngl}\n{port}\n{prompt}\n{temp}\n{top_k}\n{top_p}\n{repeat_penalty}\n{threads}")
        logger.info(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        logger.error(f"Failed to save configuration to {CONFIG_FILE}: {e}")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                lines = f.readlines()
                if len(lines) >= 10:
                    logger.info(f"Loaded configuration from {CONFIG_FILE}")
                    return [line.strip() for line in lines[:10]]
                else:
                    logger.warning(f"Configuration file {CONFIG_FILE} is incomplete")
        except Exception as e:
            logger.error(f"Failed to load configuration from {CONFIG_FILE}: {e}")
    default_threads = str(os.cpu_count() or 4)
    logger.info("Using default configuration")
    return None, None, None, None, "", "0.8", "40", "0.9", "1.1", default_threads

def check_server_running(port):
    """Verifica si un proceso llama-server está corriendo en el puerto especificado."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.name() == "llama-server" or (proc.cmdline() and "llama-server" in " ".join(proc.cmdline())):
                if f"--port {port}" in " ".join(proc.cmdline()):
                    logger.info(f"Found existing server running on port {port} with PID {proc.pid}")
                    return proc.pid
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    logger.debug(f"No server found running on port {port}")
    return None

def kill_server(pid, window):
    """Intenta matar el proceso del servidor con SIGTERM y luego SIGKILL si es necesario."""
    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
        psutil.Process(pid).wait(timeout=3)
        logger.info("Server stopped successfully")
        return True
    except psutil.TimeoutExpired:
        logger.warning("Server did not terminate with SIGTERM, sending SIGKILL")
        os.killpg(os.getpgid(pid), signal.SIGKILL)
        return True
    except Exception as e:
        logger.error(f"Failed to stop server: {e}")
        show_error(window, f"No se pudo detener el servidor: {e}")
        return False

def set_inputs_sensitive(sensitive, models_dir_entry, bin_dir_entry, model_choice, ngl_entry, port_entry, prompt_entry, temp_entry, top_k_entry, top_p_entry, repeat_penalty_entry, threads_entry):
    """Habilita o deshabilita los campos de entrada y el selector."""
    models_dir_entry.set_sensitive(sensitive)
    bin_dir_entry.set_sensitive(sensitive)
    model_choice.set_sensitive(sensitive)
    ngl_entry.set_sensitive(sensitive)
    port_entry.set_sensitive(sensitive)
    prompt_entry.set_sensitive(sensitive)
    temp_entry.set_sensitive(sensitive)
    top_k_entry.set_sensitive(sensitive)
    top_p_entry.set_sensitive(sensitive)
    repeat_penalty_entry.set_sensitive(sensitive)
    threads_entry.set_sensitive(sensitive)
    logger.debug(f"Input fields sensitivity set to {sensitive}")

def run_server(model_path, ngl, port, bin_dir, button, window, model_choice, models_dir_entry, bin_dir_entry, status_label, prompt_entry, temp_entry, temp, top_k_entry, top_k, top_p_entry, top_p, repeat_penalty_entry, repeat_penalty, threads_entry, threads):
    global process, server_running
    cmd = f"./llama-server -m '{model_path}' -ngl {ngl} --port {port} --temp {temp} --top-k {top_k} --top-p {top_p} --repeat-penalty {repeat_penalty} --threads {threads}"
    logger.info(f"Starting server with command: {cmd}")
    try:
        process = subprocess.Popen(cmd, shell=True, cwd=bin_dir, preexec_fn=os.setsid)
        button.set_label("Detener Servidor")
        button.add_css_class("destructive-action")
        server_running = True
        set_inputs_sensitive(False, models_dir_entry, bin_dir_entry, model_choice, ngl_entry, port_entry, prompt_entry, temp_entry, top_k_entry, top_p_entry, repeat_penalty_entry, threads_entry)

        model_name = os.path.basename(model_path)
        status_label.set_markup(f'El modelo <b>{model_name}</b> está corriendo en el puerto <b>{port}</b> y puedes acceder haciendo click <a href="http://localhost:{port}/">aquí</a>.')
        status_label.set_selectable(True)
        status_label.queue_draw()

        models_dir = models_dir_entry.get_text()
        bin_base = bin_dir_entry.get_text()
        prompt = prompt_entry.get_text()
        temp = temp_entry.get_text()
        top_k = top_k_entry.get_text()
        top_p = top_p_entry.get_text()
        repeat_penalty = repeat_penalty_entry.get_text()
        threads = threads_entry.get_text()
        save_config(models_dir, bin_base, ngl, port, prompt, temp, top_k, top_p, repeat_penalty, threads)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        show_error(window, f"No se pudo iniciar el servidor: {e}")

def stop_server(button, window, model_choice, models_dir_entry, bin_dir_entry, status_label, prompt_entry, temp_entry, top_k_entry, top_p_entry, repeat_penalty_entry, threads_entry):
    global process, server_running
    if process:
        logger.info("Stopping server")
        kill_server(process.pid, window)
        process = None
    button.set_label("Iniciar Servidor")
    button.remove_css_class("destructive-action")  # Eliminar clase destructive-action
    button.add_css_class("suggested-action")      # Restaurar clase suggested-action
    status_label.set_text("Indica las rutas, selecciona el modelo, indica el puerto, el prompt, el número de capas de GPU, el número de hilos, la calidez, top-k, top-p y la penalización de repetición.")
    status_label.set_selectable(False)
    status_label.queue_draw()
    server_running = False
    set_inputs_sensitive(True, models_dir_entry, bin_dir_entry, model_choice, ngl_entry, port_entry, prompt_entry, temp_entry, top_k_entry, top_p_entry, repeat_penalty_entry, threads_entry)
    logger.info("Server stopped and UI reset")

def show_info_dialog(window):
    """Lee el archivo info.json y muestra su contenido en un diálogo."""
    info_path = os.path.join("assets", "info.json")
    try:
        with open(info_path, "r") as f:
            info_data = json.load(f)
        
        # Formatear el contenido del JSON
        message = ""
        for key, value in info_data.items():
            message += f"{key.upper()}:\n"
            message += f"- Descripción: {value['description']}\n"
            message += f"- Recomendado: {value['recommended']}\n\n"

        dialog = Gtk.MessageDialog(
            transient_for=window,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Información de Configuración",
            secondary_text=message,
            use_markup=True
        )
        dialog.set_default_size(600, 400)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()
        logger.info("Displayed info dialog")
    except FileNotFoundError:
        logger.error("Info file assets/info.json not found")
        show_error(window, "No se encontró el archivo assets/info.json")
    except json.JSONDecodeError:
        logger.error("Invalid JSON format in assets/info.json")
        show_error(window, "Error al leer el archivo assets/info.json: Formato JSON inválido")
    except Exception as e:
        logger.error(f"Failed to read info file assets/info.json: {str(e)}")
        show_error(window, f"Error al leer el archivo assets/info.json: {str(e)}")

def run_server_wrapper(button, window, model_choice, models_dir_entry, bin_dir_entry, status_label, prompt_entry, temp_entry, top_k_entry, top_p_entry, repeat_penalty_entry, threads_entry):
    global server_running
    if server_running:
        stop_server(button, window, model_choice, models_dir_entry, bin_dir_entry, status_label, prompt_entry, temp_entry, top_k_entry, top_p_entry, repeat_penalty_entry, threads_entry)
    else:
        models_dir = models_dir_entry.get_text()
        bin_base = bin_dir_entry.get_text()
        ngl = ngl_entry.get_text()
        port = port_entry.get_text()
        prompt = prompt_entry.get_text()
        temp = temp_entry.get_text()
        top_k = top_k_entry.get_text()
        top_p = top_p_entry.get_text()
        repeat_penalty = repeat_penalty_entry.get_text()
        threads = threads_entry.get_text()

        if not models_dir:
            logger.error("Models directory path is required")
            show_error(window, "La ruta a modelos GGUF es obligatoria.")
            return
        if not bin_base:
            logger.error("llama.cpp base path is required")
            show_error(window, "La ruta base a llama.cpp es obligatoria.")
            return
        if not ngl:
            logger.error("GPU layers (-ngl) is required")
            show_error(window, "El número de capas GPU (-ngl) es obligatorio.")
            return
        if not port:
            logger.error("Port is required")
            show_error(window, "El puerto es obligatorio.")
            return
        if not prompt:
            logger.error("Prompt is required")
            show_error(window, "El prompt es obligatorio.")
            return
        if not temp:
            logger.error("Temperature is required")
            show_error(window, "La calidez/temperatura es obligatoria.")
            return
        if not top_k:
            logger.error("Top-k is required")
            show_error(window, "El valor de top-k es obligatorio.")
            return
        if not top_p:
            logger.error("Top-p is required")
            show_error(window, "El valor de top-p es obligatorio.")
            return
        if not repeat_penalty:
            logger.error("Repeat penalty is required")
            show_error(window, "La penalización de repetición es obligatoria.")
            return
        if not threads:
            logger.error("Number of threads is required")
            show_error(window, "El número de hilos es obligatorio.")
            return

        try:
            float(temp)
            if float(temp) < 0.1 or float(temp) > 2.0:
                logger.error("Temperature must be between 0.1 and 2.0")
                show_error(window, "La calidez/temperatura debe estar entre 0.1 y 2.0.")
                return
        except ValueError:
            logger.error("Temperature must be a valid number")
            show_error(window, "La calidez/temperatura debe ser un número válido (ej. 0.8).")
            return

        try:
            int(top_k)
            if int(top_k) < 1 or int(top_k) > 100:
                logger.error("Top-k must be between 1 and 100")
                show_error(window, "El valor de top-k debe estar entre 1 y 100.")
                return
        except ValueError:
            logger.error("Top-k must be a valid integer")
            show_error(window, "El valor de top-k debe ser un número entero válido (ej. 40).")
            return

        try:
            float(top_p)
            if float(top_p) < 0.0 or float(top_p) > 1.0:
                logger.error("Top-p must be between 0.0 and 1.0")
                show_error(window, "El valor de top-p debe estar entre 0.0 y 1.0.")
                return
        except ValueError:
            logger.error("Top-p must be a valid number")
            show_error(window, "El valor de top-p debe ser un número válido (ej. 0.9).")
            return

        try:
            float(repeat_penalty)
            if float(repeat_penalty) < 1.0 or float(repeat_penalty) > 2.0:
                logger.error("Repeat penalty must be between 1.0 and 2.0")
                show_error(window, "La penalización de repetición debe estar entre 1.0 y 2.0.")
                return
        except ValueError:
            logger.error("Repeat penalty must be a valid number")
            show_error(window, "La penalización de repetición debe ser un número válido (ej. 1.1).")
            return

        try:
            int(threads)
            max_threads = os.cpu_count() or 4
            if int(threads) < 1 or int(threads) > max_threads * 2:
                logger.error(f"Threads must be between 1 and {max_threads * 2}")
                show_error(window, f"El número de hilos debe estar entre 1 y {max_threads * 2}.")
                return
        except ValueError:
            logger.error("Threads must be a valid integer")
            show_error(window, "El número de hilos debe ser un número entero válido (ej. 4).")
            return

        existing_pid = check_server_running(port)
        if existing_pid:
            logger.warning(f"Server already running on port {port} with PID {existing_pid}")
            dialog = Gtk.MessageDialog(
                transient_for=window,
                message_type=Gtk.MessageType.WARNING,
                text=f"Un servidor llama-server ya está corriendo en el puerto {port} (PID: {existing_pid}). ¿Qué deseas hacer?",
                buttons=Gtk.ButtonsType.NONE
            )
            dialog.add_buttons(
                "Cancelar", Gtk.ResponseType.CANCEL,
                "Detener", Gtk.ResponseType.NO,
                "Detener y Continuar", Gtk.ResponseType.YES
            )

            def on_dialog_response(dialog, response_id):
                dialog.destroy()
                if response_id == Gtk.ResponseType.YES:
                    if kill_server(existing_pid, window):
                        models = find_models(models_dir)
                        if not models:
                            logger.error(f"No GGUF models found in {models_dir}")
                            show_error(window, f"No se encontraron modelos GGUF en {models_dir}.")
                            return
                        model_path = models[model_choice.get_selected()]
                        bin_dir = os.path.join(bin_base, "build", "bin")
                        if not os.path.exists(bin_dir):
                            logger.error(f"Directory {bin_dir} does not exist")
                            show_error(window, f"La ruta {bin_dir} no existe.")
                            return
                        run_server(model_path, ngl, port, bin_dir, button, window, model_choice, models_dir_entry, bin_dir_entry, status_label, prompt_entry, temp_entry, temp, top_k_entry, top_k, top_p_entry, top_p, repeat_penalty_entry, repeat_penalty, threads_entry, threads)
                elif response_id == Gtk.ResponseType.NO:
                    kill_server(existing_pid, window)

            dialog.connect("response", on_dialog_response)
            dialog.present()
            return

        models = find_models(models_dir)
        if not models:
            logger.error(f"No GGUF models found in {models_dir}")
            show_error(window, f"No se encontraron modelos GGUF en {models_dir}.")
            return

        model_path = models[model_choice.get_selected()]
        bin_dir = os.path.join(bin_base, "build", "bin")
        if not os.path.exists(bin_dir):
            logger.error(f"Directory {bin_dir} does not exist")
            show_error(window, f"La ruta {bin_dir} no existe.")
            return

        run_server(model_path, ngl, port, bin_dir, button, window, model_choice, models_dir_entry, bin_dir_entry, status_label, prompt_entry, temp_entry, temp, top_k_entry, top_k, top_p_entry, top_p, repeat_penalty_entry, repeat_penalty, threads_entry, threads)

def show_error(window, message):
    dialog = Gtk.MessageDialog(
        transient_for=window,
        buttons=Gtk.ButtonsType.OK,
        message_type=Gtk.MessageType.ERROR,
        text=message
    )
    dialog.connect("response", lambda d, r: d.destroy())
    dialog.present()
    logger.error(f"Error displayed: {message}")

def on_link_clicked(label, uri):
    logger.info(f"Link clicked: {uri}")
    try:
        Gio.AppInfo.launch_default_for_uri(uri, None)
        return True
    except Exception as e:
        logger.error(f"Failed to open link {uri}: {e}")
        return False

def on_window_destroy(window, button, model_choice, models_dir_entry, bin_dir_entry, status_label, prompt_entry, temp_entry, top_k_entry, top_p_entry, repeat_penalty_entry, threads_entry):
    logger.info("Window destroyed, stopping server")
    stop_server(button, window, model_choice, models_dir_entry, bin_dir_entry, status_label, prompt_entry, temp_entry, top_k_entry, top_p_entry, repeat_penalty_entry, threads_entry)

def update_model_list(entry, model_choice):
    models_dir = entry.get_text()
    if models_dir and os.path.isdir(models_dir):
        models = find_models(models_dir)
        model_store = Gtk.StringList()
        for model in models:
            model_store.append(os.path.basename(model))
        model_choice.set_model(model_store)
        model_choice.set_selected(0)
        logger.info(f"Updated model list with {len(models)} models")
    else:
        model_choice.set_model(Gtk.StringList())
        logger.warning("Invalid or empty models directory, cleared model list")

def on_activate(app):
    logger.info("Application activated")
    window = Gtk.ApplicationWindow(application=app)
    window.set_title("Servidor LLaMA")
    window.set_default_size(450, 450)
    window.set_decorated(True)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    box.set_margin_top(10)
    box.set_margin_bottom(10)
    box.set_margin_start(10)
    box.set_margin_end(10)

    global models_dir_entry, bin_dir_entry, model_choice, ngl_entry, port_entry, prompt_entry, temp_entry, top_k_entry, top_p_entry, repeat_penalty_entry, threads_entry
    models_dir_entry = Gtk.Entry()
    models_dir_entry.set_placeholder_text("Ruta a modelos GGUF (ej. /media/user/models)")
    bin_dir_entry = Gtk.Entry()
    bin_dir_entry.set_placeholder_text("Ruta base a llama.cpp (ej. /media/user/llama.cpp)")

    saved_models_dir, saved_bin_base, saved_ngl, saved_port, saved_prompt, saved_temp, saved_top_k, saved_top_p, saved_repeat_penalty, saved_threads = load_config()
    if saved_models_dir:
        models_dir_entry.set_text(saved_models_dir)
    if saved_bin_base:
        bin_dir_entry.set_text(saved_bin_base)

    models_dir = models_dir_entry.get_text() or os.path.dirname(os.path.realpath(__file__))
    models = find_models(models_dir)
    model_store = Gtk.StringList()
    for model in models:
        model_store.append(os.path.basename(model))
    model_choice = Gtk.DropDown(model=model_store)
    model_choice.set_selected(0)

    models_dir_entry.connect("changed", update_model_list, model_choice)

    port_entry = Gtk.Entry()
    port_entry.set_placeholder_text("Puerto (ej. 8080)")
    if saved_port:
        port_entry.set_text(saved_port)

    prompt_entry = Gtk.Entry()
    prompt_entry.set_placeholder_text("Prompt inicial (ej. I always speak in Spanish)")
    if saved_prompt:
        prompt_entry.set_text(saved_prompt)

    ngl_entry = Gtk.Entry()
    ngl_entry.set_placeholder_text("Capas GPU (-ngl)")
    if saved_ngl:
        ngl_entry.set_text(saved_ngl)

    threads_entry = Gtk.Entry()
    threads_entry.set_placeholder_text("Número de hilos (ej. 4)")
    if saved_threads:
        threads_entry.set_text(saved_threads)
    else:
        threads_entry.set_text(str(os.cpu_count() or 4))

    temp_entry = Gtk.Entry()
    temp_entry.set_placeholder_text("Calidez/Temperatura (ej. 0.8)")
    if saved_temp:
        temp_entry.set_text(saved_temp)
    else:
        temp_entry.set_text("0.8")

    top_k_entry = Gtk.Entry()
    top_k_entry.set_placeholder_text("Top-k (ej. 40)")
    if saved_top_k:
        top_k_entry.set_text(saved_top_k)
    else:
        top_k_entry.set_text("40")

    top_p_entry = Gtk.Entry()
    top_p_entry.set_placeholder_text("Top-p (ej. 0.9)")
    if saved_top_p:
        top_p_entry.set_text(saved_top_p)
    else:
        top_p_entry.set_text("0.9")

    repeat_penalty_entry = Gtk.Entry()
    repeat_penalty_entry.set_placeholder_text("Penalización de repetición (ej. 1.1)")
    if saved_repeat_penalty:
        repeat_penalty_entry.set_text(saved_repeat_penalty)
    else:
        repeat_penalty_entry.set_text("1.1")

    # Crear etiquetas para cada campo
    models_dir_label = Gtk.Label(label="Ruta a modelos GGUF:")
    models_dir_label.set_xalign(0.0)
    models_dir_label.set_margin_bottom(2)

    bin_dir_label = Gtk.Label(label="Ruta base a llama.cpp:")
    bin_dir_label.set_xalign(0.0)
    bin_dir_label.set_margin_bottom(2)

    model_choice_label = Gtk.Label(label="Modelo:")
    model_choice_label.set_xalign(0.0)
    model_choice_label.set_margin_bottom(2)

    port_label = Gtk.Label(label="Puerto:")
    port_label.set_xalign(0.0)
    port_label.set_margin_bottom(2)

    prompt_label = Gtk.Label(label="Prompt inicial:")
    prompt_label.set_xalign(0.0)
    prompt_label.set_margin_bottom(2)

    ngl_label = Gtk.Label(label="Capas GPU (-ngl):")
    ngl_label.set_xalign(0.0)
    ngl_label.set_margin_bottom(2)

    threads_label = Gtk.Label(label="Número de hilos:")
    threads_label.set_xalign(0.0)
    threads_label.set_margin_bottom(2)

    temp_label = Gtk.Label(label="Calidez/Temperatura:")
    temp_label.set_xalign(0.0)
    temp_label.set_margin_bottom(2)

    top_k_label = Gtk.Label(label="Top-k:")
    top_k_label.set_xalign(0.0)
    top_k_label.set_margin_bottom(2)

    top_p_label = Gtk.Label(label="Top-p:")
    top_p_label.set_xalign(0.0)
    top_p_label.set_margin_bottom(2)

    repeat_penalty_label = Gtk.Label(label="Penalización de repetición:")
    repeat_penalty_label.set_xalign(0.0)
    repeat_penalty_label.set_margin_bottom(2)

    button = Gtk.Button(label="Iniciar Servidor")
    button.set_margin_top(10)
    button.set_margin_bottom(10)
    button.add_css_class("suggested-action")
    button.connect("clicked", lambda b: run_server_wrapper(b, window, model_choice, models_dir_entry, bin_dir_entry, status_label, prompt_entry, temp_entry, top_k_entry, top_p_entry, repeat_penalty_entry, threads_entry))

    info_button = Gtk.Button(label="Mostrar Información")
    info_button.set_margin_top(0)
    info_button.set_margin_bottom(10)
    info_button.add_css_class("accent")
    info_button.connect("clicked", lambda b: show_info_dialog(window))

    status_label = Gtk.Label(label="Indica las rutas, selecciona el modelo, indica el puerto, el prompt, el número de capas de GPU, el número de hilos, la calidez, top-k, top-p y la penalización de repetición.")
    status_label.set_wrap(True)
    status_label.set_use_markup(True)
    status_label.connect("activate-link", on_link_clicked)

    # Añadir etiquetas y campos al box
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    box.append(models_dir_label)
    box.append(models_dir_entry)
    box.append(bin_dir_label)
    box.append(bin_dir_entry)
    box.append(model_choice_label)
    box.append(model_choice)
    box.append(port_label)
    box.append(port_entry)
    box.append(prompt_label)
    box.append(prompt_entry)
    box.append(ngl_label)
    box.append(ngl_entry)
    box.append(threads_label)
    box.append(threads_entry)
    box.append(temp_label)
    box.append(temp_entry)
    box.append(top_k_label)
    box.append(top_k_entry)
    box.append(top_p_label)
    box.append(top_p_entry)
    box.append(repeat_penalty_label)
    box.append(repeat_penalty_entry)
    box.append(button)
    box.append(info_button)
    box.append(status_label)
    box.set_margin_top(12)
    box.set_margin_bottom(24)
    box.set_margin_start(12)
    box.set_margin_end(12)

    window.set_child(box)
    window.connect("destroy", on_window_destroy, button, model_choice, models_dir_entry, bin_dir_entry, status_label, prompt_entry, temp_entry, top_k_entry, top_p_entry, repeat_penalty_entry, threads_entry)
    window.set_visible(True)

def main():
    logger.info("Starting LLaMA Server GUI application")
    app = Gtk.Application(application_id="com.llama.llamaserver")
    app.connect("activate", on_activate)
    app.run()

if __name__ == "__main__":
    main()
