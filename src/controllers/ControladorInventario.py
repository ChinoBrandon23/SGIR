import copy
import math
import time

from Validaciones.validadorInventario import validadorInventario
from services.inventario_servicio import  InventarioServicio
from views.VistaInventario import VistaInventario


class ControladorInventario:

    def __init__(self, vista:VistaInventario, servicio:InventarioServicio, validador:validadorInventario):
        self.vista = vista
        self.servicio = servicio
        self.validador = validador
        self.insumo_actual = None
        self.detalles_insumo_actual = []
        self.formulario = {}

        self.pagina_actual_lista_inventario = 1
        self.pagina_actual_lista_detalles = 1
        self.pagina_actual_tipos_insumo_disp = 1
        self.pagina_actual_marcas_disp = 1

        self.insumos_a_mostrar = None

        self.configurar_listeners()
        self.mostrar_lista_insumos()

    def configurar_listeners(self):
        self.vista.input_menu_inventario.agregar_escuchante(self.evaluar_seleccion_menu_inventario)
        self.vista.input_abrir_detalles.agregar_escuchante(self.mostrar_detalles_insumo)
        self.vista.input_menu_detalles.agregar_escuchante(self.evaluar_seleccion_menu_detalles)
        self.vista.input_menu_editar_inventario.agregar_escuchante(self.evaluar_seleccion_menu_editar)
        self.vista.input_menu_filtros.agregar_escuchante(self.evaluar_seleccion_busqueda_av)

        # para cambiar página
        self.vista.input_menu_inventario.agregar_escuchante(self.cambiar_pagina_lista_inventario)
        self.vista.input_menu_detalles.agregar_escuchante(self.cambiar_pagina_lista_detalles)
        self.vista.input_menu_editar_inventario.agregar_escuchante(self.cambiar_pagina_lista_detalles)
        self.vista.input_seleccion_tipo_insumo.agregar_escuchante(self.cambiar_pagina_lista_tipos_insumo)
        self.vista.input_seleccion_marca.agregar_escuchante(self.cambiar_pagina_lista_marcas)

    def mostrar_lista_insumos(self, lista_insumos=None):
        """
        Conecta con la capa de servicios para obtener la lista de insumos y crea un elemento de lista para cada una.
        """

        if self.insumos_a_mostrar is None:
            self.insumos_a_mostrar = self.servicio.obtener_insumos()

        self.vista.mostrar_todos_insumos(self.pagina_actual_lista_inventario,
                                         self.obtener_total_paginas_lista_inventario(self.insumos_a_mostrar))

        if lista_insumos is None:
            lista_insumos, hay_prox_pag = self.paginar_lista_inventario(self.insumos_a_mostrar, self.pagina_actual_lista_inventario)

        if self.pagina_actual_lista_inventario == 1:
            idx_ui = 0
        else:
            consola_size = self.vista.console.size[1]
            size_sin_prompt = consola_size - 6
            lineas_disp = size_sin_prompt - 6

            idx_ui = (self.pagina_actual_lista_inventario - 1) * lineas_disp

        for insumo in lista_insumos:
            # calcula si el stock está bajo o no
            if insumo.stock >= insumo.umbral:
                stock_bajo = False
            else:
                stock_bajo = True

            idx_ui += 1
            self.vista.crear_elemento_tabla_insumos(insumo, alerta_stock=stock_bajo, idx=idx_ui)

        self.vista.refrescar_pantalla()
        self.vista.mostrar_menu_insumos_prompt()

    def mostrar_detalles_insumo(self, insumo_num=None):
        if self.insumo_actual is None:
            # Si no tenemos un insumo actual, busca el insumo por el num pasado como arg
            self.insumo_actual = self.insumos_a_mostrar[int(insumo_num)-1]

        # teniendo ahora el insumo a ver, hay que obtener la lista de los detalles de compra para este insumo
        detalles_compra = self.servicio.obtener_detalles_compra_por_insumo(self.insumo_actual.num)

        lista_detalles, prox_pag = self.paginar_lista_detalles(detalles_compra, self.pagina_actual_lista_detalles)
        total_paginas_detalles = self.obtener_total_paginas_detalles(detalles_compra)

        # llama la función para crear la vista de tabla de detalles y le pasa los datos del formulario actual
        self.vista.mostrar_detalles_insumo(self.insumo_actual, pag_actual=self.pagina_actual_lista_detalles, total_pag=total_paginas_detalles, datos_editados=copy.deepcopy(self.formulario),
                                           lista_detalles=lista_detalles)

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

    def guardar_editar_menu(self):
        # Como en el controlador inventario no se crean insumos, solo se consultan, solo se usará
        # el servicio de actualizar y no de crear

        try:
            self.servicio.actualizar_insumo(self.insumo_actual)
        except ValueError:
            self.vista.refrescar_pantalla()
            self.vista.mostrar_mensaje_nombre_duplicado()
            self.vista.mostrar_opciones_editar_prompt()

        self.insumos_a_mostrar = self.servicio.obtener_insumos()

        insumo_actual_num = str(self.insumo_actual.num)
        self.cancelar_edicion_actual()
        self.mostrar_detalles_insumo(insumo_actual_num)

    def cancelar_edicion_actual(self):
        # resetea formulario e insumo actual
        self.pagina_actual_lista_inventario = 1
        self.pagina_actual_lista_detalles = 1
        self.pagina_actual_tipos_insumo_disp = 1
        self.pagina_actual_marcas_disp = 1
        self.insumo_actual = None
        self.detalles_insumo_actual = []
        self.formulario = {}

    def usuario_esta_editando(self):
        # checa si el usuario ha hecho cambios desde que entró a la vista de detalles
        if len(self.formulario.items()) > 0:
            return True
        return False

    def evaluar_seleccion_menu_inventario(self, seleccion):
        match seleccion:
            case "1":
                # Aquí debería obtener la lista de todos los insumos y pasarlos
                self.vista.mostrar_abrir_detalles_prompt(self.insumos_a_mostrar)
            case "2":
                # busqueda avanzada
                self.vista.crear_banda_opciones_busqueda_av()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_opciones_busqueda_av_prompt()

            case "m":
                # cancela la edicion actual antes de volver al menu principal
                self.cancelar_edicion_actual()

    def evaluar_seleccion_menu_detalles(self, seleccion):
        match seleccion:
            case "1":
                # volver a la vista de todos los menus
                self.cancelar_edicion_actual()
                self.mostrar_lista_insumos()
            case "2":
                # abrir opciones de editar insumo
                self.vista.crear_banda_opciones_editar()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_opciones_editar_prompt()
            case "m":
                # volver al menú principal
                self.cancelar_edicion_actual()

    def evaluar_seleccion_busqueda_av(self, seleccion):
        match seleccion:
            case "1":
                # buscar por nombre
                nombre = self.vista.mostrar_buscar_por_nombre_prompt()

                resultado_busqueda = self.servicio.obtener_insumos_por_match_nombre(nombre)

                if len(resultado_busqueda):
                    self.insumos_a_mostrar = resultado_busqueda
                else:
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_mensaje_no_resultados_busqueda_av()
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_opciones_busqueda_av_prompt()

                self.mostrar_lista_insumos()

            case "2":
                # buscar por tipo insumo
                todos_tipos_insumo = self.servicio.obtener_tipos_insumo()
                dict_tipo_insumo = {i + 1: todos_tipos_insumo[i] for i in
                                    range(len(todos_tipos_insumo))}

                opciones_tipo = [str(idx) for idx in dict_tipo_insumo]

                pagina, prox_pag = self.paginar_lista_detalles(todos_tipos_insumo, self.pagina_actual_tipos_insumo_disp)
                total_pag = self.obtener_total_paginas_detalles(todos_tipos_insumo)

                self.vista.mostrar_tipos_insumo_disponibles(pagina, self.pagina_actual_tipos_insumo_disp, total_pag)
                self.vista.refrescar_pantalla()

                tipo_num = self.vista.mostrar_buscar_por_tipo_insumo_prompt(opciones_tipo)
                tipo_clave = dict_tipo_insumo[int(tipo_num)].clave

                resultado_busqueda = self.servicio.obtener_insumos_por_tipo_insumo(tipo_clave)
                self.pagina_actual_tipos_insumo_disp = 1

                if len(resultado_busqueda):
                    self.insumos_a_mostrar = resultado_busqueda
                else:
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_mensaje_no_resultados_busqueda_av()
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_opciones_busqueda_av_prompt()

                self.mostrar_lista_insumos()

            case "3":
                # buscar por marca
                marcas_lista = self.servicio.obtener_marcas()
                opciones_marca = [str(i+1) for i in range(len(marcas_lista))]

                pagina, prox_pag = self.paginar_lista_inventario(marcas_lista, self.pagina_actual_marcas_disp)
                total_pag = self.obtener_total_paginas_lista_inventario(marcas_lista)

                self.vista.mostrar_marcas_disponibles(pagina, self.pagina_actual_tipos_insumo_disp, total_pag)
                self.vista.refrescar_pantalla()

                marca_num = self.vista.mostrar_buscar_por_marca_prompt(opciones_marca)
                marca_num = opciones_marca[int(marca_num)-1]

                resultado_busqueda = self.servicio.obtener_insumos_por_marca(marca_num)
                self.pagina_actual_marcas_disp = 1

                if len(resultado_busqueda):
                    self.insumos_a_mostrar = resultado_busqueda
                else:
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_mensaje_no_resultados_busqueda_av()
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_opciones_busqueda_av_prompt()

                self.mostrar_lista_insumos()

            case "4":
                # buscar por stock bajo
                resultado_busqueda = self.servicio.obtener_insumos_con_stock_bajo()

                if len(resultado_busqueda):
                    self.insumos_a_mostrar = resultado_busqueda
                else:
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_mensaje_no_resultados_busqueda_av()
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_opciones_busqueda_av_prompt()

                self.mostrar_lista_insumos()

            case "5":
                # mostrar todos los insumos
                self.insumos_a_mostrar = self.servicio.obtener_insumos()
                self.mostrar_lista_insumos()

            case "6":
                # volver a lista de insumos
                self.mostrar_lista_insumos()

    def evaluar_seleccion_menu_editar(self, seleccion):
        match seleccion:
            case "1":
                # abre prompt para cambiar el nombre del insumo
                nombre = self.vista.mostrar_editar_nombre_prompt()
                # checa que haya una respuesta del usuario y si es así lo debe validar
                if nombre is not None:
                    resultado_val_nombre = self.validador.validar_nombre(nombre)

                    while not resultado_val_nombre[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_nombre[1])
                        nombre = self.vista.mostrar_editar_nombre_prompt()
                        resultado_val_nombre = self.validador.validar_nombre(nombre)

                    self.formulario["nombre"] = resultado_val_nombre[1]
                    self.insumo_actual.nombre = resultado_val_nombre[1]
                self.mostrar_detalles_insumo()

            case "2":
                # abre prompt para cambiar el umbral del insumo
                self.vista.refrescar_pantalla()
                umbral = self.vista.mostrar_editar_umbral_prompt()

                if umbral is not None:
                    resultado_val_umbral = self.validador.validar_umbral(umbral)

                    while not resultado_val_umbral[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_umbral[1])
                        umbral = self.vista.mostrar_editar_umbral_prompt()
                        resultado_val_umbral = self.validador.validar_umbral(umbral)

                    self.insumo_actual.umbral = resultado_val_umbral[1]
                    self.formulario["umbral"] = resultado_val_umbral[1]
                self.mostrar_detalles_insumo()

            case "3":
                # abre prompt para editar tipo de insumo
                todos_tipos_insumo = self.servicio.obtener_tipos_insumo()
                dict_tipo_insumo = {i + 1: todos_tipos_insumo[i] for i in
                                    range(len(todos_tipos_insumo))}

                opciones_tipo = [str(idx) for idx in dict_tipo_insumo]

                # paginar
                pagina, prox_pag = self.paginar_lista_detalles(todos_tipos_insumo, self.pagina_actual_tipos_insumo_disp)
                total_pag = self.obtener_total_paginas_detalles(todos_tipos_insumo)

                self.vista.mostrar_tipos_insumo_disponibles(pagina, self.pagina_actual_tipos_insumo_disp, total_pag)
                self.vista.refrescar_pantalla()

                tipo_num = self.vista.mostrar_editar_tipo_insumo_prompt(opciones_tipo)
                tipo = None

                # Aquí se desvía para crear un nuevo tipo de insumo
                if tipo_num == "0":
                    nuevo_tipo_nom = self.vista.mostrar_crear_tipo_insumo_prompt()

                    try:
                        self.servicio.crear_tipo_insumo(nuevo_tipo_nom)
                        tipo = self.servicio.obtener_tipo_insumo_por_nombre(nuevo_tipo_nom)
                    except ValueError:
                        self.vista.refrescar_pantalla()
                        self.vista.mostrar_mensaje_tipo_insumo_ya_existe()

                elif tipo_num is not None:
                    for idx, tipo_obj in dict_tipo_insumo.items():
                        if idx == int(tipo_num):
                            tipo = dict_tipo_insumo[idx]

                if tipo:
                    self.insumo_actual.tipo_insumo = tipo
                    self.formulario["tipo_insumo"] = (copy.deepcopy(tipo))

                self.pagina_actual_tipos_insumo_disp = 1
                self.mostrar_detalles_insumo()
            case "4":
                # llama a la función para guardar
                self.guardar_editar_menu()
            case "5":
                # cancela la edición actual y vuelve a detalles
                if self.insumo_actual.num in [menu.num for menu in self.insumos_a_mostrar]:
                    self.cancelar_edicion_actual()
                    self.insumo_actual = self.servicio.obtener_insumo_por_num(self.vista.input_abrir_detalles.user_input)
                    self.mostrar_detalles_insumo()
                else:
                    self.cancelar_edicion_actual()
                    self.mostrar_lista_insumos()
            case "m":
                # vuelve al menú
                self.cancelar_edicion_actual()

    def cambiar_pagina_lista_inventario(self, mov):
        if mov == ",":
            if self.pagina_actual_lista_inventario == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
                self.mostrar_lista_insumos()
            else:
                self.pagina_actual_lista_inventario -= 1
                pagina, hay_sig_pag = self.paginar_lista_inventario(self.insumos_a_mostrar, self.pagina_actual_lista_inventario)
                self.mostrar_lista_insumos(pagina)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_inventario(self.insumos_a_mostrar, self.pagina_actual_lista_inventario)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
                self.mostrar_lista_insumos()
            else:
                self.pagina_actual_lista_inventario += 1
                pagina, hay_sig_pag = self.paginar_lista_inventario(self.insumos_a_mostrar, self.pagina_actual_lista_inventario)
                self.mostrar_lista_insumos(pagina)

    def paginar_lista_inventario(self, items: list, num_pag: int):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 6

        idx_inicio = (num_pag - 1) * lineas_disp
        idx_final = idx_inicio + lineas_disp

        if idx_final < len(items):
            prox_pag = True
        else:
            prox_pag = False

        return items[idx_inicio:idx_final], prox_pag

    def cambiar_pagina_lista_detalles(self, mov):
        detalles_lista = self.servicio.obtener_detalles_compra_por_insumo(self.insumo_actual.num)

        if mov == ",":
            if self.pagina_actual_lista_inventario == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
                self.mostrar_detalles_insumo()
            else:
                self.pagina_actual_lista_inventario -= 1

                pagina, hay_sig_pag = self.paginar_lista_detalles(detalles_lista, self.pagina_actual_lista_inventario)
                self.mostrar_detalles_insumo(pagina)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_detalles(detalles_lista, self.pagina_actual_lista_inventario)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
                self.mostrar_detalles_insumo()
            else:
                self.pagina_actual_lista_inventario += 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(detalles_lista, self.pagina_actual_lista_inventario)
                self.mostrar_detalles_insumo(pagina)

    def paginar_lista_detalles(self, items: list, num_pag: int):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 20

        idx_inicio = (num_pag - 1) * lineas_disp
        idx_final = idx_inicio + lineas_disp

        if idx_final < len(items):
            prox_pag = True
        else:
            prox_pag = False

        return items[idx_inicio:idx_final], prox_pag

    def cambiar_pagina_lista_tipos_insumo(self, mov):
        tipos_insumo = self.servicio.obtener_tipos_insumo()

        if mov == ",":
            if self.pagina_actual_tipos_insumo_disp == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
            else:
                self.pagina_actual_tipos_insumo_disp -= 1

                pagina, hay_sig_pag = self.paginar_lista_detalles(tipos_insumo, self.pagina_actual_tipos_insumo_disp)
                total_pag = self.obtener_total_paginas_detalles(tipos_insumo)
                self.vista.mostrar_tipos_insumo_disponibles(pagina, self.pagina_actual_tipos_insumo_disp, total_pag)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_detalles(tipos_insumo, self.pagina_actual_tipos_insumo_disp)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
            else:
                self.pagina_actual_tipos_insumo_disp += 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(tipos_insumo, self.pagina_actual_tipos_insumo_disp)
                total_pag = self.obtener_total_paginas_detalles(tipos_insumo)
                self.vista.mostrar_tipos_insumo_disponibles(pagina, self.pagina_actual_tipos_insumo_disp, total_pag)

    def cambiar_pagina_lista_marcas(self, mov):
        detalles_lista = self.servicio.obtener_marcas()

        if mov == ",":
            if self.pagina_actual_marcas_disp == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
            else:
                self.pagina_actual_marcas_disp -= 1

                pagina, hay_sig_pag = self.paginar_lista_detalles(detalles_lista, self.pagina_actual_marcas_disp)
                total_pag = self.obtener_total_paginas_detalles(detalles_lista)
                self.vista.mostrar_tipos_insumo_disponibles(pagina, self.pagina_actual_marcas_disp, total_pag)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_detalles(detalles_lista, self.pagina_actual_marcas_disp)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
            else:
                self.pagina_actual_marcas_disp += 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(detalles_lista, self.pagina_actual_marcas_disp)
                total_pag = self.obtener_total_paginas_detalles(detalles_lista)
                self.vista.mostrar_tipos_insumo_disponibles(pagina, self.pagina_actual_marcas_disp, total_pag)

    def obtener_total_paginas_lista_inventario(self, items: list):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 6

        if len(items) == 0:
            return 1

        return math.ceil(len(items) / lineas_disp)

    def obtener_total_paginas_detalles(self, items: list):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 20

        if len(items) == 0:
            return 1

        return math.ceil(len(items) / lineas_disp)
