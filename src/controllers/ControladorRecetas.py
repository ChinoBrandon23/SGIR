import copy
import math
from mysql.connector import Error

from models.ingrediente import Ingrediente
from models.receta import Receta
from views.VistaRecetas import VistaRecetas
from Validaciones.validadorReceta import validadorReceta
from services.receta_servicio import RecetaServicio

class ControladorRecetas:
    def __init__(self, vista:VistaRecetas, servicio_receta:RecetaServicio, validador:validadorReceta):
        self.vista = vista
        self.servicio = servicio_receta
        self.validador = validador
        self.receta_actual = None
        self.formulario = {"ingredientes":[], "instrucciones":[], "item_borrado":False}
        self.ing_idx = {}

        self.pagina_actual_lista_recetas = 1
        self.pagina_actual_lista_detalles = 1
        self.pagina_actual_lista_insumos_disponibles = 1
        self.pagina_actual_lista_recetas_disponibles = 1

        self.recetas_a_mostrar = None

        self.configurar_listeners()
        self.mostrar_lista_recetas()

    def configurar_listeners(self):
        self.vista.input_menu_recetas.agregar_escuchante(self.evaluar_seleccion_menu_recetas)
        self.vista.input_abrir_detalles.agregar_escuchante(self.mostrar_detalles_receta)
        self.vista.input_menu_detalles.agregar_escuchante(self.evaluar_seleccion_menu_detalles)
        self.vista.input_menu_editar_receta.agregar_escuchante(self.evaluar_seleccion_menu_editar)
        self.vista.input_menu_editar_ing.agregar_escuchante(self.evaluar_seleccion_editar_ing)
        self.vista.input_menu_editar_inst.agregar_escuchante(self.evaluar_seleccion_editar_inst)
        self.vista.input_menu_filtros.agregar_escuchante(self.evaluar_seleccion_busqueda_av)

        # Para cambiar de página
        self.vista.input_menu_recetas.agregar_escuchante(self.cambiar_pagina_lista_recetas)
        self.vista.input_menu_filtros.agregar_escuchante(self.cambiar_pagina_lista_recetas)
        self.vista.input_menu_detalles.agregar_escuchante(self.cambiar_pagina_lista_detalles)
        self.vista.input_menu_editar_receta.agregar_escuchante(self.cambiar_pagina_lista_detalles)
        self.vista.input_menu_editar_ing.agregar_escuchante(self.cambiar_pagina_lista_detalles)
        self.vista.input_menu_editar_inst.agregar_escuchante(self.cambiar_pagina_lista_detalles)
        self.vista.input_seleccionar_insumo.agregar_escuchante(self.cambiar_pagina_lista_insumos_disponibles)
        self.vista.input_seleccionar_receta.agregar_escuchante(self.cambiar_pagina_lista_recetas_disponibles)


    def mostrar_lista_recetas(self, pag_lista_recetas=None):
        """
        Conecta con la capa de servicios para obtener la lista de recetas y crea un elemento de lista para cada una.

        """
        if self.recetas_a_mostrar is None:
            self.recetas_a_mostrar = self.servicio.obtener_recetas()

        self.vista.mostrar_todas_recetas(self.pagina_actual_lista_recetas,
                                         self.obtener_total_paginas_lista_recetas(self.recetas_a_mostrar))

        if pag_lista_recetas is None:
            pag_lista_recetas, hay_prox_pag = self.paginar_lista_recetas(self.recetas_a_mostrar,
                                                                         self.pagina_actual_lista_recetas)

        if self.pagina_actual_lista_recetas == 1:
            idx_ui = 0
        else:
            consola_size = self.vista.console.size[1]
            size_sin_prompt = consola_size - 6
            lineas_disp = size_sin_prompt - 6

            idx_ui = (self.pagina_actual_lista_recetas - 1) * lineas_disp

        for receta in pag_lista_recetas:
            idx_ui += 1
            self.vista.crear_elemento_tabla_recetas(receta, idx_ui)

        self.vista.refrescar_pantalla()
        self.vista.mostrar_menu_recetas_prompt()

    def mostrar_detalles_receta(self, receta_num = None):
        if self.receta_actual is None:
            # Si no tenemos una receta actual, busca la receta por el num pasado como arg
            self.receta_actual = self.recetas_a_mostrar[int(receta_num)-1]
            # self.receta_actual = self.servicio.obtener_receta_por_id(receta_num)

        self.mapear_ingredientes()

        # paginado
        pagina_detalles, prox_pag = self.crear_paginado_detalles_receta()
        total_paginas = self.obtener_total_paginas_detalles()

        # llama la función para crear la vista de tabla de detalles y le pasa los datos del formulario actual
        self.vista.mostrar_detalles_receta(self.receta_actual, pagina_detalles=pagina_detalles,  pag_actual=self.pagina_actual_lista_detalles, total_pag=total_paginas, datos_editados=self.formulario, mapa_idx_ing=self.ing_idx)

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

    def mostrar_formulario_crear_receta(self):
        if self.receta_actual is None:
            self.vista.mostrar_crear_receta(None, self.ing_idx)
        else:
            self.vista.mostrar_crear_receta(self.receta_actual, self.ing_idx)
            self.vista.crear_banda_opciones_editar()
            self.vista.refrescar_pantalla()
            self.vista.mostrar_opciones_editar_prompt()

        self.vista.refrescar_pantalla()

    def guardar_receta(self):
        # Cambia los datos del formulario en el objeto actual

        if self.servicio.receta_existe(self.receta_actual.num):
            try:
                self.servicio.actualizar_receta(self.receta_actual)
                receta_num = self.receta_actual.num
            except Error:
                self.vista.refrescar_pantalla()
                self.vista.mostrar_error_receta_nombre_duplicado()
                self.vista.mostrar_opciones_editar_prompt()
        else:
            try:
                self.servicio.crear_receta(self.receta_actual)
                receta_num = self.servicio.obtener_receta_por_nombre(self.receta_actual.nombre).num
                self.recetas_a_mostrar = self.servicio.obtener_recetas()
            except ValueError:
                self.vista.refrescar_pantalla()
                self.vista.mostrar_error_crear_receta_duplicado()
                self.vista.mostrar_opciones_editar_prompt()

        # resetea el formulario porque la info ya se guardó y vuelve a la vista de detalles
        # esta debería jalar de nuevo el dato, el cual debería estar actualizado ya
        self.recetas_a_mostrar = self.servicio.obtener_recetas()
        self.cancelar_edicion_actual()
        self.receta_actual = self.servicio.obtener_receta_por_id(receta_num)
        self.mostrar_detalles_receta()

    def agregar_edicion_instruccion(self, dic_inst):
        lista_inst_editadas_idx = [next(iter(inst)) for inst in self.formulario["instrucciones"]]

        if next(iter(dic_inst)) in lista_inst_editadas_idx:
            # instruccion editada doble se remueve
            obj = [inst for inst in self.formulario["instrucciones"] if next(iter(inst)) == next(iter(dic_inst))][0]
            self.formulario["instrucciones"].remove(obj)

        self.formulario["instrucciones"].append(dic_inst)

    def filtrar_ingredientes_duplicados(self, lista_ingredientes_dispo:list[Ingrediente]):
        lista_ing_utilizados = [ing.ingrediente.nombre for ing in self.receta_actual.lista_ingredientes]

        ing_disponibles = [ing for ing in lista_ingredientes_dispo if ing.nombre not in lista_ing_utilizados]

        return ing_disponibles

    def mapear_ingredientes(self):
        # toma los ingredientes de la receta
        # itera sobre cada uno y les asigna un número para mostrar en la tabla de la vista
        if self.receta_actual:
            self.ing_idx = {}
            lista_ing = self.receta_actual.lista_ingredientes

            for i in range(len(lista_ing)):
                # agregando al dict los ingredientes originales de la receta
                self.ing_idx[i + 1] = lista_ing[i].ingrediente.nombre

    def usuario_esta_editando(self):
        # checa si el usuario ha hecho cambios desde que entró a la vista de detalles
        if len(self.formulario.items()) > 3 or len(self.formulario["ingredientes"]) or len(self.formulario["instrucciones"]) or self.formulario["item_borrado"]:
            return True
        return False

    def cancelar_edicion_actual(self):
        self.pagina_actual_lista_recetas = 1
        self.pagina_actual_lista_detalles = 1
        self.pagina_actual_lista_insumos_disponibles = 1
        self.pagina_actual_lista_recetas_disponibles = 1
        self.receta_actual = None
        self.formulario = {"ingredientes": [], "instrucciones": [], "item_borrado": False}

    def evaluar_seleccion_menu_recetas(self, seleccion):
        match seleccion:
            case "1":
                # Aquí debería obtener la lista de todas las recetas y pasarlas
                opciones = self.servicio.obtener_recetas()
                self.vista.mostrar_abrir_detalles_prompt(opciones)
            case "2":
                # Aquí crea receta
                self.mostrar_formulario_crear_receta()
                nombre = self.vista.mostrar_prompt_crear_receta_nombre()

                if nombre is not None:
                    resultado_val_nombre = self.validador.editar_nombre(nombre)

                    while not resultado_val_nombre[0]:
                        self.vista.mostrar_error_validacion(resultado_val_nombre[1])
                        nombre = self.vista.mostrar_prompt_crear_receta_nombre()
                        resultado_val_nombre = self.validador.editar_nombre(nombre)

                    porciones = self.vista.mostrar_prompt_crear_receta_porciones()
                    resultado_val_porcion = self.validador.validar_editar_porciones(porciones)

                    while not resultado_val_porcion[0]:
                        self.vista.mostrar_error_validacion(resultado_val_porcion[1])
                        porciones = self.vista.mostrar_prompt_crear_receta_porciones()
                        resultado_val_porcion = self.validador.validar_editar_porciones(porciones)

                    self.receta_actual = Receta(0, resultado_val_nombre[1], resultado_val_porcion[1], {})
                    self.mapear_ingredientes()
                    self.mostrar_formulario_crear_receta()
                else:
                    self.mostrar_lista_recetas()
            case "3":
                # búsqueda avanzada
                self.vista.crear_banda_opciones_busqueda_av()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_opciones_busqueda_av_prompt()

            case "m":
                # cancela la edicion actual antes de volver al menu
                self.cancelar_edicion_actual()

    def evaluar_seleccion_menu_detalles(self, seleccion):
        match seleccion:
            case "1":
                # volver a la vista de todas las recetas
                self.cancelar_edicion_actual()
                self.mostrar_lista_recetas()
            case "2":
                # abrir opciones de editar receta
                self.vista.crear_banda_opciones_editar()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_opciones_editar_prompt()
            case "3":
                borrar = self.vista.mostrar_prompt_eliminar_receta_prompt()
                if borrar:
                    self.servicio.borrar_receta(self.receta_actual.num)

                    self.cancelar_edicion_actual()
                    self.recetas_a_mostrar = self.servicio.obtener_recetas()
                    self.mostrar_lista_recetas()

                self.mostrar_detalles_receta()
            case "m":
                # volver al menú principal
                self.cancelar_edicion_actual()

    def evaluar_seleccion_busqueda_av(self, seleccion):
        match seleccion:
            case "1":
                # buscar por nombre
                nombre = self.vista.mostrar_buscar_por_nombre_prompt()

                recetas_encontradas = self.servicio.obtener_recetas_por_match_nombre(nombre)

                if len(recetas_encontradas):
                    self.recetas_a_mostrar = recetas_encontradas
                    self.mostrar_lista_recetas()
                else:
                    self.vista.mostrar_mensaje_no_resultados_busqueda_av()
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_opciones_busqueda_av_prompt()

            case "2":
                # buscar por num porciones
                num_porciones = self.vista.mostrar_buscar_por_porciones_prompt()

                recetas_encontradas = self.servicio.obtener_recetas_por_num_porciones(int(num_porciones))

                if len(recetas_encontradas):
                    self.recetas_a_mostrar = recetas_encontradas
                    self.mostrar_lista_recetas()
                else:
                    self.vista.mostrar_mensaje_no_resultados_busqueda_av()
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_opciones_busqueda_av_prompt()

            case "3":
                # buscar todos (restaurar búsqueda)
                self.recetas_a_mostrar = self.servicio.obtener_recetas()
                self.mostrar_lista_recetas()

            case "4":
                # volver a lista de compras
                # aquí no se hace nada
                self.mostrar_lista_recetas()

    def evaluar_seleccion_menu_editar(self, seleccion):
        match seleccion:
            case "1":
                # abre prompt para cambiar el nombre de la receta
                nombre = self.vista.mostrar_editar_nombre_prompt()
                if nombre is not None:
                    resultado_val_nombre = self.validador.editar_nombre(nombre)

                    while not resultado_val_nombre[0]:
                        self.vista.mostrar_error_validacion(resultado_val_nombre[1])
                        nombre = self.vista.mostrar_editar_nombre_prompt()
                        resultado_val_nombre = self.validador.editar_nombre(nombre)

                    self.receta_actual.nombre = resultado_val_nombre[1]
                    self.formulario["nombre"] = resultado_val_nombre[1]
                self.mostrar_detalles_receta()

            case "2":
                # abre prompt para cambiar el num de porciones
                porciones = self.vista.mostrar_editar_porciones_prompt()
                # checa que haya un valor y luego valida el num de porciones
                if porciones is not None:
                    resultado_val_porciones = self.validador.validar_editar_porciones(porciones)

                    while not resultado_val_porciones[0]:
                        self.vista.mostrar_error_validacion(resultado_val_porciones[1])
                        nombre = self.vista.mostrar_editar_porciones_prompt()
                        resultado_val_porciones = self.validador.validar_editar_porciones(nombre)

                    self.receta_actual.num_porciones = resultado_val_porciones[1]
                    self.formulario["porciones"] = resultado_val_porciones[1]
                self.mostrar_detalles_receta()

            case "3":
                # abre opciones para editar ing
                self.vista.crear_banda_opciones_editar_ingrediente()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_opciones_editar_ing_prompt()

            case "4":
                # abre opciones para editar instrucciones
                self.vista.crear_banda_opciones_editar_instrucciones()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_opciones_editar_inst_prompt()
            case "5":
                # llama a la función para guardar receta
                self.guardar_receta()
            case "6":
                # cancela la edición actual y vuelve a detalles
                if self.receta_actual.num in [receta.num for receta in self.recetas_a_mostrar]:
                    self.cancelar_edicion_actual()
                    self.receta_actual = self.servicio.obtener_receta_por_id(self.vista.input_abrir_detalles.user_input)
                    self.mostrar_detalles_receta()
                else:
                    self.cancelar_edicion_actual()
                    self.mostrar_lista_recetas()
            case "m":
                # vuelve al menú
                self.cancelar_edicion_actual()

    def evaluar_seleccion_editar_ing(self, seleccion):
        match seleccion:
            case "1":
                # crear nuevo ingrediente
                seleccion_ingrediente = self.vista.mostrar_crear_ingrediente_prompt()

                if seleccion_ingrediente == "1":
                    # seleccionando ingrediente basado en insumo
                    # aquí debería obtener la lista de ingredientes existentes y que no se repiten ya en la receta actual
                    # para evitar duplicados
                    lista_todos_ing = self.servicio.obtener_ingredientes_basados_en_insumo()
                    ing_disponibles = self.filtrar_ingredientes_duplicados(lista_todos_ing)

                    opciones = [str(i+1) for i in range(len(ing_disponibles))]

                    pagina, prox_pag = self.paginar_lista_recetas(ing_disponibles, self.pagina_actual_lista_insumos_disponibles)
                    total_pag = self.obtener_total_paginas_lista_recetas(ing_disponibles)

                    self.vista.mostrar_ingredientes_disponibles(pagina, self.pagina_actual_lista_insumos_disponibles, total_pag)
                    self.vista.refrescar_pantalla()

                    ins_num = self.vista.mostrar_seleccionar_insumo_ing_prompt(opciones)
                    ing_obj = ing_disponibles[int(ins_num)-1]

                    cantidad = self.vista.mostrar_ingresar_cantidad_ing_prompt()
                    resultado_val_cantidad = self.validador.editar_cantidad_ingrediente(cantidad)

                    while not resultado_val_cantidad[0]:
                        self.vista.mostrar_error_validacion(resultado_val_cantidad[1])
                        cantidad = self.vista.mostrar_ingresar_cantidad_ing_prompt()
                        resultado_val_cantidad = self.validador.editar_cantidad_ingrediente(cantidad)

                    unidad_medida = self.vista.mostrar_ingresar_unidad_medida_ing_prompt()
                    resultado_val_unidad_m = self.validador.editar_unidad_ingrediente(unidad_medida)

                    while not resultado_val_unidad_m[0]:
                        self.vista.mostrar_error_validacion(resultado_val_unidad_m[1])
                        unidad_medida = self.vista.mostrar_ingresar_unidad_medida_ing_prompt()
                        resultado_val_unidad_m = self.validador.editar_unidad_ingrediente(unidad_medida)

                    self.receta_actual.agregarIngrediente(ingrediente=ing_obj, cantidad=resultado_val_cantidad[1], unidad_medida=resultado_val_unidad_m[1])

                    self.pagina_actual_lista_insumos_disponibles = 1
                    self.formulario["ingredientes"].append(ing_obj.nombre)

                if seleccion_ingrediente == "2":
                    # seleccionando ingrediente basado en receta
                    lista_todos_ing = self.servicio.obtener_ingredientes_basados_en_receta()
                    ing_disponibles = self.filtrar_ingredientes_duplicados(lista_todos_ing)

                    opciones = [str(i+1) for i in range(len(ing_disponibles))]

                    pagina, prox_pag = self.paginar_lista_recetas(ing_disponibles, self.pagina_actual_lista_recetas_disponibles)
                    total_pag = self.obtener_total_paginas_lista_recetas(ing_disponibles)

                    self.vista.mostrar_ingredientes_disponibles(pagina, self.pagina_actual_lista_recetas_disponibles, total_pag)
                    self.vista.refrescar_pantalla()

                    ins_num = self.vista.mostrar_seleccionar_receta_ing_prompt(opciones)
                    ing_obj = ing_disponibles[int(ins_num)-1]

                    cantidad = self.vista.mostrar_ingresar_cantidad_ing_prompt()
                    resultado_val_cantidad = self.validador.editar_cantidad_ingrediente(cantidad)

                    while not resultado_val_cantidad[0]:
                        self.vista.mostrar_error_validacion(resultado_val_cantidad[1])
                        cantidad = self.vista.mostrar_ingresar_cantidad_ing_prompt()
                        resultado_val_cantidad = self.validador.editar_cantidad_ingrediente(cantidad)

                    unidad_medida = self.vista.mostrar_ingresar_unidad_medida_ing_prompt()
                    resultado_val_unidad_m = self.validador.editar_unidad_ingrediente(unidad_medida)

                    while not resultado_val_unidad_m[0]:
                        self.vista.mostrar_error_validacion(resultado_val_unidad_m[1])
                        unidad_medida = self.vista.mostrar_ingresar_unidad_medida_ing_prompt()
                        resultado_val_unidad_m = self.validador.editar_unidad_ingrediente(unidad_medida)

                    self.receta_actual.agregarIngrediente(ingrediente=ing_obj, cantidad=resultado_val_cantidad[1],
                                                          unidad_medida=resultado_val_unidad_m[1])

                    self.pagina_actual_lista_recetas_disponibles = 1
                    self.formulario["ingredientes"].append(ing_obj.nombre)

                self.mostrar_detalles_receta()

            case "2":
                # modificar ingrediente
                opciones_idx = [str(ing) for ing in self.ing_idx]

                num_ing = self.vista.mostrar_seleccionar_ingrediente_prompt(opciones_idx)

                cantidad = self.vista.mostrar_ingresar_cantidad_ing_prompt()
                resultado_val_cantidad = self.validador.editar_cantidad_ingrediente(cantidad)

                while not resultado_val_cantidad[0]:
                    self.vista.mostrar_error_validacion(resultado_val_cantidad[1])
                    cantidad = self.vista.mostrar_ingresar_cantidad_ing_prompt()
                    resultado_val_cantidad = self.validador.editar_cantidad_ingrediente(cantidad)

                unidad_medida = self.vista.mostrar_ingresar_unidad_medida_ing_prompt()
                resultado_val_unidad_m = self.validador.editar_unidad_ingrediente(unidad_medida)

                while not resultado_val_unidad_m[0]:
                    self.vista.mostrar_error_validacion(resultado_val_unidad_m[1])
                    unidad_medida = self.vista.mostrar_ingresar_unidad_medida_ing_prompt()
                    resultado_val_unidad_m = self.validador.editar_unidad_ingrediente(unidad_medida)

                self.receta_actual.lista_ingredientes[int(num_ing)-1].cantidad = cantidad
                self.receta_actual.lista_ingredientes[int(num_ing) - 1].unidad_medida = unidad_medida

                nombre = self.receta_actual.lista_ingredientes[int(num_ing)-1].ingrediente.nombre

                self.formulario["ingredientes"].append(nombre)

                self.mostrar_detalles_receta()

            case "3":
                #borra ingrediente
                opciones_idx = [str(ing) for ing in self.ing_idx]
                num_ing = self.vista.mostrar_borrar_ingrediente_prompt(opciones_idx)
                if num_ing is not None:
                    # busca el nombre del ing basado en el num ingresado,
                    # luego busca el obj IngredientesReceta de la receta actual basado en el nombre
                    # y lo borra de la receta
                    nombre = self.ing_idx[int(num_ing)]
                    self.receta_actual.lista_ingredientes = [ing for ing in self.receta_actual.lista_ingredientes if not ing.ingrediente.nombre == nombre]
                    self.formulario["item_borrado"] = True

                self.mostrar_detalles_receta()

            case "4":
                # volver a menu editar principal
                self.vista.crear_banda_opciones_editar()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_opciones_editar_prompt()

    def evaluar_seleccion_editar_inst(self, seleccion):
        match seleccion:
            case "1":
                instruccion = self.vista.mostrar_agregar_instruccion_prompt()
                if instruccion is not None:
                    resultado_val_instruccion = self.validador.validar_crear_instruccion(instruccion)

                    while not resultado_val_instruccion[0]:
                        self.vista.mostrar_error_validacion(resultado_val_instruccion[1])
                        instruccion = self.vista.mostrar_agregar_instruccion_prompt()
                        resultado_val_instruccion = self.validador.validar_crear_instruccion(instruccion)

                    lista_indices = [key for key in self.receta_actual.instrucciones]

                    if len(lista_indices) > 0:
                        idx = lista_indices[-1] + 1
                    else:
                        idx = 1

                    self.receta_actual.instrucciones[idx] = resultado_val_instruccion[1]
                    self.agregar_edicion_instruccion({idx:resultado_val_instruccion[1]})
                self.mostrar_detalles_receta()

            case "2":
                opciones = [str(idx) for idx in self.receta_actual.instrucciones]
                idx = self.vista.mostrar_seleccionar_instruccion_prompt(opciones)

                if idx is not None:
                    instruccion = self.vista.mostrar_editar_instruccion_prompt()

                    if instruccion:
                        resultado_val_instruccion = self.validador.validar_crear_instruccion(instruccion)

                        while not resultado_val_instruccion[0]:
                            self.vista.mostrar_error_validacion(resultado_val_instruccion[1])
                            instruccion = self.vista.mostrar_agregar_instruccion_prompt()
                            resultado_val_instruccion = self.validador.validar_crear_instruccion(instruccion)

                    self.receta_actual.instrucciones[int(idx)] = instruccion
                    self.agregar_edicion_instruccion({idx:instruccion})

                self.mostrar_detalles_receta()

            case "3":
                opciones = [str(idx) for idx in self.receta_actual.instrucciones]
                idx = self.vista.mostrar_borrar_instruccion_prompt(opciones)

                if idx is not None:
                    # borra la instruccion por su número
                    del self.receta_actual.instrucciones[int(idx)]

                    # toma las instrucciones restantes y las coloca en una lista
                    lista_inst = [v for k, v in self.receta_actual.instrucciones.items()]
                    nuevo_dict_inst = {}

                    for i in range(len(lista_inst)):
                        # crea un nuevo dict y agrega cada inst con un nuevo índice
                        nuevo_dict_inst[i + 1] = lista_inst[i]

                    # asigna el nuevo dict con las instrucciones "recorridas" a la receta actual
                    self.receta_actual.instrucciones = copy.deepcopy(nuevo_dict_inst)
                    self.formulario["item_borrado"] = True

                self.mostrar_detalles_receta()

            case "4":
                # volver a menu editar principal
                self.vista.crear_banda_opciones_editar()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_opciones_editar_prompt()

    def cambiar_pagina_lista_recetas(self, mov):
        if mov == ",":
            if self.pagina_actual_lista_recetas == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
                self.mostrar_lista_recetas()
            else:
                self.pagina_actual_lista_recetas -= 1
                pagina, hay_sig_pag = self.paginar_lista_recetas(self.recetas_a_mostrar, self.pagina_actual_lista_recetas)
                self.mostrar_lista_recetas(pagina)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_recetas(self.recetas_a_mostrar, self.pagina_actual_lista_recetas)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
                self.mostrar_lista_recetas()
            else:
                self.pagina_actual_lista_recetas += 1
                pagina, hay_sig_pag = self.paginar_lista_recetas(self.recetas_a_mostrar, self.pagina_actual_lista_recetas)
                self.mostrar_lista_recetas(pagina)

    def paginar_lista_recetas(self, items: list, num_pag: int):
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
                self.mostrar_detalles_receta()
            else:
                self.pagina_actual_lista_detalles -= 1
                pagina, sig_pag = self.crear_paginado_detalles_receta()
                self.mostrar_detalles_receta(pagina)

        elif mov == ".":
            pagina, sig_pag = self.crear_paginado_detalles_receta()
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
                self.mostrar_detalles_receta()
            else:
                self.pagina_actual_lista_detalles += 1
                pagina, sig_pag = self.crear_paginado_detalles_receta()
                self.mostrar_detalles_receta(pagina)

    def crear_paginado_detalles_receta(self):
        lista_detalles_ingredientes, prox_pag_ing = self.paginar_lista_detalles(self.receta_actual.lista_ingredientes,
                                                                            self.pagina_actual_lista_detalles)

        lista_detalles_instrucciones, prox_pag_ins = self.paginar_lista_detalles(list(self.receta_actual.instrucciones.items()),
                                                                             self.pagina_actual_lista_detalles)

        if prox_pag_ing or prox_pag_ins:
            prox_pag = True
        else:
            prox_pag = False

        diccionario_instrucciones = dict()

        for item in lista_detalles_instrucciones:
            diccionario_instrucciones[item[0]] = item[1]

        pagina_dict = dict()
        pagina_dict["lista_ingredientes"] = lista_detalles_ingredientes
        pagina_dict["instrucciones"] = diccionario_instrucciones

        return pagina_dict, prox_pag

    def paginar_lista_detalles(self, items: list, num_pag: int):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 8

        idx_inicio = (num_pag - 1) * lineas_disp
        idx_final = idx_inicio + lineas_disp

        if idx_final < len(items):
            prox_pag = True
        else:
            prox_pag = False

        return items[idx_inicio:idx_final], prox_pag

    def cambiar_pagina_lista_insumos_disponibles(self, mov):
        lista_insumos = self.servicio.obtener_ingredientes_basados_en_insumo()
        lista_insumos_filtrados = self.filtrar_ingredientes_duplicados(lista_insumos)

        total_pag = self.obtener_total_paginas_lista_recetas(lista_insumos_filtrados)

        if mov == ",":
            if self.pagina_actual_lista_insumos_disponibles == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
            else:
                self.pagina_actual_lista_insumos_disponibles -= 1
                pagina, hay_sig_pag = self.paginar_lista_recetas(lista_insumos_filtrados, self.pagina_actual_lista_insumos_disponibles)
                self.vista.mostrar_ingredientes_disponibles(pagina, self.pagina_actual_lista_insumos_disponibles, total_pag)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_recetas(lista_insumos_filtrados, self.pagina_actual_lista_insumos_disponibles)

            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
            else:
                self.pagina_actual_lista_insumos_disponibles += 1
                pagina, hay_sig_pag = self.paginar_lista_recetas(lista_insumos_filtrados, self.pagina_actual_lista_insumos_disponibles)
                self.vista.mostrar_ingredientes_disponibles(pagina, self.pagina_actual_lista_insumos_disponibles, total_pag)

    def cambiar_pagina_lista_recetas_disponibles(self, mov):
        lista_recetas = self.servicio.obtener_ingredientes_basados_en_receta()
        lista_recetas_filtradas = self.filtrar_ingredientes_duplicados(lista_recetas)

        total_pag = self.obtener_total_paginas_lista_recetas(lista_recetas_filtradas)

        if mov == ",":
            if self.pagina_actual_lista_recetas_disponibles == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
            else:
                self.pagina_actual_lista_recetas_disponibles -= 1
                pagina, hay_sig_pag = self.paginar_lista_recetas(lista_recetas_filtradas, self.pagina_actual_lista_recetas_disponibles)
                self.vista.mostrar_ingredientes_disponibles(pagina, self.pagina_actual_lista_recetas_disponibles, total_pag)

        elif mov == ".":
            pagina, sig_pag = self.paginar_lista_recetas(lista_recetas_filtradas, self.pagina_actual_lista_recetas_disponibles)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
            else:
                self.pagina_actual_lista_recetas_disponibles += 1
                pagina, hay_sig_pag = self.paginar_lista_recetas(lista_recetas_filtradas, self.pagina_actual_lista_recetas_disponibles)
                self.vista.mostrar_ingredientes_disponibles(pagina, self.pagina_actual_lista_recetas_disponibles, total_pag)

    def obtener_total_paginas_lista_recetas(self, items: list):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 6

        if len(items) == 0:
            return 1

        return math.ceil(len(items) / lineas_disp)

    def obtener_total_paginas_detalles(self):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 8

        if len(self.receta_actual.lista_ingredientes) == 0 and len(self.receta_actual.instrucciones) == 0:
            return 1

        if len(self.receta_actual.lista_ingredientes) > len(self.receta_actual.instrucciones):
            items = self.receta_actual.lista_ingredientes
        else:
            items = self.receta_actual.instrucciones

        return math.ceil(len(items) / lineas_disp)
