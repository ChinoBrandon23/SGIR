import subprocess
import os
import time

import rich
from rich.align import Align
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.prompt import Prompt

from models.platillo import Platillo
from models.venta import Venta, Consumo
from views.VistaBase import VistaBase
from views.clases_personalizadas.InputEmisor import InputEmisor


class VistaVentas(VistaBase):
    def __init__(self, console):
        super().__init__()
        self.console = console

        self.tabla_ventas = Table(title="Ventas")
        self.configurar_tabla_ventas()

        self.tabla_consumo = Table(title="Consumo")
        self.tabla_consumo.show_header = False
        self.tabla_consumo.show_lines = True

        self.input_menu_ventas = InputEmisor()
        self.input_abrir_detalles = InputEmisor()
        self.input_menu_detalles = InputEmisor()
        self.input_menu_editar = InputEmisor()
        self.input_menu_editar_consumo = InputEmisor()
        self.input_menu_filtros = InputEmisor()
        self.input_seleccion_platillo = InputEmisor()
        self.input_platillos_conflicto = InputEmisor()

        self.layout["contenido"].split_column(Layout(name="banda_pagina"), Layout(name="main"), Layout(name="opciones"))

        self.mostrar_todas_ventas(0, 0)
        self.crear_banda_opciones_principal()

    def resetear_vista(self):
        self.layout["main"].unsplit()

        self.tabla_ventas = Table(title="Ventas")
        self.configurar_tabla_ventas()
        self.tabla_consumo = Table(title="Consumo")
        self.configurar_tabla_consumo()

        self.crear_banda_opciones_principal()

    def mostrar_todas_ventas(self, pag_actual, total_pag):
        self.resetear_vista()

        self.layout["main"].update(Align.center(self.tabla_ventas, vertical="top"))
        self.mostrar_conteo_paginas(pag_actual, total_pag)

    def configurar_tabla_ventas(self):
        columnas = ["#", "Fecha", "Número de comensales", "Monto total"]

        for columna in columnas:
            self.tabla_ventas.add_column(columna)

    def crear_elemento_tabla_ventas(self, venta: Venta, idx_ui:int):
        self.tabla_ventas.add_row(str(idx_ui), str(venta.fecha), str(venta.numero_comensales), str(venta.monto_total))

    def mostrar_detalles_venta(self, venta: Venta | None, pag_detalles, pag_actual, total_pag, datos_editados, mapa_consumo):
        self.resetear_vista()
        self.mostrar_conteo_paginas(pag_actual, total_pag)

        self.layout["main"].split_column(Layout(name="panel_venta"), Layout(name="tabla_consumo"))

        self.layout["panel_venta"].size = 6

        panel = Panel(renderable=f"[bold yellow]Venta #{str(venta.num) if venta and venta.num != 0 else "-"}\n"
                                 f"[bold white]Fecha:[/bold white] {str(venta.fecha)}\n"
                                 f"[bold white]Comensales servidos:[/bold white] {str(venta.numero_comensales)}\n"
                                 f"[bold white]Monto total:[/bold white] ${str(venta.monto_total)}"
                                 f"[/bold yellow]")

        panel.height = 6

        if venta and len(pag_detalles):
            self.llenar_tabla_consumo(pag_detalles, mapa_consumo, datos_editados["consumo"])

        self.layout["panel_venta"].update(panel)
        self.layout["tabla_consumo"].update(Align.center(self.tabla_consumo, vertical="middle"))

    def configurar_tabla_consumo(self):
        encabezados = ["#", "Platillo", "Cantidad", "Importe"]

        self.tabla_consumo.show_lines = True

        for col in encabezados:
            self.tabla_consumo.add_column(col)

    def llenar_tabla_consumo(self, lista_consumo:list[Consumo], mapa_idx, consumo_editado=None):
        for consumo in lista_consumo:
            nombre_platillo = consumo.platillo.nombre

            idx_platillo = [item for item in mapa_idx if mapa_idx[item].platillo.nombre == nombre_platillo][0]

            if consumo_editado:
                # checa si un platillo que fue agregado al dict de edición está en la lista original de ingredientes,
                # lo que quiere decir que será editado, si es así entonces muestra el valor editado en vez del original
                valor_editado = next(filter(lambda x: x.platillo.nombre == nombre_platillo, consumo_editado), None)

                if valor_editado is not None:
                    # sobreescribe platillo editado (duplicado)
                    consumo_editado.remove(valor_editado)

                    self.tabla_consumo.add_row(f"[bold red]{str(idx_platillo)}[/bold red]",
                                                    f"[bold red]{nombre_platillo}[/bold red]",
                                                    f"[bold red]{str(valor_editado.cantidad_platillos)}[/bold red]",
                                                    f"[bold red]${str(valor_editado.importe)}[/bold red]")
                    continue

            # Agrega los platillos ya existentes
            self.tabla_consumo.add_row(str(idx_platillo),
                                             nombre_platillo,
                                             str(consumo.cantidad_platillos),
                                             f"${str(consumo.importe)}")

        if consumo_editado and len(consumo_editado) > 0:
            # agrega los platillos nuevos
            for platillo in consumo_editado:
                idx_platillo = [item for item in mapa_idx if mapa_idx[item] == platillo.platillo.nombre][0]

                self.tabla_consumo.add_row(f"[bold red]{idx_platillo}[/bold red]",
                                                f"[bold red]{platillo.platillo.nombre}[/bold red]",
                                                f"[bold red]{str(platillo.cantidad_platillos)}[/bold red]",
                                                f"[bold red]${str(platillo.importe)}[/bold red]")

    def mostrar_platillos_disponibles(self, lista_platillos:list[Platillo], pag_actual, total_pag):
        self.mostrar_conteo_paginas(pag_actual, total_pag)
        columnas = ["#", "Nombre"]

        tabla = Table(title="Platillos disponibles")

        for col in columnas:
            tabla.add_column(col)

        self.mostrar_conteo_paginas(pag_actual, total_pag)
        consola_size = self.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 9

        if pag_actual == 1:
            idx_ui = 0
        else:
            idx_ui = (pag_actual - 1) * lineas_disp

        for i in range(len(lista_platillos)):
            idx_ui += 1
            tabla.add_row(str(idx_ui), lista_platillos[i].nombre)

        self.layout["tabla_consumo"].update(Align.center(tabla, vertical="middle"))

    def mostrar_platillos_conflicto(self, lista_platillos:list[Platillo], pag_actual, total_pag):
        self.mostrar_conteo_paginas(pag_actual, total_pag)
        columnas = ["#", "Nombre"]

        tabla = Table(title="Platillos disponibles")

        for col in columnas:
            tabla.add_column(col)

        self.mostrar_conteo_paginas(pag_actual, total_pag)
        consola_size = self.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 9

        if pag_actual == 1:
            idx_ui = 0
        else:
            idx_ui = (pag_actual - 1) * lineas_disp

        for i in range(len(lista_platillos)):
            idx_ui += 1
            tabla.add_row(str(idx_ui), lista_platillos[i].nombre)

        self.layout["tabla_consumo"].update(Align.center(tabla, vertical="middle"))

    def mostrar_registrar_venta(self, venta:Venta | None, mapa_idx):
        self.resetear_vista()

        self.layout["main"].split_column(Layout(name="panel_venta"), Layout(name="tabla_consumo"))

        self.layout["panel_venta"].size = 6

        panel = Panel(renderable=f"[bold yellow]Venta #{str(venta.num) if venta and venta.num != 0 else "-"}\n"
                                 f"Fecha: {str(venta.fecha) if venta else ""}\n"
                                 f"Comensales servidos: {f"{str(venta.numero_comensales)}" if venta else ""}\n"
                                 f"Monto total: ${str(venta.monto_total) if venta else ""}"
                                 f"[/bold yellow]")

        panel.height = 6

        if venta:
            self.llenar_tabla_consumo(venta.detalles, mapa_idx)

        self.layout["panel_venta"].update(panel)
        self.layout["tabla_consumo"].update(Align.center(self.tabla_consumo, vertical="middle"))

    def crear_banda_opciones_principal(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Ver detalles de venta",
                    "[2] Registrar venta",
                    "[3] Filtrar búsqueda",
                    "[M] Volver al menú"]

        opciones_columna.expand = True

        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def crear_banda_opciones_detalles(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Volver a ventas",
                    "[M] Volver al menú"]

        opciones_columna.expand = True

        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def crear_banda_opciones_busqueda_av(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Por rango de fecha",
                    "[2] Mostrar todo",
                    "[3] Volver"]

        opciones_columna.expand = True

        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def crear_banda_opciones_editar(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Editar fecha",
                    "[2] Editar número de comensales",
                    "[3] Editar consumo",
                    "[4] Guardar",
                    "[5] Cancelar",
                    "[M] Volver al menú"]

        opciones_columna.expand = True
        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def crear_banda_opciones_editar_consumo(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Agregar consumo",
                    "[2] Editar cantidad",
                    "[3] Eliminar consumo",
                    "[4] Volver"]

        opciones_columna.expand = True
        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def mostrar_menu_ventas_prompt(self):
        self.input_menu_ventas.imprimir("Selecciona una opción o cambia de página [',' '.']",
                                        choices=["1", "2", "3", "m", ",", "."],
                                        show_choices=False)

        if self.input_menu_ventas.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_menu_ventas_prompt()

    def mostrar_abrir_detalles_prompt(self, lista_ventas: list[Venta]):
        self.input_abrir_detalles.imprimir("Ingresa el índice de la venta a mostrar",
                                           choices=[str(idx+1) for idx in range(len(lista_ventas))],
                                           show_choices=False)

        if self.input_abrir_detalles.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_abrir_detalles_prompt(lista_ventas)

    def mostrar_opciones_detalles_prompt(self):
        self.input_menu_detalles.imprimir("Selecciona una opción",
                                          choices=["1", "m", ",", "."],
                                          show_choices=False)

        if self.input_menu_detalles.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_opciones_detalles_prompt()

    def mostrar_opciones_busqueda_av_prompt(self):
        self.input_menu_filtros.imprimir("Selecciona una opción",
                                         choices=["1", "2", "3"],
                                         show_choices=False)

        if self.input_menu_detalles.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_opciones_detalles_prompt()

    def mostrar_prompt_eliminar_venta_prompt(self):
        confirmacion = Prompt.ask("[bold red]¡Atención! estás a punto de eliminar esta venta, confirma para continuar[/bold red]",
                                  choices=["S","N"])

        if confirmacion == "S":
            return True

        return False

    def mostrar_opciones_editar_prompt(self):
        self.input_menu_editar.imprimir("Selecciona una opción",
                                        choices=["1", "2", "3", "4", "5", "m", ",", "."],
                                        show_choices=False)

        if self.input_menu_editar.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_opciones_editar_prompt()

    def mostrar_opciones_editar_consumo_prompt(self):
        self.input_menu_editar_consumo.imprimir("Selecciona una opción",
                                        choices=["1", "2", "3", "4", ",", "."],
                                        show_choices=False)

        if self.input_menu_editar.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_opciones_editar_prompt()

    def mostrar_editar_fecha_prompt(self):
        self.refrescar_pantalla()

        fecha = Prompt.ask("[bold yellow]Ingresa la nueva fecha de venta en el siguiente formato: [[bold green]dd-mm-yyyy[/bold green]][/bold yellow]")

        if len(fecha) > 0:
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar nueva fecha: [italic white]{fecha}[/italic white][/bold yellow]",
                                      choices=["S", "N"])
            if confirmacion == "S":
                return fecha
            else:
                return None
        else:
            self.refrescar_pantalla()
            self.mostrar_editar_fecha_prompt()

    def mostrar_editar_comensales_prompt(self):
        self.refrescar_pantalla()

        comensales = Prompt.ask("[bold yellow]Ingresa el nuevo número de comensales para esta venta[/bold yellow]")

        if len(comensales):
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar número de comensales: [italic white]{comensales}[/italic white][/bold yellow]",
                                      choices=["S", "N"])
            if confirmacion == "S":
                return comensales
            else:
                return None
        else:
            self.refrescar_pantalla()
            self.mostrar_editar_comensales_prompt()

    def mostrar_editar_monto_total_prompt(self):
        self.refrescar_pantalla()

        monto_total = Prompt.ask("[bold yellow]Ingresa el nuevo monto total[/bold yellow]")

        confirmacion = Prompt.ask(f"[bold yellow]Confirma el nuevo monto total: [italic white]{monto_total}[/italic white][/bold yellow]",
                                  choices=["S","N"])

        if confirmacion == "S":
            return monto_total
        else:
            return None

    def mostrar_agregar_consumo_plat_prompt(self, opciones):
        opciones.append(",")
        opciones.append(".")
        self.refrescar_pantalla()
        num_platillo = ""

        if len(opciones) == 0:
            rich.print("[bold green]No hay platillos con precio vigente para agregar a esta venta, volviendo al menú editar...[/bold green]")
            time.sleep(3)
            return None

        while len(num_platillo) == 0 and num_platillo != "," and num_platillo != ".":
            num_platillo = self.input_seleccion_platillo.imprimir("[bold yellow]Selecciona un platillo de la lista para agregar[/bold yellow]",
                                      choices=opciones,
                                      show_choices=False)

            confirmacion = Prompt.ask(f"[bold yellow]Confirma el nuevo platillo[/bold yellow]",
                            choices=["S", "N"])

            if confirmacion == "S":
                return num_platillo

    def mostrar_agregar_consumo_cantidad_prompt(self):
        cantidad = ""

        while len(cantidad) == 0:
            self.refrescar_pantalla()
            cantidad = Prompt.ask("[bold yellow]Ingresa la cantidad de platillos consumida[bold yellow]")

            if len(cantidad) != 0:
                confirmacion = Prompt.ask(
                    f"[bold yellow]Confirma la cantidad: [italic white]{cantidad}[italic white][/bold yellow]",
                    choices=["S", "N"])

                if confirmacion == "S":
                    return cantidad
                else:
                    cantidad = ""

    def mostrar_editar_consumo_seleccion_plat(self, opciones):
        opciones.append(",")
        opciones.append(".")
        self.refrescar_pantalla()
        num_platillo = ""

        while len(num_platillo) == 0 and num_platillo != "," and num_platillo != ".":
            num_platillo = self.input_seleccion_platillo.imprimir(
                "[bold yellow]Ingresa el índice del platillo a editar[/bold yellow]",
                choices=opciones,
                show_choices=False)

            confirmacion = Prompt.ask(f"[bold yellow]Confirma selección[/bold yellow]",
                                      choices=["S", "N"])

            if confirmacion == "S":
                return num_platillo

    def mostrar_editar_cantidad_prompt(self, opciones):
        self.refrescar_pantalla()

        if len(opciones) == 0:
            rich.print("[bold green]No hay consumos para editar a esta venta, volviendo al menú editar...[/bold green]")
            time.sleep(3)
            return None, None

        num_cons = Prompt.ask("[bold yellow]Ingresa el índice del consumo a editar[/bold yellow]",
                              choices=opciones,
                              show_choices=False)

        cantidad = ""

        while len(cantidad) == 0:
            self.refrescar_pantalla()
            cantidad = Prompt.ask("[bold yellow]Ingresa la nueva cantidad para este consumo[/bold yellow]")

            if len(cantidad):
                confirmacion = Prompt.ask(f"[bold yellow]Confirma la nueva cantidad: [italic white]{cantidad}[/italic white][/bold yellow]")

                if confirmacion == "S":
                    return num_cons, cantidad
                else:
                    return None, None

    def mostrar_remover_consumo_prompt(self, opciones):
        self.refrescar_pantalla()

        if len(opciones) == 0:
            rich.print("[bold green]No hay consumos para editar a esta venta, volviendo al menú editar...[/bold green]")
            time.sleep(3)
            return None

        num = Prompt.ask("[bold yellow]Ingresa el índice del consumo a remover[/bold yellow]",
                         choices=opciones,
                         show_choices=False)

        return num

    def mostrar_buscar_por_rango_fecha_prompt(self):
        fecha_inicial = ""
        fecha_final = ""

        while len(fecha_inicial) == 0:
            self.refrescar_pantalla()
            fecha_inicial = Prompt.ask("[bold yellow]Ingresa la fecha inicial a buscar en el siguiente formato: [[bold green]dd-mm-yyyy[/bold green]][/bold yellow]")

        while len(fecha_final) == 0:
            self.refrescar_pantalla()
            fecha_final = Prompt.ask("[bold yellow]Ingresa la fecha final a buscar en el siguiente formato: [[bold green]dd-mm-yyyy[/bold green]][/bold yellow]")

        return fecha_inicial, fecha_final

    def mostrar_prompt_crear_venta_fecha(self):
        fecha = ""

        while len(fecha) == 0:
            self.refrescar_pantalla()
            fecha = Prompt.ask("Para comenzar, ingresa la fecha en que se realizó la venta o 0 para cancelar")
            if fecha == "0":
                return None

        return fecha

    def mostrar_prompt_crear_venta_comensales(self):
        num_comensales = ""

        while len(num_comensales) == 0:
            self.refrescar_pantalla()
            num_comensales = Prompt.ask("Ingresa el número de comensales")

        return num_comensales

    def mostrar_conteo_paginas(self, pag_actual, pag_total):
        paginas_columna = Columns()
        paginas = f"[bold magenta]Página {pag_actual}/{pag_total}[/bold magenta]"

        paginas_columna.expand = True
        self.layout["banda_pagina"].size = 1
        paginas_columna.add_renderable(Align.center(paginas))

        self.layout["banda_pagina"].update(paginas_columna)

    def mostrar_mensaje_no_pagina_anterior(self):
        rich.print("[bold green]Error: no hay página anterior")
        time.sleep(2)

    def mostrar_mensaje_no_pagina_siguiente(self):
        rich.print("[bold green]Error: no hay página siguiente")
        time.sleep(2)

    def mostrar_mensaje_no_resultados_busqueda_av(self):
        rich.print("[bold blue]Aviso: No se encontraron resultados para la búsqueda realizada, volviendo a al menú anterior...[/bold blue]")
        time.sleep(3)

    def mostrar_mensaje_no_platillos_disp(self):
        rich.print("[bold red]Error: No hay platillos disponibles para la fecha actual de venta, "
                   "crea un nuevo menú o cambia la fecha de venta")
        time.sleep(3)

    def mostrar_error_venta_stock_insuficiente(self):
        rich.print("[bold red]Error: No hay insumos suficientes para efectuar la venta.[/bold red]")
        time.sleep(3)

    def mostrar_mensaje_error_validacion(self, error:str):
        rich.print(f"[bold red]{error}[/bold red]")
        time.sleep(3)

    def mostrar_mensaje_advertencia_guardado(self):
        res = Prompt.ask("[bold blue]Atención: Una vez guardada la venta, no podrá ser editada. "
                         "Para confirmar guardado presione 1, para cancelar y continuar haciendo cambio, presione 2[/bold blue]",
                         choices=["1", "2"], show_choices=False)
        return res

    def mostrar_mensaje_platillos_conflicto(self, fecha_venta):
        self.refrescar_pantalla()
        eleccion = self.input_platillos_conflicto.imprimir(f"[bold yellow]Atención: Cambiar la fecha de venta a {fecha_venta} resultará en la remoción de los siguientes platillos."
                                                           f" ¿Deseas continuar?[/bold yellow][italic magenta][S, N][/italic magenta]", choices=["S", "N", ",", "."])
        if eleccion is "," or eleccion is ".":
            self.mostrar_mensaje_platillos_conflicto(fecha_venta)

        return eleccion

    def refrescar_pantalla(self):
        try:
            subprocess.run('cls' if os.name == 'nt' else 'clear')
        except FileNotFoundError:
            print(chr(27) + "[2J")
        self.console.print(self.layout, justify="center")