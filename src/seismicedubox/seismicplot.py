import pathlib
import numpy as np
import segysak as sg

from tkinter import ttk, filedialog, messagebox
from segysak.segy import get_segy_texthead, segy_loader

class seismicplot():
    def __init__(self):
        self.cubo = None


    def load_segy(self):
        try:
            cubo_path = pathlib.Path(self.cubo_entry.get())
            print('3D Seismic Data-', cubo_path, cubo_path.exists())
            print(get_segy_texthead(cubo_path))
            self.cubo = segy_loader(cubo_path, iline=5, xline=21, cdpx=73, cdpy=77, vert_domain='DEPTH')
            segy_file    = cubo_path
            print('Las dimensiones del cubo son: ', np.shape(self.cubo.data))
            print('Cubo cargado con exito 🍾')
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos sísmicos: {str(e)}")