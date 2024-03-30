# %%
import tabula
import pandas as pd
import numpy as np

# %%


def extraer_datos(acta):
    """
    Extrae los datos relevantes del acta.

    Argumentos:
    acta (str): Ruta del archivo PDF del acta.

    Retorna:
    equipo_A (Dataframe): Información sobre jugadores del equipo local (número, nombre, cuartos, faltas).
    equipo_B (Dataframe): Información sobre jugadores del equipo visitante (número, nombre, cuartos, faltas).
    PbP (Dataframe): Play by play digitalizado.
    """

    # Coordenadas de las tablas que queremos extraer [superior, izq, inferior, der]
    area_equip_A = [140, 45, 355, 408]
    area_equip_B = [390, 45, 595, 408]

    # Extraer tablas del PDF y guardarlas en DataFrames
    raw_A = tabula.read_pdf(acta, pages='all', area=area_equip_A)[0];
    raw_B = tabula.read_pdf(acta, pages='all', area=area_equip_B)[0];
    PbP = leer_pbp(acta)

    # Limpiamos las tablas de los equipos
    equipo_A = limpiar_equipo(raw_A)
    equipo_B = limpiar_equipo(raw_B)

    return equipo_A, equipo_B, PbP


# Limpiamos la tabla de jugadoras de un equipo
def limpiar_equipo(raw_i):
    # Eliminamos filas vacías
    raw_i = raw_i.drop([0, 1])
    filas_vacias = (raw_i.iloc[:, 0] == '----')
    raw_i = raw_i[~filas_vacias]

    # Renombramos columnas
    clean_i = raw_i.rename(columns={'Unnamed: 0': 'Licencia', 'Unnamed: 1': 'Nombre', 'Unnamed: 2': 'Número',
                                    'Unnamed: 3': 'Q1', 'Unnamed: 4': 'Q2', 'Unnamed: 5': 'Q3',
                                    'Unnamed: 6': 'Q4', 'Unnamed: 7': 'Q5', 'Unnamed: 8': 'Q6',
                                    'Unnamed: 9': 'F1', 'Unnamed: 10': 'F2', 'Unnamed: 11': 'F3',
                                    'Unnamed: 12': 'F4', 'Unnamed: 13': 'F5'})
    return clean_i


def leer_pbp(acta):
    """
    Lee la parte del Play by Play (Acumulació de punts) del acta.

    Argumentos:
    acta (str): Ruta del archivo PDF del acta.

    Retorna:
    PbP (Dataframe): Play by play digitalizado.
    """

    # Coordenadas tres primeros bloques (el 4o y el 5o suelen estar vacíos)
    x1 = 402; x2 = 613
    y1 = 115; y2 = 552
    area = [y1, x1, y2, x2]
    columns = [418, 430, 445, 460, 473, 485, 500, 515, 530, 543, 556, 572, 585, 600]

    # Extraer los datos del PDF
    raw_pbp = tabula.read_pdf(acta, pages='all', area=area, columns=columns, pandas_options={'header': None})[0]

    # Reorganizamos los datos
    titulos = ['Jug A', 'Anotación A', 'Min', 'Jug B', 'Anotación B']

    raw_pbp_1 = raw_pbp.iloc[0:, 0:5].reset_index(drop=True)
    raw_pbp_2 = raw_pbp.iloc[0:, 5:10].reset_index(drop=True)
    raw_pbp_3 = raw_pbp.iloc[0:, 10:15].reset_index(drop=True)

    # Ponemos títulos
    raw_pbp_1.columns = titulos
    raw_pbp_2.columns = titulos
    raw_pbp_3.columns = titulos

    # Creamos el dataframe limpio
    PbP = pd.concat([raw_pbp_1, raw_pbp_2, raw_pbp_3], axis=0, ignore_index=True)
    PbP = PbP.dropna(how='all')

    # Eliminar filas de cambio de cuarto
    caracteres_a_eliminar = ['---', '-', '===']
    PbP = PbP[~PbP['Jug A'].isin(caracteres_a_eliminar)]

    # Rellenamos los minutos en qué sucede cada jugada
    PbP['Min'] = PbP['Min'].fillna(method='ffill').astype(object)

    # Rellenamos los TL que no tienen lanzador
    for index, row in PbP.iterrows():
        if pd.isna(row['Jug A']) and pd.notna(row['Anotación A']):  # Equipo A
            PbP.at[index, 'Jug A'] = PbP.at[index-1, 'Jug A']

        if pd.isna(row['Jug B']) and pd.notna(row['Anotación B']):  # Equipo B
            PbP.at[index, 'Jug B'] = PbP.at[index-1, 'Jug B']

    return PbP


def crea_boxscore(equipo_a, equipo_b):
    """
        Creamos el dataframe vacío con los títulos

        Retorna:
        Boxscore (Dataframe): Boxscore vacío. Número, Puntos, 2p, 3p, TL intentados, TL anotados
    """
    numeros = equipo_a['Número']
    cuarto = equipo_a['Q1']
    filas_vacias = (numeros.eq('--') | cuarto.eq('--'))  # Eliminamos las filas del entrenador
    numeros_a = pd.to_numeric(numeros[~filas_vacias])
    boxscore_A = pd.DataFrame({'Número': numeros_a},
                              columns=['Número', 'Puntos', '2P', '3P', 'TL fallados', 'TL anotados'])

    numeros = equipo_b['Número']
    cuarto = equipo_b['Q1']
    filas_vacias = (numeros.eq('--') | cuarto.eq('--'))
    numeros_b = pd.to_numeric(numeros[~filas_vacias])
    boxscore_B = pd.DataFrame({'Número': numeros_b},
                              columns=['Número', 'Puntos', '2P', '3P', 'TL fallados', 'TL anotados'])

    return boxscore_A, boxscore_B


