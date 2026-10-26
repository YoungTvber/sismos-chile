from src.carga import cargar_datos, inspeccionar_datos, revisar_calidad


def main():
    ruta = "datos/sismos_chile_usgs_2000_2024.csv"
    datos = cargar_datos(ruta)

    if datos is not None:
        print("Carga realizada correctamente.")
        inspeccionar_datos(datos)
        revisar_calidad(datos)
    else:
        print("El programa finalizó sin procesar los datos.")


if __name__ == "__main__":
    main()
