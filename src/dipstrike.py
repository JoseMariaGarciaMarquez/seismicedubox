import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import itertools
import math

def calc_strikedip(pts):
    ptA, ptB, ptC = pts[0], pts[1], pts[2]
    x1, y1, z1 = float(ptA[0]), float(ptA[1]), float(ptA[2])
    x2, y2, z2 = float(ptB[0]), float(ptB[1]), float(ptB[2])
    x3, y3, z3 = float(ptC[0]), float(ptC[1]), float(ptC[2])

    u1 = float(((y1 - y2) * (z3 - z2) - (y3 - y2) * (z1 - z2)))
    u2 = float((-((x1 - x2) * (z3 - z2) - (x3 - x2) * (z1 - z2))))
    u3 = float(((x1 - x2) * (y3 - y2) - (x3 - x2) * (y1 - y2)))

    if u3 < 0:
        easting = u2
    else:
        easting = -u2

    if u3 > 0:
        northing = u1
    else:
        northing = -u1
    
    if easting >= 0:
        partA_strike = math.pow(easting, 2) + math.pow(northing, 2)
        if partA_strike != 0:
            strike = math.degrees(math.acos(northing / math.sqrt(partA_strike)))
        else:
            strike = 0
    else:
        partA_strike = northing / math.sqrt(math.pow(easting, 2) + math.pow(northing, 2))
        if partA_strike != 0:
            strike = math.degrees(2 * math.pi - math.acos(partA_strike))
        else:
            strike = 0

    # determine dip
    part1_dip = math.sqrt(math.pow(u2, 2) + math.pow(u1, 2))
    part2_dip = math.sqrt(math.pow(u1, 2) + math.pow(u2, 2) + math.pow(u3, 2))
    
    if part2_dip != 0:
        dip = math.degrees(math.asin(part1_dip / part2_dip))
    else:
        dip = 0

    return strike, dip


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

# Obtener combinaciones de índices para tríadas de puntos
idx_mskd = np.where((x >= x_limit[0]) & (x <= x_limit[1]) &
                    (y >= y_limit[0]) & (y <= y_limit[1]) &
                    (prof >= prof_limit[0]) & (prof <= prof_limit[1]))[0]

c = list(itertools.combinations(range(len(x)), 3))

strikes = []
dips = []

for ii in range(len(c)):
    pts = [list([x[c[ii][0]], y[c[ii][0]], prof[c[ii][0]]]),
           list([x[c[ii][1]], y[c[ii][1]], prof[c[ii][1]]]),
           list([x[c[ii][2]], y[c[ii][2]], prof[c[ii][2]]])]
    
    # Agregamos un print para verificar las coordenadas que se están utilizando
    #print(f"Puntos para la tríada {ii}: {pts}")
    
    strike, dip = calc_strikedip(pts)
    strikes.append(strike)
    dips.append(dip)

# Crear el gráfico de histogramas
fig, axs = plt.subplots(2, figsize=(7, 4), sharex=False, sharey=True, dpi=200)
fig.suptitle('Frecuencia de los rumbos y echados de planos formados a partir de tríadas de puntos', y=1.05, fontsize=15)

axs[0].hist(strikes, bins=36, color='blue')
axs[0].set_ylabel('Frecuencia', fontsize=14)
axs[0].set_xlabel('Rumbos con regla de la mano derecha [°]', fontsize=14)

axs[1].hist(dips, bins=30, color='blue')
axs[1].set_ylabel('Frecuencia', fontsize=14)
axs[1].set_xlabel('Echados [º]', fontsize=14)

plt.show()

# Crear el segundo gráfico
fig = plt.figure()
fig.suptitle('Histograma y diagrama de rosa de los rumbos de planos formados a partir de tríadas de puntos', y=1.05, fontsize=15)

ax0 = fig.add_subplot(121)
ax0.bar(np.arange(0, 180, 10), np.histogram(strikes, bins=18)[0], width=10, bottom=0.0, color='blue', edgecolor='k', linewidth=0.5, align='edge')
ax0.set_ylabel('Frecuencia')
ax0.set_xlabel('Rumbos con regla de la mano derecha [°]')

ax1 = fig.add_subplot(122, projection='polar')
ax1.bar(np.deg2rad(np.arange(0, 360, 10)), np.histogram(strikes, bins=36)[0], width=np.deg2rad(10), bottom=0.0, color='blue', edgecolor='k', linewidth=0.5)
ax1.set_theta_zero_location('N')
ax1.set_theta_direction(-1)
ax1.grid(True)

fig.tight_layout()
plt.show()