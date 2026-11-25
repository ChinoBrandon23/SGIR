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

from models.insumo import Insumo
from models.merma import Merma
from models.platillo import Platillo
from models.tipo_merma import TipoMerma
from views.VistaBase import VistaBase
from views.clases_personalizadas.InputEmisor import InputEmisor


class VistaMerma(VistaBase):
    def __init__(self, console):
        super().__init__()
        self.console = console

        self.tabla_merma = Table(title="Merma")
        self.configurar_tabla_merma()

        self.tabla_detalles = Table(title="Detalles")
        self.configurar_tabla_detalles()

        self.input_menu_merma = InputEmisor()
        self.input_abrir_detalles = InputEmisor()
        self.input_menu_detalles = InputEmisor()
        self.input_menu_editar_merma = InputEmisor()
        self.input_menu_filtros = InputEmisor()
        self.input_seleccion_insumos = InputEmisor()
        self.input_seleccion_platillo = InputEmisor()
        self.input_seleccion_tipo_merma = InputEmisor()

        self.layout["contenido"].split_column(Layout(name="banda_pagina"), Layout(name="main"), Layout(name="opciones"))

        self.mostrar_toda_merma(0, 0)
        self.crear_banda_opciones_principal()

    def resetear_vista(self):
        self.layout["main"].unsplit()

        self.tabla_merma = Table(title="Merma")
        self.configurar_tabla_merma()

        self.tabla_detalles = Table(title="Detalles")
        self.configurar_tabla_detalles()

        self.crear_banda_opciones_principal()

    def mostrar_toda_merma(self, pag_actual, total_pag):
        self.resetear_vista()

        self.layout["main"].update(Align.center(self.tabla_merma, vertical="top"))
        self.mostrar_conteo_paginas(pag_actual, total_pag)

    def configurar_tabla_merma(self):
        columnas = ["#", "Fecha", "Cantidad", "Unidad de medida", "Insumo", "Tipo de merma"]

        for columna in columnas:
            self.tabla_merma.add_column(columna)

    def configurar_tabla_detalles(self):
        columnas = ["Fuente", "Cantidad", "Unidad de medida", "Descripción"]

        for columna in columnas:
            self.tabla_detalles.add_column(columna)

    def crear_elemento_tabla_merma(self, merma: Merma, idx_ui:int):
        self.tabla_merma.add_row(str(idx_ui), str(merma.fecha), str(merma.cantidad), merma.unidad_medida,
                                 merma.insumo.nombre, merma.tipo_merma.nombre)

    def mostrar_detalles_merma(self, merma: Merma | None, datos_editados):
        self.resetear_vista()

        self.layout["main"].split_column(Layout(name="panel_merma"), Layout(name="tabla_detalles"))

        self.layout["panel_merma"].size = 5

        panel = Panel(renderable=f"[bold yellow]Merma #{str(merma.num) if merma and merma.num != 0 else "-"}\n"
                                 f"[bold white]Fecha:[/bold white] {"[bold red]" if "fecha" in datos_editados else ""}"
                                 f"{(str(merma.fecha)) if merma else ""}{"[/bold red]" if "fecha" in datos_editados else ""}\n"
                                 f"[bold white]Tipo de merma:[/bold white] {"[bold red]" if "tipo" in datos_editados else ""}{(str(merma.tipo_merma.nombre)) if merma else ""}"
                                 f"{"[/bold red]" if "tipo" in datos_editados else ""}")

        panel.height = 5

        if merma:
            self.llenar_tabla_detalles_merma(merma, datos_editados)

        self.layout["panel_merma"].update(panel)
        self.layout["tabla_detalles"].update(Align.center(self.tabla_detalles, vertical="middle"))

    def llenar_tabla_detalles_merma(self, merma_obj:Merma, datos_editados=None):
        self.tabla_detalles.add_row( f"{"[bold yellow]"}"
                                     f"{merma_obj.insumo.nombre if merma_obj.insumo.num != 0 else datos_editados["platillo_merma"].nombre}",
                                         f"{"[bold red]" if datos_editados and "cantidad" in datos_editados else "[bold yellow]"}"
                                         f"{str(merma_obj.cantidad)}{"[/bold red]" if datos_editados and "cantidad" in datos_editados else "[/bold yellow]"}",
                                         f"{"[bold red]" if datos_editados and "unidad_medida" in datos_editados else "[bold yellow]"}"
                                         f"{merma_obj.unidad_medida}{"[/bold red]" if datos_editados and "unidad_medida" in datos_editados else "[/bold yellow]"}",
                                         f"{"[bold red]" if datos_editados and "descripcion" in datos_editados else "[bold yellow]"}"
                                         f"{merma_obj.descripcion}{"/[bold red]" if datos_editados and "descripcion" in datos_editados else "[/bold yellow]"}")

    def mostrar_tipos_merma_disponibles(self, lista_tipo_merma:list[TipoMerma], pag_actual, total_pag):
        self.refrescar_pantalla()

        self.mostrar_conteo_paginas(pag_actual, total_pag)
        consola_size = self.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 10

        if pag_actual == 1:
            idx_ui = 0
        else:
            idx_ui = (pag_actual - 1) * lineas_disp

        columnas = ["#", "Nombre"]

        tabla = Table(title="Tipos de merma disponibles")

        for col in columnas:
            tabla.add_column(col)

        for i in range(len(lista_tipo_merma)):
            idx_ui += 1
            tabla.add_row(str(idx_ui), lista_tipo_merma[i].nombre)

        try:
            self.layout["tabla_detalles"].update(Align.center(tabla, vertical="middle"))
        except KeyError:
            self.layout["main"].update(Align.center(tabla, vertical="middle"))

    def mostrar_insumos_disponibles(self, lista_insumos:list[Insumo], pag_actual, total_pag):
        self.refrescar_pantalla()

        self.mostrar_conteo_paginas(pag_actual, total_pag)
        consola_size = self.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 10

        if pag_actual == 1:
            idx_ui = 0
        else:
            idx_ui = (pag_actual - 1) * lineas_disp

        columnas = ["#", "Nombre"]

        tabla = Table(title="Insumos disponibles")

        for col in columnas:
            tabla.add_column(col)

        for i in range(len(lista_insumos)):
            idx_ui += 1
            tabla.add_row(str(idx_ui), lista_insumos[i].nombre)

        try:
            self.layout["tabla_detalles"].update(Align.center(tabla, vertical="middle"))
        except KeyError:
            self.layout["main"].split_column(Layout(name="tabla_detalles"))
            self.layout["tabla_detalles"].update(Align.center(tabla, vertical="middle"))

    def mostrar_platillos_disponibles(self, lista_platillos:list[Platillo], pag_actual, total_pag):
        self.refrescar_pantalla()

        self.mostrar_conteo_paginas(pag_actual, total_pag)
        consola_size = self.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 10

        if pag_actual == 1:
            idx_ui = 0
        else:
            idx_ui = (pag_actual - 1) * lineas_disp

        columnas = ["#", "Nombre"]

        tabla = Table(title="Platillos disponibles")

        for col in columnas:
            tabla.add_column(col)

        for i in range(len(lista_platillos)):
            idx_ui += 1
            tabla.add_row(str(idx_ui), lista_platillos[i].nombre)

        try:
            self.layout["tabla_detalles"].update(Align.center(tabla, vertical="middle"))
        except KeyError:
            self.layout["main"].update(Align.center(tabla, vertical="middle"))

    def mostrar_registrar_merma(self, merma: Merma | None):
        self.resetear_vista()

        self.layout["main"].split_column(Layout(name="panel_merma"), Layout(name="tabla_detalles"))

        self.layout["panel_merma"].size = 5

        panel = Panel(renderable=f"[bold yellow]Merma #{str(merma.num) if merma and merma.num != 0 else "-"}\n"
                                 f"Fecha: {(str(merma.fecha)) if merma else ""}\n"
                                 f"Tipo de merma: {(str(merma.tipo_merma.nombre)) if merma else ""}")

        panel.height = 5

        if merma:
            self.llenar_tabla_detalles_merma(merma)
        else:
            self.tabla_detalles.add_row(" " * 10, " " * 10, " " * 10, " " * 10)

        self.layout["panel_merma"].update(panel)
        self.layout["tabla_detalles"].update(Align.center(self.tabla_detalles, vertical="middle"))

    def crear_banda_opciones_principal(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Ver detalles de merma",
                    "[2] Registrar merma",
                    "[3] Búsqueda avanzada",
                    "[M] Volver al menú"]

        opciones_columna.expand = True

        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def crear_banda_opciones_detalles(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Volver a mermas",
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
                    "[2] Por tipo de merma",
                    "[3] Por insumo",
                    "[4] Mostrar todo",
                    "[M] Volver al menú"]

        opciones_columna.expand = True

        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def crear_banda_opciones_editar(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Editar descripción",
                    "[2] Editar fecha",
                    "[3] Editar cantidad",
                    "[4] Editar unidad",
                    "[5] Editar tipo",
                    "[6] Guardar",
                    "[7] Cancelar",
                    "[M] Volver al menú"]

        opciones_columna.expand = True
        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def mostrar_menu_merma_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_merma.imprimir("Selecciona una opción o cambia de página [',' '.']",
                                       choices=["1", "2", "3", "m", ",", "."],
                                       show_choices=False)

        if not self.input_menu_merma.user_input or self.input_menu_merma.user_input == "," or self.input_menu_merma.user_input == ".":
            self.mostrar_menu_merma_prompt()

    def mostrar_abrir_detalles_prompt(self, lista_merma: list[Merma]):
        self.refrescar_pantalla()
        self.input_abrir_detalles.imprimir("Ingresa el índice de la merma a mostrar",
                                           choices=[str(merma.num) for merma in lista_merma],
                                           show_choices=False)

        if not self.input_abrir_detalles.user_input or self.input_abrir_detalles.user_input == "," or self.input_abrir_detalles.user_input == ".":
            self.mostrar_abrir_detalles_prompt(lista_merma)

    def mostrar_opciones_detalles_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_detalles.imprimir("Selecciona una opción",
                                          choices=["1", "2", "m"],
                                          show_choices=False)

        if not self.input_menu_detalles.user_input or self.input_menu_detalles.user_input == "," or self.input_menu_detalles.user_input == ".":
            self.mostrar_opciones_detalles_prompt()

    def mostrar_opciones_busqueda_av_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_filtros.imprimir("Selecciona una opción o cambia de página [',' '.']",
                                         choices=["1", "2", "3", "4", ",", "."],
                                         show_choices=False)

        if not self.input_menu_detalles.user_input or self.input_menu_detalles.user_input == "," or self.input_menu_detalles.user_input == ".":
            self.mostrar_opciones_detalles_prompt()

    def mostrar_prompt_eliminar_merma_prompt(self):
        confirmacion = Prompt.ask("[bold red]¡Atención! estás a punto de eliminar este registro, confirma para continuar[/bold red]",
                                  choices=["S","N"])

        if confirmacion == "S":
            return True

        return False

    def mostrar_opciones_editar_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_editar_merma.imprimir("Selecciona una opción",
                                              choices=["1", "2", "3", "4", "5", "6", "7", "m"],
                                              show_choices=False)

        if self.input_menu_editar_merma.user_input == "," or self.input_menu_editar_merma.user_input == ".":
            self.mostrar_opciones_editar_prompt()

    def mostrar_editar_descripcion_prompt(self):
        info = ""

        while len(info) == 0:
            self.refrescar_pantalla()
            info = Prompt.ask("[bold yellow]Ingresa la nueva descripción de la merma[/bold yellow]")

        self.refrescar_pantalla()

        confirmacion = Prompt.ask(f"[bold yellow]Confirmar nueva descripción[/bold yellow]", choices=["S", "N"])
        if confirmacion == "S":
            return info
        else:
            return None

    def mostrar_crear_fecha_prompt(self):
        info = ""

        while not info or len(info) == 0 :
            self.refrescar_pantalla()
            info = Prompt.ask(
                "[bold yellow]Para comenzar, ingresa la nueva fecha en el siguiente formato[/bold yellow]: [[bold green]dd-mm-yyyy[/bold green]] [bold yellow]o presiona 0 para cancelar[/bold yellow]")

            if info == "0":
                return info

        self.refrescar_pantalla()
        confirmacion = Prompt.ask(f"[bold yellow]Confirmar fecha:[/bold yellow] "
                                      f"[italic white]{info}[/italic white]", choices=["S", "N"])
        if confirmacion == "S":
            return info
        else:
            self.mostrar_editar_fecha_prompt()

    def mostrar_editar_fecha_prompt(self):
        info = ""

        while not info or len(info) == 0:
            self.refrescar_pantalla()
            info = Prompt.ask(
                "[bold yellow]Ingresa la nueva fecha en el siguiente formato[/bold yellow]: [[bold green]dd-mm-yyyy[/bold green]]")

        self.refrescar_pantalla()
        confirmacion = Prompt.ask(f"[bold yellow]Confirmar fecha:[/bold yellow] "
                                  f"[italic white]{info}[/italic white]", choices=["S", "N"])
        if confirmacion == "S":
            return info
        else:
            return None

    def mostrar_crear_unidad_medida_prompt(self):
        unidad = ""

        while len(unidad) == 0:
            self.refrescar_pantalla()
            unidad = Prompt.ask("[bold yellow]Ingresa la nueva unidad de medida\nDisponibles ->[/bold yellow] [bold green]kg / g / l / ml [/bold green]")

        self.refrescar_pantalla()
        confirmacion = Prompt.ask("[bold yellow]Confirmar nueva unidad de medida:[/bold yellow] "
                                      f"[italic white]{unidad}[/italic white]",
                                      choices=["S","N"])

        if confirmacion == "S":
            return unidad
        else:
            self.mostrar_editar_unidad_medida_prompt()

    def mostrar_editar_unidad_medida_prompt(self):
        unidad = ""

        while len(unidad) == 0:
            self.refrescar_pantalla()
            unidad = Prompt.ask("[bold yellow]Ingresa la nueva unidad de medida\nDisponibles ->[/bold yellow] [bold green]kg / g / l / ml [/bold green]")

        self.refrescar_pantalla()
        confirmacion = Prompt.ask("[bold yellow]Confirmar nueva unidad de medida:[/bold yellow] "
                                      f"[italic white]{unidad}[/italic white]",
                                      choices=["S","N"])

        if confirmacion == "S":
            return unidad
        else:
            return None

    def mostrar_crear_cantidad_prompt(self):
        cantidad = ""

        while not cantidad or len(cantidad) == 0:
            self.refrescar_pantalla()
            cantidad = Prompt.ask("[bold yellow]Ingresa la nueva cantidad de merma[/bold yellow]")

        self.refrescar_pantalla()
        confirmacion = Prompt.ask(f"[bold yellow]Confirmar nueva cantidad [italic white]{cantidad}[/italic white][/bold yellow]", choices=["S", "N"])

        if confirmacion == "S":
            return cantidad
        else:
            self.mostrar_editar_cantidad_prompt()

    def mostrar_crear_cantidad_platillo_prompt(self):
        cantidad = ""

        while not cantidad or len(cantidad) == 0:
            self.refrescar_pantalla()
            cantidad = Prompt.ask("[bold yellow]Ingresa la nueva cantidad de platillos mermados[/bold yellow]")

        self.refrescar_pantalla()
        confirmacion = Prompt.ask(f"[bold yellow]Confirmar nueva cantidad: [italic white]{cantidad}[/italic white][/bold yellow]", choices=["S", "N"])

        if confirmacion == "S":
            return cantidad
        else:
            self.mostrar_crear_cantidad_platillo_prompt()

    def mostrar_editar_cantidad_prompt(self):
        cantidad = ""

        while not cantidad or len(cantidad) == 0:
            self.refrescar_pantalla()
            cantidad = Prompt.ask("[bold yellow]Ingresa la nueva cantidad de merma[/bold yellow]")

        self.refrescar_pantalla()
        confirmacion = Prompt.ask("[bold yellow]Confirmar nueva cantidad[/bold yellow]", choices=["S", "N"])

        if confirmacion == "S":
            return cantidad
        else:
            return None


    def mostrar_editar_tipo_merma_prompt(self, opciones):
        opciones.append("0")
        if "," not in opciones:
            opciones.append(",")
            opciones.append(".")

        tipo_num = ""

        while not tipo_num or len(tipo_num) == 0 or tipo_num == "," or tipo_num == ".":
            self.refrescar_pantalla()
            tipo_num = self.input_seleccion_tipo_merma.imprimir(
                "[bold yellow]Ingresa el nuevo tipo de merma de entre las opciones o cambia de página [',' '.'] o 0 para crear un tipo nuevo[/bold yellow]",
                choices=opciones,
                show_choices=False)

        self.refrescar_pantalla()
        confirmacion = Prompt.ask(f"[bold yellow]Confirmar tipo de merma[/bold yellow] "
                                          f"[italic white]{tipo_num}[/italic white]", choices=["S", "N"])
        if confirmacion == "S":
            return tipo_num
        else:
            self.mostrar_editar_tipo_merma_prompt(opciones)

    def mostrar_crear_tipo_insumo_prompt(self):
        tipo_nombre = ""

        while tipo_nombre is None or len(tipo_nombre) == 0:
            self.refrescar_pantalla()
            tipo_nombre = Prompt.ask("[bold yellow]Ingresa el nombre del nuevo tipo de merma[/bold yellow]")

        self.refrescar_pantalla()
        confirmacion = Prompt.ask(f"[bold yellow]Confirmar crear y asignar tipo: [italic white]{tipo_nombre}[/italic white][/bold yellow]", choices=["S", "N"])

        if confirmacion == "S":
            return tipo_nombre
        else:
            self.mostrar_crear_tipo_insumo_prompt()

    def mostrar_buscar_por_rango_fecha_inicial_prompt(self):
        fecha_inicial = ""

        while fecha_inicial is None or len(fecha_inicial) == 0:
            self.refrescar_pantalla()
            fecha_inicial = Prompt.ask("[bold yellow]Ingresa la fecha inicial a buscar en el siguiente formato: [[bold green]dd-mm-yyyy[/bold green]][/bold yellow]")

        return fecha_inicial

    def mostrar_buscar_por_rango_fecha_final_prompt(self):
        fecha_final = ""

        while fecha_final is None or len(fecha_final) == 0:
            self.refrescar_pantalla()
            fecha_final = Prompt.ask("[bold yellow]Ingresa la fecha final a buscar en el siguiente formato: [[bold green]dd-mm-yyyy[/bold green]][/bold yellow]")

        return fecha_final

    def mostrar_buscar_por_tipo_merma_prompt(self, opciones):
        opciones.append(",")
        opciones.append(".")
        tipo_num = ""

        while not tipo_num or len(tipo_num) == 0 or tipo_num == "," or tipo_num == ".":
            self.refrescar_pantalla()
            tipo_num = self.input_seleccion_tipo_merma.imprimir("Selecciona el tipo de merma a buscar", choices=opciones, show_choices=False)

        return tipo_num

    def mostrar_buscar_por_insumo_prompt(self, opciones):
        opciones.append(",")
        opciones.append(".")
        insumo_num = ""

        while not insumo_num or len(insumo_num) == 0 or insumo_num == "," or insumo_num == ".":
            self.refrescar_pantalla()
            insumo_num = self.input_seleccion_insumos.imprimir("Selecciona el tipo de insumo a buscar o cambia de página [',' '.']", choices=opciones, show_choices=False)

        return insumo_num

    def mostrar_prompt_registrar_insumo_merma(self, opciones):
        if "," not in opciones:
            opciones.append(",")
            opciones.append(".")
        num = ""

        while not num or len(num) == 0 or num == "," or num == ".":
            self.refrescar_pantalla()

            num = self.input_seleccion_insumos.imprimir("[bold yellow]Selecciona el insumo del que se produjo la merma o cambia de página [',' '.'][/bold yellow]",
                             choices=opciones,
                             show_choices=False)

        self.refrescar_pantalla()
        confirmacion = Prompt.ask(f"[bold yellow]Confirmar selección de insumo[/bold yellow]",
                                          choices=["S", "N"])

        if confirmacion == "S":
            return num
        else:
            self.mostrar_prompt_registrar_insumo_merma(opciones)

    def mostrar_prompt_registrar_platillo_merma(self, opciones):
        if "," not in opciones:
            opciones.append(",")
            opciones.append(".")
        num = ""

        while not num or len(num) == 0 or num == "," or num == ".":
            self.refrescar_pantalla()

            num = self.input_seleccion_platillo.imprimir("[bold yellow]Selecciona el platillo que se mermó o cambia de página [',' '.'][/bold yellow]",
                             choices=opciones,
                             show_choices=False)

        self.refrescar_pantalla()
        confirmacion = Prompt.ask(f"[bold yellow]Confirmar selección de platillo[/bold yellow]",
                                          choices=["S", "N"])

        if confirmacion == "S":
            return num
        else:
            self.mostrar_prompt_registrar_platillo_merma(opciones)

    def mostrar_prompt_fuente_merma(self):
        self.refrescar_pantalla()
        res = Prompt.ask("[bold yellow]Para registrar la merma de un platillo presiona 1, "
                         "para registrar la merma de un insumo individual presiona 2",
                         choices=["1", "2"], show_choices=False)

        return res

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
        time.sleep(2)

    def mostrar_mensaje_error_validacion(self, error:str):
        self.refrescar_pantalla()
        rich.print(f"[bold red]{error}[/bold red]")
        time.sleep(2)

    def refrescar_pantalla(self):
        try:
            subprocess.run('cls' if os.name == 'nt' else 'clear')
        except FileNotFoundError:
            print(chr(27) + "[2J")
        self.console.print(self.layout, justify="center")
