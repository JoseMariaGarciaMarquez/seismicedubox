import os
import sys
import numpy as np
import segysak as sg
import pathlib
import subprocess
import matplotlib.pyplot as plt
import tkinter as tk
import xarray as xr

from segysak.segy import get_segy_texthead, segy_loader
from PIL import Image, ImageTk
from scipy.signal import hilbert
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

class SeismicAnalyzer:
    def __init__(self):
        self.cubo = None
        self.current_iline_index = 0
        self.current_xline_index = 0
        self.current_depth_index = 0
        self.last_profile_type = "ILINES"
        self.window = tk.Tk()
        self.setup_gui()

    def setup_gui(self):
        self.window.title("SeismicEduBox")

        icon_image = Image.open("/images/icon.png")
        icon_image = icon_image.resize((150, 150), Image.BICUBIC)
        self.icon_image = ImageTk.PhotoImage(icon_image)
        self.window.tk.call('wm', 'iconphoto', self.window._w, self.icon_image)

        # Secciones
        frame_file = ttk.LabelFrame(self.window, text="Archivo", padding=(10, 5))
        frame_file.grid(row=0, column=0, padx=10, pady=10, sticky='ew', columnspan=3)
        self.setup_file_section(frame_file)

        frame_spacing = ttk.LabelFrame(self.window, text="Espaciamiento", padding=(10, 5))
        frame_spacing.grid(row=1, column=0, padx=10, pady=10, sticky='ew', columnspan=3)
        self.setup_spacing_section(frame_spacing)

        frame_range = ttk.LabelFrame(self.window, text="Rango", padding=(10, 5))
        frame_range.grid(row=2, column=0, padx=10, pady=10, sticky='ew', columnspan=3)
        self.setup_range_section(frame_range)

        frame_folder = ttk.LabelFrame(self.window, text="Carpeta destino", padding=(10, 5))
        frame_folder.grid(row=3, column=0, padx=10, pady=10, sticky='ew', columnspan=3)
        self.setup_folder_section(frame_folder)

        frame_colormap = ttk.LabelFrame(self.window, text="Colormap", padding=(10, 5))
        frame_colormap.grid(row=4, column=0, padx=10, pady=10, sticky='ew', columnspan=3)
        self.setup_colormap_section(frame_colormap)

        # ... (otras secciones)

        tk.Button(self.window, text="⬇️ PREV", command=self.show_previous_profile).grid(row=17, column=0, padx=5, pady=5)
        tk.Button(self.window, text="⬆️ NEXT", command=self.show_next_profile).grid(row=17, column=1, padx=5, pady=5)

        self.setup_terminal_section()

        tk.Button(self.window, text="Mostrar Iline", command=self.show_next_iline).grid(row=16, column=0, padx=5, pady=5)
        tk.Button(self.window, text="Mostrar Xline", command=self.show_next_xline).grid(row=16, column=1, padx=5, pady=5)
        tk.Button(self.window, text="Mostrar Zline", command=self.show_next_depth).grid(row=16, column=2, padx=5, pady=5)
        tk.Button(self.window, text="Guardar", command=self.save_current_profile).grid(row=16, column=3, padx=5, pady=5)
        tk.Button(self.window, text="Guardar Todos", command=self.save_all_profiles).grid(row=16, column=4, padx=5, pady=5)

        self.setup_profile_type_section()

        self.setup_attributes_section()


        self.window.mainloop()

    def setup_file_section(self, frame):
        tk.Label(frame, text="Cubo sísmico: ").grid(row=0, column=0, sticky='e', pady=5)
        self.cubo_entry = tk.Entry(frame, width=30)
        self.cubo_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame, text="Buscar", command=self.browse_file).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(frame, text="Cargar", command=self.load_seismic_data).grid(row=0, column=3, padx=5, pady=5)

    def setup_spacing_section(self, frame):
        entries_spacing = [
            ("Espaciamiento en X", 10),
            ("Espaciamiento en Y", 10),
            ("Espaciamiento en Z", 10),
        ]

        for idx, (label, width) in enumerate(entries_spacing):
            tk.Label(frame, text=label).grid(row=idx, column=0, sticky='e', pady=5)
            entry = tk.Entry(frame, width=width)
            entry.grid(row=idx, column=1, padx=5, pady=5)

    def setup_range_section(self, frame):
        entries_range = [
            ("Primera iline", 10),
            ("Última iline", 10),
            ("Primera xline", 10),
            ("Última xline", 10),
            ("Primera zline", 10),
            ("Última zline", 10),
        ]

        for idx, (label, width) in enumerate(entries_range):
            tk.Label(frame, text=label).grid(row=idx, column=0, sticky='e', pady=5)
            entry = tk.Entry(frame, width=width)
            entry.grid(row=idx, column=1, padx=5, pady=5)

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

    def setup_attributes_section(self):
        frame_attributes = ttk.LabelFrame(self.window, text="Atributos", padding=(10, 5))
        frame_attributes.grid(row=10, column=0, padx=10, pady=10, sticky='ew', columnspan=3)

        lista_atributos = ['RMS', 'AI', 'FI', 'PI']

        self.setup_entry_combobox("Atributo: ", lista_atributos, frame_attributes, row=0, column=0)

        tk.Label(frame_attributes, text="Colormap: ").grid(row=1, column=0, sticky='ew', pady=5)
        colores2 = ['Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2', 'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b', 'tab20c']
        self.cmap2_combo = ttk.Combobox(frame_attributes, values=colores2)
        self.cmap2_combo.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        tk.Button(frame_attributes, text="Calcular", command=self.calculate_attributes).grid(row=2, column=0, columnspan=2, pady=5, sticky='ew')


    def setup_entry_combobox(self, label_text, combobox_values, parent_frame, row, column):
        tk.Label(parent_frame, text=label_text).grid(row=row, column=column, sticky='ew', pady=5)
        entry_combobox = ttk.Combobox(parent_frame, values=combobox_values)
        entry_combobox.grid(row=row, column=column + 1, padx=5, pady=5, sticky='ew')
        return entry_combobox



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

    def setup_terminal_section(self):
        self.terminal_text = tk.Text(self.window, wrap='word', height=50, width=30)
        self.terminal_text.grid(row=0, column=3, rowspan=10, padx=10, pady=10)
        sys.stdout = TextRedirector(self.terminal_text, "stdout")



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

    def load_seismic_data(self):
        try:
            cubo_path = pathlib.Path(self.cubo_entry.get())
            print('3D Seismic Data-', cubo_path, cubo_path.exists())
            print(get_segy_texthead(cubo_path))
            self.cubo = segy_loader(cubo_path, iline=5, xline=21, cdpx=73, cdpy=77, vert_domain='DEPTH')
            segy_file = cubo_path
            print('Las dimensiones del cubo son: ', np.shape(self.cubo.data))
            print('Cubo cargado con exito 🍾')
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos sísmicos: {str(e)}")

    def show_previous_profile(self):
        if self.last_profile_type == "ILINES":
            self.current_iline_index -= int(self.yspa_entry.get())
            self.show_next_iline()  # Llamar al método correspondiente
        elif self.last_profile_type == "XLINES":
            self.current_xline_index -= int(self.xspa_entry.get())
            self.show_next_xline()  # Llamar al método correspondiente
        elif self.last_profile_type == "ZLINES":
            self.current_depth_index -= int(self.zspa_entry.get())
            self.show_next_depth()  # Llamar al método correspondiente

    def show_next_profile(self):
        if self.last_profile_type == "ILINES":
            self.current_iline_index += int(self.yspa_entry.get())
            self.show_next_iline()  # Llamar al método correspondiente
        elif self.last_profile_type == "XLINES":
            self.current_xline_index += int(self.xspa_entry.get())
            self.show_next_xline()  # Llamar al método correspondiente
        elif self.last_profile_type == "ZLINES":
            self.current_depth_index += int(self.zspa_entry.get())
            self.show_next_depth()  # Llamar al método correspondiente



    # En el método show_next_iline
    def show_next_iline(self):
        if self.cubo is not None:
            plt.clf()  # Limpia la figura actual

            if isinstance(self.cubo, xr.Dataset):
                iline_profile = self.cubo.data.transpose('depth', 'iline', 'xline', transpose_coords=True).sel(iline=self.current_iline_index, method='nearest').plot(yincrease=False, cmap=self.cmap1_combo.get())
                iline_label = self.cubo.iline[self.current_iline_index]
            elif isinstance(self.cubo, xr.DataArray):
                iline_profile = self.cubo.transpose('depth', 'iline', 'xline', transpose_coords=True).sel(iline=self.current_iline_index, method='nearest').plot(yincrease=False, cmap=self.cmap2_combo.get())
                iline_label = self.cubo.iline[self.current_iline_index]
            else:
                print("Tipo de cubo no reconocido")
                return

            plt.grid('grey')
            plt.ylabel('DEPTH')
            plt.xlabel('XLINE')
            plt.title(f"Iline {iline_label}")
            plt.show()


    # En el método show_next_xline
    def show_next_xline(self):
        if self.cubo is not None:
            plt.clf()  # Limpia la figura actual

            if isinstance(self.cubo, xr.Dataset):
                xline_profile = self.cubo.data.transpose('depth', 'iline', 'xline', transpose_coords=True).sel(xline=self.current_xline_index, method='nearest').plot(yincrease=False, cmap=self.cmap1_combo.get())
                xline_label = self.cubo.xline[self.current_xline_index]
            elif isinstance(self.cubo, xr.DataArray):
                xline_profile = self.cubo.transpose('depth', 'iline', 'xline', transpose_coords=True).sel(xline=self.current_xline_index, method='nearest').plot(yincrease=False, cmap=self.cmap2_combo.get())
                xline_label = self.cubo.xline[self.current_xline_index]
            else:
                print("Tipo de cubo no reconocido")
                return

            plt.grid('grey')
            plt.ylabel('DEPTH')
            plt.xlabel('XLINE')
            plt.title(f"Xline {xline_label}")
            plt.show()

    def show_next_depth(self):
        if self.cubo is not None:
            plt.clf()
            
            if isinstance(self.cubo, xr.Dataset):
                depth_profile = self.cubo.data.transpose('depth', 'iline', 'xline', transpose_coords=True).sel(depth=self.current_depth_index, method='nearest').plot(cmap=self.cmap1_combo.get())
                depth_label = self.cubo.depth[self.current_depth_index]
            elif isinstance(self.cubo, xr.DataArray):
                depth_profile = self.cubo.transpose('depth', 'iline', 'xline', transpose_coords=True).sel(depth=self.current_depth_index, method='nearest').plot(cmap=self.cmap2_combo.get())
                depth_label = self.cubo.depth[self.current_depth_index]
            else:
                print("Tipo de cubo no reconocido")
                return

            plt.grid('grey')
            plt.ylabel('ILINE')
            plt.xlabel('XLINE')
            plt.title(f"Depth {depth_label}")
            plt.show()

    def update_profile_type(self, value):
        self.last_profile_type = value

    def show_profile(self, profile, profile_type, canvas):
        canvas.delete("all")
        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
        ax.plot(profile.transpose())
        ax.set_title(f"Seismic Profile ({profile_type})")
        ax.set_xlabel("Sample")
        ax.set_ylabel("Amplitude")

        canvas_widget = FigureCanvasTkAgg(fig, master=canvas)
        canvas_widget_widget = canvas_widget.get_tk_widget()
        canvas_widget_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        canvas_widget.draw()

    def save_current_profile(self):
        if self.cubo is not None:
            attribute_name = self.atributo_combo.get()
            folder_path = self.folder_entry.get()  # Obtener la ruta de la carpeta desde la entrada de la GUI

            if self.last_profile_type == "ILINES":
                index = self.current_iline_index
                line_type = "Iline"
            elif self.last_profile_type == "XLINES":
                index = self.current_xline_index
                line_type = "Xline"

            self.save_profile(attribute_name, folder_path, index, line_type)
            messagebox.showinfo("Guardar Perfil", "Perfil guardado con éxito.")

    def save_all_profiles(self):
        if self.cubo is not None:
            attribute_name = self.atributo_combo.get()
            folder_path = self.folder_entry.get()  # Obtener la ruta de la carpeta desde la entrada de la GUI
            espaciado = int(self.xspa_entry.get()) if self.last_profile_type == "ILINES" else int(self.yspa_entry.get())

            if self.last_profile_type == "ILINES":
                for iline_index in range(0, len(self.cubo.iline), espaciado):
                    self.save_profile(attribute_name, folder_path, iline_index, "Iline")
            elif self.last_profile_type == "XLINES":
                for xline_index in range(0, len(self.cubo.xline), espaciado):
                    self.save_profile(attribute_name, folder_path, xline_index, "Xline")

            messagebox.showinfo("Guardar Todos", "Todos los perfiles guardados con éxito.")

    def save_profile(self, attribute_name, folder_path, index, line_type):
        plt.clf()  # Limpia la figura actual

        if isinstance(self.cubo, xr.Dataset):
            line_profile = self.cubo.data.transpose('depth', 'iline', 'xline', transpose_coords=True).sel(**{line_type.lower(): index}, method='nearest').plot(yincrease=False, cmap=self.cmap1_combo.get())
            line_label = getattr(self.cubo, line_type.lower())[index]
        elif isinstance(self.cubo, xr.DataArray):
            line_profile = self.cubo.transpose('depth', 'iline', 'xline', transpose_coords=True).sel(**{line_type.lower(): index}, method='nearest').plot(yincrease=False, cmap=self.cmap2_combo.get())
            line_label = getattr(self.cubo, line_type.lower())[index]
        else:
            print("Tipo de cubo no reconocido")
            return

        plt.grid('grey')
        plt.ylabel('DEPTH')
        plt.xlabel(line_type)
        plt.title(f"{line_type} {line_label}")

        file_path = os.path.join(folder_path, f"profile_{attribute_name}_{line_type.lower()}{index}.png")
        plt.savefig(file_path)



    def calculate_attributes(self):
        atributo = self.atributo_combo.get()

        if atributo == 'RMS':
            self.cubo = np.sqrt(self.cubo.data**2)
        elif atributo == 'AI':
            analytic_signal = hilbert(self.cubo.data)
            new_data = np.abs(analytic_signal)
            self.cubo['data'] = (['depth', 'iline', 'xline'], new_data)
        elif atributo == 'FI':
            analytic_signal = hilbert(self.cubo.data)
            instantaneous_phase = np.unwrap(np.angle(analytic_signal))
            new_data = np.diff(instantaneous_phase) / (2.0 * np.pi)
            self.cubo['data'] = (['depth', 'iline', 'xline'], new_data)
        elif atributo == 'PI':
            analytic_signal = hilbert(self.cubo.data)
            new_data = np.unwrap(np.angle(analytic_signal))
            self.cubo['data'] = (['depth', 'iline', 'xline'], new_data)

        else:
            print("Atributo no reconocido")
            return None

        print('Variable tipo: ', type(self.cubo))
        if not isinstance(self.cubo, (xr.Dataset, xr.DataArray)):
            self.cubo = xr.DataArray(self.cubo, dims=['depth', 'iline', 'xline'])
        print('Después variable tipo: ', type(self.cubo))
        print('Cálculo exitoso')


if __name__ == '__main__':
    seismic_analyzer = SeismicAnalyzer()

