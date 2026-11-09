"""Lectura, inspección inicial y exportación de los datos de sismos de Chile (USGS)."""

import os

import pandas as pd


def cargar_datos(ruta):
    """
    Carga un conjunto de datos desde un archivo CSV.

    Parámetros
    ----------
    ruta : str
        Ruta (relativa a la raíz del proyecto) del archivo.

    Retorna
    -------
    pandas.DataFrame o None
        DataFrame con los datos cargados; None si ocurre un error.
    """
    try:
        datos = pd.read_csv(ruta)
        return datos
    except FileNotFoundError:
        print(f"Error: no se encontró el archivo '{ruta}'.")
    except pd.errors.EmptyDataError:
        print("Error: el archivo no contiene datos.")
    except pd.errors.ParserError:
        print("Error: no fue posible interpretar el archivo.")
    except UnicodeDecodeError:
        print("Error: la codificación del archivo no es compatible.")
    return None


def cargar_dataset_limpio(ruta):
    """
    Carga el dataset limpio del Avance 2 y reconstruye la columna de fecha.

    El CSV guarda las fechas como texto (algunas con fracciones de segundo y
    otras sin ellas), por eso se interpretan con el formato ISO 8601.
    """
    datos = cargar_datos(ruta)
    if datos is None:
        return None
    try:
        datos["fecha_hora"] = pd.to_datetime(datos["fecha_hora"], utc=True, format="ISO8601")
    except (ValueError, TypeError):
        # versiones antiguas de pandas no conocen format="ISO8601"
        datos["fecha_hora"] = pd.to_datetime(datos["fecha_hora"], utc=True)
    return datos


def inspeccionar_datos(datos):
    """Muestra por consola una inspección inicial del DataFrame (Avance 1)."""
    if datos is None:
        print("No existen datos disponibles para inspeccionar.")
        return

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)

    print("\nDimensiones:")
    print(datos.shape)
    print("\nColumnas:")
    print(datos.columns.tolist())
    print("\nTipos de datos:")
    print(datos.dtypes)
    print("\nPrimeros registros:")
    print(datos.head())
    print("\nValores nulos por columna:")
    print(datos.isna().sum())
    print("\nFilas duplicadas:")
    print(datos.duplicated().sum())
    print("\nResumen estadístico:")
    print(datos.describe(include="all"))


def exportar_datos(datos, ruta):
    """
    Guarda el DataFrame procesado en un CSV sin tocar el archivo original.

    Retorna True si se pudo guardar, False en caso contrario.
    """
    try:
        carpeta = os.path.dirname(ruta)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)
        datos.to_csv(ruta, index=False, encoding="utf-8")
        return True
    except OSError as error:
        print(f"Error: no fue posible guardar '{ruta}': {error}")
        return False
