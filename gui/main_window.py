# Ventana principal y eventos
import os
from gi.repository import Gtk, Gdk
from core.config import load_config, save_config
from core.utils import find_models
from gui.model_selector import update_model_list, get_selected_model_path
from gui.dialogs import show_error, show_info_dialog
from core.i18n import get_text, set_language, get_current_language, LANGUAGES
import logging

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        # --- Establecer el idioma antes de crear widgets para que todos los textos se muestren correctamente ---
        config = load_config()
        set_language(config.get("language", "es"))
        super().__init__(application=app)
        self.server_running = False
        self.process = None
        self.set_title(get_text("app_title"))
        self.set_default_size(450, 450)
        self.set_decorated(True)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.box.set_margin_top(10)
        self.box.set_margin_bottom(10)
        self.box.set_margin_start(10)
        self.box.set_margin_end(10)
        self.set_child(self.box)

        # Entradas y estado
        self.models_dir_entry = Gtk.Entry()
        self.models_dir_entry.set_placeholder_text(get_text("models_dir_placeholder"))
        self.select_folder_button = Gtk.Button(label=get_text("select_folder_button"))
        self.bin_dir_entry = Gtk.Entry()
        self.bin_dir_entry.set_placeholder_text(get_text("bin_dir_placeholder"))
        self.ngl_entry = Gtk.Entry()
        self.ngl_entry.set_placeholder_text(get_text("ngl_placeholder"))
        self.port_entry = Gtk.Entry()
        self.port_entry.set_placeholder_text(get_text("port_placeholder"))
        self.prompt_entry = Gtk.Entry()
        self.prompt_entry.set_placeholder_text(get_text("prompt_placeholder"))
        self.temp_entry = Gtk.Entry()
        self.temp_entry.set_placeholder_text(get_text("temp_placeholder"))
        self.top_k_entry = Gtk.Entry()
        self.top_k_entry.set_placeholder_text(get_text("top_k_placeholder"))
        self.top_p_entry = Gtk.Entry()
        self.top_p_entry.set_placeholder_text(get_text("top_p_placeholder"))
        self.repeat_penalty_entry = Gtk.Entry()
        self.repeat_penalty_entry.set_placeholder_text(get_text("repeat_penalty_placeholder"))
        self.threads_entry = Gtk.Entry()
        self.threads_entry.set_placeholder_text(get_text("threads_placeholder"))
        self.ctx_size_entry = Gtk.Entry()
        self.ctx_size_entry.set_placeholder_text(get_text("ctx_size_placeholder"))
        self.max_tokens_entry = Gtk.Entry()
        self.max_tokens_entry.set_placeholder_text(get_text("max_tokens_placeholder"))

        # Crea el modelo y el selector de modelos
        models_dir = self.models_dir_entry.get_text() or os.path.dirname(os.path.realpath(__file__))
        models = find_models(models_dir)
        model_store = Gtk.StringList()
        for model in models:
            model_store.append(os.path.basename(model))
        self.model_choice = Gtk.DropDown(model=model_store)
        self.model_choice.set_selected(0)

        # ... aquí iría el código que añade todos los widgets a self.box ...

        # --- IMPORTANTE ---
        # Asigna los valores de configuración SOLO después de añadir los widgets al contenedor,
        # para que los valores sean visibles en la interfaz GTK.
        config = load_config()
        print("[DEBUG] Configuración cargada:", config)
        # Convertir todos los valores a string antes de asignarlos al widget (por si vienen como int/float)
        if config.get("models_dir"):
            print("[DEBUG] models_dir:", config["models_dir"])
            self.models_dir_entry.set_text(str(config["models_dir"]))
        if config.get("bin_base"):
            print("[DEBUG] bin_base:", config["bin_base"])
            self.bin_dir_entry.set_text(str(config["bin_base"]))
        if config.get("ngl"):
            print("[DEBUG] ngl:", config["ngl"])
            self.ngl_entry.set_text(str(config["ngl"]))
        if config.get("port"):
            print("[DEBUG] port:", config["port"])
            self.port_entry.set_text(str(config["port"]))
        if config.get("prompt"):
            print("[DEBUG] prompt:", config["prompt"])
            self.prompt_entry.set_text(str(config["prompt"]))
        if config.get("temp"):
            print("[DEBUG] temp:", config["temp"])
            self.temp_entry.set_text(str(config["temp"]))
        if config.get("top_k"):
            print("[DEBUG] top_k:", config["top_k"])
            self.top_k_entry.set_text(str(config["top_k"]))
        if config.get("top_p"):
            print("[DEBUG] top_p:", config["top_p"])
            self.top_p_entry.set_text(str(config["top_p"]))
        if config.get("repeat_penalty"):
            print("[DEBUG] repeat_penalty:", config["repeat_penalty"])
            self.repeat_penalty_entry.set_text(str(config["repeat_penalty"]))
        if config.get("threads"):
            print("[DEBUG] threads:", config["threads"])
            self.threads_entry.set_text(str(config["threads"]))
        if config.get("ctx_size"):
            print("[DEBUG] ctx_size:", config["ctx_size"])
            self.ctx_size_entry.set_text(str(config["ctx_size"]))
        if config.get("max_tokens"):
            print("[DEBUG] max_tokens:", config["max_tokens"])
            self.max_tokens_entry.set_text(str(config["max_tokens"]))


        # No necesitamos CSS personalizado, usamos las clases estándar de GTK

        # Selector de idioma - creamos un botón con bandera y nombre del idioma
        # Definir las banderas para cada idioma
        flags = {
            "es": "🇪🇸",  # Bandera de España
            "en": "🇬🇧",  # Bandera de Reino Unido
            "pt": "🇵🇹",  # Bandera de Portugal
            "it": "🇮🇹",  # Bandera de Italia
            "de": "🇩🇪",  # Bandera de Alemania
            "zh": "🇨🇳",  # Bandera de China
            "ja": "🇯🇵"   # Bandera de Japón
        }
        
        # Obtener el idioma actual
        config = load_config()
        current_lang = config.get("language", "es")
        
        # Crear un contenedor horizontal para la bandera y el nombre del idioma
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        
        # Añadir la bandera del idioma actual
        flag_label = Gtk.Label(label=flags.get(current_lang, "🇪🇸"))
        flag_label.set_name("flag_label")  # Para poder identificarla después
        hbox.append(flag_label)
        
        # Añadir el nombre del idioma actual
        lang_name = get_text(f"language_{current_lang}")
        lang_label = Gtk.Label(label=lang_name)
        lang_label.set_name("lang_label")  # Para poder identificarla después
        hbox.append(lang_label)
        
        # Crear el botón con el contenedor
        self.language_button = Gtk.Button()
        self.language_button.set_child(hbox)
        
        # Conectar el evento de clic al selector de idiomas
        self.language_button.connect("clicked", self.on_language_button_clicked)
        
        # Establecer el idioma actual
        config = load_config()
        current_lang = config.get("language", "es")
        current_theme = config.get("theme", "system")
        
        # Aplicar el idioma guardado en la configuración
        set_language(current_lang)
        
        # Aplicar el tema guardado en la configuración
        self.apply_theme(current_theme)
        
        # Función para obtener los temas GTK disponibles
        def get_available_gtk_themes():
            themes = []
            try:
                # Buscar temas en las ubicaciones estándar
                theme_dirs = [
                    "/usr/share/themes",
                    os.path.expanduser("~/.themes"),
                    os.path.expanduser("~/.local/share/themes")
                ]
                
                for theme_dir in theme_dirs:
                    if os.path.exists(theme_dir):
                        for theme in os.listdir(theme_dir):
                            # Verificar si es un tema GTK válido (debe tener un directorio gtk-3.0 o gtk-4.0)
                            if (os.path.exists(os.path.join(theme_dir, theme, "gtk-3.0")) or 
                               os.path.exists(os.path.join(theme_dir, theme, "gtk-4.0"))):
                                if theme not in themes:
                                    themes.append(theme)
                
                # Ordenar los temas alfabéticamente
                themes.sort()
            except Exception as e:
                print(f"[DEBUG] Error al obtener temas GTK: {e}")
                # Temas predeterminados como respaldo
                themes = ["Adwaita", "Adwaita-dark", "HighContrast"]
            
            return themes
        
        # Obtener los temas disponibles
        self.available_themes = get_available_gtk_themes()
        print(f"[DEBUG] Temas GTK disponibles: {self.available_themes}")
        
        # Crear el botón de tema
        self.theme_button = Gtk.Button()
        
        # Crear el contenedor para el botón de tema
        theme_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        
        # Obtener el tema actual
        current_theme = config.get("theme", "system")
        
        # Obtener el tema actual del sistema
        settings = Gtk.Settings.get_default()
        system_theme = settings.get_property("gtk-theme-name") or "Adwaita"
        print(f"[DEBUG] Tema actual del sistema: {system_theme}")
        
        # Si el tema guardado es uno de los antiguos (light, dark, system), convertirlo
        if current_theme in ["light", "dark", "system"]:
            if current_theme == "light" and "dark" in system_theme.lower():
                # Intentar encontrar la versión clara del tema
                light_theme = system_theme.replace("dark", "").replace("Dark", "").strip()
                if light_theme and light_theme in self.available_themes:
                    current_theme = light_theme
            elif current_theme == "dark" and "dark" not in system_theme.lower():
                # Intentar encontrar la versión oscura del tema
                for theme in self.available_themes:
                    if system_theme in theme and ("dark" in theme.lower() or "Dark" in theme):
                        current_theme = theme
                        break
                else:
                    current_theme = "Adwaita-dark" if "Adwaita-dark" in self.available_themes else system_theme
            elif current_theme == "system":
                current_theme = system_theme
        
        # Guardar el tema actual para usarlo en la aplicación
        self.current_theme = current_theme
        
        # Crear la etiqueta para el icono del tema
        theme_icon_label = Gtk.Label()
        theme_icon_label.set_name("theme_icon_label")
        theme_icon_label.set_text("🎨")  # Icono de paleta de colores
        
        # Crear la etiqueta para el nombre del tema
        theme_name_label = Gtk.Label()
        theme_name_label.set_name("theme_name_label")
        theme_name_label.set_text(current_theme)
        
        # Añadir las etiquetas al contenedor
        theme_box.append(theme_icon_label)
        theme_box.append(theme_name_label)
        
        # Establecer el contenedor como hijo del botón
        self.theme_button.set_child(theme_box)

        # Conectar el evento de clic al selector de tema
        self.theme_button.connect("clicked", self.on_theme_button_clicked)
        
        # Crea los widgets de botones y estado (solo una vez)
        self.start_button = Gtk.Button(label=get_text("start_button"))
        self.start_button.get_style_context().add_class("suggested-action")  # Botón azul (acción recomendada)
        self.status_label = Gtk.Label(label=get_text("status_initial"))
        self.link_url = "http://localhost:8080"  # URL por defecto
        
        # Área de texto estilo terminal para mostrar la salida del servidor
        self.terminal_scroll = Gtk.ScrolledWindow()
        self.terminal_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.terminal_scroll.set_min_content_height(200)  # Altura mínima
        self.terminal_scroll.set_visible(False)  # Oculto al inicio
        
        self.terminal_view = Gtk.TextView()
        self.terminal_view.set_editable(False)  # Solo lectura
        self.terminal_view.set_cursor_visible(False)
        self.terminal_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        
        # Estilo de terminal (fondo oscuro, texto claro)
        self.terminal_view.get_style_context().add_class("monospace")
        self.terminal_buffer = self.terminal_view.get_buffer()
        
        # Crear un proveedor de CSS para el estilo de terminal
        css_terminal = b'''
        textview.terminal {
            background-color: #2d2d2d;
            color: #e0e0e0;
            font-family: monospace;
            font-size: 10px;
            padding: 8px;
        }
        '''
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css_terminal)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.terminal_view.get_style_context().add_class("terminal")
        
        self.terminal_scroll.set_child(self.terminal_view)

        # Añadir selector de idioma y tema en la parte superior
        # Crear un contenedor horizontal para los botones de idioma y tema
        top_buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        top_buttons_box.set_homogeneous(True)  # Distribuir el espacio uniformemente
        
        # Añadir los botones al contenedor
        top_buttons_box.append(self.language_button)
        top_buttons_box.append(self.theme_button)
        
        # Añadir el contenedor al layout principal
        self.box.append(top_buttons_box)
        
        # --- CAMBIO: Mostrar el campo para la base de llamacpp justo debajo de los selectores de idioma y tema ---
        self.box.append(self.bin_dir_entry)
        # Luego los widgets de modelos
        self.box.append(self.models_dir_entry)
        self.box.append(self.select_folder_button)
        self.box.append(self.model_choice)
        self.box.append(self.ngl_entry)
        self.box.append(self.threads_entry)
        self.box.append(self.port_entry)
        self.box.append(self.prompt_entry)
        self.box.append(self.temp_entry)
        self.box.append(self.top_k_entry)
        self.box.append(self.top_p_entry)
        self.box.append(self.repeat_penalty_entry)
        self.box.append(self.ctx_size_entry)
        self.box.append(self.max_tokens_entry)
        
        self.box.append(self.start_button)
        self.box.append(self.status_label)
        self.box.append(self.terminal_scroll)  # Añadir terminal al layout

        # Actualizar el selector de modelos con la ruta cargada de la configuración
        if config.get("models_dir") and os.path.isdir(config["models_dir"]):
            update_model_list(self.models_dir_entry, self.model_choice)
            if self.model_choice.get_model().get_n_items() > 0:
                self.status_label.set_label(get_text("status_models_loaded"))
            else:
                self.status_label.set_label(get_text("status_no_models"))

        # Vincular evento del botón
        self.start_button.connect("clicked", self.on_start_button_clicked)

        # Vincular actualización automática del selector de modelos
        self.models_dir_entry.connect("changed", self.on_models_dir_changed)
        self.select_folder_button.connect("clicked", self.on_select_folder_clicked)

        logging.getLogger(__name__).info("MainWindow creada y configurada")

    def on_start_button_clicked(self, button):
        if not self.server_running:
            # Solo cambiamos el botón si start_server() devuelve True (éxito)
            if self.start_server():
                self.start_button.set_label(get_text("stop_button"))
                self.start_button.get_style_context().remove_class("suggested-action")
                self.start_button.get_style_context().add_class("destructive-action")  # Botón rojo (acción destructiva)
        else:
            self.stop_server()
            self.start_button.set_label(get_text("start_button"))
            self.start_button.get_style_context().remove_class("destructive-action")
            self.start_button.get_style_context().add_class("suggested-action")


    def on_models_dir_changed(self, entry):
        """Actualiza el selector de modelos cuando cambia la ruta de modelos."""
        from gi.repository import GLib
        models_dir = entry.get_text()
        if not os.path.isdir(models_dir):
            self.model_choice.set_model(Gtk.StringList())
            self.status_label.set_label("❌ Carpeta inválida. Selecciona una carpeta válida de modelos GGUF.")
            return
        update_model_list(entry, self.model_choice)
        if self.model_choice.get_model().get_n_items() == 0:
            self.status_label.set_label("⚠️ No hay modelos GGUF en la carpeta configurada.")
        else:
            self.status_label.set_label("Modelos actualizados para la ruta seleccionada.")

    def on_select_folder_clicked(self, button):
        dialog = Gtk.FileChooserNative(
            title="Selecciona la carpeta de modelos GGUF",
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            modal=True
        )
        def on_response(native, response):
            if response == Gtk.ResponseType.ACCEPT:
                folder = native.get_file().get_path()
                self.models_dir_entry.set_text(folder)
            native.destroy()
        dialog.connect("response", on_response)
        dialog.show()

    def start_server(self):
        # Crear o reutilizar un botón para abrir el servidor en el navegador
        from gi.repository import Gtk, Gio, GLib
        import subprocess
        
        # Obtener el puerto configurado
        port = int(self.port_entry.get_text()) if self.port_entry.get_text() else 8080
        
        # Actualizar la URL del servidor
        self.link_url = f"http://localhost:{port}"
        
        # Función para abrir el navegador cuando se hace clic en el botón
        def on_open_browser_clicked(button):
            try:
                # Intentar abrir el navegador usando xdg-open en Linux
                subprocess.Popen(["xdg-open", self.link_url])
            except Exception as e:
                print(f"Error al abrir el navegador: {e}")
                show_error(self, f"{get_text("error_prefix").format(e)}")
        
        # Verificar si ya existe el botón
        if not hasattr(self, 'link_widget') or self.link_widget is None:
            # Crear el botón si no existe
            self.link_widget = Gtk.Button(label=f"Abrir en navegador ({self.link_url})")
            
            # Conectar la señal de clic al botón (solo una vez)
            self.link_widget.connect("clicked", on_open_browser_clicked)
            
            # Añadir el widget después de la etiqueta de estado
            self.box.insert_child_after(self.link_widget, self.status_label)
        else:
            # Reutilizar el botón existente
            self.link_widget.set_label(f"Abrir en navegador ({self.link_url})")
        
        # Asegurarse de que el botón esté habilitado
        self.link_widget.set_sensitive(True)

        try:
            self.status_label.set_label(get_text("status_server_starting"))
            # --- Comprobación de servidor activo en el puerto seleccionado ---
            from core.llama_server import check_server_running, kill_server
            from gi.repository import Gtk
            port = int(self.port_entry.get_text()) if self.port_entry.get_text() else 8080
            pid = check_server_running(port)
            if pid:
                dialog = Gtk.MessageDialog(
                    transient_for=self,
                    modal=True,
                    message_type=Gtk.MessageType.QUESTION,
                    buttons=Gtk.ButtonsType.YES_NO,
                    text=f"Ya hay un servidor activo\n\nYa hay un servidor LLaMA activo en el puerto {port} (PID {pid}). ¿Quieres detenerlo antes de continuar?"
                )
                # En GTK4 usamos present() y conectamos una senu00e1l para manejar la respuesta
                response_yes = [False]  # Variable para almacenar la respuesta
                    
                def on_response(dialog, response_id):
                    if response_id == Gtk.ResponseType.YES:
                        response_yes[0] = True
                    dialog.destroy()
                    
                dialog.connect("response", on_response)
                dialog.present()
                    
                # Esperamos a que se cierre el diálogo (esto bloquea hasta que se destruya)
                while dialog.get_visible():
                    from gi.repository import GLib
                    GLib.MainContext.default().iteration(True)
                        
                if response_yes[0]:  # Si el usuario hizo clic en SÍ
                    exito = kill_server(pid)
                    if not exito:
                        self.status_label.set_label("❔ No se pudo detener el servidor anterior.")
                        return False  # Fallo al detener el servidor existente
                else:
                    self.status_label.set_label("Operación cancelada por el usuario.")
                    return False  # Operación cancelada por el usuario
            # --- Fin comprobación de servidor activo ---
            # Obtención completa de parámetros desde los widgets
            # Obtener la ruta absoluta al modelo seleccionado usando la función especializada
            models_dir = self.models_dir_entry.get_text()
            model_path = get_selected_model_path(self.model_choice, models_dir)
            ngl = int(self.ngl_entry.get_text()) if hasattr(self, 'ngl_entry') else 0
            bin_base = self.bin_dir_entry.get_text()
            port = self.port_entry.get_text()
            prompt = self.prompt_entry.get_text()
            temp = self.temp_entry.get_text()
            top_k = self.top_k_entry.get_text()
            top_p = self.top_p_entry.get_text()
            repeat_penalty = self.repeat_penalty_entry.get_text()
            threads = self.threads_entry.get_text()
            ctx_size = self.ctx_size_entry.get_text()
            max_tokens = self.max_tokens_entry.get_text()

            # Guardar configuración al iniciar servidor
            save_config(models_dir, bin_base, ngl, port, prompt, temp, top_k, top_p, repeat_penalty, threads, ctx_size, max_tokens)

            # Lanzar el servidor como proceso
            import subprocess
            import threading
            
            # Mostrar el terminal y añadir una línea separadora antes de iniciar un nuevo servidor
            self.terminal_scroll.set_visible(True)  # Hacer visible el terminal
            
            # Añadir separador si ya hay contenido
            if self.terminal_buffer.get_char_count() > 0:
                self.add_terminal_text("\n" + "-"*50 + "\n\nNueva sesión del servidor:\n")
            else:
                # Si está vacío, simplemente inicializar
                self.add_terminal_text("Iniciando servidor LLaMA...\n")
            
            # Construir el comando con los parámetros correctos para llama-server
            cmd = [
                os.path.join(bin_base, "llama-server"),
                "--model", model_path,
                "--host", "0.0.0.0",
                "--port", str(port),
                "--n-gpu-layers", str(ngl),
                "--temp", str(temp),
                "--top-k", str(top_k),
                "--top-p", str(top_p),
                "--repeat-penalty", str(repeat_penalty),
                "--threads", str(threads),
                "--ctx-size", str(ctx_size),
                "--n-predict", str(max_tokens),
                "--mlock",
                "--cont-batching",
                "--flash-attn"
            ]
            
            # Guardar el prompt en la configuración pero no usarlo como parámetro directo
            # ya que --system-prompt no es un parámetro válido para llama-server
            
            # Mostrar el comando en el terminal
            self.add_terminal_text("Ejecutando: " + " ".join(cmd) + "\n\n")
            
            # Iniciar el proceso de forma segura, desconectado del proceso principal
            try:
                # Iniciar el proceso de forma segura
                self.process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT, 
                    text=True, 
                    bufsize=1
                )
                print(f"Servidor iniciado con PID {self.process.pid}")
            except Exception as e:
                print(f"Error al iniciar el proceso: {e}")
                self.status_label.set_label(f"❔ Error al iniciar el servidor: {e}")
                return False
            self.server_running = True
            self.set_inputs_sensitive(False)
            
            # Función para leer la salida del proceso en segundo plano
            def read_output():
                try:
                    for line in iter(self.process.stdout.readline, ''):
                        if line:  # Si la línea no está vacía
                            # Imprimir en la terminal normal
                            print(line, end='', flush=True)
                            
                            # Usar GLib.idle_add para actualizar la UI desde otro hilo
                            from gi.repository import GLib
                            # Usar una función auxiliar para capturar correctamente el valor de line
                            def add_line_to_terminal(text):
                                self.add_terminal_text(text)
                                return False  # Importante: devolver False para que GLib.idle_add no lo llame repetidamente
                            
                            GLib.idle_add(add_line_to_terminal, line)
                        else:
                            break
                except Exception as e:
                    from gi.repository import GLib
                    error_msg = f"Error leyendo salida: {e}\n"
                    
                    def add_error_to_terminal(text):
                        self.add_terminal_text(text)
                        return False
                    
                    GLib.idle_add(add_error_to_terminal, error_msg)
            
            # Iniciar hilo para leer la salida
            output_thread = threading.Thread(target=read_output)
            output_thread.daemon = True  # El hilo se cerrará cuando el programa principal termine
            output_thread.start()
            # Mostrar mensaje claro y actualizar botón
            url = f"http://localhost:{port}"
            self.status_label.set_label(get_text("status_server_started").format(port))
            self.link_url = url  # Actualizar la URL por si cambió el puerto
            self.link_widget.set_label(f"Abrir en navegador ({url})")
            self.link_widget.set_sensitive(True)
            logging.getLogger(__name__).info("Servidor iniciado")
            return True  # Servidor iniciado correctamente
        except Exception as e:
            self.status_label.set_label("❌ Error al iniciar el servidor.")
            logging.getLogger(__name__).error(f"No se pudo iniciar el servidor: {e}")
            show_error(self, get_text("error_server_start").format(e))
            return False  # Error al iniciar el servidor

    def stop_server(self):
        # Deshabilitar el botón del navegador cuando el servidor se detiene
        from gi.repository import Gtk, GLib
        
        if hasattr(self, 'link_widget') and self.link_widget is not None:
            # Deshabilitar el botón en lugar de eliminarlo
            self.link_widget.set_sensitive(False)
            # Cambiar el texto para indicar que el servidor está detenido
            self.link_widget.set_label("Servidor detenido - No disponible")

        # Actualizar la interfaz para mostrar el estado
        self.status_label.set_label("Deteniendo servidor...")
        
        # Verificar si hay un proceso activo para detener
        if self.process is not None:
            try:
                print("Intentando detener el servidor...")
                
                # Obtener el PID del proceso si está disponible
                pid = None
                if hasattr(self.process, 'pid'):
                    pid = self.process.pid
                
                if pid is not None:
                    print(f"Deteniendo servidor con PID {pid}...")
                    
                    # Usar nuestra función kill_server
                    try:
                        from core.llama_server import kill_server
                        exito = kill_server(pid)
                        if exito:
                            print("Servidor detenido correctamente")
                        else:
                            print("No se pudo detener el servidor completamente")
                    except Exception as e:
                        print(f"No se pudo detener el servidor: {e}")
                
                # Importante: Limpiar las referencias al proceso cuidadosamente
                if hasattr(self.process, 'stdout') and self.process.stdout is not None:
                    try:
                        self.process.stdout.close()
                    except Exception as e:
                        print(f"Error al cerrar stdout: {e}")
                
                if hasattr(self.process, 'stderr') and self.process.stderr is not None:
                    try:
                        self.process.stderr.close()
                    except Exception as e:
                        print(f"Error al cerrar stderr: {e}")
                
                print("Proceso de detención del servidor completado")
            except Exception as e:
                print(f"Error general al detener el servidor: {e}")
            finally:
                # Siempre ejecutar estas acciones al final, incluso si hubo errores
                # Desconectar el proceso de la aplicación principal
                self.process = None
                self.server_running = False
                
                # Actualizar la interfaz
                self.set_inputs_sensitive(True)
        
        # Mantener el terminal visible para que se pueda ver el historial
        self.status_label.set_label(get_text("status_server_stopped"))
        
        # Solicitar que la ventana se ajuste a su tamaño natural
        self.queue_resize()
        
        # Forzar actualización inmediata de la interfaz
        while GLib.MainContext.default().pending():
            GLib.MainContext.default().iteration(True)
        
        # Operación exitosa
        return True  # Servidor detenido correctamente

    def save_current_config(self):
        # Usar el tema actual guardado en la variable de instancia
        theme = getattr(self, 'current_theme', 'system')  # Usar 'system' como valor por defecto si no existe
        
        # Guardar la configuración actual
        save_config(
            self.models_dir_entry.get_text(),
            self.bin_dir_entry.get_text(),
            self.ngl_entry.get_text(),
            self.port_entry.get_text(),
            self.prompt_entry.get_text(),
            self.temp_entry.get_text(),
            self.top_k_entry.get_text(),
            self.top_p_entry.get_text(),
            self.repeat_penalty_entry.get_text(),
            self.threads_entry.get_text(),
            self.ctx_size_entry.get_text(),
            self.max_tokens_entry.get_text(),
            get_current_language(),
            theme
        )
        from gi.repository import GLib
        while GLib.MainContext.default().pending():
            GLib.MainContext.default().iteration(True)
        return True
        

    
    def on_language_button_clicked(self, button):
        # Mostrar menú emergente con todos los idiomas disponibles
        popover = Gtk.Popover()
        popover.set_parent(button)
        
        # Crear un contenedor vertical para los botones de idioma
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        
        # Obtener el idioma actual
        config = load_config()
        current_lang = config.get("language", "es")
        
        # Añadir un botón para cada idioma disponible
        for lang_code in LANGUAGES:
            # Obtener el nombre del idioma en el idioma actual
            lang_name = get_text(f"language_{lang_code}")
            lang_button = Gtk.Button(label=lang_name)
            
            # Resaltar el idioma actualmente seleccionado
            if lang_code == current_lang:
                lang_button.get_style_context().add_class("suggested-action")
            
            # Conectar la señal del botón
            lang_button.connect("clicked", self.on_language_selected, lang_code, popover)
            vbox.append(lang_button)
        
        popover.set_child(vbox)
        popover.popup()
    
    def on_theme_button_clicked(self, button):
        # Crear un popover para el selector de tema
        popover = Gtk.Popover()
        popover.set_parent(button)
        
        # Crear un contenedor vertical para los elementos del popover
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        
        # Añadir un título al popover
        title_label = Gtk.Label()
        title_label.set_markup("<b>" + get_text("select_theme") + "</b>")
        title_label.set_margin_bottom(10)
        box.append(title_label)
        
        # Crear un contenedor con scroll para los temas
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(200)  # Altura mínima
        scroll.set_max_content_height(400)  # Altura máxima
        
        # Contenedor para los botones de tema
        themes_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        # Crear un botón para cada tema GTK disponible
        for theme_name in self.available_themes:
            # Crear el botón directamente con el nombre del tema
            theme_button = Gtk.Button(label=theme_name)
            
            # Conectar el evento de clic
            theme_button.connect("clicked", self.on_theme_selected, theme_name, popover)
            
            # Añadir el botón al contenedor vertical
            themes_box.append(theme_button)
        
        # Añadir el contenedor de temas al scroll
        scroll.set_child(themes_box)
        
        # Añadir el scroll al contenedor principal
        box.append(scroll)
        
        # Establecer el contenedor como hijo del popover
        popover.set_child(box)
        
        # Mostrar el popover
        popover.popup()
    
    def on_language_selected(self, button, lang_code, popover):
        # Cambiar el idioma de la aplicación
        set_language(lang_code)
        
        # Cerrar el popover
        popover.popdown()
        
        # Definir las banderas para cada idioma
        flags = {
            "es": "🇪🇸",  # Bandera de España
            "en": "🇬🇧",  # Bandera de Reino Unido
            "pt": "🇵🇹",  # Bandera de Portugal
            "it": "🇮🇹",  # Bandera de Italia
            "de": "🇩🇪",  # Bandera de Alemania
            "zh": "🇨🇳",  # Bandera de China
            "ja": "🇯🇵"   # Bandera de Japón
        }
        
        # Actualizar la bandera y el nombre del idioma en el botón
        box = self.language_button.get_child()
        child = box.get_first_child()
        
        while child:
            if isinstance(child, Gtk.Label) and child.get_name() == "flag_label":
                child.set_text(flags.get(lang_code, "🇪🇸"))
            elif isinstance(child, Gtk.Label) and child.get_name() == "lang_label":
                child.set_text(get_text(f"language_{lang_code}"))
            child = child.get_next_sibling()
        
        # Actualizar todos los textos de la interfaz
        self.set_title(get_text("app_title"))
        self.models_dir_entry.set_placeholder_text(get_text("models_dir_placeholder"))
        self.select_folder_button.set_label(get_text("select_folder_button"))
        self.bin_dir_entry.set_placeholder_text(get_text("bin_dir_placeholder"))
        self.ngl_entry.set_placeholder_text(get_text("ngl_placeholder"))
        self.port_entry.set_placeholder_text(get_text("port_placeholder"))
        self.prompt_entry.set_placeholder_text(get_text("prompt_placeholder"))
        self.temp_entry.set_placeholder_text(get_text("temp_placeholder"))
        self.top_k_entry.set_placeholder_text(get_text("top_k_placeholder"))
        self.top_p_entry.set_placeholder_text(get_text("top_p_placeholder"))
        self.repeat_penalty_entry.set_placeholder_text(get_text("repeat_penalty_placeholder"))
        self.threads_entry.set_placeholder_text(get_text("threads_placeholder"))
        self.ctx_size_entry.set_placeholder_text(get_text("ctx_size_placeholder"))
        self.max_tokens_entry.set_placeholder_text(get_text("max_tokens_placeholder"))
        
        # Actualizar botones y etiquetas
        if not self.server_running:
            self.start_button.set_label(get_text("start_button"))
            if self.model_choice.get_model().get_n_items() > 0:
                self.status_label.set_label(get_text("status_models_loaded"))
            else:
                self.status_label.set_label(get_text("status_no_models"))
        else:
            self.start_button.set_label(get_text("stop_button"))
            port = self.port_entry.get_text() or "8080"
            self.status_label.set_label(get_text("status_server_started").format(port))
        
        # Actualizar también el botón de tema
        theme_box = self.theme_button.get_child()
        theme_child = theme_box.get_first_child()
        
        while theme_child:
            if isinstance(theme_child, Gtk.Label) and theme_child.get_name() == "theme_name_label":
                # Obtener el tema actual
                config = load_config()
                current_theme = config.get("theme", "system")
                # Mostrar directamente el nombre del tema sin intentar traducirlo
                theme_child.set_text(current_theme)
            theme_child = theme_child.get_next_sibling()
        
        # Guardar la preferencia de idioma
        self.save_current_config()
    
    def apply_theme(self, theme_name):
        """Aplica el tema GTK seleccionado a la aplicación
        
        Args:
            theme_name: El nombre del tema GTK a aplicar
        """
        print(f"[DEBUG] Aplicando tema GTK: {theme_name}")
        
        # Obtener la configuración de GTK
        settings = Gtk.Settings.get_default()
        
        # Guardar el tema actual en la configuración
        # Actualizamos la variable de instancia para que save_current_config la use
        self.current_theme = theme_name
        
        # Aplicar el tema GTK directamente
        try:
            # Primero, intentar establecer el tema opuesto para forzar un cambio
            is_dark_theme = "dark" in theme_name.lower() or "Dark" in theme_name
            settings.set_property("gtk-application-prefer-dark-theme", not is_dark_theme)
            
            # Procesar eventos pendientes
            from gi.repository import GLib
            while GLib.MainContext.default().pending():
                GLib.MainContext.default().iteration(True)
            
            # Establecer el tema GTK
            settings.set_property("gtk-theme-name", theme_name)
            
            # Establecer la preferencia de tema oscuro basada en el nombre del tema
            settings.set_property("gtk-application-prefer-dark-theme", is_dark_theme)
            
            print(f"[DEBUG] Tema GTK establecido: {theme_name}, modo oscuro: {is_dark_theme}")
        except Exception as e:
            print(f"[DEBUG] Error al aplicar tema GTK: {e}")
            
            # Intentar al menos establecer el modo claro/oscuro
            try:
                is_dark_theme = "dark" in theme_name.lower() or "Dark" in theme_name
                settings.set_property("gtk-application-prefer-dark-theme", is_dark_theme)
                print(f"[DEBUG] Modo oscuro establecido: {is_dark_theme}")
            except Exception as e2:
                print(f"[DEBUG] Error al establecer modo oscuro: {e2}")
    def on_theme_selected(self, button, theme_name, popover):
        # --- Solución bug: cerrar el popover SOLO después de aplicar el tema y actualizar la interfaz ---
        # Esto se hace para evitar que el redibujado cierre el popover prematuramente.
        
        # Actualizar el botón de tema
        box = self.theme_button.get_child()
        child = box.get_first_child()
        
        while child:
            if isinstance(child, Gtk.Label) and child.get_name() == "theme_icon_label":
                # Mantener el icono de paleta de colores
                child.set_text("🎨")  # Icono de paleta de colores
            elif isinstance(child, Gtk.Label) and child.get_name() == "theme_name_label":
                child.set_text(theme_name)
            child = child.get_next_sibling()
        
        # Aplicar el tema seleccionado
        self.apply_theme(theme_name)
        
        # Guardar la preferencia de tema
        self.save_current_config()
    
        # Actualizar todos los textos de la interfaz
        self.set_title(get_text("app_title"))
        
        self.models_dir_entry.set_placeholder_text(get_text("models_dir_placeholder"))
        self.select_folder_button.set_label(get_text("select_folder_button"))
        self.bin_dir_entry.set_placeholder_text(get_text("bin_dir_placeholder"))
        self.ngl_entry.set_placeholder_text(get_text("ngl_placeholder"))
        self.port_entry.set_placeholder_text(get_text("port_placeholder"))
        self.prompt_entry.set_placeholder_text(get_text("prompt_placeholder"))
        self.temp_entry.set_placeholder_text(get_text("temp_placeholder"))
        self.top_k_entry.set_placeholder_text(get_text("top_k_placeholder"))
        self.top_p_entry.set_placeholder_text(get_text("top_p_placeholder"))
        self.repeat_penalty_entry.set_placeholder_text(get_text("repeat_penalty_placeholder"))
        self.threads_entry.set_placeholder_text(get_text("threads_placeholder"))
        self.ctx_size_entry.set_placeholder_text(get_text("ctx_size_placeholder"))
        self.max_tokens_entry.set_placeholder_text(get_text("max_tokens_placeholder"))
        
        # Actualizar botones y etiquetas
        if not self.server_running:
            self.start_button.set_label(get_text("start_button"))
            if self.model_choice.get_model().get_n_items() > 0:
                self.status_label.set_label(get_text("status_models_loaded"))
            else:
                self.status_label.set_label(get_text("status_no_models"))
        else:
            self.start_button.set_label(get_text("stop_button"))
            port = self.port_entry.get_text() or "8080"
            self.status_label.set_label(get_text("status_server_started").format(port))
        
        # Guardar la preferencia de idioma
        self.save_current_config()

        # Ahora sí, cerrar el popover tras aplicar el tema y actualizar la interfaz
        popover.popdown()

    def add_terminal_text(self, text, tag=None):
        """Añade texto al terminal con formato opcional."""
        end_iter = self.terminal_buffer.get_end_iter()
        if tag:
            self.terminal_buffer.insert_with_tags(end_iter, text, tag)
        else:
            self.terminal_buffer.insert(end_iter, text)
        # Desplazar a la última línea
        self.terminal_view.scroll_to_iter(self.terminal_buffer.get_end_iter(), 0.0, False, 0.0, 0.0)
    
    def set_inputs_sensitive(self, sensitive):
        """Habilita o deshabilita los campos de entrada y el selector."""
        self.models_dir_entry.set_sensitive(sensitive)
        self.select_folder_button.set_sensitive(sensitive)
        self.bin_dir_entry.set_sensitive(sensitive)
        self.model_choice.set_sensitive(sensitive)
        self.ngl_entry.set_sensitive(sensitive)
        self.port_entry.set_sensitive(sensitive)
        self.prompt_entry.set_sensitive(sensitive)
        self.temp_entry.set_sensitive(sensitive)
        self.top_k_entry.set_sensitive(sensitive)
        self.top_p_entry.set_sensitive(sensitive)
        self.repeat_penalty_entry.set_sensitive(sensitive)
        self.threads_entry.set_sensitive(sensitive)
        self.ctx_size_entry.set_sensitive(sensitive)
        self.max_tokens_entry.set_sensitive(sensitive)
        
def create_main_window(app):
    return MainWindow(app)
