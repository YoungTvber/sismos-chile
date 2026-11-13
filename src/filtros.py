"""Filtros, series anuales e indicadores del dashboard."""

import numpy as np
import pandas as pd

ZONAS = ["norte", "centro", "sur", "austral", "insular"]
ANIOS_GRANDES = [2010, 2014, 2015]   # años de los terremotos del Maule, Iquique e Illapel
PROFUNDIDADES = ["Todas", "superficial", "intermedia"]


def filtrar(datos, anio_desde, anio_hasta, magnitud_minima, profundidad):
    """Aplica los filtros de período, magnitud mínima y clase de profundidad."""
    mascara = datos["anio_completo"] & datos["anio"].between(anio_desde, anio_hasta)
    mascara &= datos["magnitud"] >= magnitud_minima
    if profundidad != "Todas":
        mascara &= datos["clase_profundidad"] == profundidad
    return datos[mascara]


def series_por_zona(datos, zonas, anio_desde, anio_hasta, excluir_grandes=False):
    """
    Cantidad de sismos por año para cada zona (escenario) y su total.
    Los años sin sismos aparecen con cero; con excluir_grandes se omiten 2010, 2014 y 2015.
    """
    anios = [a for a in range(anio_desde, anio_hasta + 1)
             if not (excluir_grandes and a in ANIOS_GRANDES)]
    tabla = pd.DataFrame(index=pd.Index(anios, name="anio"))
    for zona in zonas:
        conteo = datos[datos["zona"] == zona].groupby("anio").size()
        tabla[zona] = conteo.reindex(anios, fill_value=0)
    tabla["Total"] = tabla[zonas].sum(axis=1) if zonas else 0
    return tabla


def pendiente(serie):
    """Pendiente de la recta de mínimos cuadrados (sismos por año cada año)."""
    if len(serie) < 2:
        return 0.0
    return float(np.polyfit(serie.index.to_numpy(dtype=float), serie.to_numpy(dtype=float), 1)[0])


def indicadores(total):
    """Promedio, máximo, mínimo, registro y tendencia de la serie anual total."""
    if len(total) == 0 or total.sum() == 0:
        return None
    pend = pendiente(total)
    media = float(total.mean())
    if abs(pend) < 0.01 * media:
        texto = "Estable"
    else:
        texto = "Aumenta" if pend > 0 else "Disminuye"
    return {
        "promedio": media,
        "maximo": int(total.max()), "anio_max": int(total.idxmax()),
        "minimo": int(total.min()), "anio_min": int(total.idxmin()),
        "registro": int(total.sum()),
        "pendiente": pend, "tendencia": texto,
    }
