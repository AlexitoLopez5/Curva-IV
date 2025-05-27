# ---------- Importamos las librerías necesarias ----------
import os
import fastf1
import pandas as pd
from datetime import datetime
from sklearn.preprocessing import LabelEncoder

# ---------- Configuración inicial ----------

# Usa solo consultas de fastf1
fastf1.ergast.Ergast.disabled = True
year = 2025

# Carpeta para cachear datos descargados
cache_path = os.path.expanduser("~/cache_f1")
os.makedirs(cache_path, exist_ok=True)

# Activar cache en fastf1 para mejorar rendimiento
fastf1.Cache.enable_cache(cache_path)

# Carpeta donde se guardarán los CSV para Grafana
grafana_dir = "/var/lib/grafana/csv"


# ---------- Diccionarios para desempate absoluto ----------

# Prioridad para pilotos (número menor = mayor prioridad)
PRIORIDAD_PILOTOS = {
    'Max Verstappen': 1, 'Lewis Hamilton': 2, 'Fernando Alonso': 3,
    'Lando Norris': 4, 'George Russell': 5, 'Charles Leclerc': 6,
    'Carlos Sainz': 7, 'Oscar Piastri': 8, 'Sergio Pérez': 9,
    'Yuki Tsunoda': 10
}

# Prioridad para equipos (similar a pilotos)
PRIORIDAD_EQUIPOS = {
    'Red Bull Racing': 1, 'Mercedes': 2, 'Ferrari': 3,
    'McLaren': 4, 'Aston Martin': 5, 'Alpine': 6,
    'Williams': 7, 'Visa RB': 8, 'Kick Sauber': 9,
    'Haas F1 Team': 10
}


# ---------- Función para verificar permisos y existencia del directorio de salida ----------

def verificar_directorio():
    if not os.path.exists(grafana_dir):
        os.makedirs(grafana_dir, exist_ok=True)

    test_file = os.path.join(grafana_dir, 'test.tmp')
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return True
    except PermissionError:
        print(f"Error de permisos en {grafana_dir}")
        return False


# ---------- Función para obtener todas las rondas de carreras ya disputadas hasta hoy ----------

def obtener_carreras():
    try:
        # Obtiene calendario de la temporada
        calendario = fastf1.get_event_schedule(year)
        hoy = datetime.now().date()
        return calendario[calendario['EventDate'].dt.date <= hoy]['RoundNumber'].tolist()
    except Exception as e:
        print(f"Error obteniendo calendario: {e}")
        return []


# ---------- Función que calcula rankings de podios (pilotos o equipos) ----------

def calcular_rankings(podios, es_piloto=True):

    # Convierte la lista de podios a DataFrame con una columna 'Nombre'
    df = pd.DataFrame(podios, columns=['Nombre'])

    # Asigna la posición en el podio basado en el índice del DataFrame
    df['PosicionPodio'] = (df.index % 3) + 1

    # Cuenta total de podios por nombre
    total_podios = df['Nombre'].value_counts().reset_index()
    total_podios.columns = ['Nombre', 'TotalPodios']

    # Cuenta de primeros lugares
    primeros = df[df['PosicionPodio'] ==
                  1]['Nombre'].value_counts().reset_index()
    primeros.columns = ['Nombre', 'PrimerosLugares']

    # Cuenta de segundos lugares
    segundos = df[df['PosicionPodio'] ==
                  2]['Nombre'].value_counts().reset_index()
    segundos.columns = ['Nombre', 'SegundosLugares']

    # Combina todos los conteos en un solo DataFrame
    ranking = total_podios.merge(primeros, on='Nombre', how='left')
    ranking = ranking.merge(segundos, on='Nombre', how='left')

    # Rellena valores NaN con 0 (por si alguien no tiene segundos o primeros lugares)
    ranking.fillna(0, inplace=True)

    # Convierte columnas a enteros
    ranking['TotalPodios'] = ranking['TotalPodios'].astype(int)
    ranking['PrimerosLugares'] = ranking['PrimerosLugares'].astype(int)
    ranking['SegundosLugares'] = ranking['SegundosLugares'].astype(int)

    # Selecciona la prioridad correspondiente para desempatar
    prioridad = PRIORIDAD_PILOTOS if es_piloto else PRIORIDAD_EQUIPOS

    # Mapea la prioridad en la columna 'Prioridad'
    ranking['Prioridad'] = ranking['Nombre'].map(prioridad).fillna(99)

    # Ordena el ranking
    ranking = ranking.sort_values(
        by=['TotalPodios', 'PrimerosLugares', 'SegundosLugares', 'Prioridad'],
        ascending=[False, False, False, True]
    )

    return ranking


# ---------- Función principal ----------

def main():
    # Verifica que el directorio de salida esté accesible y se pueda escribir
    if not verificar_directorio():
        return

    # Obtiene lista de rondas disputadas hasta hoy
    rondas = obtener_carreras()
    if not rondas:
        return

    podios_pilotos = []  # Lista para guardar nombres de pilotos que subieron al podio
    podios_equipos = []   # Lista para guardar nombres de equipos en podio

    # Recorre cada ronda para extraer los resultados
    for ronda in rondas:
        try:
            carrera = fastf1.get_session(year, ronda, 'R')
            carrera.load(telemetry=False, weather=False)
            resultados = carrera.results.sort_values(
                'Position').head(3)  # Top 3 pilotos

            # Agrega pilotos y equipos a sus listas de podios
            for _, fila in resultados.iterrows():
                podios_pilotos.append(fila['FullName'])
                podios_equipos.append(fila['TeamName'])
        except Exception as e:
            print(f"Error en ronda {ronda}: {e}")

    # Calcula los rankings ordenados de pilotos y equipos con base en podios
    ranking_pilotos = calcular_rankings(podios_pilotos, es_piloto=True)
    ranking_equipos = calcular_rankings(podios_equipos, es_piloto=False)

    # Total de carreras disputadas, usado para calcular porcentaje de podios
    rondas_totales = len(rondas)

    # Función para guardar CSV con los top 3 y sus porcentajes
    def guardar_csv(df, tipo):
        df['Porcentaje'] = (df['TotalPodios'] /
                            (rondas_totales * 3) * 100).round().astype(int)

        # Ajusta porcentajes para evitar empates
        for i in range(1, len(df)):
            if df.iloc[i]['Porcentaje'] == df.iloc[i-1]['Porcentaje']:
                df.at[i, 'Porcentaje'] = df.iloc[i]['Porcentaje'] - 1

        # Guarda solo columnas Nombre y Porcentaje del top 3 en CSV en la carpeta Grafana
        df[['Nombre', 'Porcentaje']].head(3).to_csv(
            os.path.join(grafana_dir, f'top3_{tipo}.csv'),
            index=False
        )

        # Muestra por consola el top 3 generado
        print(f"\nTop 3 {tipo}:")
        print(df.head(3)[['Nombre', 'Porcentaje']])

    # Guardamos CSV para pilotos y escuderías
    guardar_csv(ranking_pilotos, 'pilotos')
    guardar_csv(ranking_equipos, 'escuderias')


if __name__ == "__main__":
    print("Calculando podios F1 2025...")
    main()
    print("Proceso completado")
