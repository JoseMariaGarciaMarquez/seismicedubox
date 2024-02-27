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
from gui_sections import FileSection, SpacingSection, RangeSection, FolderSection, ColormapSection, ProfileTypeSection, AttributesSection
from tkinter_functions import TextRedirector, load_seismic_data, browse_file, browse_folder, save_to_csv, show_previous_profile, show_next_profile, show_current_profile, save_current_profile, save_all_profiles, calculate_attributes

class SeismicAnalyzer:
    def __init__(self):
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

        file_section = FileSection(self.window)
        file_section.grid(row=0, column=0, padx=10, pady=10, sticky='ew', columnspan=3)

        spacing_section = SpacingSection(self.window)
        spacing_section.grid(row=1, column=0, padx=10, pady=10, sticky='ew', columnspan=3)

        range_section = RangeSection(self.window)
        range_section.grid(row=2, column=0, padx=10, pady=10, sticky='ew', columnspan=3)

        folder_section = FolderSection(self.window)
        folder_section.grid(row=3, column=0, padx=10, pady=10, sticky='ew', columnspan=3)

        colormap_section = ColormapSection(self.window)
        colormap_section.grid(row=4, column=0, padx=10, pady=10, sticky='ew', columnspan=3)

        profile_type_section = ProfileTypeSection(self.window)
        profile_type_section.grid(row=17, column=2, padx=5, pady=5)

        attributes_section = AttributesSection(self.window)
        attributes_section.grid(row=10, column=0, padx=10, pady=10, sticky='ew', columnspan=3)

        tk.Button(self.window, text="⬇️ PREV", command=show_previous_profile).grid(row=17, column=0, padx=5, pady=5)
        tk.Button(self.window, text="⬆️ NEXT", command=show_next_profile).grid(row=17, column=1, padx=5, pady=5)

        self.setup_terminal_section()

        tk.Button(self.window, text="Mostrar Perfil", command=show_current_profile).grid(row=16, column=0, padx=5, pady=5)
        tk.Button(self.window, text="Guardar", command=save_current_profile).grid(row=16, column=1, padx=5, pady=5)
        tk.Button(self.window, text="Guardar Todos", command=save_all_profiles).grid(row=16, column=2, padx=5, pady=5)

        self.window.mainloop()

    def setup_terminal_section(self):
        self.terminal_text = tk.Text(self.window, wrap='word', height=50, width=30)
        self.terminal_text.grid(row=0, column=3, rowspan=10, padx=10, pady=10)
        sys.stdout = TextRedirector(self.terminal_text, "stdout")

if __name__ == '__main__':
    seismic_analyzer = SeismicAnalyzer()