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

CONFIG_FILE = ".llama-server-config.txt"
server_running = False
process = None

def find_models(models_dir):
    return glob.glob(os.path.join(models_dir, "*.gguf"))

def save_config(models_dir, bin_base, ngl, port, prompt):
    with open(CONFIG_FILE, "w") as f:
        f.write(f"{models_dir}\n{bin_base}\n{ngl}\n{port}\n{prompt}")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            lines = f.readlines()
            if len(lines) >= 4:
                return [line.strip() for line in lines[:4]] + [lines[4].strip() if len(lines) > 4 else ""]
    return None, None, None, None, ""

def check_server_running(port):
    """Verifica si un proceso llama-server está corriendo en el puerto especificado."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.name() == "llama-server" or (proc.cmdline() and "llama-server" in " ".join(proc.cmdline())):
                if f"--port {port}" in " ".join(proc.cmdline()):
                    return proc.pid
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def kill_server(pid, window):
    """Intenta matar el proceso del servidor con SIGTERM y luego SIGKILL si es necesario."""
    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
        psutil.Process(pid).wait(timeout=3)
        print("Servidor detenido correctamente")
        return True
    except psutil.TimeoutExpired:
        print("El proceso no terminó con SIGTERM, enviando SIGKILL")
        os.killpg(os.getpgid(pid), signal.SIGKILL)
        return True
    except Exception as e:
        print(f"Error al detener el servidor: {e}")
        show_error(window, f"No se pudo detener el servidor: {e}")
        return False

def set_inputs_sensitive(sensitive, models_dir_entry, bin_dir_entry, model_choice, ngl_entry, port_entry, prompt_entry):
    """Habilita o deshabilita los campos de entrada y el selector."""
    models_dir_entry.set_sensitive(sensitive)
    bin_dir_entry.set_sensitive(sensitive)
    model_choice.set_sensitive(sensitive)
    ngl_entry.set_sensitive(sensitive)
    port_entry.set_sensitive(sensitive)
    prompt_entry.set_sensitive(sensitive)

def run_server(model_path, ngl, port, bin_dir, button, window, model_choice, models_dir_entry, bin_dir_entry, status_label, prompt_entry):
    global process, server_running
    cmd = f"./llama-server -m '{model_path}' -ngl {ngl} --port {port}"
    process = subprocess.Popen(cmd, shell=True, cwd=bin_dir, preexec_fn=os.setsid)

    button.set_label("Detener Servidor")
    server_running = True
    set_inputs_sensitive(False, models_dir_entry, bin_dir_entry, model_choice, ngl_entry, port_entry, prompt_entry)

    model_name = os.path.basename(model_path)
    status_label.set_markup(f'El modelo <b>{model_name}</b> está corriendo en el puerto <b>{port}</b> y puedes acceder haciendo click <a href="http://localhost:{port}/">aquí</a>.')
    status_label.set_selectable(True)
    status_label.queue_draw()

    models_dir = models_dir_entry.get_text()
    bin_base = bin_dir_entry.get_text()
    prompt = prompt_entry.get_text()
    save_config(models_dir, bin_base, ngl, port, prompt)

def stop_server(button, window, model_choice, models_dir_entry, bin_dir_entry, status_label, prompt_entry):
    global process, server_running
    if process:
        kill_server(process.pid, window)
        process = None
    button.set_label("Iniciar Servidor")
    status_label.set_text("Indica las rutas, selecciona el modelo, indica el número de capas de GPU, el puerto y el prompt.")
    status_label.set_selectable(False)
    status_label.queue_draw()
    server_running = False
    set_inputs_sensitive(True, models_dir_entry, bin_dir_entry, model_choice, ngl_entry, port_entry, prompt_entry)

def run_server_wrapper(button, window, model_choice, models_dir_entry, bin_dir_entry, status_label, prompt_entry):
    global server_running
    if server_running:
        stop_server(button, window, model_choice, models_dir_entry, bin_dir_entry, status_label, prompt_entry)
    else:
        models_dir = models_dir_entry.get_text()
        bin_base = bin_dir_entry.get_text()
        ngl = ngl_entry.get_text()
        port = port_entry.get_text()
        prompt = prompt_entry.get_text()

        if not models_dir:
            show_error(window, "La ruta a modelos GGUF es obligatoria.")
            return
        if not bin_base:
            show_error(window, "La ruta base a llama.cpp es obligatoria.")
            return
        if not ngl:
            show_error(window, "El número de capas GPU (-ngl) es obligatorio.")
            return
        if not port:
            show_error(window, "El puerto es obligatorio.")
            return
        if not prompt:
            show_error(window, "El prompt es obligatorio.")
            return

        # Verificar si ya hay un servidor corriendo en el puerto
        existing_pid = check_server_running(port)
        if existing_pid:
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
                    # Detener el servidor y continuar
                    if kill_server(existing_pid, window):
                        models = find_models(models_dir)
                        if not models:
                            show_error(window, f"No se encontraron modelos GGUF en {models_dir}.")
                            return
                        model_path = models[model_choice.get_selected()]
                        bin_dir = os.path.join(bin_base, "build", "bin")
                        if not os.path.exists(bin_dir):
                            show_error(window, f"La ruta {bin_dir} no existe.")
                            return
                        run_server(model_path, ngl, port, bin_dir, button, window, model_choice, models_dir_entry, bin_dir_entry, status_label, prompt_entry)
                elif response_id == Gtk.ResponseType.NO:
                    # Detener el servidor y no hacer nada más
                    kill_server(existing_pid, window)

            dialog.connect("response", on_dialog_response)
            dialog.present()
            return

        models = find_models(models_dir)
        if not models:
            show_error(window, f"No se encontraron modelos GGUF en {models_dir}.")
            return

        model_path = models[model_choice.get_selected()]
        bin_dir = os.path.join(bin_base, "build", "bin")
        if not os.path.exists(bin_dir):
            show_error(window, f"La ruta {bin_dir} no existe.")
            return

        run_server(model_path, ngl, port, bin_dir, button, window, model_choice, models_dir_entry, bin_dir_entry, status_label, prompt_entry)

def show_error(window, message):
    dialog = Gtk.MessageDialog(
        transient_for=window,
        buttons=Gtk.ButtonsType.OK,
        message_type=Gtk.MessageType.ERROR,
        text=message
    )
    dialog.connect("response", lambda d, r: d.destroy())
    dialog.present()

def on_link_clicked(label, uri):
    print(f"Link clicked: {uri}")  # Depuración para verificar activaciones
    try:
        Gio.AppInfo.launch_default_for_uri(uri, None)
        return True  # Indica que el evento fue manejado
    except Exception as e:
        print(f"Error al abrir el enlace: {e}")
        return False

def on_window_destroy(window, button, model_choice, models_dir_entry, bin_dir_entry, status_label, prompt_entry):
    stop_server(button, window, model_choice, models_dir_entry, bin_dir_entry, status_label, prompt_entry)

def update_model_list(entry, model_choice):
    models_dir = entry.get_text()
    if models_dir and os.path.isdir(models_dir):
        models = find_models(models_dir)
        model_store = Gtk.StringList()
        for model in models:
            model_store.append(os.path.basename(model))
        model_choice.set_model(model_store)
        model_choice.set_selected(0)
    else:
        model_choice.set_model(Gtk.StringList())

def on_activate(app):
    window = Gtk.ApplicationWindow(application=app)
    window.set_title("Servidor LLaMA")
    window.set_default_size(450, 450)
    window.set_decorated(True)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    box.set_margin_top(10)
    box.set_margin_bottom(10)
    box.set_margin_start(10)
    box.set_margin_end(10)

    global models_dir_entry, bin_dir_entry, model_choice, ngl_entry, port_entry, prompt_entry
    models_dir_entry = Gtk.Entry()
    models_dir_entry.set_placeholder_text("Ruta a modelos GGUF (ej. /media/user/models)")
    bin_dir_entry = Gtk.Entry()
    bin_dir_entry.set_placeholder_text("Ruta base a llama.cpp (ej. /media/user/llama.cpp)")

    saved_models_dir, saved_bin_base, saved_ngl, saved_port, saved_prompt = load_config()
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

    # Connect the changed signal to update model list
    models_dir_entry.connect("changed", update_model_list, model_choice)

    ngl_entry = Gtk.Entry()
    ngl_entry.set_placeholder_text("Capas GPU (-ngl)")
    if saved_ngl:
        ngl_entry.set_text(saved_ngl)

    port_entry = Gtk.Entry()
    port_entry.set_placeholder_text("Puerto (ej. 8080)")
    if saved_port:
        port_entry.set_text(saved_port)

    prompt_entry = Gtk.Entry()
    prompt_entry.set_placeholder_text("Prompt inicial (ej. I always speak in Spanish)")
    if saved_prompt:
        prompt_entry.set_text(saved_prompt)

    button = Gtk.Button(label="Iniciar Servidor")
    button.set_margin_top(10)
    button.set_margin_bottom(10)
    button.connect("clicked", lambda b: run_server_wrapper(b, window, model_choice, models_dir_entry, bin_dir_entry, status_label, prompt_entry))

    status_label = Gtk.Label(label="Indica las rutas, selecciona el modelo, indica el número de capas de GPU, el puerto y el prompt.")
    status_label.set_wrap(True)
    status_label.set_use_markup(True)
    status_label.connect("activate-link", on_link_clicked)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    box.append(models_dir_entry)
    box.append(bin_dir_entry)
    box.append(model_choice)
    box.append(ngl_entry)
    box.append(port_entry)
    box.append(prompt_entry)
    box.append(button)
    box.append(status_label)
    box.set_margin_top(12)
    box.set_margin_bottom(12)
    box.set_margin_start(12)
    box.set_margin_end(12)

    window.set_child(box)
    window.connect("destroy", on_window_destroy, button, model_choice, models_dir_entry, bin_dir_entry, status_label, prompt_entry)
    window.set_visible(True)

def main():
    app = Gtk.Application(application_id="com.llama.llamaserver")
    app.connect("activate", on_activate)
    app.run()

if __name__ == "__main__":
    main()
