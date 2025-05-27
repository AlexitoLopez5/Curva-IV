# ---------- Importamos las librerías necesarias ----------
import fastf1
import csv
import os
from datetime import datetime


# ---------- Configuración inicial ----------

# Activamos la caché de la API para usar sus datos
fastf1.Cache.enable_cache('cache_f1')


# ---------- Definimos el calendario oficial de F1 2025 ----------

# Lista completa de carreras con sus nombres en español y fechas
CALENDARIO_2025 = [
    {"nombre": "Australia", "fecha": datetime(2025, 3, 16)},
    {"nombre": "China", "fecha": datetime(2025, 3, 23)},
    {"nombre": "Japón", "fecha": datetime(2025, 4, 6)},
    {"nombre": "Bahréin", "fecha": datetime(2025, 4, 13)},
    {"nombre": "Arabia Saudí", "fecha": datetime(2025, 4, 20)},
    {"nombre": "Miami", "fecha": datetime(2025, 5, 4)},
    {"nombre": "Emilia Romaña", "fecha": datetime(2025, 5, 18)},
    {"nombre": "Mónaco", "fecha": datetime(2025, 5, 25)},
    {"nombre": "España", "fecha": datetime(2025, 6, 1)},
    {"nombre": "Canadá", "fecha": datetime(2025, 6, 15)},
    {"nombre": "Austria", "fecha": datetime(2025, 6, 29)},
    {"nombre": "Gran Bretaña", "fecha": datetime(2025, 7, 6)},
    {"nombre": "Bélgica", "fecha": datetime(2025, 7, 27)},
    {"nombre": "Hungría", "fecha": datetime(2025, 8, 3)},
    {"nombre": "Países Bajos", "fecha": datetime(2025, 8, 31)},
    {"nombre": "Italia", "fecha": datetime(2025, 9, 7)},
    {"nombre": "Azerbaiyán", "fecha": datetime(2025, 9, 21)},
    {"nombre": "Singapur", "fecha": datetime(2025, 10, 5)},
    {"nombre": "Estados Unidos", "fecha": datetime(2025, 10, 19)},
    {"nombre": "México", "fecha": datetime(2025, 10, 26)},
    {"nombre": "São Paulo", "fecha": datetime(2025, 11, 9)},
    {"nombre": "Las Vegas", "fecha": datetime(2025, 11, 22)},
    {"nombre": "Qatar", "fecha": datetime(2025, 11, 30)},
    {"nombre": "Abu Dabi", "fecha": datetime(2025, 12, 7)}
]


# ---------- Función para obtener datos de las últimas carreras ----------

def obtener_ultimas_carreras(num_carreras=3):
    """Obtiene los datos de las últimas carreras completadas antes de la próxima carrera"""

    # Buscamos cuál es la próxima carrera en el calendario
    hoy = datetime.now()
    carreras_pasadas = []

    proxima_idx = None
    for i, carrera in enumerate(CALENDARIO_2025):
        if carrera["fecha"] > hoy:
            proxima_idx = i
            break

    # Determinamos qué carreras debemos analizar
    if proxima_idx is None:
        carreras_a_buscar = CALENDARIO_2025[-num_carreras:]
    else:
        inicio = max(0, proxima_idx - num_carreras)
        carreras_a_buscar = CALENDARIO_2025[inicio:proxima_idx]

    # Procesamos cada carrera seleccionada
    carreras_validas = []
    for carrera in reversed(carreras_a_buscar):
        try:
            session = fastf1.get_session(2025, carrera["nombre"], 'R')
            session.load(telemetry=False, weather=False)

            # Guardamos la información relevante
            carreras_validas.append({
                'nombre': carrera['nombre'],
                'fecha': carrera["fecha"],
                'session': session
            })
        except Exception as e:
            print(f" Error al cargar {carrera['nombre']}: {str(e)}")
            continue

    return carreras_validas


# ---------- Función para exportar resultados a CSV ----------

def exportar_resultados(carreras, filename):
    """Guarda los resultados de las carreras en un archivo CSV"""

    # Definimos las columnas del CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
            'Posición',
            'Gran Premio',
            'Fecha',
            'Piloto',
            'Equipo'
        ])
        writer.writeheader()

        # Procesamos cada carrera
        for carrera in carreras:
            fecha_str = carrera['fecha'].strftime(
                '%d/%m/%Y')

            # Escribimos los resultados de cada piloto
            for _, driver in carrera['session'].results.iterrows():
                writer.writerow({
                    'Posición': int(driver.Position),
                    'Gran Premio': carrera['nombre'],
                    'Fecha': fecha_str,
                    'Piloto': driver.FullName,
                    'Equipo': driver.TeamName
                })

            writer.writerow({})


# ---------- Función principal ----------

def main():
    print("\n🔍 Buscando resultados de las últimas carreras...")

    # Obtenemos datos de las últimas 3 carreras
    ultimas_carreras = obtener_ultimas_carreras(3)

    if not ultimas_carreras:
        print(" No se encontraron datos de carreras recientes")
        return

    # Configuramos la ruta de salida
    output_dir = os.path.expanduser('/home/usuario/CurvaIV/datos/resultados')

    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, 'ultimas_carreras.csv')

    if os.path.exists(filename):
        os.remove(filename)

    # Exportamos los nuevos resultados
    exportar_resultados(ultimas_carreras, filename)

    print("\n Resultados exportados exitosamente")
    print(f" Archivo: {filename}")


if __name__ == "__main__":
    main()
