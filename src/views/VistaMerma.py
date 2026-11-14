import subprocess
import os

from rich.align import Align
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.prompt import Prompt

from models.insumo import Insumo
from models.merma import Merma
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

        self.layout["contenido"].split_column(Layout(name="main"), Layout(name="opciones"))

        self.mostrar_toda_merma()
        self.crear_banda_opciones_principal()

    def resetear_vista(self):
        self.layout["main"].unsplit()

        self.tabla_merma = Table(title="Merma")
        self.configurar_tabla_merma()

        self.tabla_detalles = Table(title="Detalles")
        self.configurar_tabla_detalles()

        self.crear_banda_opciones_principal()

    def mostrar_toda_merma(self):
        self.resetear_vista()

        self.layout["main"].update(Align.center(self.tabla_merma, vertical="top"))

    def configurar_tabla_merma(self):
        columnas = ["#", "Fecha", "Cantidad", "Unidad de medida", "Insumo", "Tipo de merma"]

        for columna in columnas:
            self.tabla_merma.add_column(columna)

    def configurar_tabla_detalles(self):
        columnas = ["Insumo", "Cantidad", "Unidad de medida", "Descripción"]

        for columna in columnas:
            self.tabla_detalles.add_column(columna)

    def crear_elemento_tabla_merma(self, merma: Merma):
        self.tabla_merma.add_row(str(merma.num), str(merma.fecha), str(merma.cantidad), merma.unidad_medida,
                                 merma.insumo.nombre, merma.tipo_merma.nombre)

    def mostrar_detalles_merma(self, merma: Merma | None, datos_editados):
        self.resetear_vista()

        self.layout["main"].split_column(Layout(name="panel_merma"), Layout(name="tabla_detalles"))

        self.layout["panel_merma"].size = 5

        panel = Panel(renderable=f"[bold yellow]Merma #{str(merma.num) if merma else ""}\n"
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
        self.tabla_detalles.add_row( f"{"[bold red]" if datos_editados and "insumo" in datos_editados else "[bold yellow]"}"
                                     f"{merma_obj.insumo.nombre}{"[/bold red]" if datos_editados and "insumo" in datos_editados else "[/bold yellow]"}",
                                         f"{"[bold red]" if datos_editados and "cantidad" in datos_editados else "[bold yellow]"}"
                                         f"{str(merma_obj.cantidad)}{"[/bold red]" if datos_editados and "cantidad" in datos_editados else "[/bold yellow]"}",
                                         f"{"[bold red]" if datos_editados and "unidad_medida" in datos_editados else "[bold yellow]"}"
                                         f"{merma_obj.unidad_medida}{"[/bold red]" if datos_editados and "unidad_medida" in datos_editados else "[/bold yellow]"}",
                                         f"{"[bold red]" if datos_editados and "descripcion" in datos_editados else "[bold yellow]"}"
                                         f"{merma_obj.descripcion}{"/[bold red]" if datos_editados and "descripcion" in datos_editados else "[/bold yellow]"}")

    def mostrar_tipos_merma_disponibles(self, lista_tipo_merma:list[TipoMerma]):
        columnas = ["#", "Nombre"]

        tabla = Table(title="Tipos de merma disponibles")

        for col in columnas:
            tabla.add_column(col)

        for i in range(len(lista_tipo_merma)):
            tabla.add_row(str(i+1), lista_tipo_merma[i].nombre)

        self.layout["tabla_detalles"].update(Align.center(tabla, vertical="middle"))

    def mostrar_insumos_disponibles(self, lista_insumos:list[Insumo]):
        columnas = ["#", "Nombre"]

        tabla = Table(title="Insumos disponibles")

        for col in columnas:
            tabla.add_column(col)

        for i in range(len(lista_insumos)):
            tabla.add_row(str(i+1), lista_insumos[i].nombre)

        try:
            self.layout["tabla_detalles"].update(Align.center(tabla, vertical="middle"))
        except KeyError:
            self.layout["main"].split_column(Layout(name="tabla_detalles"))
            self.layout["tabla_detalles"].update(Align.center(tabla, vertical="middle"))

    def mostrar_registrar_merma(self, merma: Merma | None):
        self.resetear_vista()

        self.layout["main"].split_column(Layout(name="panel_merma"), Layout(name="tabla_detalles"))

        self.layout["panel_merma"].size = 5

        panel = Panel(renderable=f"[bold yellow]Merma #{str(merma.num) if merma else ""}\n"
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
                    "[1] Volver a mermas",
                    "[2] Editar merma",
                    "[3] Eliminar merma",
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
        self.input_menu_merma.imprimir("Selecciona una opción",
                                       choices=["1", "2", "m"],
                                       show_choices=False)

        if self.input_menu_merma.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_menu_merma_prompt()

    def mostrar_abrir_detalles_prompt(self, lista_merma: list[Merma]):
        self.input_abrir_detalles.imprimir("Ingresa el índice de la merma a mostrar",
                                           choices=[str(merma.num) for merma in lista_merma],
                                           show_choices=False)

        if self.input_abrir_detalles.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_abrir_detalles_prompt(lista_merma)

    def mostrar_opciones_detalles_prompt(self):
        self.input_menu_detalles.imprimir("Selecciona una opción",
                                          choices=["1", "2", "3", "m"],
                                          show_choices=False)

        if self.input_menu_detalles.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_opciones_detalles_prompt()

    def mostrar_prompt_eliminar_merma_prompt(self):
        confirmacion = Prompt.ask("[bold red]¡Atención! estás a punto de eliminar este registro, confirma para continuar[/bold red]",
                                  choices=["S","N"])

        if confirmacion == "S":
            return True

        return False

    def mostrar_opciones_editar_prompt(self):
        self.input_menu_editar_merma.imprimir("Selecciona una opción",
                                              choices=["1", "2", "3", "4", "5", "6", "7", "m"],
                                              show_choices=False)

        if self.input_menu_editar_merma.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_opciones_editar_prompt()

    def mostrar_editar_descripcion_prompt(self):
        self.refrescar_pantalla()
        info = Prompt.ask("[bold yellow]Ingresa la nueva descripción de la merma[/bold yellow]")

        if len(info) > 0:
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar nueva descripción[/bold yellow]", choices=["S", "N"])
            if confirmacion == "S":
                return info
            else:
                return None
        else:
            self.refrescar_pantalla()
            self.mostrar_editar_descripcion_prompt()

    def mostrar_editar_fecha_prompt(self):
        self.refrescar_pantalla()
        info = Prompt.ask("[bold yellow]Ingresa la nueva fecha en el siguiente formato[/bold yellow]: [[bold green]dd-mm-yyyy[/bold green]]")

        if len(info):
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar fecha:[/bold yellow] "
                                      f"[italic white]{info}[/italic white]", choices=["S", "N"])
            if confirmacion == "S":
                return info
            else:
                return None
        else:
            self.refrescar_pantalla()
            self.mostrar_editar_fecha_prompt()

    def mostrar_editar_unidad_medida_prompt(self):
        self.refrescar_pantalla()
        unidad = Prompt.ask("[bold yellow]Ingresa la nueva unidad de medida[/bold yellow]")

        if len(unidad) > 0:
            confirmacion = Prompt.ask("[bold yellow]Confirmar nueva unidad de medida:[/bold yellow] "
                                      f"[italic white]{unidad}[/italic white]",
                                      choices=["S","N"])

            if confirmacion == "S":
                return unidad
            else:
                return None
        else:
            self.refrescar_pantalla()
            self.mostrar_editar_unidad_medida_prompt()

    def mostrar_editar_cantidad_prompt(self):
        self.refrescar_pantalla()
        cantidad = Prompt.ask("[bold yellow]Ingresa la nueva cantidad de merma[/bold yellow]")

        if len(cantidad) > 0:
            confirmacion = Prompt.ask("[bold yellow]Confirmar nueva cantidad[/bold yellow]", choices=["S", "N"])

            if confirmacion == "S":
                return cantidad
            else:
                return None
        else:
            self.refrescar_pantalla()
            self.mostrar_editar_cantidad_prompt()

    def mostrar_editar_tipo_merma_prompt(self, opciones):
        self.refrescar_pantalla()
        opciones.append("0")

        tipo_num = Prompt.ask(
            "[bold yellow]Ingresa el nuevo tipo de merma de entre las opciones o 0 para crear un tipo nuevo[/bold yellow]",
            choices=opciones,
            show_choices=False)

        if tipo_num == "0":
            return tipo_num

        elif len(tipo_num):
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar tipo de merma[/bold yellow] "
                                      f"[italic white]{tipo_num}[/italic white]", choices=["S", "N"])
            if confirmacion == "S":
                return tipo_num
            else:
                return None

        else:
            self.refrescar_pantalla()
            self.mostrar_editar_tipo_merma_prompt()

    def mostrar_crear_tipo_insumo_prompt(self):
        self.refrescar_pantalla()
        tipo_nombre = Prompt.ask("[bold yellow]Ingresa el nombre del nuevo tipo de merma[/bold yellow]")

        if tipo_nombre is not None:
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar crear y asignar tipo: [italic white]{tipo_nombre}[/italic white][/bold yellow]", choices=["S", "N"])

            if confirmacion == "S":
                return tipo_nombre
            else:
                return None

    def mostrar_prompt_registrar_insumo_merma(self, opciones):
        self.refrescar_pantalla()

        num = Prompt.ask("[bold yellow]Selecciona el insumo del que se produjo la merma[/bold yellow]",
                         choices=opciones,
                         show_choices=False)

        confirmacion = Prompt.ask(f"[bold yellow]Confirmar selección de insumo[/bold yellow]",
                                  choices=["S", "N"])

        if confirmacion == "S":
            return num
        else:
            return None

    def paginar(self, items: list, num_pag: int):
        lineas_disp = ((self.console.size[1] - 6) // 2) - 6

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
