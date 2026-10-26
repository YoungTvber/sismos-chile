# Datos

## Archivo
`sismos_chile_usgs_2000_2024.csv` (6.460 registros, 22 columnas).

## Procedencia
Catálogo sísmico del USGS (Earthquake Hazards Program, ComCat), magnitud 4,5 o superior.
El archivo global (2000-2024) fue obtenido desde el repositorio público
https://github.com/nadeeshafdo/SeismicDataWorldwide (archivo `query_M4.5+_2000-2024.csv`),
que lo reproduce desde el USGS. Fecha de consulta: 25/10/2026.

Fuente original verificable: https://earthquake.usgs.gov/fdsnws/event/1/

## Procesamiento aplicado
Único filtro: se conservaron las filas cuyo campo `place` contiene la palabra "Chile".
No se modificó ningún valor.

## Cómo obtener los datos de nuevo
1. Descargar `query_M4.5+_2000-2024.csv` del repositorio indicado.
2. Filtrar con pandas:
   `d[d["place"].str.contains("Chile", na=False)]`
3. Guardar en esta carpeta como `sismos_chile_usgs_2000_2024.csv`.

## Condiciones de uso
Los datos del USGS son información del gobierno de EE. UU. de dominio público;
se solicita citar al USGS como fuente.
