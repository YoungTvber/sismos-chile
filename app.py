"""
Dashboard interactivo de sismicidad en Chile (2000-2023).

Ejecución desde la raíz del proyecto:  python app.py
Requiere: pandas, numpy y matplotlib (tkinter viene con Python).
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from src.carga import cargar_dataset_limpio          # noqa: E402
from src.filtros import (ZONAS, ANIOS_GRANDES, PROFUNDIDADES,   # noqa: E402
                         filtrar, series_por_zona, indicadores)
from src.modelos import MODELOS, proyectar            # noqa: E402

RUTA_DATOS = os.path.join(BASE, "datos", "procesados", "dataset_limpio.csv")

# Paleta
FONDO, PANEL, TARJETA = "#14171C", "#1C2027", "#232933"
TEXTO, SUAVE, ROJO, AMARILLO = "#E6E9EF", "#9AA3B2", "#E5383B", "#F5B700"
COLOR_ZONA = {"norte": "#4CC9F0", "centro": "#80ED99", "sur": "#C77DFF",
              "austral": "#FF8FA3", "insular": "#B0B8C4"}
COLOR_COMPARACION = "#4CC9F0"

# Parámetro propio de cada modelo: (etiqueta, mínimo, máximo, valor inicial)
PARAMETRO = {MODELOS[0]: None,
             MODELOS[1]: ("Ventana del promedio (años)", 2, 8, 3),
             MODELOS[2]: ("Período de la onda (años)", 3, 15, 6)}


def numero(valor, decimales=0):
    """Formato español: punto para miles y coma para decimales."""
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


class Dashboard:
    def __init__(self, root, datos):
        self.root = root
        self.datos = datos
        completos = datos[datos["anio_completo"]]
        self.anio_min, self.anio_max = int(completos["anio"].min()), int(completos["anio"].max())
        self._bloqueo = False

        # ---- variables de control ----
        self.v_desde = tk.IntVar(value=self.anio_min)
        self.v_hasta = tk.IntVar(value=self.anio_max)
        self.v_mag = tk.DoubleVar(value=4.5)
        self.v_prof = tk.StringVar(value="Todas")
        self.v_excluir = tk.BooleanVar(value=False)
        self.v_zonas = {z: tk.BooleanVar(value=(z != "insular")) for z in ZONAS}
        self.v_vision = tk.IntVar(value=self.anio_max)
        self.v_modelo = tk.StringVar(value=MODELOS[0])
        self.v_horizonte = tk.IntVar(value=5)
        self.v_param = tk.IntVar(value=3)
        self.v_ajuste = tk.IntVar(value=0)
        self.v_comparar = tk.BooleanVar(value=False)
        self.v_modelo_b = tk.StringVar(value=MODELOS[1])

        root.title("Dashboard de sismicidad en Chile · Programación Avanzada")
        root.geometry("1380x840")
        root.minsize(1150, 700)
        root.configure(bg=FONDO)
        self._estilo()
        self._construir_barra_lateral()
        self._construir_panel_principal()
        self.actualizar()

    # ------------------------------------------------------------------ estilo
    def _estilo(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("TCombobox", fieldbackground=TARJETA, background=TARJETA,
                         foreground=TEXTO, arrowcolor=TEXTO, bordercolor=TARJETA,
                         lightcolor=TARJETA, darkcolor=TARJETA)
        estilo.map("TCombobox", fieldbackground=[("readonly", TARJETA)],
                   foreground=[("readonly", TEXTO)], selectbackground=[("readonly", TARJETA)],
                   selectforeground=[("readonly", TEXTO)])
        estilo.configure("Dash.Horizontal.TScale", background=ROJO, troughcolor=TARJETA,
                         bordercolor=PANEL, lightcolor=ROJO, darkcolor=ROJO)
        estilo.map("Dash.Horizontal.TScale", background=[("disabled", "#555C68")],
                   lightcolor=[("disabled", "#555C68")], darkcolor=[("disabled", "#555C68")])
        self.root.option_add("*TCombobox*Listbox.background", TARJETA)
        self.root.option_add("*TCombobox*Listbox.foreground", TEXTO)

    # -------------------------------------------------------- barra lateral
    def _construir_barra_lateral(self):
        marco = tk.Frame(self.root, bg=PANEL, width=310)
        marco.pack(side="left", fill="y")
        marco.pack_propagate(False)
        lienzo = tk.Canvas(marco, bg=PANEL, highlightthickness=0, width=292)
        barra = tk.Scrollbar(marco, orient="vertical", command=lienzo.yview)
        interior = tk.Frame(lienzo, bg=PANEL)
        interior.bind("<Configure>", lambda e: lienzo.configure(scrollregion=lienzo.bbox("all")))
        lienzo.create_window((0, 0), window=interior, anchor="nw", width=290)
        lienzo.configure(yscrollcommand=barra.set)
        lienzo.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        for evento, delta in (("<Button-4>", -1), ("<Button-5>", 1)):
            lienzo.bind_all(evento, lambda e, d=delta: lienzo.yview_scroll(d, "units"))
        lienzo.bind_all("<MouseWheel>", lambda e: lienzo.yview_scroll(int(-e.delta / 120), "units"))

        self.barra = interior
        tk.Label(interior, text="SISMICIDAD EN CHILE", bg=PANEL, fg=ROJO,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(14, 0))
        tk.Label(interior, text="Dashboard interactivo", bg=PANEL, fg=TEXTO,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=14, pady=(0, 6))

        self._seccion("FILTROS")
        self._escala("Año desde", self.v_desde, self.anio_min, self.anio_max, 1)
        self._escala("Año hasta", self.v_hasta, self.anio_min, self.anio_max, 1)
        self._escala("Magnitud mínima", self.v_mag, 4.5, 7.0, 0.1)
        self._etiqueta("Clase de profundidad")
        caja = ttk.Combobox(self.barra, textvariable=self.v_prof, values=PROFUNDIDADES,
                            state="readonly", width=28)
        caja.pack(anchor="w", padx=14, pady=(0, 4))
        caja.bind("<<ComboboxSelected>>", lambda e: self.actualizar())
        self._casilla(f"Excluir años de grandes terremotos ({', '.join(map(str, ANIOS_GRANDES))})",
                      self.v_excluir)

        self._seccion("ESCENARIOS (ZONA)")
        for zona in ZONAS:
            self._casilla(zona.capitalize(), self.v_zonas[zona], color=COLOR_ZONA[zona])

        self._seccion("LÍNEA DE VISIÓN")
        self.escala_vision = self._escala("Año de lectura (o clic en el gráfico)", self.v_vision,
                                          self.anio_min, self.anio_max, 1)

        self._seccion("PROYECCIÓN")
        self._etiqueta("Modelo")
        caja = ttk.Combobox(self.barra, textvariable=self.v_modelo, values=MODELOS,
                            state="readonly", width=28)
        caja.pack(anchor="w", padx=14, pady=(0, 4))
        caja.bind("<<ComboboxSelected>>", lambda e: self._cambio_modelo())
        self._escala("Años a proyectar", self.v_horizonte, 1, 15, 1)
        self.etiqueta_param, self.escala_param = self._escala("Parámetro del modelo", self.v_param, 2, 8, 1,
                                                              devolver_etiqueta=True)
        self._escala("Ajuste de la proyección (%)", self.v_ajuste, -50, 100, 5)
        self._casilla("Comparar con otro método", self.v_comparar)
        caja = ttk.Combobox(self.barra, textvariable=self.v_modelo_b, values=MODELOS,
                            state="readonly", width=28)
        caja.pack(anchor="w", padx=14, pady=(0, 14))
        caja.bind("<<ComboboxSelected>>", lambda e: self.actualizar())
        self._cambio_modelo(actualizar=False)

    def _seccion(self, texto):
        tk.Label(self.barra, text=texto, bg=PANEL, fg=SUAVE, font=("Segoe UI", 8, "bold")
                 ).pack(anchor="w", padx=14, pady=(12, 2))
        tk.Frame(self.barra, bg=TARJETA, height=1).pack(fill="x", padx=14, pady=(0, 4))

    def _etiqueta(self, texto):
        etiqueta = tk.Label(self.barra, text=texto, bg=PANEL, fg=TEXTO, font=("Segoe UI", 9))
        etiqueta.pack(anchor="w", padx=14)
        return etiqueta

    def _escala(self, texto, variable, minimo, maximo, paso, devolver_etiqueta=False):
        fila = tk.Frame(self.barra, bg=PANEL)
        fila.pack(fill="x", padx=14)
        etiqueta = tk.Label(fila, text=texto, bg=PANEL, fg=TEXTO, font=("Segoe UI", 9), anchor="w")
        etiqueta.pack(side="left")
        valor = tk.Label(fila, bg=PANEL, fg=AMARILLO, font=("Segoe UI", 9, "bold"))
        valor.pack(side="right")
        escala = ttk.Scale(self.barra, from_=minimo, to=maximo, orient="horizontal",
                           style="Dash.Horizontal.TScale", length=250)
        escala.pack(anchor="w", padx=14, pady=(0, 6))
        escala.paso = paso

        def mostrar(*_):
            v = variable.get()
            valor.configure(text=f"{v:.1f}".replace(".", ",") if paso < 1 else f"{int(v)}")

        def mover(posicion):
            nuevo = round(float(posicion) / paso) * paso
            nuevo = round(nuevo, 2) if paso < 1 else int(nuevo)
            if variable.get() != nuevo:
                variable.set(nuevo)
                self.actualizar()

        def seguir(*_):
            if abs(float(escala.get()) - float(variable.get())) > 1e-9:
                escala.set(variable.get())
            mostrar()

        escala.configure(command=mover)
        variable.trace_add("write", seguir)
        escala.set(variable.get())
        mostrar()
        escala.etiqueta_valor = valor
        return (etiqueta, escala) if devolver_etiqueta else escala

    def _casilla(self, texto, variable, color=TEXTO):
        tk.Checkbutton(self.barra, text=texto, variable=variable, command=self.actualizar,
                       bg=PANEL, fg=color, selectcolor=TARJETA, activebackground=PANEL,
                       activeforeground=color, font=("Segoe UI", 9), anchor="w",
                       wraplength=250, justify="left", highlightthickness=0, bd=0).pack(anchor="w", padx=12)

    def _cambio_modelo(self, actualizar=True):
        config = PARAMETRO[self.v_modelo.get()]
        if config is None:
            self.etiqueta_param.configure(text="Parámetro del modelo (no aplica)", fg=SUAVE)
            self.escala_param.state(["disabled"])
            self.escala_param.etiqueta_valor.configure(text="")
        else:
            texto, minimo, maximo, inicial = config
            self.etiqueta_param.configure(text=texto, fg=TEXTO)
            self.escala_param.state(["!disabled"])
            self.escala_param.configure(from_=minimo, to=maximo)
            self.v_param.set(inicial)
            self.escala_param.set(inicial)
        if actualizar:
            self.actualizar()

    # -------------------------------------------------------- panel principal
    def _construir_panel_principal(self):
        panel = tk.Frame(self.root, bg=FONDO)
        panel.pack(side="left", fill="both", expand=True, padx=(10, 12), pady=10)

        tarjetas = tk.Frame(panel, bg=FONDO)
        tarjetas.pack(fill="x")
        self.kpi = {}
        for i, (clave, titulo) in enumerate([("promedio", "PROMEDIO ANUAL"), ("maximo", "MÁXIMO"),
                                             ("minimo", "MÍNIMO"), ("registro", "REGISTRO"),
                                             ("tendencia", "TENDENCIA")]):
            tarjeta = tk.Frame(tarjetas, bg=TARJETA)
            tarjeta.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            tarjetas.columnconfigure(i, weight=1, uniform="k")
            tk.Label(tarjeta, text=titulo, bg=TARJETA, fg=SUAVE, font=("Segoe UI", 8, "bold")
                     ).pack(anchor="w", padx=12, pady=(8, 0))
            valor = tk.Label(tarjeta, text="-", bg=TARJETA, fg=TEXTO, font=("Segoe UI", 19, "bold"))
            valor.pack(anchor="w", padx=12)
            detalle = tk.Label(tarjeta, text=" ", bg=TARJETA, fg=SUAVE, font=("Segoe UI", 8))
            detalle.pack(anchor="w", padx=12, pady=(0, 8))
            self.kpi[clave] = (valor, detalle)

        self.texto_interpretacion = tk.Label(panel, text="", bg=FONDO, fg=SUAVE, font=("Segoe UI", 9),
                                             justify="left", anchor="w", wraplength=1000)
        self.texto_interpretacion.pack(side="bottom", fill="x", pady=(2, 0))
        self.texto_lectura = tk.Label(panel, text="", bg=FONDO, fg=TEXTO, font=("Segoe UI", 10),
                                      justify="left", anchor="w", wraplength=1000)
        self.texto_lectura.pack(side="bottom", fill="x")

        self.figura = Figure(figsize=(9, 6), dpi=100, facecolor=FONDO)
        self.ax_hist = self.figura.add_subplot(2, 1, 1)
        self.ax_proy = self.figura.add_subplot(2, 1, 2)
        self.lienzo = FigureCanvasTkAgg(self.figura, master=panel)
        self.lienzo.get_tk_widget().pack(fill="both", expand=True, pady=(8, 6))
        self.lienzo.mpl_connect("button_press_event", self._clic_grafico)

        panel.bind("<Configure>", lambda e: (self.texto_lectura.configure(wraplength=e.width - 20),
                                             self.texto_interpretacion.configure(wraplength=e.width - 20)))

    def _clic_grafico(self, evento):
        if evento.inaxes is not None and evento.xdata is not None:
            anio = int(round(evento.xdata))
            self.v_vision.set(min(max(anio, self.v_desde.get()), self.v_hasta.get()))
            self.actualizar()

    # ------------------------------------------------------------ actualización
    def actualizar(self):
        if self._bloqueo:
            return
        self._bloqueo = True
        try:
            self._normalizar_controles()
            self._dibujar()
        finally:
            self._bloqueo = False

    def _normalizar_controles(self):
        desde, hasta = self.v_desde.get(), self.v_hasta.get()
        if hasta - desde < 2:                       # el período debe tener al menos 3 años
            if desde + 2 <= self.anio_max:
                hasta = desde + 2
            else:
                desde = hasta - 2
            self.v_desde.set(desde)
            self.v_hasta.set(hasta)
        self.escala_vision.configure(from_=desde, to=hasta)
        self.v_vision.set(min(max(self.v_vision.get(), desde), hasta))
        self.escala_vision.set(self.v_vision.get())

    def _dibujar(self):
        desde, hasta = self.v_desde.get(), self.v_hasta.get()
        zonas = [z for z in ZONAS if self.v_zonas[z].get()]
        datos = filtrar(self.datos, desde, hasta, round(self.v_mag.get(), 1), self.v_prof.get())
        tabla = series_por_zona(datos, zonas, desde, hasta, self.v_excluir.get())
        total = tabla["Total"]

        for ax in (self.ax_hist, self.ax_proy):
            ax.clear()
            ax.set_facecolor(PANEL)
            ax.tick_params(colors=SUAVE, labelsize=8)
            for lado in ("top", "right"):
                ax.spines[lado].set_visible(False)
            for lado in ("left", "bottom"):
                ax.spines[lado].set_color(TARJETA)
            ax.grid(axis="y", color=TARJETA, linewidth=0.8)
            ax.set_axisbelow(True)

        info = indicadores(total) if zonas else None
        if info is None:
            for ax in (self.ax_hist, self.ax_proy):
                ax.text(0.5, 0.5, "Sin datos: seleccione al menos un escenario o amplíe los filtros",
                        transform=ax.transAxes, ha="center", va="center", color=SUAVE, fontsize=11)
            for clave, (valor, detalle) in self.kpi.items():
                valor.configure(text="-")
                detalle.configure(text=" ")
            self.texto_lectura.configure(text="")
            self.texto_interpretacion.configure(text="")
            self.lienzo.draw_idle()
            return

        vision = self.v_vision.get()

        # ---- gráfico 1: histórico por escenario ----
        ax = self.ax_hist
        for zona in zonas:
            ax.plot(tabla.index, tabla[zona], marker="o", markersize=3, linewidth=1.5,
                    color=COLOR_ZONA[zona], label=zona.capitalize())
        ax.plot(tabla.index, total, color="white", linewidth=2.4, label="Total", zorder=5)
        ax.axvline(vision, color=SUAVE, linestyle=":", linewidth=1.4, zorder=1)
        ax.set_title("Histórico: sismos por año según escenario", color=TEXTO, fontsize=10,
                     loc="left", fontweight="bold")
        ax.set_ylabel("Sismos por año", color=SUAVE, fontsize=8)
        ax.set_xlim(desde - 0.5, hasta + 0.5)
        ax.legend(loc="upper left", ncol=len(zonas) + 1, fontsize=8, frameon=False,
                  labelcolor=TEXTO)

        # ---- gráfico 2: histórico total + proyección ----
        ax = self.ax_proy
        ax.plot(tabla.index, total, color="white", linewidth=2.2, marker="o", markersize=3,
                label="Histórico (total)")
        horizonte = self.v_horizonte.get()
        modelo = self.v_modelo.get()
        futuros, estimado = proyectar(modelo, total.index, total.to_numpy(), horizonte,
                                      self.v_param.get(), self.v_ajuste.get())
        ultimo = int(total.index[-1])
        x_fin = ultimo + horizonte
        if len(futuros):
            ax.plot(np.r_[ultimo, futuros], np.r_[total.iloc[-1], estimado], color=AMARILLO,
                    linestyle="--", linewidth=2.4, marker="o", markersize=4,
                    label=f"Proyección: {modelo}")
            ax.axvspan(ultimo, x_fin + 0.5, color=AMARILLO, alpha=0.06)
            ax.annotate(f"{numero(estimado[-1])} sismos", xy=(futuros[-1], estimado[-1]),
                        xytext=(-8, 10), textcoords="offset points", ha="right",
                        color=AMARILLO, fontsize=9, fontweight="bold")
        if self.v_comparar.get():
            modelo_b = self.v_modelo_b.get()
            parametro_b = PARAMETRO[modelo_b][3] if PARAMETRO[modelo_b] else 0
            fb, eb = proyectar(modelo_b, total.index, total.to_numpy(), horizonte,
                               parametro_b, self.v_ajuste.get())
            if len(fb):
                ax.plot(np.r_[ultimo, fb], np.r_[total.iloc[-1], eb], color=COLOR_COMPARACION,
                        linestyle="--", linewidth=1.8, marker="s", markersize=3,
                        label=f"Comparación: {modelo_b}")
        ax.axvline(vision, color=SUAVE, linestyle=":", linewidth=1.4, zorder=1)
        ax.set_title("Proyección: histórico y años futuros", color=TEXTO, fontsize=10,
                     loc="left", fontweight="bold")
        ax.set_xlabel("Año", color=SUAVE, fontsize=8)
        ax.set_ylabel("Sismos por año (total)", color=SUAVE, fontsize=8)
        ax.set_xlim(desde - 0.5, x_fin + 0.5)
        ax.legend(loc="upper left", fontsize=8, frameon=False, labelcolor=TEXTO)
        self.figura.subplots_adjust(left=0.07, right=0.985, top=0.94, bottom=0.09, hspace=0.42)
        self.lienzo.draw_idle()

        # ---- indicadores ----
        self.kpi["promedio"][0].configure(text=numero(info["promedio"], 1))
        self.kpi["promedio"][1].configure(text=f"sismos por año ({desde}-{hasta})")
        self.kpi["maximo"][0].configure(text=numero(info["maximo"]))
        self.kpi["maximo"][1].configure(text=f"en {info['anio_max']}")
        self.kpi["minimo"][0].configure(text=numero(info["minimo"]))
        self.kpi["minimo"][1].configure(text=f"en {info['anio_min']}")
        self.kpi["registro"][0].configure(text=numero(info["registro"]))
        self.kpi["registro"][1].configure(text="sismos en el período")
        flecha = {"Aumenta": "▲", "Disminuye": "▼", "Estable": "■"}[info["tendencia"]]
        color = {"Aumenta": ROJO, "Disminuye": "#80ED99", "Estable": TEXTO}[info["tendencia"]]
        self.kpi["tendencia"][0].configure(text=f"{flecha} {info['tendencia']}", fg=color)
        self.kpi["tendencia"][1].configure(text=("+" if info["pendiente"] >= 0 else "") + numero(info["pendiente"], 1) + " sismos por año cada año")

        # ---- lectura de la línea de visión y de la proyección ----
        if vision in tabla.index:
            partes = [f"{z.capitalize()} {numero(tabla.loc[vision, z])}" for z in zonas]
            lectura = (f"Línea de visión {vision}:  " + "  ·  ".join(partes) +
                       f"  ·  Total {numero(tabla.loc[vision, 'Total'])} sismos")
        else:
            lectura = f"Línea de visión {vision}: año excluido por el filtro de grandes terremotos."
        if len(futuros):
            lectura += (f"\nProyección ({modelo}): {numero(estimado[0])} sismos en {int(futuros[0])} "
                        f"y {numero(estimado[-1])} en {int(futuros[-1])}.")
        self.texto_lectura.configure(text=lectura)

        diferencia = (estimado[-1] / info["promedio"] - 1) * 100 if len(futuros) else 0
        self.texto_interpretacion.configure(text=(
            f"Lectura: la tendencia histórica {info['tendencia'].lower()} "
            f"({numero(info['pendiente'], 1)} sismos por año cada año). La proyección final queda "
            f"{numero(abs(diferencia))} % {'sobre' if diferencia >= 0 else 'bajo'} el promedio del período. "
            "Es una extrapolación simple de la frecuencia anual: no predice cuándo ocurrirá un sismo."))


def main():
    datos = cargar_dataset_limpio(RUTA_DATOS)
    raiz = tk.Tk()
    if datos is None:
        messagebox.showerror("Dashboard", f"No se pudo cargar el dataset limpio:\n{RUTA_DATOS}\n\n"
                             "Ejecute primero: python main.py limpieza")
        raiz.destroy()
        return
    Dashboard(raiz, datos)
    raiz.mainloop()


if __name__ == "__main__":
    main()
