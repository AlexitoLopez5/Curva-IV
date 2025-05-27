
# CurvaIV - Manual de Uso

## Descripción

Sistema de análisis y predicción para carreras de Fórmula 1 que utiliza datos históricos, rendimiento en clasificación, estadísticas de pilotos y características específicas de cada circuito.

## Requisitos

- Python 3.8 o superior

- Librerías requeridas:
  - pandas
  - numpy
  - scikit-learn
  - scipy
  - fastf1

## Instalación

Instalar dependencias:
pip install -r requirements.txt

Configurar caché (se creará automáticamente):
mkdir -p ~/cache_f1

## Uso básico

1. Obtener datos actualizados

Ejecutar en orden los siguientes scripts:
python3 script_coches.py
python3 script_qualy.py
python3 script_carreras.py

Estos scripts generarán archivos CSV en la carpeta `datos/resultados/`.

2. Ejecutar predicción (dentro de la carpeta datos/resultados/)
python3 prediccion.py

3. Ejecutar top3
python3 top3.py

El sistema mostrará una lista de circuitos disponibles y pedirá que selecciones uno. Tras la selección, mostrará las probabilidades de victoria para el top 10 de pilotos.

## Configuración avanzada

### Pesos por circuito

Los pesos para cada factor de predicción pueden modificarse en el diccionario `PESOS_POR_CIRCUITO` dentro de `prediccion.py`. Los factores son:

- `score_qualy`: Rendimiento en clasificación
- `score_carrera`: Rendimiento en carrera
- `score_coche`: Calidad del coche
- `score_experiencia`: Experiencia del piloto
- `score_habilidad`: Habilidad del piloto

### Integración con Grafana

El sistema incluye funcionalidad para exportar datos a Grafana.

## Documentación adicional

Para información más detallada sobre el modelo de predicción y configuración avanzada, consultar:

- Documentación técnica --> https://docs.google.com/document/d/1dCcHLazCRbmN9t3WfoXzH3etcIwDLetWYj1NxkhoNGM/edit?usp=sharing
- Sitio web del proyecto --> https://curvaiv.zapto.org

## Licencia

Este proyecto es software libre y de código abierto (open source).  
Podéis usarlo, modificarlo y redistribuirlo sin restricciones.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abra un issue o envíe un pull request con sus mejoras.
