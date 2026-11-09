"""Indicadores automatizados relacionados con la pregunta del proyecto."""

import numpy as np
import pandas as pd

from src.estadisticas import frecuencia_anual


def fmt(valor, decimales=0):
    """Formato en español: punto para miles y coma para decimales."""
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def ajuste_lineal(x, y):
    """Pendiente, intercepto y R² de la recta de mínimos cuadrados."""
    pendiente, intercepto = np.polyfit(x, y, 1)
    r2 = np.corrcoef(x, y)[0, 1] ** 2
    return float(pendiente), float(intercepto), float(r2)


def calcular_indicadores(datos):
    """Calcula los indicadores y devuelve una tabla lista para exportar."""
    anual = frecuencia_anual(datos)
    anios = anual.index.to_numpy()
    total = len(datos)
    total_completos = int(anual.sum())

    media = anual.mean()
    mediana = anual.median()

    anio_max = int(anual.idxmax())
    cant_max = int(anual.max())

    primera = anual.loc[:2011]
    segunda = anual.loc[2012:]
    med1, med2 = primera.median(), segunda.median()
    variacion = (med2 / med1 - 1) * 100

    pend, _, r2 = ajuste_lineal(anios, anual.to_numpy())
    top3 = anual.nlargest(3).index.sort_values()
    resto = anual.drop(top3)
    pend_resto, _, r2_resto = ajuste_lineal(resto.index.to_numpy(), resto.to_numpy())

    criticos = datos[datos["magnitud"] >= 6]
    n_crit = len(criticos)
    n_7 = int((datos["magnitud"] >= 7).sum())

    mayor = datos.loc[datos["magnitud"].idxmax()]
    pct_superficial = (datos["clase_profundidad"] == "superficial").mean() * 100

    filas = []

    def agregar(indicador, metodo, resultado, interpretacion):
        filas.append({"indicador": indicador, "metodo_calculo": metodo,
                      "resultado": resultado, "interpretacion": interpretacion})

    agregar("Total de sismos válidos",
            "Cantidad de filas del dataset limpio",
            f"{fmt(total)} sismos",
            f"Es la base del análisis tras la limpieza. De ellos, {fmt(total_completos)} corresponden a años completos "
            "(2000-2023), que son los que se usan para comparar años.")

    agregar("Promedio anual de sismos",
            "Media de la cantidad de sismos por año, en años completos",
            f"{fmt(media, 1)} sismos por año",
            f"En un año típico ocurren cerca de {fmt(mediana, 1)} sismos (mediana). El promedio es más alto porque "
            "unos pocos años muy activos lo elevan.")

    mismo_anio = int(mayor["fecha_hora"].year) == anio_max
    nota = (f" Coincide con el sismo de magnitud {fmt(mayor['magnitud'], 1)} de ese año y sus réplicas."
            if mismo_anio else "")
    agregar("Año de mayor actividad",
            "Año con más sismos entre los años completos",
            f"{anio_max}: {fmt(cant_max)} sismos",
            f"Ese año concentra {fmt(cant_max / total_completos * 100, 1)} % de todos los sismos de años completos y "
            f"equivale a {fmt(cant_max / media, 1)} veces el promedio.{nota}")

    agregar("Variación entre períodos",
            "Cambio porcentual de la mediana anual entre 2000-2011 y 2012-2023",
            f"{'+' if variacion >= 0 else ''}{fmt(variacion, 1)} % ({fmt(med1, 1)} a {fmt(med2, 1)} sismos por año)",
            f"El año típico del segundo período tuvo {'más' if variacion >= 0 else 'menos'} sismos que el del primero. "
            "Se usa la mediana para que los años extremos no distorsionen la comparación.")

    explica = "muy poco" if r2 < 0.1 else "una parte importante"
    agregar("Tendencia anual de la frecuencia",
            "Pendiente de la recta de mínimos cuadrados de sismos por año (numpy.polyfit)",
            f"{'+' if pend >= 0 else ''}{fmt(pend, 1)} sismos por año cada año (R² = {fmt(r2, 2)})",
            f"La recta {'sube' if pend >= 0 else 'baja'} levemente, pero el año explica {explica} de la variación "
            "entre años. La tendencia no es concluyente por sí sola.")

    agregar("Tendencia sin los tres años más activos",
            f"Misma pendiente excluyendo {', '.join(str(int(a)) for a in top3)}",
            f"{'+' if pend_resto >= 0 else ''}{fmt(pend_resto, 1)} sismos por año cada año (R² = {fmt(r2_resto, 2)})",
            f"El signo {'se mantiene' if np.sign(pend_resto) == np.sign(pend) else 'cambia'} al quitar los años con grandes "
            "terremotos y réplicas." + (" Además el ajuste mejora, es decir, esos años ocultaban una tendencia más ordenada."
                                        if r2_resto > r2 + 0.05 else ""))

    # Variación de la mediana anual por rango de magnitud (responde "cambia según la magnitud")
    completos = datos[datos["anio_completo"]]
    grupos = pd.cut(completos["magnitud"], bins=[4.5, 5.0, 6.0, 10.1], right=False,
                    labels=["4,5-4,9", "5,0-5,9", "6,0 o más"])
    por_grupo = completos.groupby(["anio", grupos], observed=False).size().unstack(fill_value=0)
    cambios = {}
    for grupo in por_grupo.columns:
        m1 = por_grupo[grupo].loc[:2011].median()
        m2 = por_grupo[grupo].loc[2012:].median()
        cambios[grupo] = (m1, m2, (m2 / m1 - 1) * 100)
    mayor_cambio = max(cambios, key=lambda g: cambios[g][2])
    detalle = "; ".join(f"{g}: {'+' if v[2] >= 0 else ''}{fmt(v[2], 1)} %" for g, v in cambios.items())
    aviso = (" Los sismos pequeños son los más sensibles a mejoras en la red de detección, así que ese aumento "
             "podría no ser real." if mayor_cambio == "4,5-4,9" else "")
    agregar("Variación según la magnitud",
            "Cambio porcentual de la mediana anual entre 2000-2011 y 2012-2023, por rango de magnitud",
            detalle,
            f"El mayor cambio ocurre en el rango {mayor_cambio}.{aviso} En magnitud 6,0 o más la mediana pasa de "
            f"{fmt(cambios['6,0 o más'][0], 1)} a {fmt(cambios['6,0 o más'][1], 1)} sismos por año: son pocos casos y la diferencia no es concluyente.")

    agregar("Casos críticos (magnitud 6,0 o más)",
            "Cantidad y porcentaje de sismos con magnitud mayor o igual a 6,0",
            f"{fmt(n_crit)} sismos ({fmt(n_crit / total * 100, 1)} %), {fmt(n_7)} de magnitud 7,0 o más",
            "Son los eventos de mayor impacto potencial en personas e infraestructura y pesan poco en el total.")

    agregar("Mayor magnitud registrada",
            "Máximo de magnitud y registro asociado",
            f"M {fmt(mayor['magnitud'], 1)}, {mayor['fecha_hora'].strftime('%d/%m/%Y')}, {fmt(mayor['profundidad_km'], 1)} km",
            f"Lugar de referencia: {mayor['lugar']}. Es el valor extremo del conjunto y sirve de referencia para los demás.")

    agregar("Sismos superficiales (menos de 70 km)",
            "Porcentaje de sismos con clase de profundidad superficial",
            f"{fmt(pct_superficial, 1)} %",
            "La mayoría de los sismos ocurre cerca de la superficie, donde el movimiento llega con más fuerza a las construcciones.")

    return pd.DataFrame(filas)
