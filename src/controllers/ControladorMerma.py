import math
import time

from Validaciones.validadorMerma import validadorMerma
from models.insumo import Insumo
from models.merma import Merma
from services.inventario_servicio import InventarioServicio
from services.merma_servicio import MermaServicio
from services.platillos_servicio import PlatillosServicio
from views.VistaMerma import VistaMerma


class ControladorMerma:
    def __init__(self, vista:VistaMerma, servicio_merma:MermaServicio, servicio_platillo:PlatillosServicio, servicio_insumo:InventarioServicio, validador:validadorMerma):
        self.vista = vista
        self.servicio_merma = servicio_merma
        self.servicio_platillo = servicio_platillo
        self.servicio_inventario = servicio_insumo
        self.validador = validador
        self.merma_actual = None
        self.formulario = {}

        self.mermas_a_mostrar = None

        self.pagina_actual_lista_mermas = 1
        self.pagina_actual_lista_insumos = 1
        self.pagina_actual_tipos_merma = 1
        self.pagina_actual_lista_platillos = 1

        self.configurar_listeners()
        self.mostrar_lista_mermas()

    def configurar_listeners(self):
        self.vista.input_menu_merma.agregar_escuchante(self.evaluar_seleccion_menu_merma)
        self.vista.input_abrir_detalles.agregar_escuchante(self.mostrar_detalles_merma)
        self.vista.input_menu_detalles.agregar_escuchante(self.evaluar_seleccion_menu_detalles)
        self.vista.input_menu_editar_merma.agregar_escuchante(self.evaluar_seleccion_menu_editar)
        self.vista.input_menu_filtros.agregar_escuchante(self.evaluar_seleccion_busqueda_av)

        # Para cambiar página
        self.vista.input_menu_merma.agregar_escuchante(self.cambiar_pagina_lista_compras)
        self.vista.input_seleccion_insumos.agregar_escuchante(self.cambiar_pagina_lista_insumos)
        self.vista.input_seleccion_tipo_merma.agregar_escuchante(self.cambiar_pagina_lista_tipos_merma)
        self.vista.input_seleccion_platillo.agregar_escuchante(self.cambiar_pagina_lista_platillos)

    def mostrar_lista_mermas(self, lista_mermas=None):
        """
        Conecta con la capa de servicios para obtener la lista de platillos y crea un elemento de lista para cada una.
        """

        if self.mermas_a_mostrar is None:
            self.mermas_a_mostrar = self.servicio_merma.obtener_mermas()

        self.vista.mostrar_toda_merma(self.pagina_actual_lista_mermas,
                                      self.obtener_total_paginas(self.mermas_a_mostrar))

        if lista_mermas is None:
            lista_mermas, hay_prox_pag = self.paginar_lista_merma(self.mermas_a_mostrar,
                                                                  self.pagina_actual_lista_mermas)

        if self.pagina_actual_lista_mermas == 1:
            idx_ui = 0
        else:
            consola_size = self.vista.console.size[1]
            size_sin_prompt = consola_size - 6
            lineas_disp = size_sin_prompt - 10  # mismo valor que paginar_lista_merma()

            idx_ui = (self.pagina_actual_lista_mermas - 1) * lineas_disp

        for compra in lista_mermas:
            idx_ui += 1
            self.vista.crear_elemento_tabla_merma(compra, idx_ui)

        self.vista.refrescar_pantalla()
        self.vista.mostrar_menu_merma_prompt()

    def mostrar_detalles_merma(self, merma_num=None):
        if merma_num is None and self.merma_actual is None:
            self.vista.mostrar_abrir_detalles_prompt(self.mermas_a_mostrar)

        if self.merma_actual is None:
            # Si no tenemos una merma actual, busca la merma por el num pasado como arg
            # idealmente con un servicio pero por ahora uso un loop para testeo
            self.merma_actual = self.servicio_merma.obtener_merma_por_numero(int(merma_num))

        # llama la función para crear la vista de detalles y le pasa los datos del formulario actual
        self.vista.mostrar_detalles_merma(self.merma_actual, datos_editados=self.formulario)

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

    def mostrar_formulario_registrar_merma(self):
        if self.merma_actual is None:
            self.vista.mostrar_registrar_merma(None)
        else:
            self.vista.mostrar_registrar_merma(self.merma_actual)
            self.vista.crear_banda_opciones_editar()
            self.vista.refrescar_pantalla()
            self.vista.mostrar_opciones_editar_prompt()

        self.vista.refrescar_pantalla()

    def guardar_editar_merma(self):
        # Cambia los datos del formulario en el objeto actual
        # para testeo, aquí debería llamar a un servicio
        if "platillo_merma" in self.formulario.keys():
            try:
                self.servicio_merma.registrar_merma_desde_platillo(self.merma_actual, self.formulario["platillo_merma"])
            except ValueError as err:
                self.vista.mostrar_mensaje_error_validacion(str(err))
                self.mostrar_detalles_merma()
        else:
            try:
                self.servicio_merma.registrar_merma(self.merma_actual)
            except ValueError as err:
                self.vista.mostrar_mensaje_error_validacion(str(err))
                self.mostrar_detalles_merma()
            
        self.cancelar_edicion_actual()
        self.mostrar_lista_mermas()

    def cancelar_edicion_actual(self):
        # resetea formulario y platillo actual
        self.pagina_actual_lista_mermas = 1
        self.pagina_actual_lista_insumos = 1
        self.pagina_actual_tipos_merma = 1

        self.merma_actual = None
        self.mermas_a_mostrar = None
        self.formulario = {}

    def usuario_esta_editando(self):
        # checa si el usuario ha hecho cambios desde que entró a la vista de detalles
        if len(self.formulario.items()) > 0:
            return True
        return False

    def evaluar_seleccion_menu_merma(self, seleccion):
        match seleccion:
            case "1":
                # Aquí debería obtener la lista de todos los platillos y pasarla
                self.vista.mostrar_abrir_detalles_prompt(self.mermas_a_mostrar)
            case "2":
                # Aquí registra merma
                self.mostrar_formulario_registrar_merma()
                self.vista.refrescar_pantalla()

                fecha = self.vista.mostrar_crear_fecha_prompt()

                if fecha and fecha != "0":
                    resultado_val_fecha = self.validador.validar_formato_fecha(fecha)

                    while not resultado_val_fecha[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_fecha[1])
                        fecha = self.vista.mostrar_crear_fecha_prompt()
                        if not fecha or fecha == "0":
                            self.mostrar_lista_mermas()
                        resultado_val_fecha = self.validador.validar_formato_fecha(fecha)

                    fecha = resultado_val_fecha[1]

                    fuente_merma = self.vista.mostrar_prompt_fuente_merma()

                    if fuente_merma == "1":
                        # merma de platillo
                        lista_platillos = self.servicio_platillo.obtener_platillos()
                        opciones_plat = [str(idx+1) for idx in range(len(lista_platillos))]

                        pagina, prox_pag = self.paginar_lista_detalles(lista_platillos, self.pagina_actual_lista_platillos)
                        total_pag = self.obtener_total_paginas_detalles(lista_platillos)

                        self.vista.mostrar_platillos_disponibles(pagina, self.pagina_actual_lista_platillos, total_pag)
                        num_plat = self.vista.mostrar_prompt_registrar_platillo_merma(opciones_plat)

                        platillo_merma = lista_platillos[int(num_plat)-1]
                        # placeholder vacío para poder hacer el obj merma
                        insumo_merma = Insumo(0, "insumo")
                        self.formulario["platillo_merma"] = platillo_merma

                    elif fuente_merma == "2":
                        # merma de insumo directamente
                        lista_insumos = self.servicio_inventario.obtener_insumos()
                        opciones_ins = [str(idx+1) for idx in range(len(lista_insumos))]

                        pagina, prox_pag = self.paginar_lista_detalles(lista_insumos, self.pagina_actual_lista_insumos)
                        total_pag = self.obtener_total_paginas_detalles(lista_insumos)

                        self.vista.mostrar_insumos_disponibles(pagina, self.pagina_actual_lista_insumos, total_pag)

                        num_ins = self.vista.mostrar_prompt_registrar_insumo_merma(opciones_ins)
                        insumo_merma = lista_insumos[int(num_ins) - 1]

                    cantidad = self.vista.mostrar_crear_cantidad_prompt()
                    resultado_val_cantidad = self.validador.validar_cantidad_insumo(cantidad)

                    while not resultado_val_cantidad[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_cantidad[1])
                        cantidad = self.vista.mostrar_crear_cantidad_prompt()
                        resultado_val_cantidad = self.validador.validar_cantidad_insumo(cantidad)

                    cantidad = resultado_val_cantidad[1]

                    if "platillo_merma" not in self.formulario.keys():
                        unidad_m = self.vista.mostrar_crear_unidad_medida_prompt()
                        resultado_val_unidad = self.validador.validar_unidad_medida(unidad_m)

                        while not resultado_val_unidad[0]:
                            self.vista.mostrar_mensaje_error_validacion(resultado_val_unidad[1])
                            unidad_m = self.vista.mostrar_crear_unidad_medida_prompt()
                            resultado_val_unidad = self.validador.validar_unidad_medida(unidad_m)

                        unidad_m = resultado_val_unidad[1]

                    else:
                        unidad_m = "pz"

                    lista_tipos_merma = self.servicio_merma.obtener_tipos_merma()
                    opciones_tipo_mer = [str(idx + 1) for idx in range(len(lista_tipos_merma))]

                    pagina, prox_pag = self.paginar_lista_detalles(lista_tipos_merma, self.pagina_actual_tipos_merma)
                    total_pag = self.obtener_total_paginas_detalles(lista_tipos_merma)

                    self.vista.mostrar_tipos_merma_disponibles(pagina, self.pagina_actual_tipos_merma, total_pag)

                    num_tipo_mer = self.vista.mostrar_editar_tipo_merma_prompt(opciones_tipo_mer)

                    if num_tipo_mer:
                        if num_tipo_mer == "0":
                            nombre_merma = self.vista.mostrar_crear_tipo_insumo_prompt()
                            resultado_val_tipo = self.validador.validar_nombre_tipo_merma(nombre_merma)

                            while not resultado_val_tipo[0]:
                                self.vista.mostrar_mensaje_error_validacion(resultado_val_tipo[1])
                                nombre_merma = self.vista.mostrar_crear_tipo_insumo_prompt()
                                resultado_val_tipo = self.validador.validar_nombre_tipo_merma(nombre_merma)

                            nombre_merma = resultado_val_tipo[1]

                            self.servicio_merma.crear_tipo_merma(nombre_merma)
                            tipo_merma = self.servicio_merma.obtener_tipo_merma_por_nombre(nombre_merma)

                        elif num_tipo_mer != "0":
                            tipo_merma = lista_tipos_merma[int(num_tipo_mer) - 1]

                        self.merma_actual = Merma(0, "", fecha, unidad_m, cantidad, insumo_merma, tipo_merma)
                        self.formulario["merma_creada"] = ""

                    self.mostrar_detalles_merma()

                else:
                    self.mostrar_lista_mermas()
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
                # volver a la vista de todas las mermas
                self.cancelar_edicion_actual()
                self.mostrar_lista_mermas()
            case "m":
                # volver al menú principal
                self.cancelar_edicion_actual()

    def evaluar_seleccion_busqueda_av(self, seleccion):
        match seleccion:
            case "1":
                rango_validado = False
                fecha_inicial = None
                fecha_final = None

                # por rango de fecha
                while not rango_validado:
                    fecha_inicial = self.vista.mostrar_buscar_por_rango_fecha_inicial_prompt()
                    resultado_val_f_inicial = self.validador.validar_formato_fecha(fecha_inicial)

                    while not resultado_val_f_inicial[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_f_inicial[1])
                        fecha_inicial = self.vista.mostrar_buscar_por_rango_fecha_inicial_prompt()
                        resultado_val_f_inicial = self.validador.validar_formato_fecha(fecha_inicial)

                    fecha_final = self.vista.mostrar_buscar_por_rango_fecha_final_prompt()

                    resultado_val_f_final = self.validador.validar_formato_fecha(fecha_final)

                    while not resultado_val_f_final[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_f_final[1])
                        fecha_inicial = self.vista.mostrar_buscar_por_rango_fecha_final_prompt()
                        resultado_val_f_final = self.validador.validar_formato_fecha(fecha_inicial)

                    resultado_val_rango = self.validador.validar_rango_fecha(fecha_inicial, fecha_final)

                    if resultado_val_rango[0]:
                        rango_validado = True
                    else:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_rango[1])

                resultados_busqueda = self.servicio_merma.obtener_mermas_por_rango_fecha(fecha_inicial, fecha_final)

                if resultados_busqueda and len(resultados_busqueda):
                    self.mermas_a_mostrar = resultados_busqueda
                else:
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_mensaje_no_resultados_busqueda_av()

                self.mostrar_lista_mermas()
            case "2":
                # por tipo de merma
                lista_tipos_merma = self.servicio_merma.obtener_tipos_merma()

                pagina, prox_pag = self.paginar_lista_detalles(lista_tipos_merma, self.pagina_actual_tipos_merma)
                total_pag = self.obtener_total_paginas_detalles(lista_tipos_merma)

                self.vista.mostrar_platillos_disponibles(pagina, self.pagina_actual_tipos_merma, total_pag)
                self.vista.refrescar_pantalla()

                opciones_tipo = {str(idx+1):lista_tipos_merma[idx] for idx in range(len(lista_tipos_merma))}
                opciones_tipo_lista = [key for key in opciones_tipo.keys()]

                tipo_num = self.vista.mostrar_buscar_por_tipo_merma_prompt(opciones_tipo_lista)
                tipo_nombre = opciones_tipo[tipo_num].clave

                resultados_busqueda = self.servicio_merma.obtener_mermas_por_tipo(tipo_nombre)
                if resultados_busqueda:
                    self.mermas_a_mostrar = resultados_busqueda
                else:
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_mensaje_no_resultados_busqueda_av()

                self.pagina_actual_tipos_merma = 1
                self.mostrar_lista_mermas()
            case "3":
                # por insumo
                lista_insumos = self.servicio_inventario.obtener_insumos()

                pagina, prox_pag = self.paginar_lista_detalles(lista_insumos, self.pagina_actual_lista_insumos)
                total_pag = self.obtener_total_paginas_detalles(lista_insumos)

                self.vista.mostrar_insumos_disponibles(pagina, self.pagina_actual_lista_insumos, total_pag)
                self.vista.refrescar_pantalla()

                opciones_insumo = [str(idx+1) for idx in range(len(lista_insumos))]

                res = self.vista.mostrar_buscar_por_insumo_prompt(opciones_insumo)
                insumo_num = lista_insumos[int(res)-1]

                resultados_busqueda = self.servicio_merma.obtener_mermas_por_insumo(insumo_num.num)

                if resultados_busqueda:
                    self.mermas_a_mostrar = resultados_busqueda
                else:
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_mensaje_no_resultados_busqueda_av()

                self.pagina_actual_lista_insumos = 1
                self.mostrar_lista_mermas()
            case "4":
                # buscar todos
                # asigna el valor a self.mermas_testeo la lista de todas las mermas con un servicio
                self.mermas_a_mostrar = self.servicio_merma.obtener_mermas()
                self.mostrar_lista_mermas()
            case "5":
                # volver a menú principal
                # aquí no se hace nada
                self.mostrar_lista_mermas()

    def evaluar_seleccion_menu_editar(self, seleccion):
        match seleccion:
            case "1":
                # abre prompt para cambiar la descripción
                descripcion = self.vista.mostrar_editar_descripcion_prompt()
                # checa que haya una respuesta del usuario y si es así lo debe validar
                if descripcion is not None:
                    resultado_val_desc = self.validador.validar_descripcion_merma(descripcion)

                    while not resultado_val_desc[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_desc[1])
                        descripcion = self.vista.mostrar_editar_descripcion_prompt()
                        if not descripcion:
                            self.mostrar_detalles_merma()
                        resultado_val_desc = self.validador.validar_descripcion_merma(descripcion)

                    descripcion = resultado_val_desc[1]

                    self.merma_actual.descripcion = descripcion
                    self.formulario["descripcion"] = descripcion

                self.mostrar_detalles_merma()

            case "2":
                # abre prompt para cambiar la fecha de la merma
                fecha = self.vista.mostrar_editar_fecha_prompt()

                # checa que haya un valor y luego valída y asigna
                if fecha:
                    resultado_val_fecha = self.validador.validar_formato_fecha(fecha)

                    while not resultado_val_fecha[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_fecha[1])
                        fecha = self.vista.mostrar_editar_fecha_prompt()
                        if not fecha:
                            self.mostrar_detalles_merma()
                        resultado_val_fecha = self.validador.validar_formato_fecha(fecha)

                    fecha = resultado_val_fecha[1]

                    self.merma_actual.fecha = fecha
                    self.formulario["fecha"] = fecha

                self.mostrar_detalles_merma()

            case "3":
                # abre opciones para editar cantidad
                cantidad = self.vista.mostrar_editar_cantidad_prompt()

                if cantidad is not None:
                    resultado_val_cantidad = self.validador.validar_cantidad_insumo(cantidad)

                    while not resultado_val_cantidad[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_cantidad[1])
                        cantidad = self.vista.mostrar_editar_cantidad_prompt()
                        if not cantidad:
                            self.mostrar_detalles_merma()
                        resultado_val_cantidad = self.validador.validar_cantidad_insumo(cantidad)

                    cantidad = resultado_val_cantidad[1]

                    self.merma_actual.cantidad = cantidad
                    self.formulario["cantidad"] = cantidad

                self.mostrar_detalles_merma()

            case "4":
                # abre opciones para editar unidad de medida
                unidad_m = self.vista.mostrar_editar_unidad_medida_prompt()

                if unidad_m is not None:
                    resultado_val_unidad = self.validador.validar_unidad_medida(unidad_m)

                    while not resultado_val_unidad[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_unidad[1])
                        unidad_m = self.vista.mostrar_editar_unidad_medida_prompt()
                        if not unidad_m:
                            self.mostrar_detalles_merma()
                        resultado_val_unidad = self.validador.validar_unidad_medida(unidad_m)

                    unidad_m = resultado_val_unidad[1]

                    self.merma_actual.unidad_medida = unidad_m
                    self.formulario["unidad_medida"] = unidad_m

                self.mostrar_detalles_merma()

            case "5":
                # abre opciones para editar tipo de merma
                lista_tipos_merma = self.servicio_merma.obtener_tipos_merma()
                opciones = [str(idx + 1) for idx in range(len(lista_tipos_merma))]

                pagina, prox_pag = self.paginar_lista_detalles(lista_tipos_merma, self.pagina_actual_tipos_merma)
                total_pag = self.obtener_total_paginas_detalles(lista_tipos_merma)

                self.vista.mostrar_platillos_disponibles(pagina, self.pagina_actual_tipos_merma, total_pag)

                tipo_merma = self.vista.mostrar_editar_tipo_merma_prompt(opciones)
                if tipo_merma:
                    if tipo_merma == "0":
                        # crear tipo
                        nombre_tipo = self.vista.mostrar_crear_tipo_insumo_prompt()
                        resultado_val_nombre = self.validador.validar_nombre_tipo_merma(nombre_tipo)

                        while not resultado_val_nombre[0]:
                            self.vista.mostrar_mensaje_error_validacion(resultado_val_nombre[1])
                            nombre_tipo = self.vista.mostrar_crear_tipo_insumo_prompt()
                            resultado_val_nombre = self.validador.validar_nombre_tipo_merma(nombre_tipo)

                        nombre_tipo = resultado_val_nombre[1]

                        self.servicio_merma.crear_tipo_merma(nombre_tipo)
                        self.merma_actual.tipo_merma = self.servicio_merma.obtener_tipo_merma_por_nombre(nombre_tipo)
                        self.formulario["tipo"] = nombre_tipo

                    if tipo_merma is not None:
                        tipo = lista_tipos_merma[int(tipo_merma)-1]
                        self.merma_actual.tipo_merma = tipo
                        self.formulario["tipo"] = tipo

                self.pagina_actual_tipos_merma = 1
                self.mostrar_detalles_merma()

            case "6":
                # llama a la función para guardar registro
                self.guardar_editar_merma()

            case "7":
                # cancela la edición actual y vuelve a detalles
                self.cancelar_edicion_actual()
                self.mostrar_lista_mermas()

            case "m":
                # vuelve al menú
                self.cancelar_edicion_actual()

    def cambiar_pagina_lista_compras(self, mov):
        if mov == ",":
            if self.pagina_actual_lista_mermas == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
                self.mostrar_lista_mermas()
            else:
                self.pagina_actual_lista_mermas -= 1
                pagina, hay_sig_pag = self.paginar_lista_merma(self.mermas_a_mostrar, self.pagina_actual_lista_mermas)
                self.mostrar_lista_mermas(pagina)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_merma(self.mermas_a_mostrar, self.pagina_actual_lista_mermas)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
                self.mostrar_lista_mermas()
            else:
                self.pagina_actual_lista_mermas += 1
                pagina, hay_sig_pag = self.paginar_lista_merma(self.mermas_a_mostrar, self.pagina_actual_lista_mermas)
                self.mostrar_lista_mermas(pagina)

    def cambiar_pagina_lista_insumos(self, mov):
        lista_insumo = self.servicio_inventario.obtener_insumos()

        if mov == ",":
            if self.pagina_actual_lista_insumos == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
            else:
                self.pagina_actual_lista_insumos -= 1
                pagina, hay_sig_pag = self.paginar_lista_merma(lista_insumo, self.pagina_actual_lista_insumos)
                total_pag = self.obtener_total_paginas_detalles(lista_insumo)
                self.vista.mostrar_insumos_disponibles(pagina, self.pagina_actual_lista_insumos, total_pag)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_merma(lista_insumo, self.pagina_actual_lista_insumos)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
            else:
                self.pagina_actual_lista_insumos += 1
                pagina, hay_sig_pag = self.paginar_lista_merma(lista_insumo, self.pagina_actual_lista_insumos)
                total_pag = self.obtener_total_paginas_detalles(lista_insumo)
                self.vista.mostrar_insumos_disponibles(pagina, self.pagina_actual_lista_insumos, total_pag)

    def cambiar_pagina_lista_tipos_merma(self, mov):
        lista_merma = self.servicio_merma.obtener_tipos_merma()
        if type(lista_merma) is not list:
            lista_merma = [lista_merma]

        if mov == ",":
            if self.pagina_actual_tipos_merma == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
            else:
                self.pagina_actual_tipos_merma -= 1
                pagina, hay_sig_pag = self.paginar_lista_merma(lista_merma, self.pagina_actual_tipos_merma)
                total_pag = self.obtener_total_paginas_detalles(lista_merma)
                self.vista.mostrar_platillos_disponibles(pagina, self.pagina_actual_tipos_merma, total_pag)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_merma(lista_merma, self.pagina_actual_tipos_merma)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
            else:
                self.pagina_actual_tipos_merma += 1
                pagina, hay_sig_pag = self.paginar_lista_merma(lista_merma, self.pagina_actual_tipos_merma)
                total_pag = self.obtener_total_paginas_detalles(lista_merma)
                self.vista.mostrar_platillos_disponibles(pagina, self.pagina_actual_tipos_merma, total_pag)

    def cambiar_pagina_lista_platillos(self, mov):
        lista_platillos = self.servicio_platillo.obtener_platillos()

        if mov == ",":
            if self.pagina_actual_lista_platillos == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
            else:
                self.pagina_actual_lista_platillos -= 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(lista_platillos, self.pagina_actual_lista_platillos)
                total_pag = self.obtener_total_paginas_detalles(lista_platillos)
                self.vista.mostrar_platillos_disponibles(pagina, self.pagina_actual_lista_platillos, total_pag)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_detalles(lista_platillos, self.pagina_actual_lista_platillos)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
            else:
                self.pagina_actual_lista_platillos += 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(lista_platillos, self.pagina_actual_lista_platillos)
                total_pag = self.obtener_total_paginas_detalles(lista_platillos)
                self.vista.mostrar_platillos_disponibles(pagina, self.pagina_actual_lista_platillos, total_pag)

    def paginar_lista_detalles(self, items: list, num_pag: int):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 10

        idx_inicio = (num_pag - 1) * lineas_disp
        idx_final = idx_inicio + lineas_disp

        if idx_final < len(items):
            prox_pag = True
        else:
            prox_pag = False

        return items[idx_inicio:idx_final], prox_pag

    def paginar_lista_merma(self, items: list, num_pag: int):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 10

        idx_inicio = (num_pag - 1) * lineas_disp
        idx_final = idx_inicio + lineas_disp

        if idx_final < len(items):
            prox_pag = True
        else:
            prox_pag = False

        return items[idx_inicio:idx_final], prox_pag

    def obtener_total_paginas_detalles(self, items: list):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 10

        if len(items) == 0:
            return 1

        return math.ceil(len(items) / lineas_disp)

    def obtener_total_paginas(self, items: list):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 10  # mismo valor que paginar_lista_merma()

        if len(items) == 0:
            return 1

        return math.ceil(len(items) / lineas_disp)
