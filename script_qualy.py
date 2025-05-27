# ---------- Importamos las librerías necesarias ----------
import fastf1
import csv
import os
from datetime import datetime


# ---------- Configuración inicial ----------

# Activamos la caché de la API para usar sus datos
fastf1.Cache.enable_cache('cache_f1')


# ---------- Función para obtener la última qualy ----------

def obtener_ultima_qualy():
    """Obtiene la última sesión de clasificación disponible antes de hoy"""

    año_actual = datetime.now().year

    try:
        # Obtenemos el calendario de eventos del año actual
        calendario = fastf1.get_event_schedule(año_actual)

        # Filtramos solo los eventos cuya fecha ya pasó
        eventos_pasados = calendario[calendario['EventDate'] < datetime.now()]

        # Si hay eventos pasados, tomamos el último
        if not eventos_pasados.empty:
            ultimo_evento = eventos_pasados.iloc[-1]
            return año_actual, ultimo_evento.RoundNumber, 'Q'

    except Exception as e:
        print(f" Error al obtener el calendario {año_actual}: {str(e)}")
        pass

    # ---------- Fallback si no se encuentra una qualy previa ----------

    try:
        # Si todo falla, cargamos el calendario de nuevo
        calendario = fastf1.get_event_schedule(año_actual)

        # Devolvemos la última ronda del calendario como emergencia
        return año_actual, calendario.iloc[-1].RoundNumber, 'Q'

    except Exception as e:
        print(f" Error al cargar eventos de fallback: {str(e)}")
        return año_actual, 1, 'Q'


# ---------- Función principal ----------

def main():
    print("\n🔍 Buscando datos de la última sesión de clasificación...")

    # Obtenemos la información de la última qualy
    año, ronda, sesion = obtener_ultima_qualy()

    try:
        session = fastf1.get_session(año, ronda, sesion)
        session.load()

        # Configuramos la ruta de salida
        output_dir = os.path.expanduser(
            '/home/usuario/CurvaIV/datos/resultados')
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, 'qualy.csv')

        if os.path.exists(filename):
            os.remove(filename)

        # Exportamos los resultados
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[
                                    'Posición', 'Piloto', 'Equipo'])
            writer.writeheader()

            for _, driver in session.results.iterrows():
                writer.writerow({
                    'Posición': int(driver.Position),
                    'Piloto': driver.FullName,
                    'Equipo': driver.TeamName
                })

        print("\n Datos de clasificación exportados exitosamente")
        print(f" Archivo: {filename}")

    except Exception as e:
        print(f"\n Error al procesar la sesión: {str(e)}\n")
        exit()


if __name__ == "__main__":
    main()
