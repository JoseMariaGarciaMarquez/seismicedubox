import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Leer datos desde el archivo CSV
df = pd.read_csv('docs/falla1.csv')

# Extraer las columnas
prof = np.array(df['PROFUNDIDAD'])
x = np.array(df['XLINES'])
y = np.array(df['ILINES'])

# Crear una figura 3D
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Definir los límites deseados
x_limit = (1, 545)
y_limit = (2113, 2679)
prof_limit = (4310, 770)

# Crear el gráfico de dispersión 3D
ax.scatter(x, y, prof, c='b', marker='o')

ax.set_xlim(x_limit)
ax.set_ylim(y_limit)
ax.set_zlim(prof_limit)

# Etiquetas de los ejes
ax.set_xlabel('XLINES')
ax.set_ylabel('ILINES')
ax.set_zlabel('PROFUNDIDAD')

# Título del gráfico
ax.set_title('Gráfico de dispersión 3D')

# Mostrar el gráfico
plt.show()
