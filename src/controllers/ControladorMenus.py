import copy
import math
import time
from datetime import datetime
import datetime
from mysql.connector import Error

from Validaciones.validadorMenus import validadorMenu
from models.menu import Menu
from views.VistaMenus import VistaMenus

from services.menu_servicio import MenuServicio

class ControladorMenus:
    def __init__(self, vista:VistaMenus, servicio:MenuServicio, validador:validadorMenu):
        self.vista = vista
        self.servicio = servicio
        self.validador = validador
        self.menu_actual = None
        self.formulario = {"platillos":[], "item_borrado":False}
        self.platillo_idx = {}

        self.pagina_actual_lista_menus = 1
        self.pagina_actual_lista_detalles = 1
        self.pagina_actual_lista_platillos_disp = 1
        self.pagina_actual_platillos_conflicto = 1

        self.platillos_conflicto = None

        self.menus_a_mostrar = None

        self.configurar_listeners()
        self.mostrar_lista_menus()

    def configurar_listeners(self):
        self.vista.input_menu_menus.agregar_escuchante(self.evaluar_seleccion_menu_menus)
        self.vista.input_abrir_detalles.agregar_escuchante(self.mostrar_detalles_menu)
        self.vista.input_menu_detalles.agregar_escuchante(self.evaluar_seleccion_menu_detalles)
        self.vista.input_menu_editar_menu.agregar_escuchante(self.evaluar_seleccion_menu_editar)
        self.vista.input_menu_editar_platillo.agregar_escuchante(self.evaluar_seleccion_editar_platillos)
        self.vista.input_menu_filtros.agregar_escuchante(self.evaluar_seleccion_busqueda_av)

        # Para cambiar página
        self.vista.input_menu_menus.agregar_escuchante(self.cambiar_pagina_lista_menus)
        self.vista.input_abrir_detalles.agregar_escuchante(self.cambiar_pagina_lista_menus)
        self.vista.input_menu_detalles.agregar_escuchante(self.cambiar_pagina_lista_detalles)
        self.vista.input_menu_editar_menu.agregar_escuchante(self.cambiar_pagina_lista_detalles)
        self.vista.input_menu_editar_platillo.agregar_escuchante(self.cambiar_pagina_lista_detalles)
        self.vista.input_seleccion_platillos_disp.agregar_escuchante(self.cambiar_pagina_lista_platillos_disp)
        self.vista.input_platillos_conflicto.agregar_escuchante(self.cambiar_pagina_lista_platillos_conflicto)

    def mostrar_lista_menus(self, pag_lista_menus=None):
        """
        Conecta con la capa de servicios para obtener la lista de recetas y crea un elemento de lista para cada una.
        """

        #calcula el numero de recetas reales: se eliminara despues
        if self.menus_a_mostrar is None:
            self.menus_a_mostrar = self.servicio.obtener_menus()

        for menu in self.menus_a_mostrar:
            menu.cantidad_platillos = self.servicio.calcular_num_platillos(menu=menu)

        # esta función en la vista resetea la vista y crea los layouts para mostrar la lista de menús
        # se pasan como arg el núm de pág actual y el total de páginas para mostrar en el panel
        self.vista.mostrar_todos_menus(self.pagina_actual_lista_menus,
                                       self.obtener_total_paginas_lista_menus(self.menus_a_mostrar))

        # checa si tenemos pag_lista_menus actual para mostrar, si no, se obtiene la página actual
        if pag_lista_menus is None:
            pag_lista_menus, hay_prox_pag = self.paginar_lista_menus(self.menus_a_mostrar, self.pagina_actual_lista_menus)

        if self.pagina_actual_lista_menus == 1:
            idx_ui = 0
        else:
            consola_size = self.vista.console.size[1]
            size_sin_prompt = consola_size - 6
            lineas_disp = size_sin_prompt - 18

            idx_ui = (self.pagina_actual_lista_menus - 1) * lineas_disp

        # se agregan a la tabla únicamente los elementos de la página actual
        for menu in pag_lista_menus:
            idx_ui += 1
            self.vista.crear_elemento_tabla_menus(menu, idx_ui)

        self.vista.refrescar_pantalla()
        self.vista.mostrar_menu_menus_prompt()

    def mostrar_detalles_menu(self, menu_num=None):
        if self.menu_actual is None and menu_num is not None:
            # Si no tenemos un menú actual, busca el menú por el num pasado como arg
            # idealmente con un servicio pero por ahora uso un loop para testeo
            self.menu_actual = self.menus_a_mostrar[int(menu_num)-1]

        self.mapear_detalle_platillo()

        # agregando paginado
        lista_detalles, prox_pag = self.paginar_lista_detalles(self.menu_actual.detalles, self.pagina_actual_lista_detalles)
        total_paginas_detalles = self.obtener_total_paginas_detalles(self.menu_actual.detalles)

        # llama la función para crear la vista de tabla de detalles y le pasa los datos del formulario actual
        self.vista.mostrar_detalles_menu(self.menu_actual, lista_detalles, self.pagina_actual_lista_detalles, total_paginas_detalles, datos_editados=copy.deepcopy(self.formulario), mapa_platillos=self.platillo_idx)

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

    def mostrar_formulario_crear_menu(self):
        if self.menu_actual is None:
            self.vista.mostrar_crear_menu(None)
        else:
            self.vista.mostrar_crear_menu(self.menu_actual)
            self.vista.crear_banda_opciones_editar()
            self.vista.refrescar_pantalla()
            self.vista.mostrar_opciones_editar_prompt()

        self.vista.refrescar_pantalla()

    def guardar_editar_menu(self):
        # Cambia los datos del formulario en el objeto actual
        # para testeo, aquí debería llamar a un servicio
        if self.servicio.menu_existe(self.menu_actual.num):
            try:
                self.servicio.actualizar_menu(menu=self.menu_actual)
                menu_actual_num = str(self.menu_actual.num)
            except ValueError:
                self.vista.refrescar_pantalla()
                self.vista.mostrar_mensaje_editar_nombre_duplicado()
                self.vista.mostrar_opciones_editar_prompt()
        else:
            try:
                self.servicio.crear_menu(self.menu_actual)
                menu_actual_num = self.servicio.obtener_menu_por_nombre(self.menu_actual.nombre).num
                self.menus_a_mostrar = self.servicio.obtener_menus()
            except Error:
                self.vista.refrescar_pantalla()
                self.vista.mostrar_mensaje_editar_nombre_duplicado()
                self.vista.mostrar_opciones_editar_prompt()

        # resetea el formulario porque la info ya se guardó y vuelve a la vista de detalles
        # esta debería jalar de nuevo el dato, el cual debería estar actualizado ya
        self.menus_a_mostrar = self.servicio.obtener_menus()
        self.cancelar_edicion_actual()
        self.menu_actual = self.servicio.obtener_menu_por_id(menu_actual_num)
        self.mostrar_detalles_menu()

    def asignar_vigencia(self, fecha_inicial, fecha_final):
        # debería validar el formato de la fecha y usar un servicio y eso
        formato = "%d-%m-%Y"

        self.menu_actual.fecha_inicial = datetime.datetime.strptime(fecha_inicial, formato).date()
        self.menu_actual.fecha_final = datetime.datetime.strptime(fecha_final, formato).date()

        self.formulario["vigencia"] = True

    def cancelar_edicion_actual(self):
        # resetea formulario y menu actual
        self.menu_actual = None
        self.pagina_actual_lista_menus = 1
        self.pagina_actual_lista_detalles = 1
        self.pagina_actual_lista_platillos_disp = 1
        self.pagina_actual_platillos_conflicto = 1
        self.formulario = {"platillos":[], "item_borrado":False}

    def usuario_esta_editando(self):
        # checa si el usuario ha hecho cambios desde que entró a la vista de detalles
        if (len(self.formulario["platillos"]) > 0 or len(self.formulario.items()) > 2) or self.formulario["item_borrado"]:
            return True
        return False

    def agregar_edicion_platillos(self, detalle_pl):
        lista_plat_editados_nombre = [pl.platillo.nombre for pl in self.formulario["platillos"]]

        if detalle_pl.platillo.nombre in lista_plat_editados_nombre:
            # checa si un ingrediente ya fue editado antes y remueve esa edicion para agregar la nueva
            obj = [pl for pl in self.formulario["platillos"] if pl.platillo.nombre == detalle_pl.platillo.nombre][0]
            self.formulario["platillos"].remove(obj)

        self.formulario["platillos"].append(detalle_pl)

    def filtrar_platillos_duplicados(self):
        lista_platillos_actual = self.servicio.obtener_platillos_disponibles(self.menu_actual.fecha_inicial, self.menu_actual.fecha_final)
        lista_platillos_en_menu = [pl.platillo.nombre for pl in self.menu_actual.detalles]
        idx_plat_disp = {i + 1: lista_platillos_actual[i] for i in range(len(lista_platillos_actual)) if
                         lista_platillos_actual[i].nombre not in lista_platillos_en_menu}

        return [idx_plat_disp[idx] for idx in idx_plat_disp]

    def mapear_detalle_platillo(self):
        # toma los platillos del menú itera sobre cada uno y les asigna un número para mostrar en la tabla de la vista
        if self.menu_actual:
            self.platillo_idx = {}
            lista_platillo = self.menu_actual.detalles

            for i in range(len(lista_platillo)):
                # agregando al dict los ingredientes originales del menu
                self.platillo_idx[i + 1] = lista_platillo[i].platillo.nombre

    def evaluar_seleccion_menu_menus(self, seleccion):
        match seleccion:
            case "1":
                # Aquí debería obtener la lista de todos los menús y pasarlos
                self.vista.mostrar_abrir_detalles_prompt(self.menus_a_mostrar)
            case "2":
                # Aquí crea menú
                self.mostrar_formulario_crear_menu()
                nombre = self.vista.mostrar_prompt_crear_menu()

                if nombre:
                    # mejor se crea el objeto para permitir la edición de este pero no se guarda hasta que el usuario
                    # escoge la opción guardar manualmente
                    resultado_val_nombre = self.validador.validar_nombre(nombre)

                    while not resultado_val_nombre[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_nombre[1])
                        nombre = self.vista.mostrar_prompt_crear_menu()
                        if nombre:
                            resultado_val_nombre = self.validador.validar_nombre(nombre)
                        else:
                            self.mostrar_lista_menus()

                    self.menu_actual = Menu(num=0, nombre=resultado_val_nombre[1], cantidad_platillos=0,
                                    fecha_inicial=datetime.date.today(),
                                    fecha_final=datetime.date.today())
                    self.formulario["nombre"] = nombre
                    self.mostrar_formulario_crear_menu()
                else:
                    self.mostrar_lista_menus()
            case "3":
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
                self.mostrar_lista_menus()
            case "2":
                # abrir opciones de editar menu
                self.vista.crear_banda_opciones_editar()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_opciones_editar_prompt()
            case "3":
                borrar = self.vista.mostrar_prompt_eliminar_menu_prompt()
                if borrar and self.menu_actual:
                    self.servicio.eliminar_menu(self.menu_actual.num)
                
                    self.cancelar_edicion_actual()
                    self.menus_a_mostrar = self.servicio.obtener_menus()
                    self.mostrar_lista_menus()

                self.mostrar_detalles_menu()
            case "m":
                # volver al menú principal
                self.cancelar_edicion_actual()

    def evaluar_seleccion_busqueda_av(self, seleccion):
        match seleccion:
            case "1":
                # buscar por nombre
                nombre = self.vista.mostrar_buscar_por_nombre_prompt()

                resultados_obtenidos = self.servicio.obtener_menus_por_match_nombre(nombre)

                if len(resultados_obtenidos):
                    self.menus_a_mostrar = resultados_obtenidos
                else:
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_mensaje_no_resultados_busqueda_av()
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_opciones_busqueda_av_prompt()

                self.mostrar_lista_menus()

            case "2":
                # buscar por vigencia
                fecha_inicial, fecha_final = self.vista.mostrar_buscar_por_vigencia_prompt()

                try:
                    resultados_obtenidos = self.servicio.obtener_menus_por_rango_fecha(fecha_inicial, fecha_final)
                    self.menus_a_mostrar = resultados_obtenidos
                except IndexError:
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_mensaje_no_resultados_busqueda_av()
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_opciones_busqueda_av_prompt()

                self.mostrar_lista_menus()

            case "3":
                # mostrar todos los menús
                self.menus_a_mostrar = self.servicio.obtener_menus()
                self.mostrar_lista_menus()

            case "4":
                # volver a lista de menús
                # Aquí no se mueve nada
                self.mostrar_lista_menus()

    def evaluar_seleccion_menu_editar(self, seleccion):
        match seleccion:
            case "1":
                # abre prompt para cambiar el nombre del menú
                nombre = self.vista.mostrar_editar_nombre_prompt()
                # checa que haya una respuesta del usuario y si es así lo debe validar
                if nombre is not None:
                    resultado_val_nombre = self.validador.validar_nombre(nombre)

                    while not resultado_val_nombre[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_nombre[1])
                        nombre = self.vista.mostrar_prompt_crear_menu()
                        resultado_val_nombre = self.validador.validar_nombre(nombre)

                    self.formulario["nombre"] = resultado_val_nombre[1]
                    self.menu_actual.nombre = resultado_val_nombre[1]
                self.mostrar_detalles_menu()

            case "2":
                # abre prompt para cambiar la vigencia del menú
                self.vista.refrescar_pantalla()
                f_inicial, f_final = self.vista.mostrar_editar_vigencia_prompt()

                if f_inicial is not None and f_final is not None:
                    resultados_val_fecha = self.validador.validar_fecha(f_inicial,f_final)

                    while not resultados_val_fecha[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultados_val_fecha[1])
                        f_inicial, f_final = self.vista.mostrar_editar_vigencia_prompt()
                        if f_inicial and f_final:
                            resultados_val_fecha = self.validador.validar_fecha(f_inicial, f_final)
                        else:
                            self.mostrar_detalles_menu()

                    fecha_incial_dt = resultados_val_fecha[1]["fecha_inicio"]
                    fecha_final_dt = resultados_val_fecha[1]["fecha_fin"]

                    self.platillos_conflicto = self.servicio.obtener_platillos_invalidos_menu(self.menu_actual, fecha_incial_dt, fecha_final_dt)

                    if len(self.platillos_conflicto):
                        # se avisa al usuario que el cambio resultaría en platillos en conflicto de fechas
                        total_pag = self.obtener_total_paginas_detalles(self.platillos_conflicto)
                        pagina, prox_pag = self.paginar_lista_detalles(self.platillos_conflicto, self.pagina_actual_platillos_conflicto)

                        self.vista.mostrar_platillos_conflicto(pagina, self.pagina_actual_platillos_conflicto, total_pag)
                        eleccion = self.vista.mostrar_mensaje_platillos_conflicto(f_inicial, f_final)

                        if eleccion == "S":
                            self.asignar_vigencia(f_inicial, f_final)

                            platillo_invalidos = self.servicio.obtener_platillos_invalidos_menu(self.menu_actual, self.menu_actual.fecha_inicial,
                                                                                       self.menu_actual.fecha_inicial)
                            platillo_invalidos_idx = [plat.num for plat in platillo_invalidos]

                            for detalle in self.menu_actual.detalles:
                                if detalle.platillo.num in platillo_invalidos_idx:
                                    self.menu_actual.detalles.remove(detalle)

                        else:
                            self.pagina_actual_platillos_conflicto = 1
                            self.platillos_conflicto = []
                            self.formulario["item_borrado"] = True
                            self.mostrar_detalles_menu()
                    else:
                        self.asignar_vigencia(f_inicial, f_final)

                self.pagina_actual_platillos_conflicto = 1
                self.platillos_conflicto = []
                self.mostrar_detalles_menu()

            case "3":
                # abre opciones para editar platillos
                self.vista.crear_banda_opciones_editar_platillos()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_editar_platillos_menu_prompt()

            case "4":
                # llama a la función para guardar menu
                self.guardar_editar_menu()
            case "5":
                # cancela la edición actual y vuelve a detalles
                if self.menu_actual.num in [menu.num for menu in self.servicio.obtener_menus()]:
                    self.cancelar_edicion_actual()
                    self.menu_actual = self.servicio.obtener_menu_por_id(self.vista.input_abrir_detalles.user_input)
                    self.mostrar_detalles_menu()
                else:
                    self.cancelar_edicion_actual()
                    self.mostrar_lista_menus()
            case "m":
                # vuelve al menú
                self.cancelar_edicion_actual()

    def evaluar_seleccion_editar_platillos(self, seleccion):
        match seleccion:
            case "1":
                # agregar platillo
                # hago una lista con los nombres (str) de los platillos que ya son parte del menú actual
                # y luego hago un dict con un # de índice y el nombre de cada platillo que existe
                # y NO es ya parte del menú para evitar añadir duplicados, estos son los platillos disponibles
                lista_plat_disp = self.filtrar_platillos_duplicados()
                # hago una lista de solo los índices de los platillos disponibles para pasarla a la vista como
                # opciones válidas de input para el usuario
                # hago otra lista con solo los nombres de los platillos para pasarla a la función que va a mostrar al
                # usuario los platillos disponibles

                opciones = [str(i+1) for i in range(len(lista_plat_disp))]

                pagina, prox_pag = self.paginar_lista_detalles(lista_plat_disp, self.pagina_actual_lista_platillos_disp)
                total_pag = self.obtener_total_paginas_detalles(lista_plat_disp)

                self.vista.mostrar_platillos_disponibles(pagina, self.pagina_actual_lista_platillos_disp, total_pag)
                self.vista.refrescar_pantalla()

                num_platillo= self.vista.mostrar_agregar_platillo_prompt(opciones)

                if num_platillo:
                    precio = self.vista.mostrar_ingresar_precio_prompt()

                    resultado_val_precio = self.validador.precio_platillo(precio)

                    while not resultado_val_precio[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_precio[1])
                        precio = self.vista.mostrar_ingresar_precio_prompt()
                        resultado_val_precio = self.validador.precio_platillo(precio)

                    nombre = lista_plat_disp[int(num_platillo)-1].nombre
                    lista_platillos_en_menu = self.servicio.obtener_platillos_disponibles(
                        self.menu_actual.fecha_inicial, self.menu_actual.fecha_final)

                    for plat in lista_platillos_en_menu:
                        if plat.nombre == nombre:
                            self.menu_actual.agregar_platillo(plat, resultado_val_precio[1])
                            self.agregar_edicion_platillos(copy.deepcopy(self.menu_actual.detalles[-1]))
                            self.menu_actual.cantidad_platillos += 1

                self.mostrar_detalles_menu()

            case "2":
                # modificar precio
                # digamos que aquí se valida el precio
                opciones = [str(idx) for idx in self.platillo_idx]
                lista_platillos = [detalle.platillo for detalle in self.menu_actual.detalles]

                total_pag_platillos = self.obtener_total_paginas_detalles(lista_platillos)

                self.vista.mostrar_platillos_disponibles(lista_platillos, self.pagina_actual_lista_platillos_disp, total_pag_platillos)
                self.vista.refrescar_pantalla()

                num = self.vista.mostrar_seleccionar_editar_platillo_prompt(opciones)

                if num:
                    precio = self.vista.mostrar_ingresar_precio_prompt()

                    resultado_val_precio = self.validador.precio_platillo(precio)

                    while not resultado_val_precio[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_precio[1])
                        precio = self.vista.mostrar_ingresar_precio_prompt()
                        resultado_val_precio = self.validador.precio_platillo(precio)

                    nombre = self.platillo_idx[int(num)]
                    for plDetalles in self.menu_actual.detalles:
                        if plDetalles.platillo.nombre == nombre:
                            plDetalles.precio = resultado_val_precio[1]
                            self.agregar_edicion_platillos(copy.deepcopy(plDetalles))

                self.mostrar_detalles_menu()

            case "3":
                # remover platillo del menú
                opciones = [str(idx) for idx in self.platillo_idx]
                num = self.vista.mostrar_remover_platillo_prompt(opciones)
                # debería validar aquí
                if num is not None:
                    # busca el nombre del platillo basado en el num ingresado,
                    # y lo borra del menú
                    nombre = self.platillo_idx[int(num)]
                    for detalle in self.menu_actual.detalles:
                        if detalle.platillo.nombre == nombre:
                            self.menu_actual.detalles.remove(detalle)
                            self.formulario["item_borrado"] = True
                            self.menu_actual.cantidad_platillos -= 1

                self.mapear_detalle_platillo()
                self.mostrar_detalles_menu()

            case "4":
                # volver a menu editar principal
                self.vista.crear_banda_opciones_editar()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_opciones_editar_prompt()

    def cambiar_pagina_lista_menus(self, mov):
        if mov == ",":
            if self.pagina_actual_lista_menus == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
                self.mostrar_lista_menus()
            else:
                self.pagina_actual_lista_menus -= 1
                pagina, hay_sig_pag = self.paginar_lista_menus(self.menus_a_mostrar, self.pagina_actual_lista_menus)
                self.mostrar_lista_menus(pagina)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_menus(self.menus_a_mostrar, self.pagina_actual_lista_menus)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
                self.mostrar_lista_menus()
            else:
                self.pagina_actual_lista_menus += 1
                pagina, hay_sig_pag = self.paginar_lista_menus(self.menus_a_mostrar, self.pagina_actual_lista_menus)
                self.mostrar_lista_menus(pagina)

    def paginar_lista_menus(self, items: list, num_pag: int):
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
        if mov == ",":
            if self.pagina_actual_lista_detalles == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
                self.mostrar_detalles_menu()
            else:
                self.pagina_actual_lista_detalles -= 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(self.menu_actual.detalles,
                                                               self.pagina_actual_lista_detalles)
                self.mostrar_detalles_menu(pagina)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_detalles(self.menu_actual.detalles, self.pagina_actual_lista_detalles)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
                self.mostrar_detalles_menu()
            else:
                self.pagina_actual_lista_detalles += 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(self.menu_actual.detalles,
                                                               self.pagina_actual_lista_detalles)
                self.mostrar_detalles_menu(pagina)

    def cambiar_pagina_lista_platillos_disp(self, mov):
        lista_platillos = self.filtrar_platillos_duplicados()

        if mov == ",":
            if self.pagina_actual_lista_platillos_disp == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
            else:
                self.pagina_actual_lista_platillos_disp -= 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(lista_platillos,
                                                               self.pagina_actual_lista_platillos_disp)
                total_pag = self.obtener_total_paginas_detalles(lista_platillos)

                self.vista.mostrar_platillos_disponibles(pagina, self.pagina_actual_lista_platillos_disp, total_pag)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_detalles(lista_platillos, self.pagina_actual_lista_platillos_disp)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
            else:
                self.pagina_actual_lista_platillos_disp += 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(lista_platillos,
                                                               self.pagina_actual_lista_platillos_disp)
                total_pag = self.obtener_total_paginas_detalles(lista_platillos)

                self.vista.mostrar_platillos_disponibles(pagina, self.pagina_actual_lista_platillos_disp, total_pag)

    def cambiar_pagina_lista_platillos_conflicto(self, mov):
        if mov == ",":
            if self.pagina_actual_platillos_conflicto == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
            else:
                self.pagina_actual_platillos_conflicto -= 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(self.platillos_conflicto,
                                                               self.pagina_actual_platillos_conflicto)
                total_pag = self.obtener_total_paginas_detalles(self.platillos_conflicto)

                self.vista.mostrar_platillos_conflicto(pagina, self.pagina_actual_platillos_conflicto, total_pag)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_detalles(self.platillos_conflicto, self.pagina_actual_platillos_conflicto)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
            else:
                self.pagina_actual_platillos_conflicto += 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(self.platillos_conflicto,
                                                               self.pagina_actual_platillos_conflicto)
                total_pag = self.obtener_total_paginas_detalles(self.platillos_conflicto)

                self.vista.mostrar_platillos_conflicto(pagina, self.pagina_actual_platillos_conflicto, total_pag)

    def paginar_lista_detalles(self, items: list, num_pag: int):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 18

        idx_inicio = (num_pag - 1) * lineas_disp
        idx_final = idx_inicio + lineas_disp

        if idx_final < len(items):
            prox_pag = True
        else:
            prox_pag = False

        return items[idx_inicio:idx_final], prox_pag

    def obtener_total_paginas_lista_menus(self, items: list):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 6

        return math.ceil(len(items) / lineas_disp)

    def obtener_total_paginas_detalles(self, items: list):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 18

        total = math.ceil(len(items) / lineas_disp)

        if total == 0:
            return 1

        return total