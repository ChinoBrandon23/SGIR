import subprocess
import os
import time

import rich
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.prompt import Prompt

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

        self.layout["contenido"].split_column(Layout(name="main"), Layout(name="opciones"))

        self.mostrar_todas_recetas()
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

    def mostrar_todas_recetas(self):
        self.resetear_vista()

        self.layout["main"].update(self.tabla_recetas)

    def configurar_tabla_recetas(self):
        columnas = ["#", "Nombre"]

        for columna in columnas:
            self.tabla_recetas.add_column(columna)

    def crear_elemento_tabla_recetas(self, receta:Receta):
        self.tabla_recetas.add_row(str(receta.num), receta.nombre)

    def mostrar_detalles_receta(self, receta:Receta, datos_editados, mapa_idx_ing):
        if self.tabla_ingredientes.row_count > 0 or self.tabla_instrucciones.row_count > 0:
            self.resetear_vista()

        self.layout["main"].split_column(Layout(name="panel_receta"),
                                         Layout(name="tabla_ing"),
                                         Layout(name="tabla_ins"))

        self.layout["panel_receta"].size = 2

        nombre_receta = datos_editados["nombre"] if "nombre" in datos_editados else receta.nombre
        nombre_receta += "**" if "nombre" in datos_editados else ""

        porciones_receta = datos_editados["porciones"] if "porciones" in datos_editados else str(receta.num_porciones)
        porciones_receta += "**" if "porciones" in datos_editados else ""

        panel = Panel(renderable=f"{"[bold red]" if "nombre" in datos_editados else "[bold yellow]"}"
                                 f"{nombre_receta}"
                                 f"{"[/bold red]" if "nombre" in datos_editados else "[/bold yellow]"}: "
                                 f"{"[bold red]" if "porciones" in datos_editados else "[italic yellow]"}"
                                 f"{porciones_receta}"
                                 f"{"[/bold red]" if "porciones" in datos_editados else "[/italic yellow]"}"
                                 f"[italic yellow] porciones [/italic yellow]")

        panel.height = 7

        if datos_editados and len(datos_editados["ingredientes"]):
            ingredientes = datos_editados["ingredientes"][:]
            self.llenar_tabla_ingredientes(receta.lista_ingredientes, mapa_idx_ing, ingredientes)
        else:
            self.llenar_tabla_ingredientes(receta.lista_ingredientes, mapa_idx_ing)

        self.llenar_tabla_instrucciones(receta.instrucciones)

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

            if ing_editados:
                # checa si un ing que fue agregado al dict de edición está en la lista original de ingredientes,
                # lo que quiere decir que será editado, si es así entonces muestra el valor editado en vez del original
                valor_editado = next(filter(lambda x: x["nombre"] == nombre_ing, ing_editados), None)

                if valor_editado is not None:
                    # sobreescribe ing editado (duplicado)
                    ing_editados.remove(valor_editado)

                    self.tabla_ingredientes.add_row(f"[bold red]{idx_ing}[/bold red]",
                                                    f"[bold red]{nombre_ing}[/bold red]",
                                                    f"[bold red]{valor_editado["cantidad"]}[/bold red]",
                                                    f"[bold red]{valor_editado["unidad_m"]}[/bold red]")

                    continue
            # Agrega los ing ya existentes
            self.tabla_ingredientes.add_row(str(idx_ing),
                                            nombre_ing,
                                            str(ingrediente.cantidad),
                                            ingrediente.unidad_medida)

        if ing_editados and len(ing_editados) > 0:
            # agrega los ing nuevos
            for ing in ing_editados:
                idx_ing = [item for item in mapa_idx_ing if mapa_idx_ing[item] == ing["nombre"]][0]

                self.tabla_ingredientes.add_row(f"[bold red]{idx_ing}[/bold red]",
                                                f"[bold red]{ing["nombre"]}[/bold red]",
                                                    f"[bold red]{ing["cantidad"]}[/bold red]",
                                                    f"[bold red]{ing["unidad_m"]}[/bold red]")

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

        self.layout["main"].split_column(Layout(name="panel_receta"),
                                         Layout(name="tabla_ing"),
                                         Layout(name="tabla_ins"))

        self.layout["panel_receta"].size = 3

        panel = Panel(renderable=f"[bold white]Crear receta\n"
                                 f"{receta.nombre if receta else "[bold magenta]Nombre de la receta[/bold magenta]"}[/bold white]. "
                                 f"Porciones: {receta.num_porciones if receta else "[bold magenta]Número de porciones[/bold magenta]"}")

        panel.height = 7

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
                    "[1] Volver a recetas",
                    "[2] Editar receta",
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
        self.input_menu_recetas.imprimir("Selecciona una opción",
                                         choices=["1", "2", "m"],
                                         show_choices=False)

        if self.input_menu_recetas.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_menu_recetas_prompt()

    def mostrar_abrir_detalles_prompt(self, lista_recetas:list[Receta]):
        self.input_abrir_detalles.imprimir("Ingresa el índice de la receta a mostrar",
                                           choices=[str(receta.num) for receta in lista_recetas],
                                           show_choices=False)

        if self.input_abrir_detalles.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_abrir_detalles_prompt(lista_recetas)

    def mostrar_opciones_detalles_prompt(self):
        self.input_menu_detalles.imprimir("Selecciona una opción",
                                          choices=["1", "2", "m"],
                                          show_choices=False)

        if self.input_menu_detalles.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_opciones_detalles_prompt()

    def mostrar_opciones_editar_prompt(self):
        self.input_menu_editar_receta.imprimir("Selecciona una opción",
                                               choices=["1", "2", "3", "4", "5", "6", "m"],
                                               show_choices=False)

        if self.input_menu_editar_receta.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_opciones_editar_prompt()

    def mostrar_editar_nombre_prompt(self):
        info = Prompt.ask("[bold yellow]Ingresa el nuevo nombre de la receta[/bold yellow]")

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

    def mostrar_editar_porciones_prompt(self):
        info = Prompt.ask("[bold yellow]Ingresa la nueva cantidad de porciones[/bold yellow]")

        if len(info):
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar número de porciones[/bold yellow] "
                                      f"[italic white]{info}[/italic white]", choices=["S", "N"])
            if confirmacion == "S":
                return info
            else:
                return None
        else:
            self.refrescar_pantalla()
            self.mostrar_editar_porciones_prompt()

    def mostrar_crear_ingrediente_prompt(self):
        info = Prompt.ask("[bold yellow]Ingresa la sig. información separada por una coma: "
                          "[bold white][Nombre de receta o insumo] [Cantidad] [Unidad de medida][/bold white]"
                          "[/bold yellow]")

        if len(info):
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar agregar ingrediente[/bold yellow] "
                                      f"[italic white]{info}[/italic white]", choices=["S", "N"])
            if confirmacion == "S":
                return info
            else:
                return None
        else:
            self.refrescar_pantalla()
            self.mostrar_crear_ingrediente_prompt()

    def mostrar_modificar_ingrediente_prompt(self, opciones):
        if len(opciones) == 0:
            rich.print("[bold green]Error: No hay ingredientes para editar, volviendo al menú editar...[/bold green]")
            time.sleep(5)
            return None, None

        ing_idx = Prompt.ask("[bold yellow]Ingresa el número del ingrediente a modificar[/bold yellow]",
                             choices=opciones,
                             show_choices=False)
        
        info = Prompt.ask("[bold yellow]Ingresa la sig. información separada por una coma: "
                          "[bold white][Cantidad] [Unidad de medida][/bold white]"
                          "[/bold yellow]")

        if len(info):
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar modificar[/bold yellow] "
                                      f"[italic white]{info}[/italic white]", choices=["S", "N"])
            if confirmacion == "S":
                return ing_idx, info
            else:
                return None
        else:
            self.refrescar_pantalla()
            self.mostrar_crear_ingrediente_prompt()

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
        self.input_menu_editar_ing.imprimir("Selecciona una opción",
                                            choices=[str(i) for i in range(1, 5)],
                                            show_choices=False)

        if self.input_menu_editar_ing.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_opciones_editar_ing_prompt()

    def mostrar_opciones_editar_inst_prompt(self):
        self.input_menu_editar_inst.imprimir("Selecciona una opción",
                                             choices=[str(i) for i in range(1, 5)],
                                             show_choices=False)

        if self.input_menu_editar_inst.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_opciones_editar_inst_prompt()

    def mostrar_agregar_instruccion_prompt(self):
        info = Prompt.ask("[bold yellow]Ingresa la instrucción[/bold yellow]")

        if info is not None:
            confirmacion = Prompt.ask("[bold yellow]Confirmar agregar instrucción[/bold yellow]", choices=["S", "N"])
            if confirmacion == "S":
                return info
            else:
                return None

    def mostrar_editar_instruccion_prompt(self, opciones):
        if len(opciones) == 0:
            rich.print("[bold green]Error: No hay instrucciones para editar, volviendo al menú editar...[/bold green]")
            time.sleep(5)
            return None, None

        inst_num = Prompt.ask("[bold yellow]Ingresa el número de la instrucción a modificar[/bold yellow]",
                              choices=opciones,
                              show_choices=False)

        nueva_inst = Prompt.ask(f"[bold yellow]Ingresa la nueva instrucción #{inst_num}[/bold yellow]")

        if nueva_inst is not None:
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar agregar nueva instrucción #{inst_num}[/bold yellow]", choices=["S", "N"])
            if confirmacion == "S":
                return inst_num, nueva_inst
            else:
                return None

    def mostrar_borrar_instruccion_prompt(self, opciones):
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

    def mostrar_prompt_crear_receta(self):
        nombre = Prompt.ask("Para comenzar, ingresa el nombre de la nueva receta o 0 para cancelar")

        if nombre is not "0":
            porciones = Prompt.ask("Ahora, ingresa el número de porciones de la receta o 0 para cancelar")

            if porciones is not "0":
                return nombre, porciones

        return None, None

    def refrescar_pantalla(self):
        subprocess.run('cls' if os.name == 'nt' else 'clear')
        self.console.print(self.layout, justify="center")

