import pandas as pd
import tabula
import numpy as np

# Archivo que vamos a leer
acta = '/Users/arnaubarrera/Desktop/Sports Analyitics/Stats PreInf A/Actes/CNT vs Lima-Horta.pdf'
#acta = '/Users/arnaubarrera/Desktop/Sports Analyitics/Stats PreInf A/Actes/CNT vs Xamba.pdf'
#acta = '/Users/arnaubarrera/Desktop/Sports Analyitics/Stats PreInf A/Actes/Bufalà vs CNT.pdf'

# Coordenadas de las tablas A M B (hay 5 en total)
x1 = 402; x2 = 473; x3 = 543; x4 = 613; x5 = 686; x6 = 754
y1 = 115; y2 = 552

coordenadas_tablas = [
    [y1, x1, y2, x2],
    [y1, x2, y2, x3],
    [y1, x3, y2, x4],
    [y1, x4, y2, x5],
    [y1, x5, y2, x6]
]

raw_pbp = []

# TODO Cambiar la lectura de la tabla de anotación. Leer A1, M1, B1 por separado. Luego A2, M2, B2, ..., Ai, Mi, Bi

# Extraer las columnas de anotación A M B y guardar cada una en un DF distinto
for area in coordenadas_tablas:
    raw_pbp_i = tabula.read_pdf(acta, pages='all', area=area)
    if raw_pbp_i:
        raw_pbp_i = raw_pbp_i[0]
        raw_pbp_i = raw_pbp_i.dropna(axis=1, how='all')  # Eliminamos columnas vacías
        raw_pbp.append(raw_pbp_i)  # Añadimos los datos de la tabla a la lista global
    else:
        break

# %% Crea un nuevo DataFrame con los títulos de las columnas como la primera fila

# Define el orden deseado de las columnas
orden_deseado = ['Jug. A', 'Anotación A', 'Min', 'Anotación B', 'Jug B']

for i in range(0, len(raw_pbp)):
    titulos_df = np.array(raw_pbp[i].columns)  # Valores de la primera fila de anotación

    if titulos_df.shape[0] == 4:  # Tiene 4 columnas (i.e no ha leído bien la columna de minutos)
        # Trabajamos c on la primera fila
        primera_fila = pd.DataFrame([titulos_df], columns=['Jug. A', 'Anotación A', 'Anotación B', 'Jug B'])
        raw_pbp[i].columns = ['Jug. A', 'Anotación A', 'Anotación B', 'Jug B']

        # A veces lee mal el PDF y mete los minutos en otra columna, de forma que en total solo hay 4 cols.
        a = raw_pbp[i]['Anotación A'].str.split(' ', expand=True)
        if not a.iloc[:, 1].empty:
            PbP['Anotación A'] = a.iloc[:, 0]
            PbP['Min'] = a.iloc[:, 1]
        else:
            b = PbP['Anotación B'].str.split(' ', expand=True)

            PbP['Anotación B'] = b.iloc[0]
            PbP['Min'] = b.iloc[1]
    elif titulos_df.shape[0] == 5:
        primera_fila = pd.DataFrame([titulos_df], columns=['Jug. A', 'Anotación A', 'Min', 'Anotación B', 'Jug B'])
        raw_pbp[i].columns = ['Jug. A', 'Anotación A', 'Min', 'Anotación B', 'Jug B']
    else:
        break

    # Verifica si el orden actual de las columnas coincide con el orden deseado
    if list(PbP.columns) != orden_deseado:
        PbP = PbP.reindex(columns=orden_deseado)  # Reordena las columnas del DataFrame



    primera_fila = primera_fila.apply(pd.to_numeric, errors='coerce')  # Comprobamos que son números. Si no, ponemos NaN
    raw_pbp[i] = pd.concat([primera_fila, raw_pbp[i]], ignore_index=True)   # Concatena el nuevo DF con el DF original

# Concatenamos verticalmente
PbP = pd.DataFrame()
PbP = pd.concat(raw_pbp, axis=0)

print('Finished')
