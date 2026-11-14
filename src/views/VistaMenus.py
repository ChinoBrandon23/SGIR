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

        self.layout["contenido"].split_column(Layout(name="main"), Layout(name="opciones"))

        self.mostrar_todos_menus()
        self.crear_banda_opciones_principal()

    def resetear_vista(self):
        self.layout["main"].unsplit()

        self.tabla_menus = Table(title="Menús")
        self.configurar_tabla_menus()
        self.tabla_detalles_menu = Table(title="Detalles")
        self.configurar_tabla_detalles_menu()

        self.crear_banda_opciones_principal()

    def mostrar_todos_menus(self):
        self.resetear_vista()

        self.layout["main"].update(Align.center(self.tabla_menus, vertical="top"))

    def configurar_tabla_menus(self):
        columnas = ["#", "Nombre", "Cantidad de platillos"]

        for columna in columnas:
            self.tabla_menus.add_column(columna)

    def crear_elemento_tabla_menus(self, menu: Menu):
        self.tabla_menus.add_row(str(menu.num), menu.nombre, str(menu.cantidad_platillos))

    def mostrar_detalles_menu(self, menu: Menu | None, datos_editados, mapa_platillos):
        self.resetear_vista()

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

        if menu and len(menu.detalles):
            self.llenar_tabla_detalles_menu(menu.detalles, mapa_platillos, datos_editados["platillos"])

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
                idx_platillo = [item for item in mapa_idx if mapa_idx[item] == platillo.platillo.nombre][0]

                self.tabla_detalles_menu.add_row(f"[bold red]{idx_platillo}[/bold red]",
                                                f"[bold red]{platillo.platillo.nombre}[/bold red]",
                                                f"[bold red]{platillo.platillo.categoria.nombre}[/bold red]",
                                                f"[bold red]${str(platillo.precio)}[/bold red]")

    def mostrar_platillos_disponibles(self, lista_platillos:list[Platillo]):
        columnas = ["#", "Nombre"]

        tabla = Table(title="Platillos disponibles")

        for col in columnas:
            tabla.add_column(col)

        for i in range(len(lista_platillos)):
            tabla.add_row(str(i+1), lista_platillos[i].nombre)

        self.layout["tabla_detalles_menus"].update(Align.center(tabla, vertical="middle"))

    def mostrar_crear_menu(self, menu: Menu | None, platillo_idx):
        self.resetear_vista()

        self.layout["main"].split_column(Layout(name="panel_menu"), Layout(name="tabla_detalles_menus"))

        self.layout["panel_menu"].size = 4

        panel = Panel(renderable=f"[bold white]Crear menú\n"
                                 f"{menu.nombre if menu else "[bold magenta]Nombre del menú[/bold magenta]"}[/bold white]")

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
                    "[1] Volver a menús",
                    "[2] Editar menú",
                    "[3] Eliminar menú",
                    "[M] Volver al menú"]

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
        self.input_menu_menus.imprimir("Selecciona una opción",
                                       choices=["1", "2", "m"],
                                       show_choices=False)

        if self.input_menu_menus.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_menu_menus_prompt()

    def mostrar_abrir_detalles_prompt(self, lista_menus: list[Menu]):
        self.input_abrir_detalles.imprimir("Ingresa el índice del menú a mostrar",
                                           choices=[str(menu.num) for menu in lista_menus],
                                           show_choices=False)

        if self.input_abrir_detalles.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_abrir_detalles_prompt(lista_menus)

    def mostrar_opciones_detalles_prompt(self):
        self.input_menu_detalles.imprimir("Selecciona una opción",
                                          choices=["1", "2", "3", "m"],
                                          show_choices=False)

        if self.input_menu_detalles.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_opciones_detalles_prompt()

    def mostrar_prompt_eliminar_menu_prompt(self):
        confirmacion = Prompt.ask("[bold red]¡Atención! estás a punto de eliminar este menú, confirma para continuar[/bold red]",
                                  choices=["S","N"])

        if confirmacion == "S":
            return True

        return False

    def mostrar_opciones_editar_prompt(self):
        self.input_menu_editar_menu.imprimir("Selecciona una opción",
                                               choices=["1", "2", "3", "4", "5", "m"],
                                               show_choices=False)

        if self.input_menu_editar_menu.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_opciones_editar_prompt()

    def mostrar_editar_nombre_prompt(self):
        info = Prompt.ask("[bold yellow]Ingresa el nuevo nombre del menú[/bold yellow]")

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

    def mostrar_editar_vigencia_prompt(self):
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
        self.input_menu_editar_platillo.imprimir("Selecciona una opción",
                                                 choices=["1","2","3","4"], show_choices=False)

    def mostrar_agregar_platillo_prompt(self, opciones):
        if len(opciones) == 0:
            rich.print("[bold green]No hay platillos disponibles para agregar a este menú, volviendo al menú editar...[/bold green]")
            time.sleep(5)
            return None, None

        num_receta = Prompt.ask("[bold yellow]Selecciona uno de los platillos disponibles[/bold yellow]",
                            choices=opciones,
                            show_choices=False)

        precio = Prompt.ask("[bold yellow]Ingresa el precio del platillo para este menú[bold yellow]", )

        if len(precio):
            confirmacion = Prompt.ask("[bold yellow]Confirmar agregar platillo[/bold yellow]",
                                      choices=["S","N"])

            if confirmacion == "S":
                return num_receta, precio
            else:
                return None, None

        return None, None

    def mostrar_editar_precio_platillo_prompt(self, opciones):
        if len(opciones) == 0:
            rich.print("[bold green]El menú actual no tiene platillos que editar, volviendo al menú editar...[/bold green]")
            time.sleep(5)

            return None, None

        num_plat = Prompt.ask("[bold yellow]Selecciona el platillo a modificar[/bold yellow]",
                              choices=opciones,
                              show_choices=False)

        precio = Prompt.ask(f"[bold yellow]Ingresa el nuevo precio del platillo #{num_plat} para este menú")

        if len(precio):
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar asignar precio ${precio} al platillo #{num_plat}",
                                      choices=["S","N"])

            if confirmacion == "S":
                return num_plat, precio
            else:
                return None, None

        return None, None


    def mostrar_remover_platillo_prompt(self, opciones):
        if len(opciones) == 0:
            rich.print("[bold green]El menú actual no tiene platillos que borrar, volviendo al menú editar...[/bold green]")
            time.sleep(5)
            return None

        num_platillo = Prompt.ask("[bold yellow]Ingresa el número del menú a remover[/bold yellow]", choices=opciones, show_choices=False)
        confirmacion = Prompt.ask(f"[bold yellow]Confirmar borrar platillo #{num_platillo}", choices=["S", "N"])

        if confirmacion == "S":
            return num_platillo

        return None

    def mostrar_prompt_crear_menu(self):
        nombre = Prompt.ask("Para comenzar, ingresa el nombre del nuevo menú o 0 para cancelar")

        if len(nombre) == 0:
            self.refrescar_pantalla()
            self.mostrar_prompt_crear_menu()

        if nombre is not "0":
            return nombre

        return None

    def paginar(self, items: list, num_pag: int):
        lineas_disp = ((self.console.size[1] - 6) // 2) - 7

        idx_inicio = (num_pag - 1) * lineas_disp
        idx_final = idx_inicio + lineas_disp

        if idx_final < len(items) - 1:
            prox_pag = True
        else:
            prox_pag = False

        return items[idx_inicio:idx_final], prox_pag

    def refrescar_pantalla(self):
        try:
            subprocess.run('cls' if os.name == 'nt' else 'clear')
        except FileNotFoundError:
            print(chr(27) + "[2J")
        self.console.print(self.layout, justify="center")
