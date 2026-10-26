# Análisis de sismicidad en Chile (2000-2024)

Proyecto Final Integrador - Programación Avanzada (Ing. Civil Plan Común, Sede Temuco).
Avance 1: definición del problema, fuente de datos, diseño del pipeline, carga e inspección inicial.

## Pregunta del proyecto
¿Cómo se distribuyen en el tiempo, el espacio y la profundidad los sismos de magnitud 4,5 o
superior registrados en Chile entre 2000 y 2024, y qué zonas concentran la mayor actividad?

## Estructura
```
datos/      dataset y documentación de su origen
reportes/   informes (avance_1.pdf)
src/        funciones del proyecto (carga.py)
main.py     punto de entrada
```

## Requisitos
- Python 3.9 o superior
- Dependencias: `pip install -r requirements.txt`

## Ejecución
Desde la raíz del proyecto:
```
python main.py
```
Carga el CSV con pandas e imprime dimensiones, columnas, tipos, nulos, duplicados,
resumen estadístico y una revisión básica de calidad.

## Fuente de datos
USGS Earthquake Catalog (ComCat). Detalles en `datos/README.md`.

## Integrantes
Completar con los nombres del equipo.
