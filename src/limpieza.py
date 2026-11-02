"""Limpieza: nombres de columnas, texto, duplicados, área de estudio y valores nulos."""

import pandas as pd

from src.validaciones import REGION_FUERA_AREA

MAPA_COLUMNAS = {
    "id": "id_evento",
    "time": "fecha_hora",
    "latitude": "latitud",
    "longitude": "longitud",
    "depth": "profundidad_km",
    "mag": "magnitud",
    "magType": "tipo_magnitud",
    "place": "lugar",
    "status": "estado",
    "type": "tipo_evento",
    "net": "red",
    "nst": "n_estaciones",
    "gap": "brecha_azimutal",
    "rms": "rms",
    "magNst": "n_estaciones_magnitud",
    "updated": "actualizado",
    "dmin": "dist_min_estacion",
    "horizontalError": "error_horizontal_km",
    "depthError": "error_profundidad_km",
    "magError": "error_magnitud",
    "locationSource": "fuente_ubicacion",
    "magSource": "fuente_magnitud",
}

COLUMNAS_CATEGORICAS = ["tipo_magnitud", "estado", "tipo_evento", "red",
                        "fuente_ubicacion", "fuente_magnitud"]

# Metadatos que no aportan a la pregunta del proyecto (frecuencia anual por magnitud).
COLUMNAS_METADATOS = ["actualizado", "fuente_ubicacion", "fuente_magnitud"]

# Variables de calidad con muchos nulos y sin uso en el análisis: se eliminan.
NULOS_ELIMINAR = {
    "dist_min_estacion": "más de la mitad de los valores faltan y no se usa en el análisis",
    "error_horizontal_km": "más de la mitad de los valores faltan y no se usa en el análisis",
    "error_magnitud": "más de la mitad de los valores faltan y no se usa en el análisis",
    "error_profundidad_km": "40 % de faltantes y es una medida de precisión que no se usa en el análisis",
}

# Variables de calidad con pocos nulos: se conservan, porque el nulo significa "no informado".
NULOS_MANTENER = {
    "n_estaciones": "el nulo indica que la red no informó el dato; imputarlo inventaría información",
    "brecha_azimutal": "el nulo indica que la red no informó el dato; imputarlo inventaría información",
    "rms": "el nulo indica que la red no informó el dato; imputarlo inventaría información",
    "n_estaciones_magnitud": "el nulo indica que la red no informó el dato; imputarlo inventaría información",
}


def normalizar_columnas(datos, registro):
    """Renombra las columnas a nombres descriptivos en español (snake_case)."""
    datos = datos.rename(columns=MAPA_COLUMNAS)
    registro.append(f"Columnas renombradas: {len(MAPA_COLUMNAS)} (nombres en español y sin abreviaturas).")
    return datos


def limpiar_texto(datos, registro):
    """Elimina espacios sobrantes y unifica minúsculas en las columnas de código."""
    modificados = 0
    for col in datos.select_dtypes(include=["object", "string"]).columns:
        original = datos[col]
        limpio = original.str.strip().str.replace(r"\s+", " ", regex=True)
        if col in COLUMNAS_CATEGORICAS:
            limpio = limpio.str.lower()
        modificados += int((original.fillna("") != limpio.fillna("")).sum())
        datos[col] = limpio
    registro.append(f"Texto: espacios y mayúsculas corregidos en {modificados} celdas.")
    return datos


def eliminar_duplicados(datos, registro):
    """Elimina filas completamente idénticas y registra cuántas había."""
    antes = len(datos)
    datos = datos.drop_duplicates()
    registro.append(f"Duplicados: {antes - len(datos)} filas idénticas eliminadas.")
    repetidos = int(datos["id_evento"].duplicated().sum())
    registro.append(f"Identificadores repetidos: {repetidos}.")
    return datos


def filtrar_area_estudio(datos, registro):
    """
    Elimina los eventos de la dorsal oceánica West Chile Rise.

    Justificación: ocurren en mar abierto, lejos de la costa, y corresponden a otro
    ambiente tectónico (dorsal oceánica) que la subducción que se quiere estudiar.
    """
    mascara = datos["lugar"].str.contains(REGION_FUERA_AREA, na=False)
    registro.append(
        f"Fuera del área de estudio: {int(mascara.sum())} registros de '{REGION_FUERA_AREA}' eliminados "
        "(dorsal oceánica en mar abierto, distinta a la zona de subducción bajo estudio)."
    )
    return datos[~mascara].copy()


def eliminar_columnas_metadatos(datos, registro):
    """Elimina columnas de metadatos que no se usan en el análisis."""
    datos = datos.drop(columns=COLUMNAS_METADATOS)
    registro.append(f"Columnas eliminadas por no aportar al análisis: {COLUMNAS_METADATOS}.")
    return datos


def tratar_nulos(datos, nulos_iniciales, registro):
    """
    Aplica una estrategia distinta a cada variable con nulos.

    nulos_iniciales : Series con los nulos del conjunto original (nombres ya normalizados).
    Retorna el DataFrame tratado y una tabla con el detalle de cada decisión.
    """
    filas = []
    for columna, motivo in NULOS_ELIMINAR.items():
        filas.append({"variable": columna, "nulos_iniciales": int(nulos_iniciales[columna]),
                      "estrategia": "Eliminar la columna", "justificacion": motivo,
                      "nulos_finales": "no aplica"})
    datos = datos.drop(columns=list(NULOS_ELIMINAR))

    for columna, motivo in NULOS_MANTENER.items():
        filas.append({"variable": columna, "nulos_iniciales": int(nulos_iniciales[columna]),
                      "estrategia": "Mantener el nulo", "justificacion": motivo,
                      "nulos_finales": int(datos[columna].isna().sum())})

    tabla = pd.DataFrame(filas)
    registro.append("Nulos: 4 columnas eliminadas y 4 conservadas con nulos (ver tabla). "
                    "No se reemplazó ningún nulo por cero.")
    return datos, tabla
