"""Diagnóstico de calidad y validaciones de columnas, tipos y rangos."""

import pandas as pd

# Eventos de esta región son de una dorsal oceánica, fuera del área de estudio.
REGION_FUERA_AREA = "West Chile Rise"

# Rangos válidos sobre el conjunto original (nombres en inglés del USGS).
RANGOS_ORIGINAL = {
    "mag": (4.5, 10),
    "depth": (0, 700),
    "latitude": (-56, -17),
    "longitude": (-113, -66),
}

# Rangos válidos sobre el conjunto limpio.
RANGOS_LIMPIO = {
    "magnitud": (4.5, 10),
    "profundidad_km": (0, 700),
    "latitud": (-56, -17),
    "longitud": (-113, -66),
    "anio": (2000, 2024),
    "mes": (1, 12),
}

COLUMNAS_ESPERADAS = [
    "id_evento", "fecha_hora", "latitud", "longitud", "profundidad_km", "magnitud",
    "tipo_magnitud", "lugar", "estado", "tipo_evento", "red", "n_estaciones",
    "brecha_azimutal", "rms", "n_estaciones_magnitud",
    "anio", "mes", "anio_completo", "rango_magnitud", "clase_profundidad", "zona",
]

TIPOS_ESPERADOS = {
    "fecha_hora": "datetime64",
    "latitud": "float64",
    "longitud": "float64",
    "profundidad_km": "float64",
    "magnitud": "float64",
    "n_estaciones": "Int64",
    "n_estaciones_magnitud": "Int64",
    "tipo_magnitud": "category",
    "estado": "category",
    "tipo_evento": "category",
    "red": "category",
    "rango_magnitud": "category",
    "clase_profundidad": "category",
    "zona": "category",
    "anio_completo": "bool",
}

CATEGORICAS_ORIGINAL = ["magType", "status", "type", "net", "locationSource", "magSource"]


def contar_fuera_de_rango(datos, rangos):
    """Cuenta, por variable, los valores que quedan fuera de su rango válido."""
    resultado = {}
    for columna, (minimo, maximo) in rangos.items():
        if columna in datos.columns:
            resultado[columna] = int((~datos[columna].between(minimo, maximo)).sum())
    return resultado


def diagnosticar_calidad(datos):
    """
    Diagnóstico de calidad del conjunto ORIGINAL (columnas del USGS).
    Imprime los indicadores y devuelve un resumen para la comparación final.
    """
    filas, columnas = datos.shape
    nulos = datos.isna().sum()
    porcentaje = (nulos / filas * 100).round(1)
    con_nulos = pd.DataFrame({"nulos": nulos, "porcentaje": porcentaje})
    con_nulos = con_nulos[con_nulos["nulos"] > 0].sort_values("nulos", ascending=False)

    duplicadas = int(datos.duplicated().sum())
    ids_repetidos = int(datos["id"].duplicated().sum())

    fuera = contar_fuera_de_rango(datos, RANGOS_ORIGINAL)
    fuera_area = int(datos["place"].str.contains(REGION_FUERA_AREA, na=False).sum())

    # Categorías inconsistentes: valores que solo difieren en mayúsculas o espacios.
    inconsistentes = 0
    for col in CATEGORICAS_ORIGINAL:
        crudo = datos[col].dropna().nunique()
        normal = datos[col].dropna().astype(str).str.strip().str.lower().nunique()
        inconsistentes += int(crudo - normal)

    print(f"Filas: {filas} | Columnas: {columnas}")
    print("\nValores nulos (columnas con nulos):")
    print(con_nulos.to_string())
    print(f"\nTotal de valores nulos: {int(nulos.sum())}")
    print(f"Filas duplicadas: {duplicadas}")
    print(f"Identificadores repetidos: {ids_repetidos}")
    print("Valores fuera de rango:", fuera)
    print(f"Eventos fuera del área de estudio ({REGION_FUERA_AREA}): {fuera_area}")
    print(f"Categorías inconsistentes: {inconsistentes}")

    return {
        "filas": filas,
        "columnas": columnas,
        "nulos": int(nulos.sum()),
        "duplicadas": duplicadas,
        "fuera_rango": sum(fuera.values()) + fuera_area,
    }


def validar_columnas(datos):
    """Comprueba que estén todas las columnas esperadas y que no sobre ninguna."""
    faltan = [c for c in COLUMNAS_ESPERADAS if c not in datos.columns]
    sobran = [c for c in datos.columns if c not in COLUMNAS_ESPERADAS]
    return faltan, sobran


def validar_tipos(datos):
    """Devuelve las columnas cuyo tipo no coincide con el esperado."""
    errores = []
    for columna, esperado in TIPOS_ESPERADOS.items():
        if columna not in datos.columns:
            continue
        real = str(datos[columna].dtype)
        if not real.startswith(esperado):
            errores.append(f"{columna}: esperado {esperado}, encontrado {real}")
    return errores


