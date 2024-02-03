import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata

# Leer datos desde los archivos CSV
df1 = pd.read_csv('docs/estructura3.csv')
df2 = pd.read_csv('docs/estructura32.csv')

# Extraer las columnas para el primer conjunto de datos
prof1 = np.array(df1['PROFUNDIDAD'])
x1 = np.array(df1['XLINES'])
y1 = np.array(df1['ILINES'])

# Extraer las columnas para el segundo conjunto de datos
prof2 = np.array(df2['PROFUNDIDAD'])
x2 = np.array(df2['XLINES'])
y2 = np.array(df2['ILINES'])

# Definir los límites deseados
x_limit = (1, 545)
y_limit = (2113, 2679)
prof_limit = (4310, 770)

# Crear una cuadrícula para la interpolación del primer conjunto de datos
xi1 = np.linspace(x_limit[0], x_limit[1], 100)
yi1 = np.linspace(y_limit[0], y_limit[1], 100)
xi1, yi1 = np.meshgrid(xi1, yi1)
zi1 = griddata((x1, y1), prof1, (xi1, yi1), method='linear')

# Crear una cuadrícula para la interpolación del segundo conjunto de datos
xi2 = np.linspace(x_limit[0], x_limit[1], 100)
yi2 = np.linspace(y_limit[0], y_limit[1], 100)
xi2, yi2 = np.meshgrid(xi2, yi2)
zi2 = griddata((x2, y2), prof2, (xi2, yi2), method='linear')

# Crear una figura 3D para ambos conjuntos de datos
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')

# Plotear el primer conjunto de datos en la figura 3D
surf1 = ax.plot_surface(xi1, yi1, zi1, cmap='viridis', alpha=0.7)

# Plotear el segundo conjunto de datos en la misma figura 3D
surf2 = ax.plot_surface(xi2, yi2, zi2, cmap='viridis', alpha=0.7)

# Establecer límites y etiquetas de los ejes
ax.set_xlim(x_limit)
ax.set_ylim(y_limit)
ax.set_zlim(prof_limit)
ax.set_xlabel('XLINES')
ax.set_ylabel('ILINES')
ax.set_zlabel('PROFUNDIDAD')
ax.set_title('Superposición de Estructura 1 y Estructura 2')

# Mostrar el gráfico
plt.show()

# Calcular la diferencia entre zi1 y zi2
diff_zi = zi2 - zi1

# Crear un mapa de isopacas en 2D
plt.figure(figsize=(10, 6))
contour = plt.contourf(xi1, yi1, diff_zi, levels=20, cmap='viridis')
plt.colorbar(contour, label='Grosor[m]')

# Establecer etiquetas y título
plt.xlabel('XLINES')
plt.ylabel('ILINES')
plt.title('Mapa de Isopacas')

# Mostrar el gráfico
plt.show()