# ---------- Importamos las librerías necesarias para el análisis de datos ----------
import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler, MinMaxScaler
from sklearn.utils.validation import check_array
from scipy import stats


# ---------- Definimos los pesos para cada circuito ----------

#               [score_qualy, score_carrera, score_coche, score_experiencia, score_habilidad]
PESOS_POR_CIRCUITO = {

    # Circuitos donde la qualy es lo más importante
    "Bakú":                       [0.40, 0.10, 0.25, 0.05, 0.20],
    "Hungaroring":                [0.35, 0.15, 0.25, 0.05, 0.20],
    "Jeddah":                    [0.35, 0.15, 0.25, 0.05, 0.20],
    "Marina Bay":                 [0.38, 0.12, 0.25, 0.05, 0.20],
    "Montecarlo":                 [0.80, 0.05, 0.10, 0.02, 0.03],

    # Circuitos donde el rendimiento en carrera es más importante
    "Interlagos":                 [0.30, 0.20, 0.25, 0.05, 0.20],
    "Red Bull Ring":              [0.30, 0.20, 0.25, 0.05, 0.20],
    "Silverstone":                [0.28, 0.22, 0.25, 0.05, 0.20],
    "Spa-Francorchamps":          [0.25, 0.25, 0.25, 0.05, 0.20],

    # Circuitos estándar con equilibrio entre qualy y carrera
    "Barcelona-Catalunya":        [0.33, 0.17, 0.25, 0.05, 0.20],
    "Circuit of the Americas (COTA)": [0.32, 0.18, 0.25, 0.05, 0.20],
    "Imola":                     [0.35, 0.15, 0.25, 0.05, 0.20],
    "Las Vegas Street Circuit":  [0.38, 0.12, 0.25, 0.05, 0.20],
    "Lusail":                    [0.30, 0.20, 0.25, 0.05, 0.20],
    "Melbourne":                 [0.32, 0.18, 0.25, 0.05, 0.20],
    "Miami":                     [0.35, 0.15, 0.25, 0.05, 0.20],
    "Monza":                     [0.30, 0.20, 0.25, 0.05, 0.20],
    "Montreal":                  [0.35, 0.15, 0.25, 0.05, 0.20],
    "Shanghái":                  [0.33, 0.17, 0.25, 0.05, 0.20],
    "Suzuka":                    [0.35, 0.15, 0.25, 0.05, 0.20],
    "Yas Marina":                [0.32, 0.18, 0.25, 0.05, 0.20],
    "Zandvoort":                 [0.35, 0.15, 0.25, 0.05, 0.20],
    "Hermanos Rodríguez":        [0.32, 0.18, 0.25, 0.05, 0.20],

    # Por defecto
    "default":                   [0.30, 0.20, 0.25, 0.05, 0.20]
}


# ---------- Función para cargar los datos desde los archivos CSV ----------

def cargar_datos():

    # Leemos los CSV con datos
    df_carreras = pd.read_csv("ultimas_carreras.csv").dropna(how='all')
    df_coches = pd.read_csv("coches.csv")
    df_qualy = pd.read_csv("qualy.csv")

    # Asignamos un valor a la experiencia, talento y cosistencia a cada piloto
    pilotos = ['M. Verstappen', 'L. Norris', 'O. Piastri', 'C. Leclerc', 'G. Russell',
               'K. Antonelli', 'L. Hamilton', 'I. Hadjar', 'A. Albon', 'O. Bearman',
               'F. Alonso', 'Y. Tsunoda', 'P. Gasly', 'C. Sainz Jr.', 'F. Colapinto',
               'N. Hulkenberg', 'L. Lawson', 'E. Ocon', 'G. Bortoleto', 'L. Stroll']
    experiencia = [16, 5, 2, 6, 5, 0, 17, 0,
                   5, 1, 20, 4, 7, 9, 0, 12, 1, 7, 0, 7]
    talento = [20, 15, 12, 19, 18, 10, 14, 9, 16,
               11, 20, 13, 14, 17, 8, 12, 9, 14, 7, 10]
    consistencia = [20, 12, 9, 16, 17, 8, 20, 7,
                    15, 9, 18, 10, 13, 14, 6, 11, 8, 13, 5, 9]

    # Creamos un DataFrame con los datos de los pilotos
    df_pilotos = pd.DataFrame({
        'Piloto': pilotos,
        'Experiencia': experiencia,
        'Talento': talento,
        'Consistencia': consistencia
    })

    # Calculamos estadísticas de las carreras
    stats_carreras = df_carreras.groupby('Piloto')['Posición'].agg(
        media_posicion='mean',
        mejor_posicion='min',
        desviacion_posicion='std',
        carreras_completadas='count'
    ).reset_index()

    # Combinamos todos los datos en un solo DataFrame
    df = df_qualy.merge(
        stats_carreras,
        on='Piloto', how='left'
    ).merge(
        df_coches[['Piloto', 'Mejor Tiempo (s)']],
        on='Piloto', how='left'
    ).merge(
        df_pilotos,
        on='Piloto', how='left'
    )

    return df


# ---------- Función para limpiar y preparar los datos ----------

