import numpy as np
import pandas as pd 

class filtros:
    def __init__(self, signal, x, y) -> None:
        self.signal = signal
        self.x = x
        self.y = y

    def media_movil_b(self):
        """
        Aplica un filtro de media móvil a una señal para suavizarla.
        
        Parámetros:
        - señal: un arreglo de numpy que contiene los valores de la señal a suavizar.
        - n_ventana: un entero que indica el tamaño de la ventana de media móvil.
        
        Retorna:
        - un arreglo de numpy que contiene los valores de la señal suavizada.
        """
        
        # Crear un arreglo de numpy con los valores de la señal suavizada
        señal_filtr = np.zeros(len(self.signal))
        
        # Aplicar la media móvil a la señal
        for i in range(n_ventana, len(self.signall)-n_ventana):
            señal_filtr[i] = np.mean(self.signal[i-n_ventana:i+n_ventana+1])
        
        # Completar los extremos de la señal utilizando el método de reflejo
        for i in range(n_ventana):
            señal_filtr[i] = np.mean(self.signal[:i+n_ventana+1])
            señal_filtr[len(self.signall)-i-1] = np.mean(self.signal[len(self.signall)-i-1-n_ventana:])

        # Retornar la señal suavizada
        return señal_filtr