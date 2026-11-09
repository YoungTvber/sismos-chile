"""Gráficos con Matplotlib (Pyplot) guardados como archivos PNG."""

import os

import matplotlib
matplotlib.use("Agg")  # no abre ventanas: solo guarda los archivos
import matplotlib.pyplot as plt
import numpy as np

from src.estadisticas import frecuencia_anual, ORDEN_RANGOS
from src.indicadores import ajuste_lineal, fmt

ROJO = "#E5383B"
GRIS = "#4A5568"
CLARO = "#9AA3B2"


def _estilo(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e5e7eb", linewidth=0.8)
    ax.set_axisbelow(True)


def _guardar(fig, ruta):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    fig.tight_layout()
    fig.savefig(ruta, dpi=200)
    plt.close(fig)
    return ruta


def grafico_frecuencia_anual(datos, ruta):
    """Gráfico de líneas: cantidad de sismos por año con su tendencia lineal."""
    anual = frecuencia_anual(datos)
    x = anual.index.to_numpy()
    pend, intercepto, _ = ajuste_lineal(x, anual.to_numpy())

    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    ax.plot(x, anual.values, marker="o", markersize=4.5, color=GRIS, linewidth=1.8, label="Sismos por año")
    ax.plot(x, pend * x + intercepto, linestyle="--", color=ROJO, linewidth=1.8,
            label=f"Tendencia lineal ({'+' if pend >= 0 else ''}{fmt(pend, 1)} sismos por año)")
    ax.axhline(anual.median(), color=CLARO, linestyle=":", linewidth=1.5,
               label=f"Mediana anual ({fmt(anual.median(), 1)})")
    for anio in anual.nlargest(3).index:
        ax.annotate(f"{anio}\n{fmt(anual[anio])}", xy=(anio, anual[anio]), xytext=(0, 9),
                    textcoords="offset points", ha="center", fontsize=8.5, color=GRIS)
    ax.set_ylim(0, anual.max() * 1.18)
    ax.set_title("Frecuencia anual de sismos de magnitud 4,5 o más en Chile (2000-2023)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Año")
    ax.set_ylabel("Cantidad de sismos (eventos por año)")
    ax.set_xticks(range(int(x.min()), int(x.max()) + 1, 2))
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    _estilo(ax)
    return _guardar(fig, ruta)


def grafico_magnitud_por_anio(datos, ruta):
    """Barras apiladas: sismos por año según el rango de magnitud."""
    completos = datos[datos["anio_completo"]]
    tabla = completos.groupby(["anio", "rango_magnitud"]).size().unstack(fill_value=0)
    tabla = tabla.reindex(columns=ORDEN_RANGOS, fill_value=0)
    colores = [CLARO, GRIS, ROJO, "#7F1D1D"]

    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    base = np.zeros(len(tabla))
    for rango, color in zip(ORDEN_RANGOS, colores):
        ax.bar(tabla.index, tabla[rango], bottom=base, color=color, label=f"Magnitud {rango}", width=0.8)
        base += tabla[rango].to_numpy()
    ax.set_title("Sismos por año según el rango de magnitud (2000-2023)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Año")
    ax.set_ylabel("Cantidad de sismos (eventos por año)")
    ax.set_xticks(range(int(tabla.index.min()), int(tabla.index.max()) + 1, 2))
    ax.legend(frameon=False, loc="upper left", fontsize=9, title="Rango de magnitud", title_fontsize=9)
    _estilo(ax)
    return _guardar(fig, ruta)


def grafico_histograma_magnitud(datos, ruta):
    """Histograma de magnitudes con escala logarítmica en el eje vertical."""
    mag = datos["magnitud"]
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    ax.hist(mag, bins=np.arange(4.45, mag.max() + 0.15, 0.1), color=GRIS, edgecolor="white", linewidth=0.5)
    ax.set_yscale("log")
    ax.axvline(mag.mean(), color=ROJO, linestyle="--", linewidth=1.8, label=f"Media ({fmt(mag.mean(), 2)})")
    ax.axvline(mag.median(), color=CLARO, linestyle=":", linewidth=2, label=f"Mediana ({fmt(mag.median(), 1)})")
    ax.annotate(f"Máximo: M {fmt(mag.max(), 1)}", xy=(mag.max(), 1), xytext=(mag.max() - 0.9, 6),
                arrowprops=dict(arrowstyle="->", color=GRIS), fontsize=9, color=GRIS)
    ax.set_title("Distribución de las magnitudes de los sismos (2000-2024)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Magnitud (escala del USGS)")
    ax.set_ylabel("Cantidad de sismos (escala logarítmica)")
    ax.legend(frameon=False, fontsize=9)
    _estilo(ax)
    return _guardar(fig, ruta)


def crear_graficos(datos, carpeta):
    """Genera los tres gráficos y devuelve las rutas de los archivos creados."""
    return [
        grafico_frecuencia_anual(datos, os.path.join(carpeta, "grafico_01.png")),
        grafico_magnitud_por_anio(datos, os.path.join(carpeta, "grafico_02.png")),
        grafico_histograma_magnitud(datos, os.path.join(carpeta, "grafico_03.png")),
    ]
