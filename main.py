import os
import sys

import pandas as pd

from src.carga import cargar_dataset_limpio, exportar_datos
from src.estadisticas import calcular_estadisticas
from src.indicadores import calcular_indicadores
from src.procesamiento import ejecutar_limpieza
from src.validaciones import verificar_calculos
from src.visualizaciones import crear_graficos

RUTA_LIMPIO = "datos/procesados/dataset_limpio.csv"
RUTA_ESTADISTICAS = "resultados/estadisticas.csv"
RUTA_INDICADORES = "resultados/indicadores.csv"
CARPETA_GRAFICOS = "resultados/graficos"


def titulo(texto):
    print("\n" + "=" * 60)
    print(texto)
    print("=" * 60)


def main():
    # python main.py limpieza  -> repite solo el pipeline de limpieza (Avance 2)
    if len(sys.argv) > 1 and sys.argv[1] == "limpieza":
        ejecutar_limpieza()
        return

    # El Avance 3 parte del dataset limpio; si no existe, se genera primero.
    if not os.path.exists(RUTA_LIMPIO):
        print("No se encontró el dataset limpio. Se ejecuta la limpieza del Avance 2.")
        ejecutar_limpieza()

    titulo("1. CARGA DEL DATASET LIMPIO")
    datos = cargar_dataset_limpio(RUTA_LIMPIO)
    if datos is None:
        print("El programa finalizó sin procesar los datos.")
        return
    print(f"Registros: {len(datos)} | Variables: {datos.shape[1]}")

    titulo("2. ESTADÍSTICAS DESCRIPTIVAS")
    estadisticas = calcular_estadisticas(datos)
    numericas = estadisticas[estadisticas["tipo"] == "numerica"]
    resumen = numericas.pivot(index="medida", columns="variable", values="valor")
    orden = ["registros", "media", "mediana", "minimo", "maximo", "rango",
             "desviacion_estandar", "cuartil_1", "cuartil_3"]
    pd.set_option("display.width", 200)
    print(resumen.loc[orden].round(2).to_string())
    print("\nFrecuencias (rango de magnitud y zona):")
    for variable in ["rango_magnitud", "zona"]:
        sub = estadisticas[estadisticas["variable"] == variable]
        print(sub[["variable", "medida", "valor", "porcentaje"]].to_string(index=False))
    exportar_datos(estadisticas, RUTA_ESTADISTICAS)
    print(f"\nArchivo generado: {RUTA_ESTADISTICAS}")

    titulo("3. INDICADORES AUTOMATIZADOS")
    indicadores = calcular_indicadores(datos)
    for _, fila in indicadores.iterrows():
        print(f"- {fila['indicador']}: {fila['resultado']}")
    exportar_datos(indicadores, RUTA_INDICADORES)
    print(f"\nArchivo generado: {RUTA_INDICADORES}")

    titulo("4. GRÁFICOS")
    for ruta in crear_graficos(datos, CARPETA_GRAFICOS):
        print(f"Gráfico guardado: {ruta}")

    titulo("5. VERIFICACIÓN DE CÁLCULOS")
    if verificar_calculos(datos, estadisticas, indicadores):
        print("\nTodas las verificaciones se cumplieron.")
    else:
        print("\nAlgunas verificaciones fallaron: revisar los cálculos.")


if __name__ == "__main__":
    main()
