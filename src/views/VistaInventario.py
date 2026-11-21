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

from models.compra import DetalleCompra
from models.insumo import Insumo
from models.marca import Marca
from models.tipo_insumo import TipoInsumo
from views.VistaBase import VistaBase
from views.clases_personalizadas.InputEmisor import InputEmisor


class VistaInventario(VistaBase):
    def __init__(self, console):
        super().__init__()
        self.console = console

        self.tabla_inventario = Table(title="Inventario")
        self.configurar_tabla_insumos()

        self.tabla_detalles = Table(title="Detalles")
        self.configurar_tabla_detalles()

        self.input_menu_inventario = InputEmisor()
        self.input_abrir_detalles = InputEmisor()
        self.input_menu_detalles = InputEmisor()
        self.input_menu_editar_inventario = InputEmisor()
        self.input_menu_filtros = InputEmisor()
        self.input_seleccion_tipo_insumo = InputEmisor()
        self.input_seleccion_marca = InputEmisor()

        self.layout["contenido"].split_column(Layout(name="banda_pagina"), Layout(name="main"), Layout(name="opciones"))

        self.mostrar_todos_insumos(0, 0)
        self.crear_banda_opciones_principal()

    def resetear_vista(self):
        self.layout["main"].unsplit()

        self.tabla_inventario = Table(title="Inventario")
        self.configurar_tabla_insumos()
        self.tabla_detalles = Table(title="Detalles")
        self.configurar_tabla_detalles()

        self.crear_banda_opciones_principal()

    def mostrar_todos_insumos(self, pag_actual:int, total_pag:int):
        self.resetear_vista()

        self.layout["main"].update(Align.center(self.tabla_inventario, vertical="top"))
        self.mostrar_conteo_paginas(pag_actual, total_pag)

    def configurar_tabla_insumos(self):
        columnas = ["#", "Nombre", "Tipo de insumo", "Marca", "Umbral", "Stock", "Alerta"]

        for columna in columnas:
            self.tabla_inventario.add_column(columna)

    def crear_elemento_tabla_insumos(self, insumo: Insumo, alerta_stock:bool, idx:int):
        if alerta_stock:
            celda_alerta = "[bold red]:warning: Stock bajo[/bold red]"
        else:
            celda_alerta = ""

        self.tabla_inventario.add_row(str(idx), insumo.nombre, insumo.tipo_insumo.nombre,
                                      insumo.marca.nombre,str(insumo.umbral), str(insumo.stock), celda_alerta)

    def mostrar_detalles_insumo(self, insumo: Insumo | None, pag_actual, total_pag, lista_detalles:list[DetalleCompra], datos_editados):
        self.resetear_vista()

        self.mostrar_conteo_paginas(pag_actual, total_pag)
        self.layout["main"].split_column(Layout(name="panel_insumo"), Layout(name="tabla_detalles_insumo"))
        self.layout["panel_insumo"].size = 6

        panel = Panel(renderable=f"{"[bold red]" if "nombre" in datos_editados else "[bold yellow]"}"
                                 f"{insumo.nombre if insumo and insumo.nombre else "Insumo"}"
                                 f"{"[/bold red]" if "nombre" in datos_editados else "[/bold yellow]"}\n"
                                 f"{"[bold red]" if "stock" in datos_editados else "[bold yellow]"}"
                                 f"[bold white]Stock:[/bold white] {insumo.stock if insumo and insumo.stock else ""}"
                                 f"{"[/bold red]" if "stock" in datos_editados else "[/bold yellow]"} "
                                 f"{"[bold red]" if "umbral" in datos_editados else "[bold yellow]"} "
                                 f"[bold white]Umbral:[/bold white] {insumo.umbral if insumo and insumo.umbral else ""}"
                                 f"{"[/bold red]" if "umbral" in datos_editados else "[/bold yellow]"}\n"
                                 f"{"[bold red]" if "tipo_insumo" in datos_editados else "[bold yellow]"}"
                                 f"[bold white]Tipo de insumo:[/bold white] {insumo.tipo_insumo.nombre if insumo and insumo.tipo_insumo.nombre else ""}"
                                 f"{"[/bold red]" if "tipo_insumo" in datos_editados else "[/bold yellow]"}\n"
                                 f"{"[bold red]" if "marca" in datos_editados else "[bold yellow]"}"
                                 f"[bold white]Marca:[/bold white] {insumo.marca.nombre if insumo and insumo.marca.nombre else ""}"
                                 f"{"[/bold red]" if "marca" in datos_editados else "[/bold yellow]"}")

        panel.height = 6

        if len(lista_detalles):
            self.llenar_tabla_detalles(lista_detalles)

        self.layout["panel_insumo"].update(panel)
        self.layout["tabla_detalles_insumo"].update(Align.center(self.tabla_detalles, vertical="middle"))

    def configurar_tabla_detalles(self):
        encabezados = ["Fecha de compra", "Cantidad actual", "Unidad de medida", "Fecha de caducidad", "Monto Unitario", "Importe"]

        self.tabla_detalles.show_lines = True

        for col in encabezados:
            self.tabla_detalles.add_column(col)

    def llenar_tabla_detalles(self, lista_detalles:list[DetalleCompra]):
        for detalle in lista_detalles:
            self.tabla_detalles.add_row(str(detalle.fecha_compra), str(detalle.cantidad_actual), detalle.unidad_medida, str(detalle.fecha_caducidad), str(detalle.monto_unitario), str(detalle.importe))

    def crear_banda_opciones_principal(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Ver detalles de insumo",
                    "[2] Búsqueda avanzada",
                    "[M] Volver al menú"]

        opciones_columna.expand = True

        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def crear_banda_opciones_detalles(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Volver a inventario",
                    "[2] Editar insumo",
                    "[M] Volver al menú"]

        opciones_columna.expand = True

        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def crear_banda_opciones_busqueda_av(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Por nombre",
                    "[2] Por tipo de insumo",
                    "[3] Por marca",
                    "[4] Por stock bajo",
                    "[5] Mostrar todo",
                    "[6] Volver a menús"]

        opciones_columna.expand = True

        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def crear_banda_opciones_editar(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Editar nombre",
                    "[2] Editar umbral",
                    "[3] Editar tipo de insumo",
                    "[4] Guardar",
                    "[5] Cancelar",
                    "[M] Volver al menú"]

        opciones_columna.expand = True
        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def mostrar_menu_insumos_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_inventario.imprimir("Selecciona una opción o cambia de página [',' '.']",
                                            choices=["1", "2", "m", ",", "."],
                                            show_choices=False)

        if self.input_menu_inventario.user_input is None:
            self.mostrar_menu_insumos_prompt()

    def mostrar_abrir_detalles_prompt(self, lista_insumos: list[Insumo]):
        self.refrescar_pantalla()
        self.input_abrir_detalles.imprimir("Ingresa el índice del insumo a mostrar",
                                           choices=[str(i+1) for i in range(len(lista_insumos))],
                                           show_choices=False)

        if self.input_abrir_detalles.user_input is None:
            self.mostrar_abrir_detalles_prompt(lista_insumos)

    def mostrar_opciones_detalles_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_detalles.imprimir("Selecciona una opción o cambia de página [',' '.']",
                                          choices=["1", "2", "m", ",", "."],
                                          show_choices=False)

        if self.input_menu_detalles.user_input is None:
            self.mostrar_opciones_detalles_prompt()

    def mostrar_opciones_busqueda_av_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_filtros.imprimir("Selecciona una opción o cambia de página [',' '.']",
                                         choices=["1", "2", "3", "4", "5", "6", ",", "."],
                                         show_choices=False)

        if self.input_menu_filtros.user_input == "," or self.input_menu_filtros.user_input == ".":
            self.mostrar_opciones_busqueda_av_prompt()

    def mostrar_prompt_eliminar_insumo_prompt(self):
        self.refrescar_pantalla()
        confirmacion = Prompt.ask("[bold red]¡Atención! estás a punto de eliminar este insumo, confirma para continuar[/bold red]",
                                  choices=["S","N"])

        if confirmacion == "S":
            return True

        return False

    def mostrar_opciones_editar_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_editar_inventario.imprimir("Selecciona una opción o cambia de página [',' '.']",
                                                   choices=["1", "2", "3", "4", "5", "m", ",", "."],
                                                   show_choices=False)

        if self.input_menu_editar_inventario.user_input is None:
            self.mostrar_opciones_editar_prompt()

    def mostrar_editar_nombre_prompt(self):
        self.refrescar_pantalla()
        info = Prompt.ask("[bold yellow]Ingresa el nuevo nombre del insumo[/bold yellow]")

        if len(info) > 0:
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar nuevo nombre[/bold yellow] "
                                      f"[italic white]{info}[/italic white]", choices=["S", "N"])
            if confirmacion == "S":
                return info
            else:
                return None
        else:
            self.mostrar_editar_nombre_prompt()

    def mostrar_editar_umbral_prompt(self):
        self.refrescar_pantalla()
        umbral = Prompt.ask("[bold yellow]Ingresa el nuevo umbral para este insumo[/bold yellow]")

        if len(umbral) > 0:
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar nuevo umbral[/bold yellow] "
                                      f"[italic white]{umbral}[/italic white]", choices=["S", "N"])
            if confirmacion == "S":
                return umbral
            else:
                return None
        else:
            self.mostrar_editar_umbral_prompt()

    def mostrar_tipos_insumo_disponibles(self, lista_tipos:list[TipoInsumo], pag_actual, total_pag):
        columnas = ["#", "Nombre"]

        tabla = Table(title="Tipos de insumo disponibles")

        consola_size = self.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 20

        if pag_actual == 1:
            idx_ui = 0
        else:
            idx_ui = (pag_actual - 1) * lineas_disp

        for col in columnas:
            tabla.add_column(col)

        if len(lista_tipos):
            for i in range(len(lista_tipos)):
                idx_ui += 1
                tabla.add_row(str(idx_ui), lista_tipos[i].nombre)
        else:
            tabla.add_row(" " * 10, " " * 10)

        try:
            self.layout["tabla_detalles_insumo"].update(Align.center(tabla, vertical="middle"))
        except KeyError:
            self.layout["main"].update(Align.center(tabla, vertical="middle"))

    def mostrar_marcas_disponibles(self, lista_marcas:list[Marca], pag_actual, total_pag):
        columnas = ["#", "Nombre"]

        tabla = Table(title="Marcas disponibles")

        self.mostrar_conteo_paginas(pag_actual, total_pag)

        consola_size = self.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 20

        if pag_actual == 1:
            idx_ui = 0
        else:
            idx_ui = (pag_actual - 1) * lineas_disp

        for col in columnas:
            tabla.add_column(col)

        if len(lista_marcas):
            for i in range(len(lista_marcas)):
                idx_ui += 1
                tabla.add_row(str(idx_ui), lista_marcas[i].nombre)
        else:
            tabla.add_row(" " * 10, " " * 10)

        try:
            self.layout["tabla_detalles_insumo"].update(Align.center(tabla, vertical="middle"))
        except KeyError:
            self.layout["main"].update(Align.center(tabla, vertical="middle"))

    def mostrar_editar_tipo_insumo_prompt(self, opciones):
        opciones.append("0")
        opciones.append(",")
        opciones.append(".")

        tipo_ins = ""

        while len(tipo_ins) == 0 or tipo_ins == "," or tipo_ins == ".":
            self.refrescar_pantalla()
            tipo_ins = self.input_seleccion_tipo_insumo.imprimir("[bold yellow]Selecciona el tipo de insumo de entre las opciones o presiona 0 para crear un nuevo tipo[/bold yellow]",
                                  choices=opciones,
                                  show_choices=False)

        confirmacion = Prompt.ask(f"[bold yellow]Confirmar selección de tipo de insumo[bold yellow]", choices=["S", "N"])

        if confirmacion == "S":
            return tipo_ins
        return None

    def mostrar_crear_tipo_insumo_prompt(self):
        tipo_nombre = ""

        while len(tipo_nombre) == 0:
            self.refrescar_pantalla()
            tipo_nombre = Prompt.ask("[bold yellow]Ingresa el nombre del nuevo tipo de insumo[/bold yellow]")

        confirmacion = Prompt.ask(f"[bold yellow]Confirmar crear nuevo tipo de insumo: [italic white]{tipo_nombre}[/italic white][/bold yellow]", choices=["S", "N"])

        if confirmacion == "S":
            return tipo_nombre
        return None

    def mostrar_buscar_por_nombre_prompt(self):
        nombre = ""

        while len(nombre) == 0:
            self.refrescar_pantalla()
            nombre = Prompt.ask("[bold yellow]Ingresa el nombre a buscar[/bold yellow]")

        return nombre

    def mostrar_buscar_por_tipo_insumo_prompt(self, opciones):
        opciones.append(".")
        opciones.append(",")

        tipo_ins = ""

        while len(tipo_ins) == 0 or tipo_ins == "," or tipo_ins == ".":
            self.refrescar_pantalla()
            tipo_ins = self.input_seleccion_tipo_insumo.imprimir( "[bold yellow]Selecciona el tipo de insumo a buscar de entre las opciones o cambia de página [',' '.'][/bold yellow]",
                choices=opciones,
                show_choices=False)

        return tipo_ins

    def mostrar_buscar_por_marca_prompt(self, opciones):
        opciones.append(".")
        opciones.append(",")

        marca_num = ""

        while len(marca_num) == 0 or marca_num == "," or marca_num == ".":
            self.refrescar_pantalla()
            marca_num = self.input_seleccion_marca.imprimir("[bold yellow]Selecciona la marca a buscar de entre las opciones o cambia de página [',' '.'][/bold yellow]",
                              choices=opciones,
                              show_choices=False)

        return marca_num

    def mostrar_prompt_crear_menu(self):
        nombre = Prompt.ask("Para comenzar, ingresa el nombre del nuevo menú o 0 para cancelar")

        if len(nombre) == 0:
            self.refrescar_pantalla()
            self.mostrar_prompt_crear_menu()

        if nombre is not "0":
            return nombre

        return None

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

    def mostrar_mensaje_tipo_insumo_ya_existe(self):
        rich.print("[bold blue]Error: el tipo de insumo que intenta crear ya existe, volviendo al menú anterior...[/bold blue]")
        time.sleep(2)

    def mostrar_mensaje_no_resultados_busqueda_av(self):
        rich.print("[bold blue]Aviso: No se encontraron resultados para la búsqueda realizada, volviendo a al menú de búsqueda avanzada...[/bold blue]")
        time.sleep(3)

    def mostrar_mensaje_nombre_duplicado(self):
        rich.print("[bold red]Error: El nombre ingresado ya existe. Cambia el nombre actual o edita el insumo existente.[/bold red]")
        time.sleep(3)

    def mostrar_mensaje_error_validacion(self, error:str):
        rich.print(f"[bold red]{error}[/bold red]")
        time.sleep(3)

    def refrescar_pantalla(self):
        try:
            subprocess.run('cls' if os.name == 'nt' else 'clear')
        except FileNotFoundError:
            print(chr(27) + "[2J")
        self.console.print(self.layout, justify="center")
