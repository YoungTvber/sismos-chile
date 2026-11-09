"""Estadística descriptiva del catálogo de sismos limpio."""

import pandas as pd

VARIABLES_NUMERICAS = ["magnitud", "profundidad_km", "latitud", "longitud"]
VARIABLES_CATEGORICAS = ["rango_magnitud", "clase_profundidad", "zona", "tipo_magnitud", "estado"]
ORDEN_RANGOS = ["4.5-4.9", "5.0-5.9", "6.0-6.9", "7.0 o más"]


def frecuencia_anual(datos):
    """Cantidad de sismos por año, usando solo años completos (2024 queda fuera)."""
    completos = datos[datos["anio_completo"]]
    return completos.groupby("anio").size()


def medidas_numericas(serie):
    """Devuelve las medidas descriptivas de una serie numérica como diccionario."""
    return {
        "registros": int(serie.count()),
        "media": serie.mean(),
        "mediana": serie.median(),
        "minimo": serie.min(),
        "maximo": serie.max(),
        "rango": serie.max() - serie.min(),
        "desviacion_estandar": serie.std(),
        "cuartil_1": serie.quantile(0.25),
        "cuartil_3": serie.quantile(0.75),
    }


def estadisticas_numericas(datos):
    """Medidas descriptivas de las variables numéricas y de la frecuencia anual."""
    filas = []
    series = {v: datos[v] for v in VARIABLES_NUMERICAS}
    series["sismos_por_anio"] = frecuencia_anual(datos)
    for variable, serie in series.items():
        for medida, valor in medidas_numericas(serie).items():
            filas.append({"tipo": "numerica", "variable": variable, "medida": medida,
                          "valor": round(float(valor), 3), "porcentaje": ""})
    return pd.DataFrame(filas)


def frecuencias_categoricas(datos):
    """Frecuencia absoluta y porcentaje de cada categoría."""
    filas = []
    for variable in VARIABLES_CATEGORICAS:
        conteo = datos[variable].value_counts()
        if variable == "rango_magnitud":
            conteo = conteo.reindex(ORDEN_RANGOS).fillna(0).astype(int)
        for categoria, cantidad in conteo.items():
            filas.append({"tipo": "categorica", "variable": variable, "medida": categoria,
                          "valor": int(cantidad),
                          "porcentaje": round(cantidad / len(datos) * 100, 2)})
    return pd.DataFrame(filas)


def calcular_estadisticas(datos):
    """Tabla única con las estadísticas numéricas y las frecuencias categóricas."""
    tabla = pd.concat([estadisticas_numericas(datos), frecuencias_categoricas(datos)],
                      ignore_index=True)
    # las frecuencias son enteros; las medidas numéricas conservan sus decimales
    tabla["valor"] = tabla["valor"].astype(object)
    es_entero = (tabla["tipo"] == "categorica") | (tabla["medida"] == "registros")
    tabla.loc[es_entero, "valor"] = tabla.loc[es_entero, "valor"].astype(int)
    return tabla
