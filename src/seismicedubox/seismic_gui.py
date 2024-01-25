# Graphical User Interface
import tkinter as tk

from seismicplot import seismicplot

class seismic_gui:
    def __init__(self):
        self.window = tk.TK()

    def main_window(self):
        self.window.title("SeismicEduBox")