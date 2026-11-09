# Análisis de sismicidad en Chile (2000-2024)

Proyecto Final Integrador - Programación Avanzada (Ing. Civil Plan Común, Sede Temuco).
- Avance 1: problema, fuente de datos, pipeline y carga inicial.
- Avance 2: diagnóstico de calidad, limpieza, tratamiento de nulos y transformaciones.
- Avance 3: estadística descriptiva, indicadores automatizados y gráficos.

## Pregunta del proyecto
¿La frecuencia anual de los sismos de magnitud 4,5 o superior en Chile aumenta o disminuye
entre 2000 y 2024, y cambia según la magnitud?

## Estructura
```
datos/
  originales/   conjunto original del USGS (no se modifica)
  procesados/   dataset_limpio.csv (resultado de la limpieza)
resultados/
  estadisticas.csv      estadísticas descriptivas
  indicadores.csv       indicadores automatizados
  graficos/             grafico_01.png, grafico_02.png, grafico_03.png
reportes/       avance_1.pdf, avance_2.pdf, avance_3.pdf y registro_limpieza.txt
src/
  carga.py              lectura y exportación
  limpieza.py           nombres, texto, duplicados, área de estudio y nulos
  transformaciones.py   conversión de tipos y variables nuevas
  validaciones.py       diagnóstico, validación y verificación de cálculos
  procesamiento.py      pipeline de limpieza del Avance 2
  estadisticas.py       estadística descriptiva
  indicadores.py        indicadores automatizados
  visualizaciones.py    gráficos con Pyplot
main.py                 ejecuta el análisis del Avance 3
```

## Requisitos
- Python 3.9 o superior
- Dependencias: `pip install -r requirements.txt` (pandas, numpy y matplotlib)

## Ejecución
Desde la raíz del proyecto:
```
python main.py
```
El programa carga `datos/procesados/dataset_limpio.csv`, calcula las estadísticas y los
indicadores, genera los tres gráficos y verifica los cálculos. Los resultados quedan en
`resultados/`. Si el dataset limpio no existe, ejecuta antes la limpieza del Avance 2.

Para repetir solo la limpieza (Avance 2):
```
python main.py limpieza
```

## Resultados principales
- 6.014 sismos analizados; 10 indicadores y 3 gráficos generados automáticamente.
- La mediana anual de sismos sube de 146,5 a 197,5 entre 2000-2011 y 2012-2023, pero la
  tendencia no es concluyente: 2010, 2014 y 2015 concentran los grandes terremotos.

## Fuente de datos
USGS Earthquake Catalog (ComCat). Detalles en `datos/README.md`.

## Repositorio
https://github.com/YoungTvber/sismos-chile

## Integrantes
- Benjamin Agurto
- Maximiliano Segovia
- Cristóbal Fernández
