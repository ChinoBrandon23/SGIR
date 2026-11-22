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

from models.categoria import Categoria
from models.platillo import Platillo
from models.receta import Receta
from views.VistaBase import VistaBase
from views.clases_personalizadas.InputEmisor import InputEmisor


class VistaPlatillos(VistaBase):
    def __init__(self, console):
        super().__init__()
        self.console = console

        self.tabla_platillos = Table(title="Platillos")
        self.configurar_tabla_platillos()

        self.tabla_detalles = Table(title="Detalles")
        self.tabla_detalles.show_header = False
        self.tabla_detalles.show_lines = True

        self.input_menu_platillos = InputEmisor()
        self.input_abrir_detalles = InputEmisor()
        self.input_menu_detalles = InputEmisor()
        self.input_menu_editar_platillo = InputEmisor()
        self.input_menu_filtros = InputEmisor()
        self.input_seleccion_categoria = InputEmisor()
        self.input_seleccion_receta = InputEmisor()

        self.layout["contenido"].split_column(Layout(name="banda_pagina"), Layout(name="main"), Layout(name="opciones"))

        self.mostrar_todos_platillos(0, 0)
        self.crear_banda_opciones_principal()

    def resetear_vista(self):
        self.layout["main"].unsplit()

        self.tabla_platillos = Table(title="Platillos")
        self.configurar_tabla_platillos()
        self.tabla_detalles = Table(title="Detalles")
        self.tabla_detalles.show_header = False
        self.tabla_detalles.show_lines = True

        self.crear_banda_opciones_principal()

    def mostrar_todos_platillos(self, pag_actual, total_pag):
        self.resetear_vista()

        self.layout["main"].update(Align.center(self.tabla_platillos, vertical="top"))
        self.mostrar_conteo_paginas(pag_actual, total_pag)

    def configurar_tabla_platillos(self):
        columnas = ["#", "Nombre", "Categoria"]

        for columna in columnas:
            self.tabla_platillos.add_column(columna)

    def crear_elemento_tabla_platillos(self, platillo: Platillo, idx:int):
        self.tabla_platillos.add_row(str(idx), platillo.nombre, platillo.categoria.nombre)

    def mostrar_detalles_platillo(self, platillo: Platillo | None, datos_editados):
        self.resetear_vista()

        self.layout["main"].split_column(Layout(name="panel_platillo"), Layout(name="tabla_detalles"))

        self.layout["panel_platillo"].size = 3

        nombre_platillo = datos_editados["nombre"] if "nombre" in datos_editados else platillo.nombre

        panel = Panel(renderable=f"{"[bold red]" if "nombre" in datos_editados else "[bold yellow]"}"
                                 f"{nombre_platillo}"
                                 f"{"[/bold red]" if "nombre" in datos_editados else "[/bold yellow]"}")

        panel.height = 3

        if platillo.categoria is not None:
            if "categoria" in datos_editados:
                self.tabla_detalles.add_row("Categoría", f"[bold red]{platillo.categoria.nombre}[/bold red]")
            else:
                self.tabla_detalles.add_row("Categoría", platillo.categoria.nombre)
        else:
            self.tabla_detalles.add_row("Categoría", " " * 10)

        if platillo.receta is not None:
            if "receta" in datos_editados:
                self.tabla_detalles.add_row("Receta base", f"[bold red]{platillo.receta.nombre}[/bold red]")
            else:
                self.tabla_detalles.add_row("Receta base", platillo.receta.nombre)
        else:
            self.tabla_detalles.add_row("Receta base", " " * 10)

        self.layout["panel_platillo"].update(panel)
        self.layout["tabla_detalles"].update(Align.center(self.tabla_detalles, vertical="middle"))

    def mostrar_categorias_disponibles(self, lista_categorias:list[Categoria], pag_actual, total_pag):
        columnas = ["#", "Categoria"]
        tabla = Table(title="Categorías disponibles")

        self.mostrar_conteo_paginas(pag_actual, total_pag)

        consola_size = self.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 9

        if pag_actual == 1:
            idx_ui = 0
        else:
            idx_ui = (pag_actual - 1) * lineas_disp

        for col in columnas:
            tabla.add_column(col)

        for i in range(len(lista_categorias)):
            idx_ui += 1
            tabla.add_row(str(idx_ui), lista_categorias[i].nombre)

        try:
            self.layout["tabla_detalles"].update(Align.center(tabla, vertical="middle"))
        except KeyError:
            self.layout["main"].update(Align.center(tabla, vertical="middle"))

    def mostrar_recetas_disponibles(self, lista_recetas:list[Receta], pag_actual, total_pag):
        columnas = ["#", "Nombre"]
        tabla = Table(title="Recetas disponibles")

        self.mostrar_conteo_paginas(pag_actual, total_pag)

        consola_size = self.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 9

        if pag_actual == 1:
            idx_ui = 0
        else:
            idx_ui = (pag_actual - 1) * lineas_disp

        for col in columnas:
            tabla.add_column(col)

        for i in range(len(lista_recetas)):
            idx_ui += 1
            tabla.add_row(str(idx_ui), lista_recetas[i].nombre)

        self.layout["tabla_detalles"].update(Align.center(tabla, vertical="middle"))

    def mostrar_crear_platillo(self, platillo: Platillo | None):
        self.resetear_vista()

        self.layout["main"].split_column(Layout(name="panel_platillo"), Layout(name="tabla_detalles"))

        self.layout["panel_platillo"].size = 4

        panel = Panel(renderable=f"[bold white]Crear platillo\n"
                                 f"{platillo.nombre if platillo else "[bold magenta]Nombre del platillo[/bold magenta]"}[/bold white]")

        panel.height = 4

        if platillo:
            if platillo.categoria:
                self.tabla_detalles.add_row("Categoría", platillo.categoria.nombre)
            else:
                self.tabla_detalles.add_row("Categoría", " " * 10)
            if platillo.receta:
                self.tabla_detalles.add_row("Receta base", platillo.receta.nombre)
            else:
                self.tabla_detalles.add_row("Receta base", " " * 10)

        self.layout["panel_platillo"].update(panel)
        self.layout["tabla_detalles"].update(Align.center(self.tabla_detalles, vertical="middle"))

    def crear_banda_opciones_principal(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Ver detalles de platillo",
                    "[2] Crear platillo",
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
                    "[1] Volver a platillos",
                    "[2] Editar platillo",
                    "[3] Eliminar platillo",
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
                    "[2] Por categoría",
                    "[3] Mostrar todo",
                    "[4] Volver a platillos"]

        opciones_columna.expand = True

        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def crear_banda_opciones_editar(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Editar nombre",
                    "[2] Editar categoría",
                    "[3] Editar receta base",
                    "[4] Guardar",
                    "[5] Cancelar",
                    "[M] Volver al menú"]

        opciones_columna.expand = True
        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def mostrar_menu_platillos_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_platillos.imprimir("Selecciona una opción o cambia de página [',' '.']",
                                           choices=["1", "2", "3", "m", ".", ","],
                                           show_choices=False)

        if self.input_menu_platillos.user_input is None:
            self.mostrar_menu_platillos_prompt()

    def mostrar_abrir_detalles_prompt(self, lista_platillos: list[Platillo]):
        self.refrescar_pantalla()
        self.input_abrir_detalles.imprimir("Ingresa el índice del platillo a mostrar",
                                           choices=[str(i+1) for i in range(len(lista_platillos))],
                                           show_choices=False)

        if self.input_abrir_detalles.user_input is None:
            self.mostrar_abrir_detalles_prompt(lista_platillos)

    def mostrar_opciones_detalles_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_detalles.imprimir("Selecciona una opción",
                                          choices=["1", "2", "3", "m"],
                                          show_choices=False)

        if self.input_menu_detalles.user_input is None:
            self.mostrar_opciones_detalles_prompt()

    def mostrar_opciones_busqueda_av_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_filtros.imprimir("Selecciona una opción o cambia de página [',' '.']",
                                          choices=["1", "2", "3", "4", ",", "."],
                                          show_choices=False)

        if self.input_menu_filtros.user_input == "," or self.input_menu_filtros.user_input == ".":
            self.mostrar_opciones_busqueda_av_prompt()

    def mostrar_prompt_eliminar_platillo_prompt(self):
        self.refrescar_pantalla()
        confirmacion = Prompt.ask("[bold red]¡Atención! estás a punto de eliminar este platillo, confirma para continuar[/bold red]",
                                  choices=["S","N"])

        if confirmacion == "S":
            return True

        return False

    def mostrar_opciones_editar_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_editar_platillo.imprimir("Selecciona una opción",
                                               choices=["1", "2", "3", "4", "5", "m"],
                                               show_choices=False)

        if self.input_menu_editar_platillo.user_input is None:
            self.mostrar_opciones_editar_prompt()

    def mostrar_editar_nombre_prompt(self):
        self.refrescar_pantalla()
        info = Prompt.ask("[bold yellow]Ingresa el nuevo nombre del platillo[/bold yellow]")

        if len(info) > 0:
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar nuevo nombre[/bold yellow] "
                                      f"[italic white]{info}[/italic white]", choices=["S", "N"])
            if confirmacion == "S":
                return info
            else:
                return None
        else:
            self.refrescar_pantalla()
            self.mostrar_editar_nombre_prompt()

    def mostrar_editar_categoria_prompt(self, opciones):
        opciones.append("0")
        opciones.append(",")
        opciones.append(".")

        info = ""

        while len(info) == 0 or info == "," or info == ".":
            self.refrescar_pantalla()
            info = self.input_seleccion_categoria.imprimir(
                "[bold yellow]Ingresa la nueva categoría de entre las opciones, 0 para crear una categoría nueva o cambia de página [',' '.'][/bold yellow]",
                choices=opciones,
                show_choices=False)

        if info == "0":
            return info
        elif len(info):
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar categoría[/bold yellow] "
                                      f"[italic white]{info}[/italic white]", choices=["S", "N"])
            if confirmacion == "S":
                return info
            else:
                return None
        else:
            self.mostrar_editar_categoria_prompt()

    def mostrar_editar_receta_base_prompt(self, opciones):
        opciones.append(",")
        opciones.append(".")

        num_receta = ""

        while len(num_receta) == 0 or num_receta == "," or num_receta == ".":
            self.refrescar_pantalla()
            num_receta = self.input_seleccion_receta.imprimir(
                "[bold yellow]Ingresa la nueva receta base de entre las opciones o cambia de página [',' '.'][/bold yellow]",
                choices=opciones,
                show_choices=False)

        confirmacion = Prompt.ask("[bold yellow]Confirmar nueva receta base[/bold yellow]",
                                  choices=["S","N"])

        if confirmacion == "S":
            return num_receta
        else:
            return None

    def mostrar_crear_categoria_prompt(self):
        self.refrescar_pantalla()
        cat_nombre = Prompt.ask("[bold yellow]Ingresa el nombre de la nueva categoría[/bold yellow]")

        if cat_nombre is not None:
            confirmacion = Prompt.ask("[bold yellow]Confirmar crear y asignar categoría[/bold yellow]", choices=["S", "N"])

            if confirmacion == "S":
                return cat_nombre
            else:
                return None

    def mostrar_prompt_crear_platillo(self):
        self.refrescar_pantalla()
        nombre = Prompt.ask("Para comenzar, ingresa el nombre del nuevo platillo o 0 para cancelar")

        if len(nombre) == 0:
            self.refrescar_pantalla()
            self.mostrar_prompt_crear_platillo()

        if nombre is not "0":
            return nombre

        return None

    def mostrar_buscar_por_nombre_prompt(self):
        nombre = ""

        while len(nombre) == 0:
            self.refrescar_pantalla()
            nombre = Prompt.ask("[bold yellow]Ingresa el nombre a buscar[/bold yellow]")

        return nombre

    def mostrar_buscar_por_categoria_prompt(self, opciones):
        opciones.append(",")
        opciones.append(".")
        cat_num = ""

        while len(cat_num) == 0 or cat_num == "," or cat_num == ".":
            self.refrescar_pantalla()
            cat_num = self.input_seleccion_categoria.imprimir("[bold yellow]Ingresa índice de la categoría a buscar o cambia de página [',' '.'] [/bold yellow]", choices=opciones, show_choices=False)

        return cat_num

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

    def mostrar_mensaje_editar_nombre_duplicado(self):
        rich.print("[bold red]Error: El nombre ingresado ya existe. Cambia el nombre actual o edita el platillo existente.[/bold red]")
        time.sleep(2)

    def mostrar_mensaje_error_validacion(self, error:str):
        rich.print(f"[bold red]{error}[/bold red]")
        time.sleep(3)

    def refrescar_pantalla(self):
        try:
            subprocess.run('cls' if os.name == 'nt' else 'clear')
        except FileNotFoundError:
            print(chr(27) + "[2J")
        self.console.print(self.layout, justify="center")
