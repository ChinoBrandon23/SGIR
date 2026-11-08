import subprocess
import os
import time

import rich
from rich.align import Align
from rich.console import Group
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.prompt import Prompt

from models.compra import Compra, DetalleCompra
from models.insumo import Insumo
from models.marca import Marca
from models.proveedor import Proveedor
from models.tipo_insumo import TipoInsumo
from views.VistaBase import VistaBase
from views.clases_personalizadas.InputEmisor import InputEmisor


class VistaCompras(VistaBase):
    def __init__(self, console):
        super().__init__()
        self.console = console

        self.tabla_compras = Table(title="Compras")
        self.configurar_tabla_compras()

        self.tabla_detalles_menu = Table(title="Detalles")
        self.configurar_tabla_detalles_compra()

        self.input_menu_compras = InputEmisor()
        self.input_abrir_detalles = InputEmisor()
        self.input_menu_detalles = InputEmisor()
        self.input_menu_editar_compra = InputEmisor()
        self.input_menu_editar_insumo = InputEmisor()

        self.layout["contenido"].split_column(Layout(name="main"), Layout(name="opciones"))

        self.mostrar_todas_compras()
        self.crear_banda_opciones_principal()

    def resetear_vista(self):
        self.layout["main"].unsplit()

        self.tabla_compras = Table(title="Compras")
        self.configurar_tabla_compras()
        self.tabla_detalles_menu = Table(title="Detalles")
        self.configurar_tabla_detalles_compra()

        self.crear_banda_opciones_principal()

    def mostrar_todas_compras(self):
        self.resetear_vista()

        self.layout["main"].update(Align.center(self.tabla_compras, vertical="top"))

    def configurar_tabla_compras(self):
        columnas = ["#", "Fecha de creación", "Total bruto", "Proveedor"]

        for columna in columnas:
            self.tabla_compras.add_column(columna)

    def crear_elemento_tabla_compras(self, compra: Compra):
        self.tabla_compras.add_row(str(compra.num), str(compra.fecha_creacion), f"${str(compra.total_bruto)}", compra.proveedor.nombre)

    def mostrar_detalles_compra(self, compra: Compra | None, datos_editados, mapa_insumos):
        self.resetear_vista()

        self.layout["main"].split_column(Layout(name="panel_menu"), Layout(name="tabla_detalles_compra"))
        self.layout["panel_menu"].size = 6

        panel = Panel(renderable=f"[bold yellow]Compra #{compra.num}\n"
                                 f"Fecha de creación: {compra.fecha_creacion if compra.fecha_creacion else ""}\n"
                                 f"{"[bold red]" if "total_bruto" in datos_editados else ""}"
                                 f"Total bruto: {f"${compra.total_bruto}" if compra.total_bruto else ""}"
                                 f"{"[/bold red]" if "total_bruto" in datos_editados else ""}\n"
                                 f"{"[bold red]" if "proveedor" in datos_editados else ""}"
                                 f"Proveedor: {compra.proveedor.nombre if compra.proveedor else ""}"
                                 f"{"[/bold red]" if "proveedor" in datos_editados else ""}"
                                 f"[/bold yellow]")

        panel.height = 6

        if compra and len(compra.lista_compras):
            self.llenar_tabla_detalles_compra(compra.lista_compras, mapa_insumos, datos_editados["insumos"])

        self.layout["panel_menu"].update(panel)
        self.layout["tabla_detalles_compra"].update(Align.center(self.tabla_detalles_menu, vertical="middle"))

    def configurar_tabla_detalles_compra(self):
        encabezados = ["#", "Insumo", "Marca", "Cantidad", "Unidad de medida", "Monto unitario", "Importe", "Fecha de compra", "Caducidad"]

        self.tabla_detalles_menu.show_lines = True

        for col in encabezados:
            self.tabla_detalles_menu.add_column(col)

    def llenar_tabla_detalles_compra(self, lista_compras:list[DetalleCompra], mapa_idx, insumos_editados=None):
        for detalle_compra in lista_compras:
            nombre_insumo = detalle_compra.insumo.nombre

            idx_insumo = [item for item in mapa_idx if mapa_idx[item].insumo.nombre == nombre_insumo][0]

            if insumos_editados:
                # checa si un platillo que fue agregado al dict de edición está en la lista original de ingredientes,
                # lo que quiere decir que será editado, si es así entonces muestra el valor editado en vez del original
                valor_editado = next(filter(lambda x: x.insumo.nombre == nombre_insumo, insumos_editados), None)

                if valor_editado is not None:
                    # sobreescribe platillo editado (duplicado)
                    insumos_editados.remove(valor_editado)

                    self.tabla_detalles_menu.add_row(f"[bold red]{str(idx_insumo)}[/bold red]",
                                                    f"[bold red]{nombre_insumo}[/bold red]",
                                                    f"[bold red]{valor_editado.insumo.marca.nombre}[/bold red]",
                                                    f"[bold red]{str(valor_editado.cantidad)}[/bold red]",
                                                    f"[bold red]{valor_editado.unidad_medida}[/bold red]",
                                                    f"[bold red]${str(valor_editado.monto_unitario)}[/bold red]",
                                                    f"[bold red]${str(valor_editado.importe)}[/bold red]",
                                                    f"[bold red]{str(valor_editado.fecha_compra)}[/bold red]",
                                                    f"[bold red]{str(valor_editado.fecha_caducidad)}[/bold red]")

                    continue
            # Agrega los platillos ya existentes
            self.tabla_detalles_menu.add_row(str(idx_insumo),
                                             nombre_insumo,
                                             detalle_compra.insumo.marca.nombre,
                                             str(detalle_compra.cantidad),
                                             detalle_compra.unidad_medida,
                                             f"${detalle_compra.monto_unitario}",
                                             f"${detalle_compra.importe}",
                                             str(detalle_compra.fecha_compra),
                                             str(detalle_compra.fecha_caducidad))

        if insumos_editados and len(insumos_editados) > 0:
            # agrega los platillos nuevos
            for detalle_compra in insumos_editados:
                idx_insumo = [item for item in mapa_idx if mapa_idx[item] == detalle_compra.insumo.nombre][0]

                self.tabla_detalles_menu.add_row(f"[bold red]{str(idx_insumo)}[/bold red]",
                                                    f"[bold red]{nombre_insumo}[/bold red]",
                                                    f"[bold red]{detalle_compra.insumo.marca.nombre}[/bold red]",
                                                    f"[bold red]{str(detalle_compra.cantidad)}[/bold red]",
                                                    f"[bold red]{detalle_compra.unidad_medida}[/bold red]"
                                                    f"[bold red]#{detalle_compra.monto_unitario}[/bold red]",
                                                    f"[bold red]${str(detalle_compra.importe)}[/bold red]",
                                                    f"[bold red]{str(detalle_compra.fecha_compra)}[/bold red]",
                                                    f"[bold red]{str(detalle_compra.fecha_caducidad)}[/bold red]")

    def mostrar_proveedores_disponibles(self, lista_proveedores:list[Proveedor]):
        columnas = ["#", "Nombre"]

        tabla = Table(title="Proveedores disponibles")

        for col in columnas:
            tabla.add_column(col)

        for i in range(len(lista_proveedores)):
            tabla.add_row(str(i+1), lista_proveedores[i].nombre)

        try:
            self.layout["tabla_detalles_compra"].update(Align.center(tabla, vertical="middle"))
        except KeyError:
            self.layout["main"].split_column(Layout(name="tabla_detalles_compra"))
            self.layout["tabla_detalles_compra"].update(Align.center(tabla, vertical="middle"))

    def mostrar_insumos_disponibles(self, lista_insumos:list[Insumo]):
        columnas = ["#", "Nombre", "Marca"]

        tabla = Table(title="Insumos disponibles")

        for col in columnas:
            tabla.add_column(col)

        if len(lista_insumos):
            for i in range(len(lista_insumos)):
                tabla.add_row(str(i+1), lista_insumos[i].nombre, lista_insumos[i].marca.nombre)
        else:
            tabla.add_row(" " * 10, " " * 10, " " * 10)

        self.layout["tabla_detalles_compra"].update(Align.center(tabla, vertical="middle"))

    def mostrar_marcas_disponibles(self, lista_marcas:list[Marca]):
        columnas = ["#", "Nombre"]

        tabla = Table(title="Marcas disponibles")

        for col in columnas:
            tabla.add_column(col)

        if len(lista_marcas):
            for i in range(len(lista_marcas)):
                tabla.add_row(str(i+1), lista_marcas[i].nombre)
        else:
            tabla.add_row(" " * 10, " " * 10)

        self.layout["tabla_detalles_compra"].update(Align.center(tabla, vertical="middle"))

    def mostrar_tipos_insumo_disponibles(self, lista_tipos:list[TipoInsumo]):
        columnas = ["#", "Nombre"]

        tabla = Table(title="Tipos de insumo disponibles")

        for col in columnas:
            tabla.add_column(col)

        if len(lista_tipos):
            for i in range(len(lista_tipos)):
                tabla.add_row(str(i+1), lista_tipos[i].nombre)
        else:
            tabla.add_row(" " * 10, " " * 10)

        self.layout["tabla_detalles_compra"].update(Align.center(tabla, vertical="middle"))

    def mostrar_crear_registro_compra(self, compra: Compra | None, insumo_idx):
        self.resetear_vista()

        self.layout["main"].split_column(Layout(name="panel_menu"), Layout(name="tabla_detalles_compra"))

        self.layout["panel_menu"].size = 6

        panel = Panel(renderable=f"[bold yellow]Compra {f"#{compra.num}" if compra else ""}\n"
                                 f"Fecha de creación: {compra.fecha_creacion if compra else ""}\n"
                                 f"Total bruto: {f"${compra.total_bruto}" if compra else ""}\n"
                                 f"Proveedor: {compra.proveedor.nombre if compra and compra.proveedor else ""}[/bold yellow]")

        panel.height = 6

        if compra:
            if len(compra.lista_compras):
                self.llenar_tabla_detalles_compra(compra.lista_compras, insumo_idx)

        self.layout["panel_menu"].update(panel)
        self.layout["tabla_detalles_compra"].update(Align.center(self.tabla_detalles_menu, vertical="middle"))

    def crear_banda_opciones_principal(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Ver detalles de compra",
                    "[2] Registrar compra",
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
                    "[1] Volver a compras",
                    "[2] Editar compra",
                    "[3] Eliminar compra",
                    "[M] Volver al menú"]

        opciones_columna.expand = True

        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def crear_banda_opciones_editar(self):
        opciones_columna = Columns()

        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Editar proveedor",
                    "[2] Agregar insumo",
                    "[3] Editar insumo",
                    "[4] Remover insumo",
                    "[5] Guardar",
                    "[6] Cancelar",
                    "[M] Volver al menú"]

        opciones_columna.expand = True

        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(Group(opciones_columna))

    def crear_banda_opciones_editar_insumos(self):
        opciones_columna = Columns()
        opciones = ["[bold yellow]Opciones:[/bold yellow]",
                    "[1] Editar cantidad",
                    "[2] Editar unidad de medida",
                    "[3] Editar monto unitario",
                    "[4] Editar fecha de compra",
                    "[5] Editar caducidad",
                    "[6] Volver"]

        opciones_columna.expand = True
        self.layout["opciones"].size = 1

        for opcion in opciones:
            opciones_columna.add_renderable(opcion)

        self.layout["opciones"].update(opciones_columna)

    def mostrar_menu_compras_prompt(self):
        self.input_menu_compras.imprimir("Selecciona una opción",
                                         choices=["1", "2", "m"],
                                         show_choices=False)

        if self.input_menu_compras.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_menu_compras_prompt()

    def mostrar_abrir_detalles_prompt(self, lista_compras: list[Compra]):
        self.input_abrir_detalles.imprimir("Ingresa el índice de la compra a mostrar",
                                           choices=[str(compra.num) for compra in lista_compras],
                                           show_choices=False)

        if self.input_abrir_detalles.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_abrir_detalles_prompt(lista_compras)

    def mostrar_opciones_detalles_prompt(self):
        self.input_menu_detalles.imprimir("Selecciona una opción",
                                          choices=["1", "2", "3", "m"],
                                          show_choices=False)

        if self.input_menu_detalles.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_opciones_detalles_prompt()

    def mostrar_prompt_eliminar_compra_prompt(self):
        confirmacion = Prompt.ask("[bold red]¡Atención! estás a punto de eliminar esta compra, confirma para continuar[/bold red]",
                                  choices=["S","N"])

        if confirmacion == "S":
            return True

        return False

    def mostrar_opciones_editar_prompt(self):
        self.input_menu_editar_compra.imprimir("Selecciona una opción",
                                               choices=["1", "2", "3", "4", "5", "6","m"],
                                               show_choices=False)

        if self.input_menu_editar_compra.user_input is None:
            self.refrescar_pantalla()
            self.mostrar_opciones_editar_prompt()

    def mostrar_editar_fecha_creacion_prompt(self):
        info = Prompt.ask("[bold yellow]Ingresa la nueva fecha de creación de la compra en el siguiente formato[/bold yellow]: [[bold green]dd-mm-yyyy[/bold green]]")

        if len(info) > 0:
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar nueva fecha de creación[/bold yellow] "
                                      f"[italic white]{info}[/italic white]", choices=["S", "N"])
            if confirmacion == "S":
                return info
            else:
                return None
        else:
            self.refrescar_pantalla()
            self.mostrar_editar_fecha_creacion_prompt()

    def mostrar_editar_total_bruto_prompt(self):
        total = Prompt.ask("[bold yellow]Ingresa el nuevo total bruto[/bold yellow]")

        if len(total):
            confirmacion = Prompt.ask(f"[bold yellow]Confirmar nuevo total bruto de ${total}", choices=["S", "N"])

            if confirmacion == "S":
                return total

            return None
        else:
            self.refrescar_pantalla()
            self.mostrar_editar_total_bruto_prompt()

    def mostrar_editar_proveedor_prompt(self, opciones):
        opciones.append("0")

        prov = Prompt.ask(f"[bold yellow]Selecciona uno de los proveedores disponibles o ingresa 0 para crear un proveedor",
                          choices=opciones,
                          show_choices=False)

        if prov == "0":
            return prov

        confirmacion = Prompt.ask("[bold yellow]Confirmar cambio de proveedor[/bold yellow]", choices=["S", "N"])

        if confirmacion == "S":
            return prov

        return None

    def mostrar_crear_proveedor_prompt(self):
        proveedor = ""

        while len(proveedor) == 0:
            self.refrescar_pantalla()
            proveedor = Prompt.ask("[bold yellow]Ingresa el nombre del nuevo proveedor[/bold yellow]")

        confirmacion = Prompt.ask(
            f"[bold yellow]Confirma el nombre del nuevo proveedor: [bold red]{proveedor}[/bold red][/bold yellow]",
            choices=["S", "N"])

        if confirmacion == "S":
            return proveedor
        return None

    def mostrar_editar_insumos_menu_prompt(self):
        self.input_menu_editar_insumo.imprimir("Selecciona una opción",
                                               choices=["1","2","3","4","5","6"], show_choices=False)

    def mostrar_seleccionar_insumo_prompt(self, opciones):
        opciones.append("0")

        num_insumo = Prompt.ask("[bold yellow]Selecciona uno de los insumos de la lista o ingresa 0 para crear uno[/bold yellow]",
                                choices=opciones,
                                show_choices=False)

        if num_insumo == "0":
            return num_insumo

        if len(num_insumo):
            confirmacion = Prompt.ask("[bold yellow]Confirmar agregar insumo[/bold yellow]",
                                      choices=["S","N"])

            if confirmacion == "S":
                return num_insumo
            else:
                return None
        else:
            self.refrescar_pantalla()
            self.mostrar_seleccionar_insumo_prompt(opciones)

    def mostrar_agregar_insumo_prompt(self):
        monto_unitario = ""
        importe = ""
        fecha_compra = ""
        fecha_caducidad = ""
        cantidad = ""
        unidad_medida = ""

        while len(fecha_compra) == 0:
            self.refrescar_pantalla()
            fecha_compra = Prompt.ask("[bold yellow]Ingresa la fecha de compra del insumo en el siguiente formato: [[bold green]dd-mm-yyyy[/bold green]][/bold yellow]")

            if len(fecha_compra):
                confirmacion = Prompt.ask(
                    f"[bold yellow]Confirma fecha de compra: [bold red]{fecha_compra}[/bold red][/bold yellow]", choices=["S", "N"])

                if confirmacion == "S":
                    break
                else:
                    fecha_compra = ""

        while len(cantidad) == 0:
            self.refrescar_pantalla()
            cantidad = Prompt.ask("[bold yellow]Ingresa la cantidad comprada del insumo[/bold yellow]")

            if len(cantidad):
                confirmacion = Prompt.ask(
                    f"[bold yellow]Confirma cantidad: [bold red]{cantidad}[/bold red][/bold yellow]", choices=["S", "N"])

                if confirmacion == "S":
                    break
                else:
                    cantidad = ""

        while len(unidad_medida) == 0:
            self.refrescar_pantalla()
            unidad_medida = Prompt.ask("[bold yellow]Ingresa la unidad de medida para la cantidad del insumo[/bold yellow]")

            if len(unidad_medida):
                confirmacion = Prompt.ask(
                    f"[bold yellow]Confirma cantidad: [bold red]{unidad_medida}[/bold red][/bold yellow]", choices=["S", "N"])

                if confirmacion == "S":
                    break
                else:
                    unidad_medida = ""

        while len(monto_unitario) == 0:
            self.refrescar_pantalla()
            monto_unitario = Prompt.ask("[bold yellow]Ingresa el monto unitario del insumo[/bold yellow]")

            if len(monto_unitario):
                confirmacion = Prompt.ask(f"[bold yellow]Confirma monto unitario: [bold red]{monto_unitario}[/bold red][/bold yellow]", choices=["S", "N"])

                if confirmacion == "S":
                    break
                else:
                    monto_unitario = ""

        # while len(importe) == 0:
        #     self.refrescar_pantalla()
        #     importe = Prompt.ask("[bold yellow]Ingresa el importe total del insumo[/bold yellow]")
        #
        #     if len(monto_unitario):
        #         confirmacion = Prompt.ask(
        #             f"[bold yellow]Confirma importe: [bold red]{importe}[/bold red][/bold yellow]", choices=["S", "N"])
        #
        #         if confirmacion == "S":
        #             break
        #         else:
        #             importe = ""

        while len(fecha_caducidad) == 0:
            self.refrescar_pantalla()
            fecha_caducidad = Prompt.ask("[bold yellow]Ingresa la fecha de caducidad del insumo en el siguiente formato: [[bold green]dd-mm-yyyy[/bold green]][/bold yellow]")

            if len(fecha_caducidad):
                confirmacion = Prompt.ask(
                    f"[bold yellow]Confirma fecha de caducidad: [bold red]{fecha_caducidad}[/bold red][/bold yellow]", choices=["S", "N"])

                if confirmacion == "S":
                    break
                else:
                    fecha_caducidad = ""

        return monto_unitario, fecha_compra, fecha_caducidad, cantidad, unidad_medida

    def mostrar_crear_insumo_prompt(self):
        nombre = ""
        umbral = ""

        while len(nombre) == 0:
            self.refrescar_pantalla()
            nombre = Prompt.ask("[bold yellow]Ingresa el nombre del nuevo insumo. Utiliza un nombre genérico[/bold yellow]")
            if len(nombre) > 0:
                confirmacion = Prompt.ask(f"[bold yellow]Confirmar nombre del insumo: [bold red]{nombre}[/bold red]", choices=["S", "N"])

                if confirmacion == "S":
                    break
                else:
                    nombre = ""

        while len(umbral) == 0:
            self.refrescar_pantalla()
            umbral = Prompt.ask("[bold yellow]Ingresa el umbral (sin unidad de medida) para este insumo[/bold yellow]")

            if len(umbral) > 0:
                confirmacion = Prompt.ask(f"[bold yellow]Confirmar umbral del insumo: [bold red]{umbral} unidades[/bold red][/bold yellow]", choices=["S", "N"])

                if confirmacion == "S":
                    break
                else:
                    umbral = ""

        return nombre, umbral

    def mostrar_seleccionar_marca_prompt(self, opciones):
        opciones.append("0")

        marca_num = Prompt.ask("[bold yellow]Selecciona la marca de entre las opciones disponibles o presiona 0 para registrar una nueva",
                               choices=opciones,
                               show_choices=False)

        confirmacion = Prompt.ask(f"[bold yellow]Confirmar selección de marca[/bold yellow]", choices=["S", "N"])

        if confirmacion == "S":
            return marca_num
        return None

    def mostrar_crear_marca_prompt(self):
        marca_nom = ""

        while len(marca_nom) == 0:
            self.refrescar_pantalla()
            marca_nom = Prompt.ask("[bold yellow]Ingresa el nombre de la nueva marca[/bold yellow]")

        confirmacion = Prompt.ask(f"[bold yellow]Confirmar nombre de la nueva marca: [bold red]{marca_nom}[/bold red][/bold yellow]", choices=["S", "N"])

        if confirmacion == "S":
            return marca_nom
        return None

    def mostrar_seleccionar_tipo_insumo_prompt(self, opciones):
        opciones.append("0")

        tipo_ins = Prompt.ask("[bold yellow]Selecciona el tipo de insumo de entre las opciones o presiona 0 para crear un nuevo tipo[/bold yellow]",
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

        confirmacion = Prompt.ask(f"[bold yellow]Confirmar crear nuevo tipo de insumo: [bold red]{tipo_nombre}[/bold red][/bold yellow]", choices=["S", "N"])

        if confirmacion == "S":
            return tipo_nombre
        return None

    def mostrar_editar_insumo_prompt(self, opciones):
        if len(opciones) == 0:
            rich.print("[bold green]La compra actual no tiene insumos que editar, volviendo al menú anterior...[/bold green]")
            time.sleep(5)

            return None, None

        num_insumo = Prompt.ask("[bold yellow]Selecciona el insumo a modificar[/bold yellow]",
                               choices=opciones,
                               show_choices=False)

        if len(num_insumo):
            return num_insumo
        else:
            self.refrescar_pantalla()
            self.mostrar_editar_insumo_prompt(opciones)

    def mostrar_remover_insumo_prompt(self, opciones):
        if len(opciones) == 0:
            rich.print("[bold green]La compra actual no tiene insumos que remover, volviendo al menú anterior...[/bold green]")
            time.sleep(5)
            return None

        num_insumo = Prompt.ask("[bold yellow]Ingresa el número del insumo a remover[/bold yellow]", choices=opciones, show_choices=False)
        confirmacion = Prompt.ask(f"[bold yellow]Confirmar borrar insumo [bold red]#{num_insumo}[/bold red][/bold yellow]", choices=["S", "N"])

        if confirmacion == "S":
            return num_insumo

        return None

    def mostrar_editar_cantidad_insumo_prompt(self, opciones):
        if len(opciones) == 0:
            rich.print("[bold green]La compra actual no tiene insumos que editar, volviendo al menú anterior...[/bold green]")
            time.sleep(5)
            return None, None

        cantidad = ""

        num_ins = Prompt.ask("[bold yellow]Ingresa el índice del insumo a editar[/bold yellow]",
                                 choices=opciones,
                                 show_choices=False)

        while len(cantidad) == 0:
            self.refrescar_pantalla()
            cantidad = Prompt.ask("[bold yellow]Ingresa la nueva cantidad para este insumo[/bold yellow]")

            if len(cantidad):
                confirmacion = Prompt.ask(f"[bold yellow]Confirma la nueva cantidad: [bold red]{cantidad}[/bold red][/bold yellow]", choices=["S", "N"])

                if confirmacion == "S":
                    return num_ins, cantidad
                else:
                    return None, None

    def mostrar_editar_unidad_medida_prompt(self, opciones):
        if len(opciones) == 0:
            rich.print("[bold green]La compra actual no tiene insumos que editar, volviendo al menú anterior...[/bold green]")
            time.sleep(5)
            return None, None

        unidad_m = ""

        num_ins = Prompt.ask("[bold yellow]Ingresa el índice del insumo a editar[/bold yellow]",
                                 choices=opciones,
                                 show_choices=False)

        while len(unidad_m) == 0:
            self.refrescar_pantalla()
            unidad_m = Prompt.ask("[bold yellow]Ingresa la nueva unidad de medida para este insumo[/bold yellow]")

            if len(unidad_m):
                confirmacion = Prompt.ask(f"[bold yellow]Confirma la nueva unidad de medida: [bold red]{unidad_m}[/bold red][/bold yellow]", choices=["S", "N"])

                if confirmacion == "S":
                    return num_ins, unidad_m
                else:
                    return None, None

    def mostrar_editar_monto_unitario_prompt(self, opciones):
        if len(opciones) == 0:
            rich.print("[bold green]La compra actual no tiene insumos que editar, volviendo al menú anterior...[/bold green]")
            time.sleep(5)
            return None, None

        monto = ""

        num_ins = Prompt.ask("[bold yellow]Ingresa el índice del insumo a editar[/bold yellow]",
                             choices=opciones,
                             show_choices=False)

        while len(monto) == 0:
            self.refrescar_pantalla()
            monto = Prompt.ask("[bold yellow]Ingresa el nuevo monto unitario[/bold yellow]")

            if len(monto):
                confirmacion = Prompt.ask(f"[bold yellow]Confirma el nuevo monto: [bold red]{monto}[/bold red][/bold yellow]", choices=["S", "N"])

                if confirmacion == "S":
                    return num_ins, monto
                else:
                    return None, None

    def mostrar_editar_fecha_compra_prompt(self, opciones):
        if len(opciones) == 0:
            rich.print("[bold green]La compra actual no tiene insumos que editar, volviendo al menú anterior...[/bold green]")
            time.sleep(5)
            return None, None

        fecha = ""

        num_ins = Prompt.ask("[bold yellow]Ingresa el índice del insumo a editar[/bold yellow]",
                             choices=opciones,
                             show_choices=False)

        while len(fecha) == 0:
            self.refrescar_pantalla()
            fecha = Prompt.ask("[bold yellow]Ingresa la nueva fecha de compra para este insumo en el siguiente formato: [[bold green]dd-mm-yyyy[/bold green]][/bold yellow][/bold yellow]")

            if len(fecha):
                confirmacion = Prompt.ask(f"[bold yellow]Confirma la fecha de compra: [bold red]{fecha}[/bold red][/bold yellow]", choices=["S", "N"])

                if confirmacion == "S":
                    return num_ins, fecha
                else:
                    return None, None

    def mostrar_editar_fecha_caducidad_prompt(self, opciones):
        if len(opciones) == 0:
            rich.print("[bold green]La compra actual no tiene insumos que editar, volviendo al menú anterior...[/bold green]")
            time.sleep(5)
            return None, None

        fecha = ""

        num_ins = Prompt.ask("[bold yellow]Ingresa el índice del insumo a editar[/bold yellow]",
                             choices=opciones,
                             show_choices=False)

        while len(fecha) == 0:
            self.refrescar_pantalla()
            fecha = Prompt.ask("[bold yellow]Ingresa la nueva fecha de compra para este insumo en el siguiente formato: [[bold green]dd-mm-yyyy[/bold green]][/bold yellow][/bold yellow]")

            if len(fecha):
                confirmacion = Prompt.ask(f"[bold yellow]Confirma la fecha de compra: [bold red]{fecha}[/bold red][/bold yellow]", choices=["S", "N"])

                if confirmacion == "S":
                    return num_ins, fecha
                else:
                    return None, None

    def mostrar_prompt_registrar_compra(self):
        proveedor = Prompt.ask("Para comenzar, ingresa el índice del proveedor de la compra o 0 para registrar uno nuevo")

        if len(proveedor) == 0:
            return proveedor

        return proveedor

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
