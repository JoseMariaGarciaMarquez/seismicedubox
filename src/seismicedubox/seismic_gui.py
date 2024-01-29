# Graphical User Interface
import os
import sys
import tkinter as tk

from PIL import Image, ImageTk
from seismicplot import seismicplot
from tkinter import ttk, filedialog, messagebox

class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag
    def write(self, str):
        self.widget.configure(state='normal')
        self.widget.insert(tk.END, str, (self.tag,))
        self.widget.configure(state='disabled')
        self.widget.see(tk.END)
        self.widget.update_idletasks()

class seismic_gui:
    def __init__(self):
        self.window = tk.Tk()

    def main_window(self):
        self.window.title("SeismicEduBox")

        icon_image = Image.open("images/icono.png")
        icon_image = icon_image.resize((150, 150), Image.BICUBIC)
        self.icon_image = ImageTk.PhotoImage(icon_image)
        self.window.tk.call('wm', 'iconphoto', self.window._w, self.icon_image)

        self.icon_image = ImageTk.PhotoImage(icon_image)
        tk.Label(self.window, image=self.icon_image).grid(row=10, column=3, padx=10, pady=10)

        # ... (Resto del código)

        notebook = ttk.Notebook(self.window)

        # Pestaña 1: Archivo
        frame_file = ttk.Frame(notebook)
        notebook.add(frame_file, text='Archivo')
        self.setup_file_section(frame_file)

        # Pestaña 2: Espaciamiento
        frame_spacing = ttk.Frame(notebook)
        notebook.add(frame_spacing, text='Espaciamiento')
        self.setup_spacing_section(frame_spacing)

        # Pestaña 3: Rango
        frame_range = ttk.Frame(notebook)
        notebook.add(frame_range, text='Rango')
        self.setup_range_section(frame_range)

        # Pestaña 4: Carpeta destino
        frame_folder = ttk.Frame(notebook)
        notebook.add(frame_folder, text='Carpeta destino')
        self.setup_folder_section(frame_folder)

        # Pestaña 5: Colormap
        frame_colormap = ttk.Frame(notebook)
        notebook.add(frame_colormap, text='Colormap')
        self.setup_colormap_section(frame_colormap)

        # Pestaña 6: Atributos
        frame_attributes = ttk.Frame(notebook)
        notebook.add(frame_attributes, text='Atributos')
        self.setup_attributes_section(frame_attributes)

        notebook.pack(expand=1, fill='both')

        # Botones y terminal
        tk.Button(self.window, text="⬇️ PREV", command=self.show_previous_profile).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.window, text="⬆️ NEXT", command=self.show_next_profile).pack(side=tk.LEFT, padx=5, pady=5)

        self.setup_terminal_section()

        tk.Button(self.window, text="Mostrar Perfil", command=self.show_current_profile).pack(side=tk.RIGHT, padx=5, pady=5)
        tk.Button(self.window, text="Guardar", command=self.save_current_profile).pack(side=tk.RIGHT, padx=5, pady=5)
        tk.Button(self.window, text="Guardar Todos", command=self.save_all_profiles).pack(side=tk.RIGHT, padx=5, pady=5)

        self.setup_profile_type_section()

        self.window.mainloop()

    # Resto de las funciones...
    def setup_file_section(self, frame):
        tk.Label(frame, text="Cubo sísmico: ").grid(row=0, column=0, sticky='e', pady=5)
        self.cubo_entry = tk.Entry(frame, width=30)
        self.cubo_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame, text="Buscar", command=self.browse_file).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(frame, text="Cargar", command=self.load_seismic_data).grid(row=0, column=3, padx=5, pady=5)

    def setup_spacing_section(self, frame):
        tk.Label(frame, text="Espaciamiento en Y").grid(row=0, column=0, sticky='e', pady=5)
        self.yspa_entry = tk.Entry(frame, width=10)
        self.yspa_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Espaciamiento en X").grid(row=1, column=0, sticky='e', pady=5)
        self.xspa_entry = tk.Entry(frame, width=10)
        self.xspa_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="Espaciamiento en Z").grid(row=2, column=0, sticky='e', pady=5)
        self.zspa_entry = tk.Entry(frame, width=10)
        self.zspa_entry.grid(row=2, column=1, padx=5, pady=5)

    def setup_range_section(self, frame):
        tk.Label(frame, text="Primera iline").grid(row=0, column=0, sticky='e', pady=5)
        self.first_iline = tk.Entry(frame, width=10)
        self.first_iline.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Última iline").grid(row=1, column=0, sticky='e', pady=5)
        self.last_iline = tk.Entry(frame, width=10)
        self.last_iline.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="Primera xline").grid(row=2, column=0, sticky='e', pady=5)
        self.first_xline = tk.Entry(frame, width=10)
        self.first_xline.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(frame, text="Última xline").grid(row=3, column=0, sticky='e', pady=5)
        self.last_xline = tk.Entry(frame, width=10)
        self.last_xline.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(frame, text="Profundidad inicial").grid(row=4, column=0, sticky='e', pady=5)
        self.first_zline = tk.Entry(frame, width=10)
        self.first_zline.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(frame, text="Profundidad final").grid(row=5, column=0, sticky='e', pady=5)
        self.last_zline = tk.Entry(frame, width=10)
        self.last_zline.grid(row=5, column=1, padx=5, pady=5)


    def lista(self):
        try:
            # Obtener valores iniciales y finales de la sección de rango
            first_iline_value = int(self.first_iline.get())
            last_iline_value = int(self.last_iline.get())
            first_xline_value = int(self.first_xline.get())
            last_xline_value = int(self.last_xline.get())
            first_zline_value = int(self.first_zline.get())
            last_zline_value = int(self.last_zline.get())

            # Obtener valores de espaciamiento de la sección de espaciamiento
            y_spacing_value = int(self.yspa_entry.get())
            x_spacing_value = int(self.xspa_entry.get())
            z_spacing_value = int(self.zspa_entry.get())

            # Crear listas utilizando range y los valores proporcionados
            self.iporfiles = list(range(first_iline_value, last_iline_value + 1, int(y_spacing_value)))
            self.xporfiles = list(range(first_xline_value, last_xline_value + 1, int(x_spacing_value)))
            self.zporfiles = list(range(first_zline_value, last_zline_value + 1, int(z_spacing_value)))

        except ValueError as e:
            messagebox.showerror("Error", f"Error: {e}")


    def setup_folder_section(self, frame):
        tk.Label(frame, text="Carpeta destino: ").grid(row=0, column=0, sticky='e', pady=5)
        self.folder_entry = tk.Entry(frame)
        self.folder_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame, text="Buscar", command=self.browse_folder).grid(row=0, column=2)

    def setup_colormap_section(self, frame):
        tk.Label(frame, text="Colormap: ").grid(row=0, column=0, sticky='e', pady=5)
        colores1 = ['BrBG', 'PRGn', 'PiYG', 'PuOr', 'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']
        self.cmap1_combo = ttk.Combobox(frame, values=colores1)
        self.cmap1_combo.grid(row=0, column=1)
        self.cmap1_combo.set(colores1[0])  # Set default value

        colores2 = ['Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2', 'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b', 'tab20c']
        self.cmap2_combo = ttk.Combobox(frame, values=colores2)
        self.cmap2_combo.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self.cmap2_combo.set(colores2[0])  # Set default value

    def setup_terminal_section(self):
        self.terminal_text = tk.Text(self.window, wrap='word', height=10, width=85)
        self.terminal_text.grid(row=5, column=3, rowspan=10, padx=10, pady=10)
        sys.stdout = TextRedirector(self.terminal_text, "stdout")

    def setup_profile_type_section(self):
        self.profile_type_var = tk.StringVar(value="ILINES")
        profile_type_menu = tk.OptionMenu(self.window, self.profile_type_var, "ILINES", "XLINES", "ZLINES", command=self.update_profile_type)
        profile_type_menu.grid(row=17, column=2, padx=5, pady=5)
    def setup_attributes_section(self, frame):
        tk.Label(frame, text="Atributo: ").grid(row=0, column=0)
        self.atributo_combo = ttk.Combobox(frame, values=['RMS', 'AI', 'FI', 'PI'])
        self.atributo_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        tk.Label(frame, text="Colormap: ").grid(row=1, column=0, sticky='ew', pady=5)
        colores2 = ['Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2', 'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b', 'tab20c']
        self.cmap2_combo = ttk.Combobox(frame, values=colores2)
        self.cmap2_combo.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        tk.Button(frame, text="Calcular", command=self.calculate_attributes).grid(row=2, column=0, columnspan=2, pady=5, sticky='ew')

        # Configurar la función de actualización del atributo directamente
        self.atributo_combo.bind("<<ComboboxSelected>>", lambda event: setattr(self, 'atributo', self.atributo_combo.get()))

    def browse_file(self):
        try:
            file_path = filedialog.askopenfilename()
            self.cubo_entry.delete(0, tk.END)
            self.cubo_entry.insert(0, file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error al seleccionar archivo: {str(e)}")

    def browse_folder(self):
        try:
            folder_path = filedialog.askdirectory()
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error al seleccionar carpeta: {str(e)}")



if __name__ == '__main__':
    gui = seismic_gui()
    gui.main_window()