def tl_fallados(pbp, boxscore_a, boxscore_b):
    """
        Actualiza el boxscore con los TL fallados por cada jugadora

        Argumentos:
        pbp (Dataframe): Raw pbp que saca la función extraer_datos()
        boxscore (Dataframe): Boxscore vacío.

        Retorna:
        pbp (Dataframe): Play by Play actualizado sin TL fallados
        boxscore (Dataframe): Boxscore actualizado con los TL fallados (dorsal jugadora y cantidad de TL fallados)
    """

    # Encontrar las celdas que tienen el valor '-'
    tl_fallados_A = pbp.loc[pbp['Anotación A'] == '-']
    pbp = pbp.drop(tl_fallados_A.axes[0])  # Eliminamos los TL fallados del Play by Play
    tl_fallados_A = tl_fallados_A[['Jug A']].value_counts()  # Cuenta los tiros libre fallados por cada jugadora

    tl_fallados_B = pbp.loc[pbp['Anotación B'] == '-']
    pbp = pbp.drop(tl_fallados_B.axes[0])
    tl_fallados_B = tl_fallados_B[['Jug B', 'Anotación B']].value_counts()

    # Metemos los TL fallados en el boxscore TODO: Optimizar
    for fila in tl_fallados_A.index:
        jugadora = int(fila[0])
        fila_boxscore = (boxscore_a['Número'] == jugadora)
        boxscore_a.loc[fila_boxscore, 'TL fallados'] = tl_fallados_A[fila]

    for fila in tl_fallados_B.index:
        jugadora = int(fila[0])
        fila_boxscore = (boxscore_b['Número'] == jugadora)
        boxscore_b.loc[fila_boxscore, 'TL fallados'] = tl_fallados_B[fila]

    return pbp, boxscore_a, boxscore_b


def tipo_anotacion(pbp):
    """
        Calcula la diferencia entre dos anotaciones consecutivas de los equipos para saber ...
        qué tipo de tiro se ha anotado (2P, 3P, TL)

        Argumentos:
        pbp (Dataframe): Pbp limpio, sin los TL fallados

        Retorna:
        pbp (Dataframe): Play by Play con valor de la anotación
    """

    # Creamos una fila inicial con marcador 0-0
    fila_0 = pd.DataFrame({'Jug A': [np.nan], 'Anotación A': [0], 'Min': [0], 'Jug B': [np.nan], 'Anotación B': [0]},
                          index=[0])
    pbp = pd.concat([fila_0, pbp]).reset_index(drop=True)

    # Hacemos la diferencia entre anotaciones para saber de qué tipo ha sido la canasta (2p, 3p, TL)
    pbp['Anotación A'] = pbp['Anotación A'].fillna(method='ffill')  # Cambiamos NaN por úiltimo valor anotado
    pbp['Anotación A'] = pd.to_numeric(pbp['Anotación A'], errors='coerce')  # Convertimos las filas a números
    pbp['Anotación A'] = pbp['Anotación A'].diff()  # Calcular diferencia entre la anotación actual y la acumulada

    pbp['Anotación B'] = pbp['Anotación B'].fillna(method='ffill')
    pbp['Anotación B'] = pd.to_numeric(pbp['Anotación B'], errors='coerce')
    pbp['Anotación B'] = pbp['Anotación B'].diff()

    return pbp


def actualiza_boxscore(pbp, boxscore, equipo='A'):
    """
        Actualiza el boxscore con las anotaciones de las jugadoras del equipo seleccionado.

        Argumentos:
        pbp (Dataframe): Pbp con el tipo de anotaciónd e cada jugadora (el que saca la función tipo_anotacion() )
        equipo (str): 'A', 'B'. Default 'A'. Equipo del que queremos sacar el boxscore

        Retorna:
        boxscore (Dataframe): Boxscore actualizado con el número de anotaciones de cada jugadora del equipo
    """

    # Sacamos el tipo de anotación para cada jugadora
    if equipo == 'A':
        anotaciones = pbp[['Jug A', 'Anotación A']].value_counts()
    else:
        anotaciones = pbp[['Jug B', 'Anotación B']].value_counts()

    # Actualizamos el boxscore con estos datos
    for fila in anotaciones.index:
        jugadora = int(fila[0])
        tipo_lanzamiento = fila[1]
        fila_boxscore = (boxscore['Número'] == jugadora)
        if tipo_lanzamiento == 2.0:
            boxscore.loc[fila_boxscore, '2P'] = anotaciones[fila]
        elif tipo_lanzamiento == 1.0:
            boxscore.loc[fila_boxscore, 'TL anotados'] = anotaciones[fila]
        elif tipo_lanzamiento == 3.0:
            boxscore.loc[fila_boxscore, '3P'] = anotaciones[fila]

    # Reemplazar NaN por 0
    boxscore = boxscore.fillna(0).infer_objects(copy=False)

    # Sumamos puntos totales
    suma_puntos(boxscore)

    return boxscore


def suma_puntos(boxscore):
    """
    Lee el boxscore suma los puntos para cada jugadora.

    Argumentos:
    Boxscore (Dataframe): Boxscore de un equipo, con los tiros de 2P, 3P y TL rellenados, pero sin los puntos totales

    Retorna:
    Boxscore (Dataframe): Boxscore los puntos totales de cada jugadora
    """

    # Rellenar la columna de puntos totales
    for index, jugadora in boxscore.iterrows():
        dos  = jugadora['2P']
        tres = jugadora['3P']
        TL   = jugadora['TL anotados']

        puntos = 2 * dos + 3 * tres + 1 * TL
        boxscore.loc[index, 'Puntos'] = puntos

    return boxscore
