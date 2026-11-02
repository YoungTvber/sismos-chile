# Análisis de sismicidad en Chile (2000-2024)

Proyecto Final Integrador - Programación Avanzada (Ing. Civil Plan Común, Sede Temuco).
Avance 1: problema, fuente de datos, pipeline y carga inicial.
Avance 2: diagnóstico de calidad, limpieza, tratamiento de nulos, transformaciones y validación.

## Pregunta del proyecto
¿La frecuencia anual de los sismos de magnitud 4,5 o superior en Chile aumenta o disminuye
entre 2000 y 2024, y cambia según la magnitud?

## Estructura
```
datos/
  originales/   conjunto original del USGS (no se modifica)
  procesados/   dataset_limpio.csv (resultado del pipeline)
reportes/       avance_1.pdf, avance_2.pdf y registro_limpieza.txt
src/
  carga.py            lectura y exportación
  limpieza.py         nombres, texto, duplicados, área de estudio y nulos
  transformaciones.py conversión de tipos y variables nuevas
  validaciones.py     diagnóstico y validación de columnas, tipos y rangos
main.py               ejecuta el pipeline completo
```

## Requisitos
- Python 3.9 o superior
- Dependencias: `pip install -r requirements.txt`

## Ejecución
Desde la raíz del proyecto:
```
python main.py
```
El programa sigue este orden: carga, diagnóstico, limpieza, tratamiento de nulos,
transformaciones, validación y exportación. Genera `datos/procesados/dataset_limpio.csv`
y `reportes/registro_limpieza.txt`, sin modificar el archivo original.

## Fuente de datos
USGS Earthquake Catalog (ComCat). Detalles en `datos/README.md`.

## Repositorio
https://github.com/YoungTvber/sismos-chile

## Integrantes
- Benjamin Agurto
- Maximiliano Segovia
- Cristóbal Fernández
