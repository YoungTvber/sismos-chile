"""Transformaciones: conversión de tipos y creación de variables."""

import pandas as pd


def convertir_fecha(datos, registro):
    """Convierte fecha_hora de texto a fecha y hora (UTC)."""
    datos["fecha_hora"] = pd.to_datetime(datos["fecha_hora"], utc=True, errors="coerce")
    registro.append("Transformación: fecha_hora convertida de texto a datetime64 (UTC).")
    return datos


def convertir_tipos(datos, registro):
    """Convierte conteos a entero con nulos y los códigos a categorías."""
    for col in ["n_estaciones", "n_estaciones_magnitud"]:
        datos[col] = datos[col].astype("Int64")
    for col in ["tipo_magnitud", "estado", "tipo_evento", "red"]:
        datos[col] = datos[col].astype("category")
    registro.append("Transformación: n_estaciones y n_estaciones_magnitud a Int64; "
                    "tipo_magnitud, estado, tipo_evento y red a category.")
    return datos


def crear_variables(datos, registro):
    """Crea año, mes, bandera de año completo y clasificaciones por rango."""
    datos["anio"] = datos["fecha_hora"].dt.year
    datos["mes"] = datos["fecha_hora"].dt.month
    # El archivo termina el 5 de enero de 2024, así que 2024 no es un año completo.
    datos["anio_completo"] = datos["anio"] < 2024

    datos["rango_magnitud"] = pd.cut(
        datos["magnitud"], bins=[4.5, 5.0, 6.0, 7.0, 10.1], right=False,
        labels=["4.5-4.9", "5.0-5.9", "6.0-6.9", "7.0 o más"])

    datos["clase_profundidad"] = pd.cut(
        datos["profundidad_km"], bins=[0, 70, 300, 701], right=False,
        labels=["superficial", "intermedia", "profunda"])

    zona = pd.cut(datos["latitud"], bins=[-90, -43, -37, -30, 0], right=False,
                  labels=["austral", "sur", "centro", "norte"]).astype(str)
    zona[datos["longitud"] < -100] = "insular"   # Rapa Nui (Isla de Pascua)
    datos["zona"] = zona.astype("category")

    registro.append("Variables nuevas: anio, mes, anio_completo, rango_magnitud, "
                    "clase_profundidad y zona (por latitud; insular para Rapa Nui).")
    return datos