def preprocesar(df):
    df = df.copy()

    # Rellenamos valores faltantes con valores por defecto
    df['Experiencia'] = df['Experiencia'].fillna(0).astype(int)
    df['Talento'] = df['Talento'].fillna(10).astype(int)
    df['Consistencia'] = df['Consistencia'].fillna(10).astype(int)

    # Rellenamos estadísticas de carrera con el peor caso posible
    max_pos = df['Posición'].max()
    for col in ['media_posicion', 'mejor_posicion']:
        df[col] = df[col].fillna(max_pos)

    # Rellenamos la desviación estándar con la desviación general si falta
    if 'desviacion_posicion' in df.columns:
        df['desviacion_posicion'] = df['desviacion_posicion'].fillna(
            df['Posición'].std())

    # Procesamos los tiempos de vuelta del coche
    df['Mejor Tiempo (s)'] = pd.to_numeric(
        df['Mejor Tiempo (s)'], errors='coerce')
    df['Mejor Tiempo (s)'] = df['Mejor Tiempo (s)'].fillna(
        df['Mejor Tiempo (s)'].median())

    return df


# ---------- Función para calcular los scores de cada piloto ----------

def calcular_scores(df, circuito="default"):

    # Calculamos el score de qualy
    df['score_qualy'] = 1 / df['Posición']

    # Calculamos el score de carrera considerando posición media y consistencia
    df['score_carrera'] = (1 / df['media_posicion']) * \
        (1 / (1 + df.get('desviacion_posicion', 0)))

    # Calculamos el score del coche basado en el mejor tiempo
    df['score_coche'] = 1 / (df['Mejor Tiempo (s)'] ** 0.9)

    # Calculamos el score de experiencia
    df['score_experiencia'] = np.sqrt(df['Experiencia'] + 1)

    # Calculamos el score de habilidad combinando talento y consistencia
    df['score_habilidad'] = (df['Talento'] * 0.8 + df['Consistencia'] * 0.2)

    # Normalizamos los scores para que sean comparables
    features = ['score_qualy', 'score_carrera',
                'score_coche', 'score_experiencia', 'score_habilidad']
    features = [f for f in features if f in df.columns]

    # Aplicamos RobustScaler para reducir el efecto de outliers
    scaler = RobustScaler()
    scores_norm = scaler.fit_transform(df[features])

    # Aplicamos MinMaxScaler para llevar todo a escala 0-1
    minmax = MinMaxScaler()
    scores_norm = minmax.fit_transform(scores_norm)

    # Obtenemos los pesos específicos para este circuito
    pesos = np.array(PESOS_POR_CIRCUITO.get(
        circuito, PESOS_POR_CIRCUITO["default"]))

    # Aseguramos que coincida con las features disponibles
    pesos = pesos[:len(features)]

    # Calculamos el score final combinando todos los scores con los pesos
    df['score_final'] = np.dot(scores_norm, pesos)

    return df


# ---------- Función para generar los resultados finales con probabilidades ----------

def generar_resultados(df):
    # Calculamos las probabilidades de victoria con un suavizado
    df['Probabilidad_Victoria'] = (np.power(df['score_final'], 1.5) /
                                   np.power(df['score_final'], 1.5).sum() * 100).round(1)

    # Creamos el resultado final ordenado y mostramos solo el top 10
    resultado = (df[['Piloto', 'Equipo', 'Probabilidad_Victoria']]
                 .sort_values('Probabilidad_Victoria', ascending=False)
                 .head(10)
                 .reset_index(drop=True))
    resultado.index += 1  # Empezamos el ranking desde 1

    return resultado

# Función para que el usuario seleccione un circuito


def seleccionar_circuito():
    print("Circuitos disponibles:")
    circuitos = sorted(PESOS_POR_CIRCUITO.keys())

    # Mostramos todos los circuitos
    for i, circuito in enumerate(circuitos, 1):
        if circuito != "default":
            print(f"{i}. {circuito}")

    # Bucle para seleccionar el circuito
    while True:
        try:
            seleccion = int(input("\nSeleccione el número del circuito: "))
            if 1 <= seleccion <= len(circuitos)-1:
                return circuitos[seleccion-1]
            else:
                print("Por favor, ingrese un número válido.")
        except ValueError:
            print("Por favor, ingrese un número.")


# ---------- Punto de entrada principal del programa ----------

if __name__ == "__main__":
    print("Calculando probabilidades de victoria...\n")

    try:

        # Seleccionamos el circuito
        circuito = seleccionar_circuito()
        print(f"\nUsando pesos para el circuito: {circuito}\n")

        # Cargamos, procesamos y calculamos los datos
        df = cargar_datos()
        df = preprocesar(df)
        df = calcular_scores(df, circuito=circuito)
        resultado = generar_resultados(df)

        # Mostramos los resultados
        print("TOP 10 PREDICCIONES DE VICTORIA\n")
        print(resultado.to_string())

        # Guardamos los resultados en archivos CSV para Grafana
        resultado.to_csv('/var/lib/grafana/csv/curva4.csv',
                         index_label='Ranking')
        resultado[['Probabilidad_Victoria', 'Piloto']].to_csv(
            '/var/lib/grafana/csv/queso_curva4.csv', index=False)

        print("\nResultados guardados en /var/lib/grafana/csv")

    except Exception as e:
        print(f"\nError: {str(e)}")
