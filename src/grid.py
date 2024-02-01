import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata

# Leer datos desde el archivo CSV
df = pd.read_csv('docs/estructura.csv')

# Extraer las columnas
prof = np.array(df['PROFUNDIDAD'])
x = np.array(df['XLINES'])
y = np.array(df['ILINES'])

# Definir los límites deseados
x_limit = (1, 545)
y_limit = (2113, 2679)
prof_limit = (4310, 770)

# Crear una cuadrícula para la interpolación
xi = np.linspace(x_limit[0], x_limit[1], 100)
yi = np.linspace(y_limit[0], y_limit[1], 100)
xi, yi = np.meshgrid(xi, yi)

# Interpolar los datos
zi = griddata((x, y), prof, (xi, yi), method='linear')

# Crear una figura 3D
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Crear el gráfico de malla 3D
ax.plot_surface(xi, yi, zi, cmap='viridis', edgecolor='none')

# Establecer límites en los ejes
ax.set_xlim(x_limit)
ax.set_ylim(y_limit)
ax.set_zlim(prof_limit)

# Etiquetas de los ejes
ax.set_xlabel('XLINES')
ax.set_ylabel('ILINES')
ax.set_zlabel('PROFUNDIDAD')

# Título del gráfico
ax.set_title('Estructura')

# Mostrar el gráfico
plt.show()