def validar_dataset(datos):
    """
    Valida columnas, tipos, rangos, identificadores y nulos en variables clave.
    Imprime el resultado y devuelve True si todo es correcto.
    """
    problemas = []

    faltan, sobran = validar_columnas(datos)
    if faltan:
        problemas.append(f"Columnas faltantes: {faltan}")
    if sobran:
        problemas.append(f"Columnas no esperadas: {sobran}")

    problemas += validar_tipos(datos)

    for columna, cantidad in contar_fuera_de_rango(datos, RANGOS_LIMPIO).items():
        if cantidad:
            problemas.append(f"{columna}: {cantidad} valores fuera de rango")

    if datos["id_evento"].duplicated().any():
        problemas.append("Existen identificadores repetidos")
    if datos["lugar"].str.contains(REGION_FUERA_AREA, na=False).any():
        problemas.append("Quedan eventos fuera del área de estudio")

    clave = ["id_evento", "fecha_hora", "latitud", "longitud", "profundidad_km", "magnitud",
             "anio", "rango_magnitud", "clase_profundidad", "zona"]
    for columna in clave:
        if columna in datos.columns and datos[columna].isna().any():
            problemas.append(f"{columna}: contiene nulos")

    print("Columnas:", "OK" if not faltan and not sobran else "con diferencias")
    print("Tipos de datos:", "OK" if not validar_tipos(datos) else "con diferencias")
    print("Rangos:", "OK" if not any(contar_fuera_de_rango(datos, RANGOS_LIMPIO).values()) else "con valores fuera de rango")
    print("Identificadores únicos:", "OK" if not datos["id_evento"].duplicated().any() else "con repetidos")
    if problemas:
        print("\nProblemas encontrados:")
        for p in problemas:
            print(" -", p)
        return False
    print("\nValidación completa: sin problemas.")
    return True


def comparar_antes_despues(antes, despues, transformadas, nuevas):
    """Imprime la tabla comparativa del conjunto antes y después del proceso."""
    filas = [
        ("Filas", antes["filas"], despues["filas"]),
        ("Columnas", antes["columnas"], despues["columnas"]),
        ("Valores nulos", antes["nulos"], despues["nulos"]),
        ("Filas duplicadas", antes["duplicadas"], despues["duplicadas"]),
        ("Valores fuera de rango", antes["fuera_rango"], despues["fuera_rango"]),
        ("Variables transformadas", 0, transformadas),
        ("Variables nuevas", 0, nuevas),
    ]
    print(f"{'Indicador':<26}{'Antes':>8}{'Después':>10}")
    for nombre, a, d in filas:
        print(f"{nombre:<26}{a:>8}{d:>10}")


def resumen_final(datos):
    """Resumen del conjunto limpio con las mismas métricas del diagnóstico."""
    fuera = contar_fuera_de_rango(datos, RANGOS_LIMPIO)
    fuera_area = int(datos["lugar"].str.contains(REGION_FUERA_AREA, na=False).sum())
    return {
        "filas": datos.shape[0],
        "columnas": datos.shape[1],
        "nulos": int(datos.isna().sum().sum()),
        "duplicadas": int(datos.duplicated().sum()),
        "fuera_rango": sum(fuera.values()) + fuera_area,
    }


def verificar_calculos(datos, estadisticas, indicadores):
    """
    Comprueba los resultados del Avance 3 con cálculos independientes.
    Imprime cada verificación y devuelve True si todas se cumplen.
    """
    from src.estadisticas import frecuencia_anual   # import local para evitar ciclos
    from src.indicadores import ajuste_lineal

    anual = frecuencia_anual(datos)
    mag = estadisticas[(estadisticas["variable"] == "magnitud")].set_index("medida")["valor"]
    x = anual.index.to_numpy(dtype=float)
    y = anual.to_numpy(dtype=float)
    pendiente_manual = ((x - x.mean()) * (y - y.mean())).sum() / ((x - x.mean()) ** 2).sum()
    pendiente_numpy = ajuste_lineal(x, y)[0]

    controles = [
        ("Frecuencia anual + años incompletos = total de registros",
         int(anual.sum()) + int((~datos["anio_completo"]).sum()) == len(datos)),
        ("Media de la magnitud coincide con pandas.describe()",
         abs(mag["media"] - datos["magnitud"].describe()["mean"]) < 0.001),
        ("Desviación estándar de la magnitud coincide con pandas.describe()",
         abs(mag["desviacion_estandar"] - datos["magnitud"].describe()["std"]) < 0.001),
        ("Rango = máximo - mínimo en todas las variables numéricas",
         all(abs(g.set_index("medida").loc["rango", "valor"] -
                 (g.set_index("medida").loc["maximo", "valor"] - g.set_index("medida").loc["minimo", "valor"])) < 0.01
             for _, g in estadisticas[estadisticas["tipo"] == "numerica"].groupby("variable"))),
        ("Los porcentajes de cada variable categórica suman 100 %",
         all(abs(g["porcentaje"].astype(float).sum() - 100) < 0.1
             for _, g in estadisticas[estadisticas["tipo"] == "categorica"].groupby("variable"))),
        ("Pendiente de numpy coincide con la fórmula de mínimos cuadrados",
         abs(pendiente_manual - pendiente_numpy) < 1e-9),
        ("Total de sismos del indicador 1 coincide con el número de filas",
         str(len(datos)).replace(",", "") in indicadores.loc[0, "resultado"].replace(".", "")),
    ]
    todo_ok = True
    for descripcion, ok in controles:
        print(("[OK]    " if ok else "[ERROR] ") + descripcion)
        todo_ok = todo_ok and ok
    return todo_ok
