import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Leer datos desde el archivo CSV
df = pd.read_csv('docs/estructura.csv')

# Extraer las columnas
prof = np.array(df['PROFUNDIDAD'])
x = np.array(df['XLINES'])
y = np.array(df['ILINES'])

# Crear una figura 3D
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Crear el gráfico de dispersión 3D
ax.scatter(x, y, prof, c='b', marker='o')

# Etiquetas de los ejes
ax.set_xlabel('XLINES')
ax.set_ylabel('ILINES')
ax.set_zlabel('PROFUNDIDAD')

# Título del gráfico
ax.set_title('Gráfico de dispersión 3D')

# Mostrar el gráfico
plt.show()
