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

        self.layout["contenido"].split_column(Layout(name="main"), Layout(name="opciones"))

        self.mostrar_todas_ventas()
        self.crear_banda_opciones_principal()

    def resetear_vista(self):
        self.layout["main"].unsplit()

        self.tabla_ventas = Table(title="Ventas")
        self.configurar_tabla_ventas()
        self.tabla_consumo = Table(title="Consumo")
        self.configurar_tabla_consumo()

        self.crear_banda_opciones_principal()

    def mostrar_todas_ventas(self):
        self.resetear_vista()

        self.layout["main"].update(Align.center(self.tabla_ventas, vertical="top"))

    def configurar_tabla_ventas(self):
        columnas = ["#", "Fecha", "Número de comensales", "Monto total"]

        for columna in columnas:
            self.tabla_ventas.add_column(columna)

    def crear_elemento_tabla_ventas(self, venta: Venta):
        self.tabla_ventas.add_row(str(venta.num), str(venta.fecha), str(venta.numero_comensales), str(venta.monto_total))

    def mostrar_detalles_venta(self, venta: Venta | None, datos_editados, mapa_consumo):
        self.resetear_vista()

        self.layout["main"].split_column(Layout(name="panel_venta"), Layout(name="tabla_consumo"))

        self.layout["panel_venta"].size = 6

        panel = Panel(renderable=f"[bold yellow]Venta #{str(venta.num)}\n"
                                 f"[bold white]Fecha:[/bold white] {str(venta.fecha)}\n"
                                 f"[bold white]Comensales servidos:[/bold white] {str(venta.numero_comensales)}\n"
                                 f"[bold white]Monto total:[/bold white] ${str(venta.monto_total)}"
                                 f"[/bold yellow]")

        panel.height = 6

        if venta and len(venta.detalles):
            self.llenar_tabla_consumo(venta.detalles, mapa_consumo, datos_editados["consumo"])

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

    def mostrar_platillos_disponibles(self, lista_platillos:list[Platillo]):
        columnas = ["#", "Nombre"]

        tabla = Table(title="Platillos disponibles")

        for col in columnas:
            tabla.add_column(col)

        for i in range(len(lista_platillos)):
            tabla.add_row(str(i+1), lista_platillos[i].nombre)

        self.layout["tabla_consumo"].update(Align.center(tabla, vertical="middle"))

    def mostrar_registrar_venta(self, venta:Venta | None, mapa_idx):
        self.resetear_vista()

        self.layout["main"].split_column(Layout(name="panel_venta"), Layout(name="tabla_consumo"))

        self.layout["panel_venta"].size = 6

        panel = Panel(renderable=f"[bold yellow]Venta #{str(venta.num) if venta else "N/A"}\n"
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
                    "[2] Editar venta",
                    "[3] Eliminar venta",
                    "[M] Volver al menú"]

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
        self.input_menu_ventas.imprimir("Selecciona una opción",
                                        choices=["1", "2", "m"],
                                        show_choices=False)

        if self.input_menu_ventas.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_menu_ventas_prompt()

    def mostrar_abrir_detalles_prompt(self, lista_ventas: list[Venta]):
        self.input_abrir_detalles.imprimir("Ingresa el índice de la venta a mostrar",
                                           choices=[str(venta.num) for venta in lista_ventas],
                                           show_choices=False)

        if self.input_abrir_detalles.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_abrir_detalles_prompt(lista_ventas)

    def mostrar_opciones_detalles_prompt(self):
        self.input_menu_detalles.imprimir("Selecciona una opción",
                                          choices=["1", "2", "3", "m"],
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
                                        choices=["1", "2", "3", "4", "5", "m"],
                                        show_choices=False)

        if self.input_menu_editar.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_opciones_editar_prompt()

    def mostrar_opciones_editar_consumo_prompt(self):
        self.input_menu_editar_consumo.imprimir("Selecciona una opción",
                                        choices=["1", "2", "3", "4"],
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

    def mostrar_agregar_consumo_prompt(self, opciones):
        self.refrescar_pantalla()

        if len(opciones) == 0:
            rich.print("[bold green]No hay platillos con precio vigente para agregar a esta venta, volviendo al menú editar...[/bold green]")
            time.sleep(5)
            return None, None

        num_platillo = Prompt.ask("[bold yellow]Selecciona un platillo de la lista para agregar[/bold yellow]",
                                  choices=opciones,
                                  show_choices=False)

        confirmacion = Prompt.ask(f"[bold yellow]Confirma el nuevo platillo[/bold yellow]",
                        choices=["S", "N"])

        if confirmacion == "S":
            cantidad = ""

            while len(cantidad) == 0:
                self.refrescar_pantalla()
                cantidad = Prompt.ask("[bold yellow]Ingresa la cantidad de platillos consumida[bold yellow]")

                if len(cantidad) != 0:
                    confirmacion2 = Prompt.ask(f"[bold yellow]Confirma la cantidad: [italic white]{cantidad}[italic white][/bold yellow]",
                                    choices=["S", "N"])

                    if confirmacion2 == "S":
                        return num_platillo, cantidad
                    else:
                        cantidad = ""
        else:
            self.mostrar_agregar_consumo_prompt()

    def mostrar_editar_cantidad_prompt(self, opciones):
        self.refrescar_pantalla()

        if len(opciones) == 0:
            rich.print("[bold green]No hay consumos para editar a esta venta, volviendo al menú editar...[/bold green]")
            time.sleep(5)
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
            time.sleep(5)
            return None, None

        num = Prompt.ask("[bold yellow]Ingresa el índice del consumo a remover[/bold yellow]",
                         choices=opciones,
                         show_choices=False)

        return num

    def mostrar_prompt_crear_venta(self):
        fecha = ""
        num_comensales = ""

        while len(fecha) == 0:
            self.refrescar_pantalla()
            fecha = Prompt.ask("Para comenzar, ingresa la fecha en que se realizó la venta o 0 para cancelar")
            if fecha == "0":
                return None, None

        while len(num_comensales) == 0:
            self.refrescar_pantalla()
            num_comensales = Prompt.ask("Ingresa el número de comensales o 0 para cancelar")
            if fecha == "0":
                return None, None

        return fecha, num_comensales

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
        subprocess.run('cls' if os.name == 'nt' else 'clear')
        self.console.print(self.layout, justify="center")