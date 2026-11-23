import copy
import datetime
import math
import time

from Validaciones.validadorVentas import ValidadorVentas
from models.categoria import Categoria
from models.ingrediente import Ingrediente
from models.insumo import Insumo
from models.platillo import Platillo
from models.receta import Receta
from models.venta import Venta, Consumo
from services.platillos_servicio import PlatillosServicio
from services.venta_servicio import VentaServicio
from views.VistaVentas import VistaVentas


class ControladorVentas:
    def __init__(self, vista:VistaVentas, servicio:VentaServicio, validador:ValidadorVentas):
        self.vista = vista
        self.servicio = servicio
        self.validador = validador
        self.venta_actual = None
        self.formulario = {"consumo":[], "item_borrado":False}
        self.consumo_idx = {}

        self.pagina_actual_lista_ventas = 1
        self.pagina_actual_lista_detalles = 1
        self.pagina_actual_lista_platillos_disp = 1
        self.pagina_actual_platillos_conflicto = 1

        self.platillos_conflicto = None

        self.ventas_a_mostrar = None

        self.configurar_listeners()
        self.mostrar_lista_ventas()

    def configurar_listeners(self):
        self.vista.input_menu_ventas.agregar_escuchante(self.evaluar_seleccion_menu_ventas)
        self.vista.input_abrir_detalles.agregar_escuchante(self.mostrar_detalles_venta)
        self.vista.input_menu_detalles.agregar_escuchante(self.evaluar_seleccion_menu_detalles)
        self.vista.input_menu_editar.agregar_escuchante(self.evaluar_seleccion_menu_editar)
        self.vista.input_menu_editar_consumo.agregar_escuchante(self.evaluar_seleccion_menu_editar_consumo)
        self.vista.input_menu_filtros.agregar_escuchante(self.evaluar_seleccion_busqueda_av)

        # Para cambiar página
        self.vista.input_menu_ventas.agregar_escuchante(self.cambiar_pagina_lista_ventas)
        self.vista.input_menu_detalles.agregar_escuchante(self.cambiar_pagina_lista_detalles)
        self.vista.input_menu_editar.agregar_escuchante(self.cambiar_pagina_lista_detalles)
        self.vista.input_menu_editar_consumo.agregar_escuchante(self.cambiar_pagina_lista_detalles)
        self.vista.input_seleccion_platillo.agregar_escuchante(self.cambiar_pagina_lista_platillos_disp)
        self.vista.input_platillos_conflicto.agregar_escuchante(self.cambiar_pagina_lista_platillos_conflicto)

    def mostrar_lista_ventas(self,  lista_ventas=None):
        """
        Conecta con la capa de servicios para obtener la lista de ventas y crea un elemento de lista para cada una.
        """

        if self.ventas_a_mostrar is None:
            self.ventas_a_mostrar = self.servicio.obtener_ventas()

        self.vista.mostrar_todas_ventas(self.pagina_actual_lista_ventas,
                                        self.obtener_total_paginas_lista_ventas(self.ventas_a_mostrar))

        if lista_ventas is None:
            lista_ventas, hay_prox_pag = self.paginar_lista_ventas(self.ventas_a_mostrar, self.pagina_actual_lista_ventas)

        if self.pagina_actual_lista_ventas == 1:
            idx_ui = 0
        else:
            consola_size = self.vista.console.size[1]
            size_sin_prompt = consola_size - 6
            lineas_disp = size_sin_prompt - 7

            idx_ui = (self.pagina_actual_lista_ventas - 1) * lineas_disp

        for compra in lista_ventas:
            idx_ui += 1
            self.vista.crear_elemento_tabla_ventas(compra, idx_ui)

        self.vista.refrescar_pantalla()
        self.vista.mostrar_menu_ventas_prompt()

    def mostrar_detalles_venta(self, venta_num=None):
        if venta_num is None and self.venta_actual is None:
            self.vista.mostrar_abrir_detalles_prompt(self.servicio.obtener_ventas())

        if self.venta_actual is None:
            self.venta_actual = self.ventas_a_mostrar[int(venta_num)-1]

        self.mapear_detalle_venta()

        pagina, prox_pag = self.paginar_lista_detalles(self.venta_actual.detalles,
                                                               self.pagina_actual_lista_detalles)
        total_paginas_detalles = self.obtener_total_paginas_detalles(self.venta_actual.detalles)

        # llama la función para crear la vista de detalles y le pasa los datos del formulario actual
        self.vista.mostrar_detalles_venta(self.venta_actual, pagina, self.pagina_actual_lista_detalles, total_paginas_detalles, copy.deepcopy(self.formulario), self.consumo_idx)

        if self.usuario_esta_editando():
            # si actualmente el formulario tiene info, muestra las opciones de edicion y su prompt
            self.vista.crear_banda_opciones_editar()
            self.vista.refrescar_pantalla()
            self.vista.mostrar_opciones_editar_prompt()
        else:
            # si no hay info en el formulario, entonces queremos que nos de las opciones normales
            self.vista.crear_banda_opciones_detalles()
            self.vista.refrescar_pantalla()
            self.vista.mostrar_opciones_detalles_prompt()

    def mostrar_formulario_crear_venta(self):
        if self.venta_actual is None:
            self.vista.mostrar_registrar_venta(None, self.consumo_idx)
        else:
            self.vista.mostrar_registrar_venta(self.venta_actual, self.consumo_idx)
            self.vista.crear_banda_opciones_editar()
            self.vista.refrescar_pantalla()
            self.vista.mostrar_opciones_editar_prompt()

        self.vista.refrescar_pantalla()

    def guardar_editar_venta(self):
        try:
            confirmacion_guardar = self.vista.mostrar_mensaje_advertencia_guardado()

            if confirmacion_guardar == "1":
                self.servicio.registrar_venta(self.venta_actual)

                self.cancelar_edicion_actual()
                self.venta_actual = self.servicio.obtener_ultima_venta()
                self.mostrar_detalles_venta()
            else:
                self.mostrar_detalles_venta()
        except ValueError:
            self.vista.mostrar_error_venta_stock_insuficiente()
            self.mostrar_detalles_venta()

    def cancelar_edicion_actual(self):
        # resetea formulario y platillo actual
        self.venta_actual = None
        self.formulario = {"consumo":[], "item_borrado":False}

    def usuario_esta_editando(self):
        # checa si el usuario ha hecho cambios desde que entró a la vista de detalles

        if len(self.formulario.items()) > 2 or len(self.formulario["consumo"]) or self.formulario["item_borrado"]:
            return True
        return False

    def agregar_edicion_consumo(self, detalle_venta):
        lista_plat_editados_nombre = [det.platillo.nombre for det in self.formulario["consumo"]]

        if detalle_venta.platillo.nombre in lista_plat_editados_nombre:
            # checa si un ingrediente ya fue editado antes y remueve esa edicion para agregar la nueva
            obj = [det for det in self.formulario["consumo"] if det.platillo.nombre == detalle_venta.platillo.nombre][0]
            self.formulario["consumo"].remove(obj)

        self.formulario["consumo"].append(detalle_venta)

    def mapear_detalle_venta(self):
        # toma los platillos del detalle de la venta, itera sobre cada uno
        # y les asigna un número para mostrar en la tabla de la vista
        if self.venta_actual:
            self.consumo_idx = {}
            lista_consumo = self.venta_actual.detalles

            for i in range(len(lista_consumo)):
                self.consumo_idx[i + 1] = lista_consumo[i]

    def actualizar_monto_total_venta(self):
        total_actual = 0

        for cons in self.venta_actual.detalles:
            total_actual += cons.importe

        if total_actual != self.venta_actual.monto_total:
            self.venta_actual.monto_total = total_actual
            self.formulario["monto_total"] = total_actual

    def evaluar_seleccion_menu_ventas(self, seleccion):
        match seleccion:
            case "1":
                # Aquí debería obtener la lista de todas las ventas y pasarla
                self.vista.mostrar_abrir_detalles_prompt(self.ventas_a_mostrar)
            case "2":
                # Aquí crea venta
                self.mostrar_formulario_crear_venta()
                fecha = self.vista.mostrar_prompt_crear_venta_fecha()

                if fecha:
                    resultado_val_fecha = self.validador.validar_formato_fecha(fecha)

                    while not resultado_val_fecha[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_fecha[1])
                        fecha = self.vista.mostrar_prompt_crear_venta_fecha()
                        resultado_val_fecha = self.validador.validar_formato_fecha(fecha)

                    fecha = resultado_val_fecha[1]

                    num_comensales = self.vista.mostrar_prompt_crear_venta_comensales()
                    resultado_val_comensales = self.validador.validar_num_comensales(num_comensales)

                    while not resultado_val_comensales[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_comensales[1])
                        num_comensales = self.vista.mostrar_prompt_crear_venta_comensales()
                        resultado_val_comensales = self.validador.validar_num_comensales(num_comensales)

                    num_comensales = resultado_val_comensales[1]

                    self.venta_actual = Venta(0, fecha, num_comensales, 0)
                    self.formulario["nueva_venta"] = copy.deepcopy(self.venta_actual)
                    self.mostrar_detalles_venta()
                else:
                    self.mostrar_lista_ventas()
            case "3":
                self.vista.crear_banda_opciones_busqueda_av()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_opciones_busqueda_av_prompt()

            case "m":
                # cancela la edicion actual antes de volver al menu
                self.cancelar_edicion_actual()

    def evaluar_seleccion_menu_detalles(self, seleccion):
        match seleccion:
            case "1":
                # volver a la vista de todas las ventas
                self.cancelar_edicion_actual()
                self.mostrar_lista_ventas()
            case "2":
                # abrir opciones de editar venta
                self.vista.crear_banda_opciones_editar()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_opciones_editar_prompt()
            case "3":
                # borrar = self.vista.mostrar_prompt_eliminar_venta_prompt()
                # if borrar:
                #     for venta in self.ventas_a_mostrar:
                #         if venta.num == self.venta_actual.num:
                #             self.platillos_testeo.remove(venta)
                #             break

                self.cancelar_edicion_actual()
                self.mostrar_lista_ventas()
            case "m":
                # volver al menú principal
                self.cancelar_edicion_actual()

    def evaluar_seleccion_busqueda_av(self, seleccion):
        match seleccion:
            case "1":
                # por rango de fecha
                fecha_inicial, fecha_final = self.vista.mostrar_buscar_por_rango_fecha_prompt()
                resultado_val_fecha = self.validador.validar_rango_fecha(fecha_inicial, fecha_final)

                while not resultado_val_fecha[0]:
                    self.vista.mostrar_mensaje_error_validacion(resultado_val_fecha[1])
                    fecha_inicial, fecha_final = self.vista.mostrar_buscar_por_rango_fecha_prompt()
                    resultado_val_fecha = self.validador.validar_rango_fecha(fecha_inicial, fecha_final)

                fecha_inicial, fecha_final = resultado_val_fecha[1][0], resultado_val_fecha[1][1]

                resultados_busqueda = self.servicio.obtener_ventas_por_rango_fecha(fecha_inicial, fecha_final)

                if resultados_busqueda and len(resultados_busqueda):
                    self.ventas_a_mostrar = resultados_busqueda
                else:
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_mensaje_no_resultados_busqueda_av()
                    self.vista.refrescar_pantalla()

                self.mostrar_lista_ventas()

            case "2":
                # restaurar búsqueda
                self.ventas_a_mostrar = self.servicio.obtener_ventas()
                self.mostrar_lista_ventas()

            case "3":
                # volver a lista de ventas
                self.mostrar_lista_ventas()


    def evaluar_seleccion_menu_editar(self, seleccion):
        match seleccion:
            case "1":
                # abre prompt para editar la fecha de venta
                fecha = self.vista.mostrar_editar_fecha_prompt()
                # checa que haya una respuesta del usuario y si es así lo debe validar
                if fecha is not None:
                    resultado_val_fecha = self.validador.validar_formato_fecha(fecha)

                    while not resultado_val_fecha[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_fecha[1])
                        fecha = self.vista.mostrar_editar_fecha_prompt()
                        resultado_val_fecha = self.validador.validar_formato_fecha(fecha)

                    fecha = resultado_val_fecha[1]

                    # valida los platillos actuales
                    if len(self.venta_actual.detalles):
                        platillos_conflicto = self.servicio.obtener_platillos_conflicto_fecha(self.venta_actual.detalles, fecha)

                        if len(platillos_conflicto):
                            pagina, prox_pag = self.paginar_lista_detalles(platillos_conflicto, self.pagina_actual_platillos_conflicto)
                            total_pag = self.obtener_total_paginas_detalles(platillos_conflicto)

                            self.vista.mostrar_platillos_conflicto(pagina, self.pagina_actual_platillos_conflicto, total_pag)
                            seleccion = self.vista.mostrar_mensaje_platillos_conflicto(fecha)

                            if seleccion == "S":
                                self.venta_actual.fecha = fecha
                                self.formulario["fecha"] = fecha

                                nombre_platillos_conflicto = [platillo.nombre for platillo in platillos_conflicto]
                                for consumo in self.venta_actual.detalles:
                                    # remueve los platillos en conflicto
                                    if consumo.platillo.nombre in nombre_platillos_conflicto:
                                        self.consumo_idx = {k: v for k, v in self.consumo_idx.items() if v != consumo}
                                        self.formulario["consumo"].remove(consumo)
                                        self.venta_actual.detalles.remove(consumo)

                        # finalmente actualiza el precio de los platillos que se van a quedar en la venta actual
                        for consumo in self.venta_actual.detalles:
                            precio = self.servicio.obtener_precio_venta_platillo(fecha, consumo.platillo.num)
                            consumo.importe = precio * consumo.cantidad_platillos

                        # actualiza el monto total
                        self.actualizar_monto_total_venta()

                    else:
                        self.venta_actual.fecha = fecha
                        self.formulario["fecha"] = fecha

                self.pagina_actual_platillos_conflicto = 1
                self.mostrar_detalles_venta()

            case "2":
                # abre prompt para editar el num de comensales
                num_comensales = self.vista.mostrar_editar_comensales_prompt()

                # checa que haya un valor y luego valída y asigna
                if num_comensales:
                    resultado_val_comensales = self.validador.validar_num_comensales(num_comensales)

                    while not resultado_val_comensales[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_comensales[1])
                        num_comensales = self.vista.mostrar_prompt_crear_venta_comensales()
                        resultado_val_comensales = self.validador.validar_num_comensales(num_comensales)

                    num_comensales = resultado_val_comensales[1]
                    self.formulario["comensales"] = num_comensales

                self.mostrar_detalles_venta()

            case "3":
                # abre opciones para editar consumo
                self.vista.crear_banda_opciones_editar_consumo()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_opciones_editar_consumo_prompt()
            case "4":
                # llama a la función para guardar
                self.guardar_editar_venta()

            case "5":
                # cancela la edición actual y vuelve a detalles
                if self.venta_actual.num in [venta.num for venta in self.ventas_a_mostrar]:
                    self.cancelar_edicion_actual()
                    self.mostrar_detalles_venta(self.vista.input_abrir_detalles.user_input)
                else:
                    self.cancelar_edicion_actual()
                    self.mostrar_lista_ventas()
            case "m":
                # vuelve al menú
                self.cancelar_edicion_actual()

    def evaluar_seleccion_menu_editar_consumo(self, seleccion):
        match seleccion:
            case "1":
                # Aquí debería hacer muchas cosas más que omitiré porque igual se tendrá que hacer
                # con un servicio después y de momento no me afecta en la vista
                # En primer lugar, los platillos candidatos a ser agregados deben ser aquellos
                # que pertenecen a un menú activo al día de la compra únicamente (no el día en que se crea
                # el registro sino el que el usuario escoge como fecha de compra al momento de registrarla),
                # luego de esa lista de platillos activos, se quitan aquellos que ya están en la venta agregados
                # (es decir los duplicados, este paso si lo simulo aquí), esa lista de platillos resultante es
                # de donde se saca la lista de opciones y la que se pasa a la vista para mostrar.
                # Además, al momento de agregar el platillo como consumo a la venta, debe jalar el precio
                # de acuerdo al menú vigente el día de la compra, multiplicarlo por la cantidad y eso es lo
                # que pasa como argumento en la función de "agregar_consumo", aquí tengo hardcoded un 200
                # como testeo nomás
                lista_platillos = self.servicio.obtener_platillos_disponibles_por_fecha(self.venta_actual.fecha)

                if lista_platillos is None or len(lista_platillos) == 0:
                    self.vista.mostrar_mensaje_no_platillos_disp()
                else:
                    lista_platillos_actuales = [pl.platillo.nombre for pl in self.venta_actual.detalles]
                    idx_plat_disp = {i + 1: lista_platillos[i] for i in range(len(lista_platillos)) if
                                     lista_platillos[i].nombre not in lista_platillos_actuales}

                    opciones = [str(i) for i in idx_plat_disp]
                    lista_plat_disp = [idx_plat_disp[idx] for idx in idx_plat_disp]

                    pagina, prox_pag = self.paginar_lista_detalles(lista_plat_disp, self.pagina_actual_lista_platillos_disp)
                    total_pag = self.obtener_total_paginas_detalles(lista_plat_disp)

                    self.vista.mostrar_platillos_disponibles(pagina, self.pagina_actual_lista_platillos_disp, total_pag)

                    num_platillo = self.vista.mostrar_agregar_consumo_plat_prompt(opciones)

                    if num_platillo:
                        cantidad = self.vista.mostrar_agregar_consumo_cantidad_prompt()
                        resultados_val_cantidad = self.validador.validar_cantidad_consumo(cantidad)

                        while not resultados_val_cantidad[0]:
                            self.vista.mostrar_mensaje_error_validacion(resultados_val_cantidad[1])
                            cantidad = self.vista.mostrar_agregar_consumo_cantidad_prompt()
                            resultados_val_cantidad = self.validador.validar_cantidad_consumo(cantidad)

                        cantidad = resultados_val_cantidad[1]

                        platillo = idx_plat_disp[int(num_platillo)]

                        precio_platillo = self.servicio.obtener_precio_venta_platillo(self.venta_actual.fecha, platillo.num)
                        importe = precio_platillo*cantidad

                        self.venta_actual.agregar_consumo((copy.deepcopy(platillo)), importe, cantidad)
                        self.agregar_edicion_consumo((self.venta_actual.detalles[-1]))
                        self.actualizar_monto_total_venta()

                self.pagina_actual_lista_platillos_disp = 1
                self.mostrar_detalles_venta()
            case "2":
                # editar cantidad
                opciones = [str(idx) for idx in self.consumo_idx]
                num = self.vista.mostrar_editar_consumo_seleccion_plat(opciones)

                if num:
                    cantidad = self.vista.mostrar_agregar_consumo_cantidad_prompt()
                    resultado_val_cantidad = self.validador.validar_cantidad_consumo(cantidad)

                    while not resultado_val_cantidad[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_cantidad[1])
                        cantidad = self.vista.mostrar_agregar_consumo_cantidad_prompt()
                        resultado_val_cantidad = self.validador.validar_cantidad_consumo(cantidad)

                    cantidad = resultado_val_cantidad[1]

                    nombre = self.consumo_idx[int(num)].platillo.nombre

                    for cons in self.venta_actual.detalles:
                        if cons.platillo.nombre == nombre:
                            # Aquí edito la cantidad y actualizo el importe haciendo la multiplicación de
                            # cantidad * precio del platillo. Como no tengo de donde jalar el precio
                            # porque no tengo menú aquí, hice un paso extra con la variable precio_platillo donde
                            # calculo cuál es el precio antes de cambiar la cantidad con una división y luego uso ese
                            # precio para calcular el nuevo importe con la nueva cantidad. Esto se hará con una
                            # función después de todos modos

                            precio_platillo = cons.importe / cons.cantidad_platillos
                            cons.cantidad_platillos = cantidad
                            cons.importe = cons.cantidad_platillos * precio_platillo
                            self.actualizar_monto_total_venta()
                            self.agregar_edicion_consumo(cons)

                self.mostrar_detalles_venta()

            case "3":
                # eliminar consumo
                opciones = [str(idx) for idx in self.consumo_idx]
                num = self.vista.mostrar_remover_consumo_prompt(opciones)

                nombre = self.consumo_idx[int(num)]

                for cons in self.venta_actual.detalles:
                    if cons.platillo.nombre == nombre:
                        self.venta_actual.monto_total -= cons.importe
                        self.venta_actual.cantidad_platillos -= 1

                        self.consumo_idx = {k: v for k, v in self.consumo_idx.items() if v != cons}
                        self.formulario["consumo"].remove(cons)
                        self.venta_actual.remove(cons)
                        self.formulario["item_borrado"] = True
                        self.actualizar_monto_total_venta()

                self.mostrar_detalles_venta()

            case "4":
                # volver a la vista anterior
                self.vista.crear_banda_opciones_editar()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_opciones_editar_prompt()

    def cambiar_pagina_lista_ventas(self, mov):
        if mov == ",":
            if self.pagina_actual_lista_ventas == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
                self.mostrar_lista_ventas()
            else:
                self.pagina_actual_lista_ventas -= 1
                pagina, hay_sig_pag = self.paginar_lista_ventas(self.ventas_a_mostrar, self.pagina_actual_lista_ventas)
                self.mostrar_lista_ventas(pagina)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_ventas(self.ventas_a_mostrar, self.pagina_actual_lista_ventas)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
                self.mostrar_lista_ventas()
            else:
                self.pagina_actual_lista_ventas += 1
                pagina, hay_sig_pag = self.paginar_lista_ventas(self.ventas_a_mostrar, self.pagina_actual_lista_ventas)
                self.mostrar_lista_ventas(pagina)

    def cambiar_pagina_lista_platillos_disp(self, mov):
        lista_platillos = self.servicio.obtener_platillos_disponibles_por_fecha(self.venta_actual.fecha)

        lista_platillos_actuales = [pl.platillo.nombre for pl in self.venta_actual.detalles]
        idx_plat_disp = {i + 1: lista_platillos[i] for i in range(len(lista_platillos)) if
                         lista_platillos[i].nombre not in lista_platillos_actuales}

        lista_plat_disp = [idx_plat_disp[idx] for idx in idx_plat_disp]

        if mov == ",":
            if self.pagina_actual_lista_platillos_disp == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
            else:
                self.pagina_actual_lista_platillos_disp -= 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(lista_plat_disp, self.pagina_actual_lista_platillos_disp)
                total_pag = self.obtener_total_paginas_detalles(lista_plat_disp)
                self.vista.mostrar_platillos_disponibles(pagina, self.pagina_actual_lista_platillos_disp, total_pag)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_detalles(lista_plat_disp, self.pagina_actual_lista_platillos_disp)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
            else:
                self.pagina_actual_lista_platillos_disp += 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(lista_plat_disp, self.pagina_actual_lista_platillos_disp)
                total_pag = self.obtener_total_paginas_detalles(lista_plat_disp)
                self.vista.mostrar_platillos_disponibles(pagina, self.pagina_actual_lista_platillos_disp, total_pag)

    def cambiar_pagina_lista_platillos_conflicto(self, mov):
        if mov == ",":
            if self.pagina_actual_platillos_conflicto == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
            else:
                self.pagina_actual_platillos_conflicto -= 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(self.platillos_conflicto, self.pagina_actual_platillos_conflicto)
                total_pag = self.obtener_total_paginas_detalles(self.platillos_conflicto)
                self.vista.mostrar_platillos_disponibles(pagina, self.pagina_actual_platillos_conflicto, total_pag)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_detalles(self.platillos_conflicto, self.pagina_actual_platillos_conflicto)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
            else:
                self.pagina_actual_platillos_conflicto += 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(self.platillos_conflicto, self.pagina_actual_platillos_conflicto)
                total_pag = self.obtener_total_paginas_detalles(self.platillos_conflicto)
                self.vista.mostrar_platillos_disponibles(pagina, self.pagina_actual_platillos_conflicto, total_pag)

    def paginar_lista_ventas(self, items: list, num_pag: int):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 7

        idx_inicio = (num_pag - 1) * lineas_disp
        idx_final = idx_inicio + lineas_disp

        if idx_final < len(items):
            prox_pag = True
        else:
            prox_pag = False

        return items[idx_inicio:idx_final], prox_pag

    def cambiar_pagina_lista_detalles(self, mov):
        if mov == ",":
            if self.pagina_actual_lista_detalles == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
                self.mostrar_detalles_venta()
            else:
                self.pagina_actual_lista_detalles -= 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(self.venta_actual.detalles,
                                                               self.pagina_actual_lista_detalles)
                self.mostrar_detalles_venta(pagina)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_detalles(self.venta_actual.detalles, self.pagina_actual_lista_detalles)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
                self.mostrar_detalles_venta()
            else:
                self.pagina_actual_lista_detalles += 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(self.venta_actual.detalles,
                                                               self.pagina_actual_lista_detalles)
                self.mostrar_detalles_venta(pagina)

    def paginar_lista_detalles(self, items: list, num_pag: int):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 9

        idx_inicio = (num_pag - 1) * lineas_disp
        idx_final = idx_inicio + lineas_disp

        if idx_final < len(items):
            prox_pag = True
        else:
            prox_pag = False

        return items[idx_inicio:idx_final], prox_pag

    def obtener_total_paginas_lista_ventas(self, items: list):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 7

        if len(items) == 0:
            return 1

        return math.ceil(len(items) / lineas_disp)

    def obtener_total_paginas_detalles(self, items: list):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 9

        if len(items) == 0:
            return 1

        return math.ceil(len(items) / lineas_disp)