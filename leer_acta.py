import functions as fcbq

# Archivo que vamos a leer
acta = '/Users/arnaubarrera/Desktop/Sports Analyitics/Stats PreInf A/Actes/CNT vs Lima-Horta.pdf'
# acta = '/Users/arnaubarrera/Desktop/Sports Analyitics/Stats PreInf A/Actes/CNT vs Xamba.pdf'
# acta = '/Users/arnaubarrera/Desktop/Sports Analyitics/Stats PreInf A/Actes/Bufalà vs CNT.pdf'

# Leemos los datos del acta en PDF
[equipo_A, equipo_B, raw_pbp] = fcbq.extraer_datos(acta)

# Creamos Boxscore vacío (Número, Puntos, 2p, 3p, TL intentados, TL anotados)
[boxscore_A, boxscore_B] = fcbq.crea_boxscore(equipo_A, equipo_B)

# Actualizamos boxscore con TL fallados y los eliminamos del PbP
[pbp, boxscore_A, boxscore_B] = fcbq.tl_fallados(raw_pbp, boxscore_A, boxscore_B)

# Limpiamos el PbP dejando solo el número de la jugadora y el tipo de anotación
pbp = fcbq.tipo_anotacion(pbp)

# Actualizamos el boxscore con el número de anotaciones de cada jugadora
boxscore_A = fcbq.actualiza_boxscore(pbp, boxscore_A, 'A')
boxscore_B = fcbq.actualiza_boxscore(pbp, boxscore_B, 'B')

print('Finished')
