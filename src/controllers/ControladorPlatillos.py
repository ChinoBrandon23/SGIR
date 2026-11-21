import math
from mysql.connector import Error

from Validaciones.validadorPlatillos import validadorPlatillos
from models.platillo import Platillo
from views.VistaPlatillos import VistaPlatillos


class ControladorPlatillos:
    def __init__(self, vista:VistaPlatillos, servicio_platillos, servicio_recetas, validador:validadorPlatillos):
        self.vista = vista
        self.servicio_platillos = servicio_platillos
        self.servicio_recetas = servicio_recetas
        self.validador = validador
        self.platillo_actual = None
        self.formulario = {}

        self.pagina_actual_lista_platillos = 1
        self.pagina_actual_lista_categorias = 1
        self.pagina_actual_lista_recetas = 1

        self.platillos_a_mostrar = None

        self.configurar_listeners()
        self.mostrar_lista_platillos()

    def configurar_listeners(self):
        self.vista.input_menu_platillos.agregar_escuchante(self.evaluar_seleccion_menu_recetas)
        self.vista.input_abrir_detalles.agregar_escuchante(self.mostrar_detalles_platillo)
        self.vista.input_menu_detalles.agregar_escuchante(self.evaluar_seleccion_menu_detalles)
        self.vista.input_menu_editar_platillo.agregar_escuchante(self.evaluar_seleccion_menu_editar)
        self.vista.input_menu_filtros.agregar_escuchante(self.evaluar_seleccion_busqueda_av)

        # Para cambio de páginas
        self.vista.input_menu_platillos.agregar_escuchante(self.cambiar_pagina_lista_platillos)
        self.vista.input_seleccion_categoria.agregar_escuchante(self.cambiar_pagina_lista_categorias)
        self.vista.input_seleccion_receta.agregar_escuchante(self.cambiar_pagina_lista_recetas_disp)
        self.vista.input_menu_filtros.agregar_escuchante(self.cambiar_pagina_lista_platillos)

    def mostrar_lista_platillos(self, pag_platillos=None):
        """
        Conecta con la capa de servicios para obtener la lista de platillos y crea un elemento de lista para cada una.
        """

        if self.platillos_a_mostrar is None:
            self.platillos_a_mostrar = self.servicio_platillos.obtener_platillos()

        self.vista.mostrar_todos_platillos(self.pagina_actual_lista_platillos,
                                           self.obtener_total_paginas_platillos(self.platillos_a_mostrar))

        if pag_platillos is None:
            pag_platillos, hay_prox_pag = self.paginar_lista_platillos(self.platillos_a_mostrar,
                                                                       self.pagina_actual_lista_platillos)

        if self.pagina_actual_lista_platillos == 1:
            idx_ui = 0
        else:
            consola_size = self.vista.console.size[1]
            size_sin_prompt = consola_size - 6
            lineas_disp = size_sin_prompt - 6

            idx_ui = (self.pagina_actual_lista_platillos - 1) * lineas_disp

        for platillo in pag_platillos:
            idx_ui += 1
            self.vista.crear_elemento_tabla_platillos(platillo, idx_ui)

        self.vista.refrescar_pantalla()
        self.vista.mostrar_menu_platillos_prompt()

    def mostrar_detalles_platillo(self, platillo_num=None):
        if self.platillo_actual is None:
            # Si no tenemos un platillo actual, busca el platillo por el num pasado como arg
            # idealmente con un servicio pero por ahora uso un loop para testeo
            self.platillo_actual = self.platillos_a_mostrar[int(platillo_num)-1]

        # llama la función para crear la vista de detalles y le pasa los datos del formulario actual
        self.vista.mostrar_detalles_platillo(self.platillo_actual, datos_editados=self.formulario)

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

    def mostrar_formulario_crear_platillo(self):
        if self.platillo_actual is None:
            self.vista.mostrar_crear_platillo(None)
        else:
            self.vista.mostrar_crear_platillo(self.platillo_actual)
            self.vista.crear_banda_opciones_editar()
            self.vista.refrescar_pantalla()
            self.vista.mostrar_opciones_editar_prompt()

        self.vista.refrescar_pantalla()

    def guardar_editar_platillo(self):
        # Cambia los datos del formulario en el objeto actual
        # para testeo, aquí debería llamar a un servicio

        if self.servicio_platillos.platillo_existe(self.platillo_actual.num):
            try:
                self.servicio_platillos.actualizar_platillo(self.platillo_actual)
                platillo_actual_num = str(self.platillo_actual.num)
            except ValueError:
                self.vista.refrescar_pantalla()
                self.vista.mostrar_mensaje_editar_nombre_duplicado()
                self.vista.mostrar_opciones_editar_prompt()
        else:
            try:
                self.servicio_platillos.crear_platillo(self.platillo_actual)
                platillo_actual_num = self.servicio_platillos.obtener_platillo_por_nombre(self.platillo_actual.nombre).num
                self.platillos_a_mostrar = self.servicio_platillos.obtener_platillos()
            except ValueError, Error:
                self.vista.refrescar_pantalla()
                self.vista.mostrar_mensaje_editar_nombre_duplicado()
                self.vista.mostrar_opciones_editar_prompt()

        # resetea el formulario porque la info ya se guardó y vuelve a la vista de detalles
        # esta debería jalar de nuevo el dato, el cual debería estar actualizado ya

        self.platillos_a_mostrar = self.servicio_platillos.obtener_platillos()
        self.cancelar_edicion_actual()
        self.platillo_actual = self.servicio_platillos.obtener_platillo_por_num(platillo_actual_num)
        self.mostrar_detalles_platillo()

    def cancelar_edicion_actual(self):
        # resetea formulario y platillo actual
        self.pagina_actual_lista_platillos = 1
        self.pagina_actual_lista_categorias = 1
        self.pagina_actual_lista_recetas = 1
        self.platillo_actual = None
        self.formulario = {}

    def usuario_esta_editando(self):
        # checa si el usuario ha hecho cambios desde que entró a la vista de detalles
        if len(self.formulario.items()):
            return True
        return False

    def evaluar_seleccion_menu_recetas(self, seleccion):
        match seleccion:
            case "1":
                # Aquí debería obtener la lista de todos los platillos y pasarla
                self.vista.mostrar_abrir_detalles_prompt(self.platillos_a_mostrar)
            case "2":
                # Aquí crea platillo
                self.mostrar_formulario_crear_platillo()
                nombre = self.vista.mostrar_prompt_crear_platillo()
                if nombre is not None:
                    resultado_val_nombre = self.validador.edicion_nombre_platillo(nombre)

                    while not resultado_val_nombre[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_nombre[1])
                        nombre = self.vista.mostrar_prompt_crear_platillo()
                        if nombre is None:
                            self.mostrar_lista_platillos()
                        else:
                            resultado_val_nombre = self.validador.edicion_nombre_platillo(nombre)

                    self.platillo_actual = Platillo(0, resultado_val_nombre[1])
                    self.mostrar_formulario_crear_platillo()
                else:
                    self.mostrar_lista_platillos()
            case "3":
                # aquí debería haber filtros de búsqueda
                self.vista.crear_banda_opciones_busqueda_av()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_opciones_busqueda_av_prompt()
            case "m":
                # cancela la edicion actual antes de volver al menu
                self.cancelar_edicion_actual()

    def evaluar_seleccion_menu_detalles(self, seleccion):
        match seleccion:
            case "1":
                # volver a la vista de todos los platillos
                self.cancelar_edicion_actual()
                self.mostrar_lista_platillos()
            case "2":
                # abrir opciones de editar platillo
                self.vista.crear_banda_opciones_editar()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_opciones_editar_prompt()
            case "3":
                borrar = self.vista.mostrar_prompt_eliminar_platillo_prompt()
                if borrar:
                    self.servicio_platillos.borrar_platillo(self.platillo_actual.num)

                    self.cancelar_edicion_actual()
                    self.platillos_a_mostrar = self.servicio_platillos.obtener_platillos()
                    self.mostrar_lista_platillos()
                else:
                    self.mostrar_detalles_platillo()

            case "m":
                # volver al menú principal
                self.cancelar_edicion_actual()

    def evaluar_seleccion_busqueda_av(self, seleccion):
        match seleccion:
            case "1":
                # buscar por nombre
                nombre = self.vista.mostrar_buscar_por_nombre_prompt()

                resultados_obtenidos = self.servicio_platillos.obtener_platillos_match_nombre(nombre)

                if len(resultados_obtenidos):
                    self.platillos_a_mostrar = resultados_obtenidos
                else:
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_mensaje_no_resultados_busqueda_av()
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_opciones_busqueda_av_prompt()

                # esta línea se queda aquí
                self.mostrar_lista_platillos()
            case "2":
                # buscar por categoría
                categorias_lista = self.servicio_platillos.obtener_categorias()
                total_pag = self.obtener_total_paginas_detalles(categorias_lista)

                self.vista.mostrar_categorias_disponibles(categorias_lista, self.pagina_actual_lista_categorias, total_pag)
                self.vista.refrescar_pantalla()

                opciones = [str(i + 1) for i in range(len(categorias_lista))]
                num_cat = self.vista.mostrar_buscar_por_categoria_prompt(opciones)

                categoria_clave = [categorias_lista[i] for i in range(len(categorias_lista)) if i == int(num_cat) - 1][0].clave

                resultados_obtenidos = self.servicio_platillos.obtener_platillos_por_categoria(categoria_clave)

                if len(resultados_obtenidos):
                    self.platillos_a_mostrar = resultados_obtenidos
                else:
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_mensaje_no_resultados_busqueda_av()
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_opciones_busqueda_av_prompt()

                self.pagina_actual_lista_categorias = 1
                self.mostrar_lista_platillos()

            case "3":
                # Restablece los resultados para mostrarlos todos, algo como así:
                self.platillos_a_mostrar = self.servicio_platillos.obtener_platillos()

                self.mostrar_lista_platillos()

            case "4":
                # aquí no se debe hacer nada extra, es solo para volver a la vista principal de platillos
                self.mostrar_lista_platillos()

    def evaluar_seleccion_menu_editar(self, seleccion):
        match seleccion:
            case "1":
                # abre prompt para cambiar el nombre del platillo
                nombre = self.vista.mostrar_editar_nombre_prompt()
                # checa que haya una respuesta del usuario y si es así lo debe validar
                if nombre is not None:
                    resultado_val_nombre = self.validador.edicion_nombre_platillo(nombre)

                    while not resultado_val_nombre[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_nombre[1])
                        nombre = self.vista.mostrar_editar_nombre_prompt()
                        if nombre is None:
                            self.mostrar_detalles_platillo()
                        else:
                            resultado_val_nombre = self.validador.edicion_nombre_platillo(nombre)

                    self.platillo_actual.nombre = nombre
                    self.formulario["nombre"] = nombre

                self.mostrar_detalles_platillo()

            case "2":
                # abre prompt para cambiar la categoria
                lista_categorias = self.servicio_platillos.obtener_categorias()

                total_pag = self.obtener_total_paginas_detalles(lista_categorias)
                pagina, prox_pag = self.paginar_lista_categorias(lista_categorias, self.pagina_actual_lista_categorias)

                self.vista.mostrar_categorias_disponibles(pagina, self.pagina_actual_lista_categorias, total_pag)
                self.vista.refrescar_pantalla()
                opciones = [str(i + 1) for i in range(len(lista_categorias))]
                categoria_num = self.vista.mostrar_editar_categoria_prompt(opciones)

                if categoria_num == "0":
                    self.vista.refrescar_pantalla()
                    nombre_cat = self.vista.mostrar_crear_categoria_prompt()

                    if nombre_cat is not None:
                        resultado_val_categoria = self.validador.creacion_categoria(nombre_cat)

                        while not resultado_val_categoria[0]:
                            self.vista.mostrar_mensaje_error_validacion(resultado_val_categoria[1])
                            nombre_cat = self.vista.mostrar_crear_categoria_prompt()
                            resultado_val_categoria = self.validador.creacion_categoria(nombre_cat)

                        self.servicio_platillos.crear_categoria(nombre_cat)
                        categoria = self.servicio_platillos.obtener_categoria_por_nombre(nombre_cat)

                        self.platillo_actual.categoria = categoria
                        self.formulario["categoria"] = categoria

                # checa que haya un valor y luego valída y asigna
                elif categoria_num is not None:
                    categoria = [lista_categorias[i] for i in range(len(lista_categorias)) if i == int(categoria_num)-1][0]
                    self.platillo_actual.categoria = categoria
                    self.formulario["categoria"] = categoria

                self.pagina_actual_lista_categorias = 1
                self.mostrar_detalles_platillo()

            case "3":
                # abre opciones para editar receta base
                lista_recetas = self.servicio_recetas.obtener_recetas()

                total_pag_recetas = self.obtener_total_paginas_detalles(lista_recetas)
                pagina, prox_pag = self.paginar_lista_recetas_disp(lista_recetas, self.pagina_actual_lista_recetas)

                self.vista.mostrar_recetas_disponibles(pagina, self.pagina_actual_lista_recetas, total_pag_recetas)
                self.vista.refrescar_pantalla()

                opciones = [str(receta.num) for receta in lista_recetas]
                num_receta = self.vista.mostrar_editar_receta_base_prompt(opciones)

                if num_receta is not None:
                    receta = [lista_recetas[i] for i in range(len(lista_recetas)) if i == int(num_receta)-1][0]
                    self.platillo_actual.receta = receta
                    self.formulario["receta"] = receta

                self.pagina_actual_lista_recetas = 1
                self.mostrar_detalles_platillo()
            case "4":
                # llama a la función para guardar platillo
                self.guardar_editar_platillo()

            case "5":
                # cancela la edición actual y vuelve a detalles
                if self.platillo_actual and self.platillo_actual.num != "0":
                    num = self.platillo_actual.num
                    self.cancelar_edicion_actual()
                    self.platillo_actual = self.servicio_platillos.obtener_platillo_por_num(num)
                else:
                    self.cancelar_edicion_actual()
                self.mostrar_detalles_platillo()
            case "m":
                # vuelve al menú
                self.cancelar_edicion_actual()

    def cambiar_pagina_lista_platillos(self, mov):
        if mov == ",":
            if self.pagina_actual_lista_platillos == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
                self.mostrar_lista_platillos()
            else:
                self.pagina_actual_lista_platillos -= 1
                pagina, hay_sig_pag = self.paginar_lista_platillos(self.platillos_a_mostrar,
                                                                   self.pagina_actual_lista_platillos)
                self.mostrar_lista_platillos(pagina)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_platillos(self.platillos_a_mostrar, self.pagina_actual_lista_platillos)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
                self.mostrar_lista_platillos()
            else:
                self.pagina_actual_lista_platillos += 1
                pagina, hay_sig_pag = self.paginar_lista_platillos(self.platillos_a_mostrar,
                                                                   self.pagina_actual_lista_platillos)
                self.mostrar_lista_platillos(pagina)

    def paginar_lista_platillos(self, items: list, num_pag: int):
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

    def cambiar_pagina_lista_categorias(self, mov):
        lista_categorias = self.servicio_platillos.obtener_categorias()

        if mov == ",":
            if self.pagina_actual_lista_categorias == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
            else:
                self.pagina_actual_lista_categorias -= 1
                pagina, hay_sig_pag = self.paginar_lista_categorias(lista_categorias,
                                                                   self.pagina_actual_lista_categorias)
                total_pag = self.obtener_total_paginas_detalles(lista_categorias)
                self.vista.mostrar_categorias_disponibles(pagina, self.pagina_actual_lista_categorias, total_pag)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_categorias(lista_categorias, self.pagina_actual_lista_categorias)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
            else:
                self.pagina_actual_lista_categorias += 1
                pagina, hay_sig_pag = self.paginar_lista_categorias(lista_categorias,
                                                                   self.pagina_actual_lista_categorias)
                total_pag = self.obtener_total_paginas_detalles(lista_categorias)
                self.vista.mostrar_categorias_disponibles(pagina, self.pagina_actual_lista_categorias, total_pag)

    def paginar_lista_categorias(self, items: list, num_pag: int):
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

    def cambiar_pagina_lista_recetas_disp(self, mov):
        lista_recetas = self.servicio_recetas.obtener_recetas()

        if mov == ",":
            if self.pagina_actual_lista_recetas == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
            else:
                self.pagina_actual_lista_recetas -= 1
                pagina, hay_sig_pag = self.paginar_lista_recetas_disp(lista_recetas,
                                                                   self.pagina_actual_lista_recetas)
                total_pag = self.obtener_total_paginas_detalles(lista_recetas)
                self.vista.mostrar_recetas_disponibles(pagina, self.pagina_actual_lista_recetas, total_pag)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_recetas_disp(lista_recetas, self.pagina_actual_lista_recetas)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
            else:
                self.pagina_actual_lista_recetas += 1
                pagina, hay_sig_pag = self.paginar_lista_recetas_disp(lista_recetas,
                                                                   self.pagina_actual_lista_recetas)
                total_pag = self.obtener_total_paginas_detalles(lista_recetas)
                self.vista.mostrar_recetas_disponibles(pagina, self.pagina_actual_lista_recetas, total_pag)

    def paginar_lista_recetas_disp(self, items: list, num_pag: int):
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

    def obtener_total_paginas_platillos(self, items: list):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 7

        return math.ceil(len(items) / lineas_disp)

    def obtener_total_paginas_detalles(self, items: list):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 9

        return math.ceil(len(items) / lineas_disp)

