"""Carga e inspección inicial del catálogo de sismos de Chile (USGS)."""

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


def inspeccionar_datos(datos):
    """Muestra por consola una inspección inicial del DataFrame."""
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


def revisar_calidad(datos):
    """
    Revisión adicional de problemas esperables en el catálogo sísmico.
    Solo informa; no modifica el DataFrame.
    """
    if datos is None:
        return

    print("\nRevisión de calidad:")
    print("- Identificadores repetidos (id):", datos["id"].duplicated().sum())

    fechas = pd.to_datetime(datos["time"], errors="coerce", utc=True)
    print("- Fechas de 'time' no convertibles:", fechas.isna().sum())
    print("- Tipo actual de 'time':", datos["time"].dtype)

    print("- Magnitudes fuera de [0, 10]:",
          (~datos["mag"].between(0, 10)).sum())
    print("- Profundidades fuera de [0, 700] km:",
          (~datos["depth"].between(0, 700)).sum())
    print("- Latitudes fuera del rango esperado para Chile:",
          (~datos["latitude"].between(-60, -15)).sum())
    print("- Registros con eventos distintos de 'earthquake':",
          (datos["type"] != "earthquake").sum())
    print("- Registros con estado 'automatic' (sin revisión):",
          (datos["status"] == "automatic").sum())

    print("\nTipos de magnitud (magType):")
    print(datos["magType"].value_counts())
