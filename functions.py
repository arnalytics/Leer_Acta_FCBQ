# %%
import tabula


# %%

def extraer_datos(acta):
    # Coordenadas de las tablas que queremos extraer [superior, izq, inferior, der]
    area_equip_A = [140, 45, 355, 408]
    area_equip_B = [390, 45, 595, 408]
    area_playBplay = [114, 402, 538, 754]

    # Extraer tablas del PDF y guardarlas en DataFrames
    raw_A = tabula.read_pdf(acta, pages='all', area=area_equip_A);     raw_A = raw_A[0]
    raw_B = tabula.read_pdf(acta, pages='all', area=area_equip_B);     raw_B = raw_B[0]
    raw_pbp = tabula.read_pdf(acta, pages='all', area=area_playBplay); raw_pbp = raw_pbp[0]

    # Limpiamos las tablas de los equipos
    clean_A = limpiar_equipo(raw_A)
    clean_B = limpiar_equipo(raw_B)

    # Limpiamos el Play by Play
    clean_pbp = limpiar_pbp(raw_pbp)

    return clean_A, clean_B, clean_pbp


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


def limpiar_pbp(raw_pbp):

    return 1
