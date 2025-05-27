# ---------- Importamos las librerías necesarias ----------
import fastf1
import csv
import os
from datetime import datetime


# ---------- Configuración inicial ----------

# Activamos la caché de la API para usar sus datos
fastf1.Cache.enable_cache('cache_f1')


# ---------- Preparamos la ruta de salida ----------

# Definimos la ruta donde se guardará el archivo CSV
output_dir = os.path.expanduser('/home/usuario/CurvaIV/datos/resultados')
os.makedirs(output_dir, exist_ok=True)
filename = os.path.join(output_dir, 'coches.csv')
if os.path.exists(filename):
    os.remove(filename)


# ---------- Obtenemos los datos del evento de tests ----------

# Establecemos el año y la ronda de test
año = 2025
ronda = 1

try:
    # Cargamos la sesión de entrenamientos libres 1
    session = fastf1.get_session(año, ronda, 'FP1')
    session.load()  # Carga los datos de la sesión

    # Creamos un diccionario para almacenar el mejor tiempo por equipo
    mejores_tiempos = {}

    # Recorremos cada piloto único que participó en la sesión
    for drv in session.laps['Driver'].unique():
        # Seleccionamos la vuelta más rápida del piloto
        driver_laps = session.laps.pick_driver(drv).pick_fastest()

        # Obtenemos el equipo y el tiempo de esa vuelta
        equipo = driver_laps['Team']
        tiempo = driver_laps['LapTime'].total_seconds()

        # Verificamos si es el mejor tiempo del equipo o si es más rápido que el anterior
        if equipo not in mejores_tiempos or tiempo < mejores_tiempos[equipo]['tiempo']:
            mejores_tiempos[equipo] = {
                'tiempo': tiempo,
                'piloto': session.get_driver(drv)['FullName']
            }

    # ---------- Ordenamos los equipos según el mejor tiempo ----------

    # Creamos un ranking ordenado por tiempo más rápido (menor a mayor)
    ranking = sorted(mejores_tiempos.items(), key=lambda x: x[1]['tiempo'])

    # ---------- Exportamos los resultados a un archivo CSV ----------

    # Hacemos el archivo CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Posición', 'Equipo', 'Piloto', 'Mejor Tiempo (s)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Escribimos cada entrada del ranking con su posición
        for i, (equipo, datos) in enumerate(ranking, start=1):
            writer.writerow({
                'Posición': i,
                'Equipo': equipo,
                'Piloto': datos['piloto'],
                'Mejor Tiempo (s)': round(datos['tiempo'], 3)
            })

    # Confirmamos que todo se ha completado correctamente
    print(f"Coches completado")

except Exception as e:
    print(f"Error al cargar datos de test: {str(e)}")
