import os
import sys
import numpy as np
import segysak as sg
import pathlib
import subprocess
import matplotlib.pyplot as plt
import tkinter as tk
import xarray as xr
import csv

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
    # Variables globales para el objeto de la gráfica
        self.ax = None
        self.fig = None
        self.cubo = None
        self.current_iline_index = 0
        self.current_xline_index = 0
        self.current_depth_index = 0
        self.last_profile_type = "ILINES"
        self.window = tk.Tk()
        self.setup_gui()

    def setup_gui(self):
        self.window.title("SeismicEduBox")

        icon_image = Image.open("images/icono.png")
        icon_image = icon_image.resize((150, 150), Image.BICUBIC)
        self.icon_image = ImageTk.PhotoImage(icon_image)
        self.window.tk.call('wm', 'iconphoto', self.window._w, self.icon_image)

        self.icon_image = ImageTk.PhotoImage(icon_image)
        tk.Label(self.window, image=self.icon_image).grid(row=10, column=3, padx=10, pady=10)

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

        tk.Button(self.window, text="Mostrar Perfil", command=self.show_current_profile).grid(row=16, column=0, padx=5, pady=5)
        tk.Button(self.window, text="Guardar", command=self.save_current_profile).grid(row=16, column=1, padx=5, pady=5)
        tk.Button(self.window, text="Guardar Todos", command=self.save_all_profiles).grid(row=16, column=2, padx=5, pady=5)

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

    def setup_attributes_section(self):
        frame_attributes = ttk.LabelFrame(self.window, text="Atributos", padding=(10, 5))
        frame_attributes.grid(row=10, column=0, padx=10, pady=10, sticky='ew', columnspan=3)

        lista_atributos = ['RMS', 'AI', 'FI', 'PI']

        atributo_label = tk.Label(frame_attributes, text="Atributo: ")
        atributo_label.grid(row=0, column=0)

        self.atributo_combo = ttk.Combobox(frame_attributes, values=lista_atributos)
        self.atributo_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        tk.Label(frame_attributes, text="Colormap: ").grid(row=1, column=0, sticky='ew', pady=5)
        colores2 = ['Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2', 'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b', 'tab20c']
        self.cmap2_combo = ttk.Combobox(frame_attributes, values=colores2)
        self.cmap2_combo.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        tk.Button(frame_attributes, text="Calcular", command=self.calculate_attributes).grid(row=2, column=0, columnspan=2, pady=5, sticky='ew')

        # Configurar la función de actualización del atributo directamente
        self.atributo_combo.bind("<<ComboboxSelected>>", lambda event: setattr(self, 'atributo', self.atributo_combo.get()))


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



    def on_click(self, event):
        x, y = event.xdata, event.ydata
        if x is not None and y is not None:
            print(f"Coordenadas del clic: {x:.2f}, {y:.2f}")
            self.save_to_csv(x, y)

    def save_to_csv(self, x, y):
        with open('estructura.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            # Encabezados
            if file.tell() == 0:  # Solo escribe encabezados si el archivo está vacío
                writer.writerow(['PROFUNDIDAD', 'XLINES', 'ILINES'])
            if self.last_profile_type == "ILINES":
                writer.writerow([y, x,  self.iporfiles[self.current_iline_index]])
            elif self.last_profile_type == "XLINES":
                writer.writerow([y,  self.xporfiles[self.current_xline_index], x])
            elif self.last_profile_type == "ZLINES":
                writer.writerow([ self.zporfiles[self.current_depth_index], x, y])
            else:
                print("Tipo de perfil no reconocido")
                return

            print("Coordenadas guardadas en 'estructura.csv'")

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
            print(self.cubo)
            print('Las dimensiones del cubo son: ', np.shape(self.cubo.data))
            print('Cubo cargado con exito 🍾')
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos sísmicos: {str(e)}")

    # En la función show_previous_profile
    def show_previous_profile(self):
        self.lista()
        try:
            if self.last_profile_type == "ILINES":
                self.current_iline_index -= 1
            elif self.last_profile_type == "XLINES":
                self.current_xline_index -= 1
            elif self.last_profile_type == "ZLINES":
                self.current_depth_index -= 1

            # Si el índice es negativo, reiniciar al último perfil
            if self.current_iline_index < 0:
                self.current_iline_index = len(self.iporfiles) - 1
            if self.current_xline_index < 0:
                self.current_xline_index = len(self.xporfiles) - 1
            if self.current_depth_index < 0:
                self.current_depth_index = len(self.zporfiles) - 1

            # Mostrar el valor actual
            self.show_current_profile()

        except IndexError:
            messagebox.showwarning("Advertencia", "Ya estás en el primer perfil disponible.")

    # En la función show_next_profile
    def show_next_profile(self):
        self.lista()
        try:
            if self.last_profile_type == "ILINES":
                self.current_iline_index += 1
            elif self.last_profile_type == "XLINES":
                self.current_xline_index += 1
            elif self.last_profile_type == "ZLINES":
                self.current_depth_index += 1

            # Si el índice supera el último perfil, reiniciar al primer perfil
            if self.current_iline_index >= len(self.iporfiles):
                self.current_iline_index = 0
            if self.current_xline_index >= len(self.xporfiles):
                self.current_xline_index = 0
            if self.current_depth_index >= len(self.zporfiles):
                self.current_depth_index = 0

            # Mostrar el valor actual
            self.show_current_profile()

        except IndexError:
            messagebox.showwarning("Advertencia", "Ya estás en el último perfil disponible.")

    def show_current_profile(self):
        self.lista()
        print('Tipo actual de perfil: ', self.last_profile_type)

        if self.last_profile_type == "ILINES":
            current_iline_value = self.iporfiles[self.current_iline_index]
            print('Mostrando Iline #{}'.format(current_iline_value))
            plt.clf()
            if isinstance(self.cubo, xr.Dataset):
                iline_profile = self.cubo.data.transpose('depth', 'iline', 'xline', transpose_coords=True).sel(iline=current_iline_value, method='nearest').plot(yincrease=False, cmap=self.cmap1_combo.get())
                iline_label = current_iline_value
            elif isinstance(self.cubo, xr.DataArray):
                iline_profile = self.cubo.transpose('depth', 'iline', 'xline', transpose_coords=True).sel(iline=current_iline_value, method='nearest').plot(yincrease=False, cmap=self.cmap2_combo.get())
                iline_label = current_iline_value
            else:
                print("Tipo de cubo no reconocido")
                return

            plt.grid('grey')
            plt.ylabel('DEPTH')
            plt.xlabel('XLINE')

            # Almacena el objeto de la gráfica y conecta el evento de clic
            self.fig = plt.gcf()
            self.ax = plt.gca()
            self.fig.canvas.mpl_connect('button_press_event', self.on_click)

            plt.show()

        elif self.last_profile_type == "XLINES":
            current_xline_value = self.xporfiles[self.current_xline_index]
            print('Mostrando Xline #{}'.format(current_xline_value))
            plt.clf()
            if isinstance(self.cubo, xr.Dataset):
                xline_profile = self.cubo.data.transpose('depth', 'iline', 'xline', transpose_coords=True).sel(xline=current_xline_value, method='nearest').plot(yincrease=False, cmap=self.cmap1_combo.get())
                xline_label = current_xline_value
            elif isinstance(self.cubo, xr.DataArray):
                xline_profile = self.cubo.transpose('depth', 'iline', 'xline', transpose_coords=True).sel(xline=current_xline_value, method='nearest').plot(yincrease=False, cmap=self.cmap2_combo.get())
                xline_label = current_xline_value
            else:
                print("Tipo de cubo no reconocido")
                return

            plt.grid('grey')
            plt.ylabel('DEPTH')
            plt.xlabel('ILINE')

            # Almacena el objeto de la gráfica y conecta el evento de clic
            self.fig = plt.gcf()
            self.ax = plt.gca()
            self.fig.canvas.mpl_connect('button_press_event', self.on_click)

            plt.show()

        elif self.last_profile_type == "ZLINES":
            current_depth_value = self.zporfiles[self.current_depth_index]
            print('Mostrando profundiad de {}[m]'.format(current_depth_value))
            plt.clf()
            if isinstance(self.cubo, xr.Dataset):
                depth_profile = self.cubo.data.transpose('depth', 'iline', 'xline', transpose_coords=True).sel(depth=current_depth_value, method='nearest').plot(cmap=self.cmap1_combo.get())
                depth_label = current_depth_value
            elif isinstance(self.cubo, xr.DataArray):
                depth_profile = self.cubo.transpose('depth', 'iline', 'xline', transpose_coords=True).sel(depth=current_depth_value, method='nearest').plot(cmap=self.cmap2_combo.get())
                depth_label = current_depth_value
            else:
                print("Tipo de cubo no reconocido")
                return

            plt.grid('grey')
            plt.ylabel('ILINE')
            plt.xlabel('XLINE')

            # Almacena el objeto de la gráfica y conecta el evento de clic
            self.fig = plt.gcf()
            self.ax = plt.gca()
            self.fig.canvas.mpl_connect('button_press_event', self.on_click)

            plt.show()
            


        
    def update_profile_type(self, value):
        self.last_profile_type = value

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

            if self.last_profile_type == "ILINES":
                for porfil in self.iporfiles:
                   self.save_profile (attribute_name, folder_path, porfil, 'Iline')
            elif self.last_profile_type == "XLINES":
                for porfil in self.xporfiles:
                    self.save_profile(attribute_name, folder_path, porfil, 'Xline')
            elif self.last_profile_type == "ZLINES":
                for porfil in self.zporfiles:
                    self.save_profile(attribute_name, folder_path, porfil, "DEPTH")

            messagebox.showinfo("Guardar Todos", "Todos los perfiles guardados con éxito.")

    def save_profile(self, attribute_name, folder_path, index, line_type):
        plt.clf()  # Limpia la figura actual

        if isinstance(self.cubo, xr.Dataset):
            line_profile = self.cubo.data.transpose('depth', 'iline', 'xline', transpose_coords=True).sel(**{line_type.lower(): index}, method='nearest').plot(yincrease=False, cmap=self.cmap1_combo.get())
            if self.last_profile_type == "ILINES":
                plt.grid('grey')
                plt.ylabel('DEPTH')
                plt.xlabel('XLINE')
            elif self.last_profile_type == "XLINES":
                plt.grid('grey')
                plt.ylabel('DEPTH')
                plt.xlabel('ILINE')
            elif self.last_profile_type == "ZLINES":
                plt.grid('grey')
                plt.ylabel('ILINE')
                plt.xlabel('XLINE')
        elif isinstance(self.cubo, xr.DataArray):
            line_profile = self.cubo.transpose('depth', 'iline', 'xline', transpose_coords=True).sel(**{line_type.lower(): index}, method='nearest').plot(yincrease=False, cmap=self.cmap2_combo.get())
            if self.last_profile_type == "ILINES":
                plt.grid('grey')
                plt.ylabel('DEPTH')
                plt.xlabel('XLINE')
            elif self.last_profile_type == "XLINES":
                plt.grid('grey')
                plt.ylabel('DEPTH')
                plt.xlabel('ILINE')
            elif self.last_profile_type == "ZLINES":
                plt.grid('grey')
                plt.ylabel('ILINE')
                plt.xlabel('XLINE')
        else:
            print("Tipo de cubo no reconocido")
            return


        file_path = os.path.join(folder_path, f"profile_{attribute_name}_{line_type.lower()}{index}.png")
        plt.savefig(file_path)




    def calculate_attributes(self):
        atributo = self.atributo
        print(atributo)

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
