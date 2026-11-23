import datetime
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

from models.menu import Menu, DetalleMenu
from models.platillo import Platillo
from views.VistaBase import VistaBase
from views.clases_personalizadas.InputEmisor import InputEmisor


class VistaMenus(VistaBase):
    def __init__(self, console):
        super().__init__()
        self.console = console

        self.tabla_menus = Table(title="Menús")
        self.configurar_tabla_menus()

        self.tabla_detalles_menu = Table(title="Detalles")
        self.configurar_tabla_detalles_menu()

        self.input_menu_menus = InputEmisor()
        self.input_abrir_detalles = InputEmisor()
        self.input_menu_detalles = InputEmisor()
        self.input_menu_editar_menu = InputEmisor()
        self.input_menu_editar_platillo = InputEmisor()
        self.input_menu_filtros = InputEmisor()
        self.input_seleccion_platillos_disp = InputEmisor()
        self.input_platillos_conflicto = InputEmisor()

        self.layout["contenido"].split_column(Layout(name="banda_pagina"), Layout(name="main"), Layout(name="opciones"))

        self.mostrar_todos_menus(0, 0)
        self.crear_banda_opciones_principal()

    def resetear_vista(self):
        self.layout["main"].unsplit()

        self.tabla_menus = Table(title="Menús")
        self.configurar_tabla_menus()
        self.tabla_detalles_menu = Table(title="Detalles")
        self.configurar_tabla_detalles_menu()

        self.crear_banda_opciones_principal()

    def mostrar_todos_menus(self, pag_actual, total_pag):
        self.resetear_vista()

        self.layout["main"].update(Align.center(self.tabla_menus, vertical="top"))
        self.mostrar_conteo_paginas(pag_actual, total_pag)

    def configurar_tabla_menus(self):
        columnas = ["#", "Nombre", "Cantidad de platillos"]

        for columna in columnas:
            self.tabla_menus.add_column(columna)

    def crear_elemento_tabla_menus(self, menu: Menu, idx:int):
        self.tabla_menus.add_row(str(idx), menu.nombre, str(menu.cantidad_platillos))

    def mostrar_detalles_menu(self, menu: Menu | None, pag_detalles_menu, pag_actual, total_pag, datos_editados, mapa_platillos):
        self.resetear_vista()

        self.mostrar_conteo_paginas(pag_actual, total_pag)
        self.layout["main"].split_column(Layout(name="panel_menu"), Layout(name="tabla_detalles_menus"))
        self.layout["panel_menu"].size = 4

        nombre_menu = f"{menu.nombre}" if "nombre" in datos_editados else menu.nombre

        if menu.fecha_inicial and menu.fecha_final:
            vigencia_menu = f"{datetime.datetime.strftime(menu.fecha_inicial, "%d-%m-%Y")} a {datetime.date.strftime(menu.fecha_final, "%d-%m-%Y")}"
        else:
            vigencia_menu = "N/A"

        panel = Panel(renderable=f"{"[bold red]" if "nombre" in datos_editados else "[bold yellow]"}"
                                 f"{nombre_menu}\n"
                                 f"{"[/bold red]" if "nombre" in datos_editados else "[/bold yellow]"}"
                                 f"{"[bold red]" if "vigencia" in datos_editados else "[yellow]"}"
                                 f"[bold white]Vigencia:[/bold white] [italic]{vigencia_menu}[/italic]"
                                 f"{"[/bold red]" if "vigencia" in datos_editados else "[yellow]"}")

        panel.height = 4

        if menu and len(pag_detalles_menu):
            self.llenar_tabla_detalles_menu(pag_detalles_menu, mapa_platillos, datos_editados["platillos"])

        self.layout["panel_menu"].update(panel)
        self.layout["tabla_detalles_menus"].update(Align.center(self.tabla_detalles_menu, vertical="middle"))

    def configurar_tabla_detalles_menu(self):
        encabezados = ["#", "Platillo", "Categoría", "Precio"]

        self.tabla_detalles_menu.show_lines = True

        for col in encabezados:
            self.tabla_detalles_menu.add_column(col)

    def llenar_tabla_detalles_menu(self, lista_platillos:list[DetalleMenu], mapa_idx, platillos_editados=None):
        for detalle_platillo in lista_platillos:
            nombre_platillo = detalle_platillo.platillo.nombre

            idx_platillo = [item for item in mapa_idx if mapa_idx[item] == nombre_platillo][0]

            if platillos_editados:
                # checa si un platillo que fue agregado al dict de edición está en la lista original de ingredientes,
                # lo que quiere decir que será editado, si es así entonces muestra el valor editado en vez del original
                valor_editado = next(filter(lambda x: x.platillo.nombre == nombre_platillo, platillos_editados), None)

                if valor_editado is not None:
                    # sobreescribe platillo editado (duplicado)
                    platillos_editados.remove(valor_editado)

                    self.tabla_detalles_menu.add_row(f"[bold red]{str(idx_platillo)}[/bold red]",
                                                    f"[bold red]{nombre_platillo}[/bold red]",
                                                    f"[bold red]{valor_editado.platillo.categoria.nombre}[/bold red]",
                                                    f"[bold red]${str(valor_editado.precio)}[/bold red]")

                    continue
            # Agrega los platillos ya existentes
            self.tabla_detalles_menu.add_row(str(idx_platillo),
                                             nombre_platillo,
                                             detalle_platillo.platillo.categoria.nombre,
                                             f"${str(detalle_platillo.precio)}")

        if platillos_editados and len(platillos_editados) > 0:
            # agrega los platillos nuevos
            for platillo in platillos_editados:
                try:
                    idx_platillo = [item for item in mapa_idx if mapa_idx[item] == platillo.platillo.nombre][0]
                except IndexError:
                    # quiere decir que se borró el platillo del
                    continue

                self.tabla_detalles_menu.add_row(f"[bold red]{idx_platillo}[/bold red]",
                                                f"[bold red]{platillo.platillo.nombre}[/bold red]",
                                                f"[bold red]{platillo.platillo.categoria.nombre}[/bold red]",
                                                f"[bold red]${str(platillo.precio)}[/bold red]")

    def mostrar_platillos_disponibles(self, lista_platillos:list[Platillo], pag_actual, total_pag):
        self.mostrar_conteo_paginas(pag_actual, total_pag)

        consola_size = self.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 18

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

        self.layout["tabla_detalles_menus"].update(Align.center(tabla, vertical="middle"))

    def mostrar_platillos_conflicto(self, lista_platillos: list[Platillo], pag_actual, total_pag):
        self.mostrar_conteo_paginas(pag_actual, total_pag)

        consola_size = self.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 18

        if pag_actual == 1:
            idx_ui = 0
        else:
            idx_ui = (pag_actual - 1) * lineas_disp

        columnas = ["#", "Nombre"]

        tabla = Table(title="Platillos en conflicto de fechas")

        for col in columnas:
            tabla.add_column(col)

        for i in range(len(lista_platillos)):
            idx_ui += 1
            tabla.add_row(str(idx_ui), lista_platillos[i].nombre)

        self.layout["tabla_detalles_menus"].update(Align.center(tabla, vertical="middle"))

    def mostrar_crear_menu(self, menu: Menu | None):
        self.resetear_vista()

        self.layout["main"].split_column(Layout(name="panel_menu"), Layout(name="tabla_detalles_menus"))

        self.layout["panel_menu"].size = 4

        panel = Panel(renderable=f"[bold white]Crear menú\n"
                                 f"{menu.nombre if menu else "[bold magenta]Nombre del menú[/bold magenta]"}\n"
                                 f"{f"Vigencia: {menu.fecha_inicial} - {menu.fecha_final}" if menu else "[bold magenta]Vigencia: N/A[/bold magenta]"}[/bold white]")

        panel.height = 4

        if menu:
            if len(menu.detalles):
                self.llenar_tabla_detalles_menu(menu.detalles)

        self.layout["panel_menu"].update(panel)
        self.layout["tabla_detalles_menus"].update(Align.center(self.tabla_detalles_menu, vertical="middle"))

    def crear_banda_opciones_principal(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Ver detalles de menú",
                    "[2] Crear menú",
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
                    "[1] Volver a menús",
                    "[2] Editar menú",
                    "[3] Eliminar menú",
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
                    "[2] Por vigencia",
                    "[3] Mostrar todo",
                    "[4] Volver a menús"]

        opciones_columna.expand = True

        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def crear_banda_opciones_editar(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Editar nombre",
                    "[2] Editar vigencia",
                    "[3] Editar platillos",
                    "[4] Guardar",
                    "[5] Cancelar",
                    "[M] Volver al menú"]

        opciones_columna.expand = True
        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def crear_banda_opciones_editar_platillos(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Agregar platillo",
                    "[2] Modificar precio",
                    "[3] Remover platillo",
                    "[4] Volver"]

        opciones_columna.expand = True
        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def mostrar_menu_menus_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_menus.imprimir("Selecciona una opción o cambia de página [',' '.']",
                                       choices=["1", "2", "3", "m", ",", "."],
                                       show_choices=False)

        if self.input_menu_menus.user_input == "," or self.input_menu_menus.user_input == ".":
            self.mostrar_menu_menus_prompt()

    def mostrar_abrir_detalles_prompt(self, lista_menus: list[Menu]):
        self.refrescar_pantalla()
        self.input_abrir_detalles.imprimir("Ingresa el índice del menú a mostrar",
                                           choices=[str(i+1) for i in range(len(lista_menus))],
                                           show_choices=False)

    def mostrar_opciones_busqueda_av_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_filtros.imprimir("Selecciona una opción o cambia de página [',' '.']",
                                         choices=["1", "2", "3", "4", ",", "."],
                                         show_choices=False)

        if self.input_menu_filtros.user_input == "," or self.input_menu_filtros.user_input == ".":
            self.mostrar_opciones_busqueda_av_prompt()

    def mostrar_opciones_detalles_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_detalles.imprimir("Selecciona una opción o cambia de página [',' '.']",
                                          choices=["1", "2", "3", "m", ",", "."],
                                          show_choices=False)

        if self.input_menu_detalles == "." or self.input_menu_detalles == ".":
            self.mostrar_opciones_detalles_prompt()

    def mostrar_prompt_eliminar_menu_prompt(self):
        self.refrescar_pantalla()
        confirmacion = Prompt.ask("[bold red]¡Atención! estás a punto de eliminar este menú, confirma para continuar[/bold red]",
                                  choices=["S","N"])

        if confirmacion == "S":
            return True

        return False

    def mostrar_opciones_editar_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_editar_menu.imprimir("Selecciona una opción o cambia de página [',' '.']",
                                               choices=["1", "2", "3", "4", "5", "m", ",", "."],
                                               show_choices=False)

        if self.input_menu_editar_menu == "," or self.input_menu_editar_menu == ".":
            self.mostrar_opciones_editar_prompt()

    def mostrar_editar_nombre_prompt(self):
        self.refrescar_pantalla()
        info = Prompt.ask("[bold yellow]Ingresa el nuevo nombre del menú[/bold yellow]")

        if len(info) > 0:
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar nuevo nombre[/bold yellow] "
                                      f"[italic white]{info}[/italic white]", choices=["S", "N"])
            if confirmacion == "S":
                return info
            else:
                return None
        else:
            self.mostrar_editar_nombre_prompt()

    def mostrar_editar_vigencia_prompt(self):
        self.refrescar_pantalla()
        fecha_inicial = Prompt.ask("[bold yellow]Ingresa la fecha inicial en el siguiente formato o 0 para salir[/bold yellow]: [[bold green]dd-mm-yyyy[/bold green]]")

        if fecha_inicial == "0":
            return None, None

        if len(fecha_inicial):
            fecha_final = Prompt.ask("[bold yellow]Ingresa la fecha final en el siguiente formato o 0 para salir[/bold yellow]: [[bold green]dd-mm-yyyy[/bold green]]")

            if fecha_final == "0":
                return None, None

            if len(fecha_final):
                return fecha_inicial, fecha_final

        return None, None

    def mostrar_editar_platillos_menu_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_editar_platillo.imprimir("Selecciona una opción o cambia de página [',' '.']",
                                                 choices=["1","2","3","4", ",", "."], show_choices=False)

        if self.input_menu_editar_platillo == "," or self.input_menu_editar_platillo == ".":
            self.refrescar_pantalla()
            self.mostrar_editar_platillos_menu_prompt()

    def mostrar_agregar_platillo_prompt(self, opciones):
        self.refrescar_pantalla()
        if len(opciones) == 0:
            rich.print("[bold green]No hay platillos disponibles para agregar a este menú, volviendo al menú editar...[/bold green]")
            time.sleep(5)
            return None, None

        num_receta = ""
        opciones.append(",")
        opciones.append(".")

        while len(num_receta) == 0 or num_receta == "," or num_receta == ".":
            self.refrescar_pantalla()
            num_receta = self.input_seleccion_platillos_disp.imprimir("[bold yellow]Selecciona uno de los platillos disponibles[/bold yellow]",
                                choices=opciones,
                                show_choices=False)


        confirmacion = Prompt.ask("[bold yellow]Confirmar agregar platillo[/bold yellow]",
                                      choices=["S","N"])

        if confirmacion == "S":
            return num_receta
        else:
            return None

    def mostrar_ingresar_precio_prompt(self):
        self.refrescar_pantalla()
        precio = ""

        while len(precio) == 0:
            precio = Prompt.ask("[bold yellow]Ingresa el precio del platillo para este menú[bold yellow]")

        return precio

    def mostrar_seleccionar_editar_platillo_prompt(self, opciones):
        self.refrescar_pantalla()
        if len(opciones) == 0:
            rich.print("[bold green]El menú actual no tiene platillos que editar, volviendo al menú editar...[/bold green]")
            time.sleep(5)
            return None

        num_plat = Prompt.ask("[bold yellow]Selecciona el platillo a modificar[/bold yellow]",
                              choices=opciones,
                              show_choices=False)

        return num_plat

    def mostrar_remover_platillo_prompt(self, opciones):
        self.refrescar_pantalla()
        if len(opciones) == 0:
            rich.print("[bold green]El menú actual no tiene platillos que borrar, volviendo al menú editar...[/bold green]")
            time.sleep(5)
            return None

        num_platillo = Prompt.ask("[bold yellow]Ingresa el número del menú a remover[/bold yellow]", choices=opciones, show_choices=False)
        confirmacion = Prompt.ask(f"[bold yellow]Confirmar borrar platillo #{num_platillo}", choices=["S", "N"])

        if confirmacion == "S":
            return num_platillo

        return None

    def mostrar_buscar_por_nombre_prompt(self):
        nombre = ""

        while len(nombre) == 0:
            self.refrescar_pantalla()
            nombre = Prompt.ask("[bold yellow]Ingresa el nombre a buscar[/bold yellow]")

        return nombre

    def mostrar_buscar_por_vigencia_prompt(self):
        fecha_inicial = ""
        fecha_final = ""

        while len(fecha_inicial) == 0:
            self.refrescar_pantalla()
            fecha_inicial = Prompt.ask("[bold yellow]Ingresa la fecha inicial de búsqueda en el siguiente formato: [[bold green]dd-mm-yyyy[/bold green]][/bold yellow]")

        while len(fecha_final) == 0:
            self.refrescar_pantalla()
            fecha_final = Prompt.ask("[bold yellow]Ingresa la fecha final de búsqueda en el sigueinte formato: [[bold green]dd-mm-yyyy[/bold green]][/bold yellow]")

        return fecha_inicial, fecha_final

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

    def mostrar_mensaje_no_resultados_busqueda_av(self):
        rich.print("[bold blue]Aviso: No se encontraron resultados para la búsqueda realizada, volviendo a al menú de búsqueda avanzada...[/bold blue]")
        time.sleep(3)

    def mostrar_mensaje_crear_menu_duplicado(self):
        rich.print("[bold red]Error: El menú que intenta guardar ya existe. Cambia el nombre actual o edita la receta existente.[/bold red]")
        time.sleep(3)

    def mostrar_mensaje_editar_nombre_duplicado(self):
        rich.print("[bold red]Error: El nombre ingresado ya existe. Cambia el nombre actual o edita la receta existente.[/bold red]")
        time.sleep(3)

    def mostrar_mensaje_error_validacion(self, error:str):
        rich.print(f"[bold red]{error}[/bold red]")
        time.sleep(3)

    def mostrar_mensaje_platillos_conflicto(self, fecha_inicial, fecha_final):
        self.refrescar_pantalla()
        eleccion = self.input_platillos_conflicto.imprimir(f"[bold yellow]Atención: Cambiar la vigencia del menú a {fecha_inicial} - {fecha_final} resultará en la remoción de los siguientes platillos."
                                                           f" ¿Deseas continuar?[/bold yellow][italic magenta][S, N][/italic magenta]", choices=["S", "N", ",", "."])
        if eleccion is "," or eleccion is ".":
            self.mostrar_mensaje_platillos_conflicto(fecha_inicial, fecha_final)

        return eleccion

    def refrescar_pantalla(self):
        try:
            subprocess.run('cls' if os.name == 'nt' else 'clear')
        except FileNotFoundError:
            print(chr(27) + "[2J")
        self.console.print(self.layout, justify="center")
