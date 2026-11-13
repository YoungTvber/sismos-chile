"""Modelos matemáticos de proyección sobre la frecuencia anual de sismos."""

import numpy as np

MODELOS = ["Tendencia lineal", "Promedio móvil", "Media ± desviación (onda)"]


def _minimo_cero(valores):
    """La cantidad de sismos no puede ser negativa."""
    return np.maximum(valores, 0)


def proyectar_lineal(anios, valores, horizonte, ajuste=0.0):
    """
    Regresión lineal por mínimos cuadrados: y = a + b·x.

    La proyección parte del último valor ajustado y avanza con la pendiente b.
    ajuste (%) modifica la pendiente: b' = b · (1 + ajuste/100).
    """
    pendiente, intercepto = np.polyfit(anios, valores, 1)
    ultimo = anios[-1]
    base = pendiente * ultimo + intercepto
    futuros = ultimo + np.arange(1, horizonte + 1)
    estimado = base + pendiente * (1 + ajuste / 100) * (futuros - ultimo)
    return futuros, _minimo_cero(estimado)


def proyectar_promedio_movil(anios, valores, horizonte, ventana=3, ajuste=0.0):
    """
    Promedio móvil: cada año proyectado es el promedio de los últimos `ventana`
    valores (reales o ya proyectados). ajuste (%) escala el nivel proyectado.
    """
    ventana = max(1, min(int(ventana), len(valores)))
    historial = list(map(float, valores))
    resultado = []
    for _ in range(horizonte):
        siguiente = float(np.mean(historial[-ventana:]))
        historial.append(siguiente)
        resultado.append(siguiente)
    futuros = anios[-1] + np.arange(1, horizonte + 1)
    return futuros, _minimo_cero(np.array(resultado) * (1 + ajuste / 100))


def proyectar_onda(anios, valores, horizonte, periodo=6, ajuste=0.0):
    """
    Media ± desviación: onda sinusoidal centrada en el promedio histórico.

    y(t) = μ + A · sin(2π (t - t_último) / T + φ),  con A = σ · (1 + ajuste/100)
    φ se elige para que la onda continúe desde el último valor observado.
    """
    media = float(np.mean(valores))
    desviacion = float(np.std(valores, ddof=1)) if len(valores) > 1 else 0.0
    amplitud = desviacion * (1 + ajuste / 100)
    ultimo = anios[-1]
    if amplitud > 0:
        fase = np.arcsin(np.clip((valores[-1] - media) / amplitud, -1, 1))
    else:
        fase = 0.0
    futuros = ultimo + np.arange(1, horizonte + 1)
    estimado = media + amplitud * np.sin(2 * np.pi * (futuros - ultimo) / periodo + fase)
    return futuros, _minimo_cero(estimado)


def proyectar(modelo, anios, valores, horizonte, parametro, ajuste):
    """Despacha al modelo elegido. Devuelve (años futuros, valores proyectados)."""
    anios = np.asarray(anios, dtype=float)
    valores = np.asarray(valores, dtype=float)
    if len(anios) < 2:
        return np.array([]), np.array([])
    if modelo == MODELOS[0]:
        return proyectar_lineal(anios, valores, horizonte, ajuste)
    if modelo == MODELOS[1]:
        return proyectar_promedio_movil(anios, valores, horizonte, parametro, ajuste)
    return proyectar_onda(anios, valores, horizonte, parametro, ajuste)
