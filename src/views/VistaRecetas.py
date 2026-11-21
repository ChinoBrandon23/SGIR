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

from models.ingrediente import Ingrediente
from models.insumo import Insumo
from models.receta import Receta, IngredientesReceta
from views.VistaBase import VistaBase
from views.clases_personalizadas.InputEmisor import InputEmisor

class VistaRecetas(VistaBase):
    def __init__(self, console):
        super().__init__()
        self.console = console

        self.tabla_recetas = Table(title="Recetas")
        self.configurar_tabla_recetas()

        self.tabla_ingredientes = Table()
        self.configurar_tabla_ingredientes()

        self.tabla_instrucciones = Table()
        self.configurar_tabla_instrucciones()

        self.input_menu_recetas = InputEmisor()
        self.input_abrir_detalles = InputEmisor()
        self.input_menu_detalles = InputEmisor()
        self.input_menu_editar_receta = InputEmisor()
        self.input_menu_editar_ing = InputEmisor()
        self.input_menu_editar_inst = InputEmisor()
        self.input_menu_filtros = InputEmisor()
        self.input_seleccionar_insumo = InputEmisor()
        self.input_seleccionar_receta = InputEmisor()

        self.layout["contenido"].split_column(Layout(name="banda_pagina"), Layout(name="main"), Layout(name="opciones"))

        self.mostrar_todas_recetas(0, 0)
        self.crear_banda_opciones_principal()

    def resetear_vista(self):
        self.layout["main"].unsplit()

        self.tabla_recetas = Table(title="Recetas")
        self.configurar_tabla_recetas()
        self.tabla_ingredientes = Table()
        self.configurar_tabla_ingredientes()
        self.tabla_instrucciones = Table()
        self.configurar_tabla_instrucciones()

        self.crear_banda_opciones_principal()

    def mostrar_todas_recetas(self, pag_actual, total_pag):
        self.resetear_vista()

        self.layout["main"].update(Align.center(self.tabla_recetas, vertical="top"))
        self.mostrar_conteo_paginas(pag_actual, total_pag)

    def configurar_tabla_recetas(self):
        columnas = ["#", "Nombre"]

        for columna in columnas:
            self.tabla_recetas.add_column(columna)

    def crear_elemento_tabla_recetas(self, receta:Receta, idx):
        self.tabla_recetas.add_row(str(idx), receta.nombre)

    def mostrar_detalles_receta(self, receta:Receta,  pagina_detalles:dict, pag_actual, total_pag, datos_editados, mapa_idx_ing):
        self.mostrar_conteo_paginas(pag_actual, total_pag)

        if self.tabla_ingredientes.row_count > 0 or self.tabla_instrucciones.row_count > 0:
            self.resetear_vista()

        self.layout["main"].split_column(Layout(name="panel_receta"), Layout(name="tablas"))
        self.layout["tablas"].split_row(Layout(name="tabla_ing"),
                                         Layout(name="tabla_ins"))

        self.layout["panel_receta"].size = 3

        panel = Panel(renderable=f"{"[bold red]" if "nombre" in datos_editados else "[bold yellow]"}"
                                 f"{receta.nombre}"
                                 f"{"[/bold red]" if "nombre" in datos_editados else "[/bold yellow]"}: "
                                 f"{"[bold red]" if "porciones" in datos_editados else "[italic yellow]"}"
                                 f"{str(receta.num_porciones)}"
                                 f"{"[/bold red]" if "porciones" in datos_editados else "[/italic yellow]"}"
                                 f"[italic yellow] porciones [/italic yellow]")

        panel.height = 3

        if receta and len(pagina_detalles["lista_ingredientes"]):
            self.llenar_tabla_ingredientes(pagina_detalles["lista_ingredientes"], mapa_idx_ing, datos_editados["ingredientes"])

        if receta and len(pagina_detalles["instrucciones"]):
            self.llenar_tabla_instrucciones(pagina_detalles["instrucciones"])

        self.layout["panel_receta"].update(panel)
        self.layout["tabla_ing"].update(self.tabla_ingredientes)
        self.layout["tabla_ins"].update(self.tabla_instrucciones)

    def configurar_tabla_ingredientes(self):
        columnas = ["#", "Nombre", "Cantidad", "Unidad de medida"]
        self.tabla_ingredientes.title = "Ingredientes"
        self.tabla_ingredientes.expand = True

        for col in columnas:
            self.tabla_ingredientes.add_column(col)

    def llenar_tabla_ingredientes(self, lista_ingredientes:list[IngredientesReceta], mapa_idx_ing:list, ing_editados=None):
        for ingrediente in lista_ingredientes:
            nombre_ing = ingrediente.ingrediente.nombre

            idx_ing = [item for item in mapa_idx_ing if mapa_idx_ing[item] == nombre_ing][0]

            if nombre_ing in ing_editados:
                # checa si un ing fue editado de acuerdo a la lista de ing editados, para marcarlo en rojo si es así
                self.tabla_ingredientes.add_row(f"[bold red]{str(idx_ing)}[/bold red]",
                                                f"[bold red]{nombre_ing}[/bold red]",
                                                f"[bold red]{str(ingrediente.cantidad)}[/bold red]",
                                                f"[bold red]{ingrediente.unidad_medida}[/bold red]")
            else:
                # Los muestra en color blanco si no han sido editados
                self.tabla_ingredientes.add_row(str(idx_ing),
                                                nombre_ing,
                                                str(ingrediente.cantidad),
                                                ingrediente.unidad_medida)

    def configurar_tabla_instrucciones(self):
        columnas = ["#", "Instrucción"]
        self.tabla_instrucciones.title = "Instrucciones de preparación"
        self.tabla_instrucciones.expand = True

        for col in columnas:
            self.tabla_instrucciones.add_column(col)

    def llenar_tabla_instrucciones(self, lista_instrucciones:dict[str, str]):
        for num, instruccion in lista_instrucciones.items():
            self.tabla_instrucciones.add_row(str(num), instruccion)

    def mostrar_crear_receta(self, receta:Receta|None, mapa_idx_ing):
        self.resetear_vista()

        self.layout["main"].split_column(Layout(name="panel_receta"), Layout(name="tablas"))
        self.layout["tablas"].split_row(Layout(name="tabla_ing"),
                                        Layout(name="tabla_ins"))

        self.layout["panel_receta"].size = 4

        panel = Panel(renderable=f"[bold white]Crear receta\n"
                                 f"{receta.nombre if receta else "[bold magenta]Nombre de la receta[/bold magenta]"}[/bold white]. "
                                 f"Porciones: {receta.num_porciones if receta else "[bold magenta]Número de porciones[/bold magenta]"}")

        panel.height = 4

        if receta and len(receta.lista_ingredientes) > 1:
            self.llenar_tabla_ingredientes(receta.lista_ingredientes, mapa_idx_ing)

        if receta:
            self.llenar_tabla_instrucciones(receta.instrucciones)

        self.layout["panel_receta"].update(panel)
        self.layout["opciones"].update(Columns())
        self.layout["tabla_ing"].update(self.tabla_ingredientes)
        self.layout["tabla_ins"].update(self.tabla_instrucciones)


    def crear_banda_opciones_principal(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Ver detalles de receta",
                    "[2] Crear receta",
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
                    "[1] Volver a recetas",
                    "[2] Editar receta",
                    "[3] Eliminar receta",
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
                    "[2] Por número de porciones",
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
                    "[2] Editar porciones",
                    "[3] Editar ingredientes",
                    "[4] Editar instrucciones",
                    "[5] Guardar",
                    "[6] Cancelar",
                    "[M] Volver al menú"]

        opciones_columna.expand = True
        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def crear_banda_opciones_editar_ingrediente(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Agregar ingrediente",
                    "[2] Modificar ingrediente",
                    "[3] Eliminar ingrediente",
                    "[4] Volver"]

        opciones_columna.expand = True
        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def crear_banda_opciones_editar_instrucciones(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Agregar instrucción",
                    "[2] Modificar instrucción",
                    "[3] Eliminar instrucción",
                    "[4] Volver"]

        opciones_columna.expand = True
        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def mostrar_menu_recetas_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_recetas.imprimir("Selecciona una opción o cambia de página [',' '.']",
                                         choices=["1", "2", "3", "m", ",", "."],
                                         show_choices=False)

        if self.input_menu_recetas.user_input is None:
            self.mostrar_menu_recetas_prompt()

    def mostrar_abrir_detalles_prompt(self, lista_recetas:list[Receta]):
        self.refrescar_pantalla()
        self.input_abrir_detalles.imprimir("Ingresa el índice de la receta a mostrar",
                                           choices=[str(i+1) for i in range(len(lista_recetas))],
                                           show_choices=False)

        if self.input_abrir_detalles.user_input is None:
            self.mostrar_abrir_detalles_prompt(lista_recetas)

    def mostrar_opciones_detalles_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_detalles.imprimir("Selecciona una opción o cambia de página [',' '.']",
                                          choices=["1", "2", "3", "m", ",", "."],
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

    def mostrar_prompt_eliminar_receta_prompt(self):
        self.refrescar_pantalla()
        confirmacion = Prompt.ask("[bold red]¡Atención! estás a punto de eliminar esta receta, cualquier platillo vinculado a ella será eliminado también\nConfirma para continuar[/bold red]",
                                  choices=["S","N"])

        if confirmacion == "S":
            return True

        return False

    def mostrar_opciones_editar_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_editar_receta.imprimir("Selecciona una opción o cambia de página [',' '.']",
                                               choices=["1", "2", "3", "4", "5", "6", "m", ",", "."],
                                               show_choices=False)

        if self.input_menu_editar_receta.user_input is None:
            self.mostrar_opciones_editar_prompt()

    def mostrar_editar_nombre_prompt(self):
        self.refrescar_pantalla()
        info = Prompt.ask("[bold yellow]Ingresa el nuevo nombre de la receta[/bold yellow]")

        if len(info) > 0:
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar nuevo nombre[/bold yellow] "
                                      f"[italic white]{info}[/italic white]", choices=["S", "N"])
            if confirmacion == "S":
                return info
            else:
                return None
        else:
            self.mostrar_editar_nombre_prompt()

    def mostrar_editar_porciones_prompt(self):
        self.refrescar_pantalla()
        info = Prompt.ask("[bold yellow]Ingresa la nueva cantidad de porciones[/bold yellow]")

        if len(info):
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar número de porciones[/bold yellow] "
                                      f"[italic white]{info}[/italic white]", choices=["S", "N"])
            if confirmacion == "S":
                return info
            else:
                return None
        else:
            self.mostrar_editar_porciones_prompt()

    def mostrar_crear_ingrediente_prompt(self):
        self.refrescar_pantalla()

        info = Prompt.ask("[bold yellow]Ingresa 1 para agregar ingrediente basado en insumo "
                          "o 2 para agregar un ingrediente basado en una receta[/bold yellow]",
                          choices=["1", "2"], show_choices=False)

        return info

    def mostrar_ingredientes_disponibles(self, lista_ingredientes:list[Ingrediente], pag_actual, total_pag):
        self.layout["tablas"].unsplit()
        self.mostrar_conteo_paginas(pag_actual, total_pag)

        consola_size = self.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 8

        if pag_actual == 1:
            idx_ui = 0
        else:
            idx_ui = (pag_actual - 1) * lineas_disp

        columnas = ["#", "Nombre"]

        tabla = Table(title="Ingredientes disponibles")

        for col in columnas:
            tabla.add_column(col)

        for i in range(len(lista_ingredientes)):
            idx_ui += 1
            tabla.add_row(str(idx_ui), lista_ingredientes[i].nombre)

        self.layout["tablas"].update(Align.center(tabla, vertical="middle"))

    def mostrar_seleccionar_insumo_ing_prompt(self, opciones):
        opciones.append(",")
        opciones.append(".")

        ins_num = None

        while ins_num is None or ins_num == "," or ins_num == ".":
            self.refrescar_pantalla()
            ins_num = self.input_seleccionar_insumo.imprimir(
                "[bold yellow]Ingresa el índice del ingrediente a agregar o cambia de página [',' '.'][/bold yellow]",
                choices=opciones,
                show_choices=False)

        return ins_num

    def mostrar_seleccionar_receta_ing_prompt(self, opciones):
        opciones.append(",")
        opciones.append(".")

        receta_num = None

        while receta_num is None or receta_num == "," or receta_num == ".":
            self.refrescar_pantalla()
            receta_num = self.input_seleccionar_receta.imprimir(
                "[bold yellow]Ingresa el índice del ingrediente a agregar o cambia de página [',' '.'][/bold yellow]",
                choices=opciones,
                show_choices=False)

        return receta_num

    def mostrar_ingresar_cantidad_ing_prompt(self):
        cantidad = ""

        while len(cantidad) == 0:
            self.refrescar_pantalla()
            cantidad = Prompt.ask("[bold yellow]Ingresa la cantidad para este ingrediente[/bold yellow]")

        return cantidad

    def mostrar_ingresar_unidad_medida_ing_prompt(self):
        unidad_m = ""

        while len(unidad_m) == 0:
            self.refrescar_pantalla()
            unidad_m = Prompt.ask("[bold yellow]Ingresa la unidad de medida para este ingrediente\nDisponibles ->[/bold yellow] [bold green]kg / g / l / ml[/bold green]")

        return unidad_m

    def mostrar_borrar_ingrediente_prompt(self, opciones):
        if len(opciones) == 0:
            rich.print("[bold green]Error: No hay ingredientes para borrar, volviendo al menú editar...[/bold green]")
            time.sleep(5)
            return None

        num_ing = Prompt.ask("[bold yellow]Ingresa el número del ingrediente a borrar[/bold yellow]",
                             choices=opciones,
                             show_choices=False)

        if num_ing is not None:
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar borrar ingrediente[/bold yellow] "
                                      f"[italic white]#{num_ing}[/italic white]", choices=["S", "N"])
            if confirmacion == "S":
                return num_ing
            else:
                return None

    def mostrar_opciones_editar_ing_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_editar_ing.imprimir("Selecciona una opción o cambia de página [',' '.']",
                                            choices=["1", "2", "3", "4", ",", "."],
                                            show_choices=False)

        if self.input_menu_editar_ing.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_opciones_editar_ing_prompt()

    def mostrar_opciones_editar_inst_prompt(self):
        self.refrescar_pantalla()
        self.input_menu_editar_inst.imprimir("Selecciona una opción o cambia de página [',' '.']",
                                             choices=["1", "2", "3", "4", ",", "."],
                                             show_choices=False)

        if self.input_menu_editar_inst.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_opciones_editar_inst_prompt()

    def mostrar_agregar_instruccion_prompt(self):
        self.refrescar_pantalla()
        info = Prompt.ask("[bold yellow]Ingresa la instrucción[/bold yellow]")

        if info is not None:
            confirmacion = Prompt.ask("[bold yellow]Confirmar agregar instrucción[/bold yellow]", choices=["S", "N"])
            if confirmacion == "S":
                return info
            else:
                return None

    def mostrar_editar_instruccion_prompt(self):
        self.refrescar_pantalla()
        nueva_inst = Prompt.ask(f"[bold yellow]Ingresa la nueva instrucción[/bold yellow]")

        if nueva_inst is not None:
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar agregar nueva instrucción[/bold yellow]", choices=["S", "N"])
            if confirmacion == "S":
                return nueva_inst
            else:
                return None

    def mostrar_seleccionar_instruccion_prompt(self, opciones):
        self.refrescar_pantalla()
        if len(opciones) == 0:
            rich.print("[bold green]Error: No hay instrucciones para editar, volviendo al menú editar...[/bold green]")
            time.sleep(5)
            return None

        inst_num = Prompt.ask("[bold yellow]Ingresa el número de la instrucción a modificar[/bold yellow]",
                              choices=opciones,
                              show_choices=False)

        return inst_num

    def mostrar_borrar_instruccion_prompt(self, opciones):
        self.refrescar_pantalla()
        if len(opciones) == 0:
            rich.print("[bold green]Error: No hay instrucciones para editar, volviendo al menú editar...[/bold green]")
            time.sleep(5)
            return None

        inst_num = Prompt.ask("[bold yellow]Ingresa el número de la instrucción a borrar[/bold yellow]",
                              choices=opciones,
                              show_choices=False)

        if inst_num is not None:
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar borrar ingrediente #{inst_num}[/bold yellow]",
                                      choices=["S", "N"])

            if confirmacion == "S":
                return inst_num
            else:
                return None

    def mostrar_seleccionar_ingrediente_prompt(self, opciones):
        self.refrescar_pantalla()

        if len(opciones) == 0:
            rich.print("[bold green]Error: No hay ingredientes para editar, volviendo al menú editar...[/bold green]")
            time.sleep(5)
            return None, None

        ing_idx = Prompt.ask("[bold yellow]Ingresa el número del ingrediente a modificar[/bold yellow]",
                             choices=opciones,
                             show_choices=False)

        return ing_idx

    def mostrar_buscar_por_nombre_prompt(self):
        nombre = ""

        while len(nombre) == 0:
            self.refrescar_pantalla()
            nombre = Prompt.ask("[bold yellow]Ingresa el nombre a buscar[/bold yellow]")

        return nombre

    def mostrar_buscar_por_porciones_prompt(self):
        num_porciones = ""

        while len(num_porciones) == 0:
            self.refrescar_pantalla()
            num_porciones = Prompt.ask("[bold yellow]Ingresa el número de porciones a buscar[/bold yellow]")

        return num_porciones

    def mostrar_prompt_crear_receta_nombre(self):
        nombre = ""

        if len(nombre) == 0 and nombre != "0":
            self.refrescar_pantalla()
            nombre = Prompt.ask("Para comenzar, ingresa el nombre de la nueva receta o 0 para cancelar")

        if nombre == "0":
            return None

        return nombre

    def mostrar_prompt_crear_receta_porciones(self):
        porciones = ""

        if len(porciones) == 0:
            self.refrescar_pantalla()
            porciones = Prompt.ask("Ahora, ingresa el número de porciones de la receta")

        return porciones

    def mostrar_conteo_paginas(self, pag_actual, pag_total):
        paginas_columna = Columns()
        paginas = f"[bold magenta]Página {pag_actual}/{pag_total}[/bold magenta]"

        paginas_columna.expand = True
        self.layout["banda_pagina"].size = 1
        paginas_columna.add_renderable(Align.center(paginas))

        self.layout["banda_pagina"].update(paginas_columna)

    def mostrar_mensaje_no_pagina_anterior(self):
        rich.print("[bold green]Error: No hay página anterior")
        time.sleep(2)

    def mostrar_mensaje_no_pagina_siguiente(self):
        rich.print("[bold green]Error: No hay página siguiente")
        time.sleep(2)

    def mostrar_mensaje_no_resultados_busqueda_av(self):
        rich.print("[bold blue]Aviso: No se encontraron resultados para la búsqueda realizada, volviendo a al menú de búsqueda avanzada...[/bold blue]")
        time.sleep(3)

    def mostrar_error_crear_receta_duplicado(self):
        rich.print("[bold red]Error: La receta que intentas crear ya existe, cambia el nombre actual o edita la receta existente[/bold red]")
        time.sleep(3)

    def mostrar_error_receta_nombre_duplicado(self):
        rich.print("[bold red]Error: El nombre ingresado ya existe, cambia el nombre actual o edita la receta existente[/bold red]")
        time.sleep(3)

    def mostrar_error_validacion(self, error:str):
        rich.print(f"[bold red]{error}[/bold red]")
        time.sleep(3)

    def refrescar_pantalla(self):
        try:
            subprocess.run('cls' if os.name == 'nt' else 'clear')
        except FileNotFoundError:
            print(chr(27) + "[2J")
        self.console.print(self.layout, justify="center")
