from src.carga import cargar_datos, exportar_datos
from src.limpieza import (normalizar_columnas, limpiar_texto, eliminar_duplicados,
                          filtrar_area_estudio, eliminar_columnas_metadatos, tratar_nulos)
from src.transformaciones import convertir_fecha, convertir_tipos, crear_variables
from src.validaciones import (diagnosticar_calidad, validar_dataset,
                              comparar_antes_despues, resumen_final)

RUTA_ORIGINAL = "datos/originales/sismos_chile_usgs_2000_2024.csv"
RUTA_LIMPIO = "datos/procesados/dataset_limpio.csv"
RUTA_REGISTRO = "reportes/registro_limpieza.txt"

# Variables que cambian de tipo y variables nuevas (para la comparación final)
N_TRANSFORMADAS = 7
N_NUEVAS = 6


def titulo(texto):
    print("\n" + "=" * 60)
    print(texto)
    print("=" * 60)


def mostrar_registro(registro, desde):
    """Imprime las acciones registradas desde la posición indicada."""
    for linea in registro[desde:]:
        print("-", linea)
    return len(registro)


def main():
    registro = []
    vistas = 0

    titulo("1. CARGA")
    original = cargar_datos(RUTA_ORIGINAL)
    if original is None:
        print("El programa finalizó sin procesar los datos.")
        return
    print("Carga realizada correctamente.")

    titulo("2. DIAGNÓSTICO DEL CONJUNTO ORIGINAL")
    antes = diagnosticar_calidad(original)

    titulo("3. LIMPIEZA")
    datos = original.copy()          # el original no se modifica
    datos = normalizar_columnas(datos, registro)
    nulos_iniciales = datos.isna().sum()
    datos = limpiar_texto(datos, registro)
    datos = eliminar_duplicados(datos, registro)
    datos = filtrar_area_estudio(datos, registro)
    datos = eliminar_columnas_metadatos(datos, registro)
    vistas = mostrar_registro(registro, vistas)

    titulo("4. TRATAMIENTO DE NULOS")
    datos, tabla_nulos = tratar_nulos(datos, nulos_iniciales, registro)
    print(tabla_nulos[["variable", "nulos_iniciales", "estrategia", "nulos_finales"]].to_string(index=False))
    vistas = mostrar_registro(registro, vistas)

    titulo("5. TRANSFORMACIONES")
    datos = convertir_fecha(datos, registro)
    datos = convertir_tipos(datos, registro)
    datos = crear_variables(datos, registro)
    vistas = mostrar_registro(registro, vistas)
    print(datos[["fecha_hora", "magnitud", "anio", "mes", "rango_magnitud",
                 "clase_profundidad", "zona"]].head())

    titulo("6. VALIDACIÓN")
    valido = validar_dataset(datos)

    titulo("7. EXPORTACIÓN")
    if valido and exportar_datos(datos, RUTA_LIMPIO):
        print(f"Archivo generado: {RUTA_LIMPIO}")
    else:
        print("No se exportó el archivo porque la validación falló.")
        return

    titulo("COMPARACIÓN ANTES Y DESPUÉS")
    despues = resumen_final(datos)
    comparar_antes_despues(antes, despues, N_TRANSFORMADAS, N_NUEVAS)

    with open(RUTA_REGISTRO, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(registro) + "\n")
    print(f"\nRegistro de la limpieza guardado en {RUTA_REGISTRO}")


if __name__ == "__main__":
    main()
