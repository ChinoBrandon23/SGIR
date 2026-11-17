import copy
import math
import sys
import time

from models.ingrediente import Ingrediente
from models.insumo import Insumo
from models.marca import Marca
from models.receta import Receta
from models.tipo_insumo import TipoInsumo
from services.inventario_servicio import InventarioServicio 
from views.VistaRecetas import VistaRecetas

from services.receta_servicio import RecetaServicio

class ControladorRecetas:
    def __init__(self, vista:VistaRecetas, servicio_receta:RecetaServicio):
        self.vista = vista
        self.servicio = servicio_receta
        self.receta_actual = None
        self.formulario = {"ingredientes":[], "instrucciones":[], "item_borrado":False}
        self.ing_idx = {}

        self.pagina_actual_lista_compras = 1
        self.pagina_actual_lista_detalles = 1

        self.recetas_testeo = None

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

    def mostrar_lista_recetas(self, lista_recetas=None):
        """
        Conecta con la capa de servicios para obtener la lista de recetas y crea un elemento de lista para cada una.

        """
        if self.recetas_testeo is None:
            self.recetas_testeo = self.servicio.obtener_recetas()

        self.vista.mostrar_todas_recetas(self.pagina_actual_lista_compras,
                                         self.obtener_total_paginas_lista_compras(self.recetas_testeo))

        if lista_recetas is None:
            lista_recetas, hay_prox_pag = self.paginar_lista_recetas(self.recetas_testeo,
                                                                     self.pagina_actual_lista_compras)

        for receta in lista_recetas:
            self.vista.crear_elemento_tabla_recetas(receta)

        self.vista.refrescar_pantalla()
        self.vista.mostrar_menu_recetas_prompt()

    def mostrar_detalles_receta(self, receta_num = None):
        if self.receta_actual is None:
            # Si no tenemos una receta actual, busca la receta por el num pasado como arg
            self.receta_actual = self.servicio.obtener_receta_por_id(receta_num)
        self.mapear_ingredientes()
        # llama la función para crear la vista de tabla de detalles y le pasa los datos del formulario actual
        self.vista.mostrar_detalles_receta(self.receta_actual, datos_editados=self.formulario, mapa_idx_ing=self.ing_idx)

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

    def guardar_editar_receta(self):
        # Cambia los datos del formulario en el objeto actual
        # para testeo, aquí debería llamar a un servicio

        self.servicio.actualizar_receta(self.receta_actual)

        # resetea el formulario porque la info ya se guardó y vuelve a la vista de detalles
        # esta debería jalar de nuevo el dato, el cual debería estar actualizado ya
        receta_actual_num = str(self.receta_actual.num)
        self.cancelar_edicion_actual()
        self.mostrar_detalles_receta(receta_actual_num)

    def agregar_edicion_instruccion(self, dic_inst):
        lista_inst_editadas_idx = [next(iter(inst)) for inst in self.formulario["instrucciones"]]

        if next(iter(dic_inst)) in lista_inst_editadas_idx:
            # instruccion editada doble se remueve
            obj = [inst for inst in self.formulario["instrucciones"] if next(iter(inst)) == next(iter(dic_inst))][0]
            self.formulario["instrucciones"].remove(obj)

        self.formulario["instrucciones"].append(dic_inst)

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
        self.receta_actual = None
        self.formulario = {"ingredientes": [], "instrucciones": [], "item_borrado": False}

    def evaluar_seleccion_menu_recetas(self, seleccion):
        match seleccion:
            case "1":
                # Aquí debería obtener la lista de todas las recetas y pasarlas
                self.recetas_testeo = self.servicio.obtener_recetas()
                self.vista.mostrar_abrir_detalles_prompt(self.recetas_testeo)
            case "2":
                # Aquí crea receta
                self.mostrar_formulario_crear_receta()
                nombre, porciones = self.vista.mostrar_prompt_crear_receta()
                if nombre is not None and porciones is not None:
                    # debería llamar al servicio para crear una receta nueva
                    num = len(self.recetas_testeo) + 1
                    self.receta_actual = Receta(num, nombre, porciones, {})
                    self.servicio.crear_receta(receta=self.receta_actual)
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
                self.mostrar_lista_recetas()
            case "m":
                # volver al menú principal
                self.cancelar_edicion_actual()

    def evaluar_seleccion_busqueda_av(self, seleccion):
        match seleccion:
            case "1":
                # buscar por nombre
                nombre = self.vista.mostrar_buscar_por_nombre_prompt()

                # busca el nombre validado con un servicio y la lista resultante se asigna a self.recetas_testeo

                self.mostrar_lista_recetas()

            case "2":
                # buscar por num porciones
                num_porciones = self.vista.mostrar_buscar_por_porciones_prompt()

                # usa el num_porciones para buscar por num de porciones, y se asigna a self.compras_testeo como arriba

                self.mostrar_lista_recetas()

            case "3":
                # buscar todos (restaurar búsqueda)
                self.recetas_testeo = self.servicio.obtener_recetas()

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
                # checa que haya una respuesta del usuario y si es así lo debe validar
                if nombre is not None:
                    self.receta_actual.nombre = nombre
                    self.formulario["nombre"] = nombre
                self.mostrar_detalles_receta()

            case "2":
                # abre prompt para cambiar el num de porciones
                porciones = self.vista.mostrar_editar_porciones_prompt()
                # checa que haya un valor y luego valida el num de porciones
                if porciones is not None:
                    self.receta_actual.num_porciones = porciones
                    self.formulario["porciones"] = porciones
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
                self.guardar_editar_receta()
            case "6":
                # cancela la edición actual y vuelve a detalles
                if self.receta_actual.num in [receta.num for receta in self.recetas_testeo]:
                    self.cancelar_edicion_actual()
                    self.mostrar_detalles_receta(self.vista.input_abrir_detalles.user_input)
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

                    lista_ing_utilizados = [ing.ingrediente.nombre for ing in self.receta_actual.lista_ingredientes]

                    ing_disponibles = [ing for ing in lista_todos_ing if ing.nombre not in lista_ing_utilizados]
                    opciones = [str(i + 1) for i in range(len(ing_disponibles))]

                    self.vista.mostrar_ingredientes_disponibles(ing_disponibles)
                    self.vista.refrescar_pantalla()

                    ins_num = self.vista.mostrar_seleccionar_insumo_prompt(opciones)
                    ing_obj = ing_disponibles[int(ins_num)-1]

                    cantidad = self.vista.mostrar_ingresar_cantidad_ing_prompt()

                    unidad_medida = self.vista.mostrar_ingresar_unidad_medida_ing_prompt()

                    self.receta_actual.agregarIngrediente(ingrediente=ing_obj, cantidad=cantidad, unidad_medida=unidad_medida)

                    self.formulario["ingredientes"].append(ing_obj.nombre)

                if seleccion_ingrediente == "2":
                    # seleccionando ingrediente basado en receta
                    lista_todos_ing = self.servicio.obtener_ingredientes_basados_en_receta()

                    lista_ing_utilizados = [ing.ingrediente.nombre for ing in self.receta_actual.lista_ingredientes]

                    ing_disponibles = [ing for ing in lista_todos_ing if ing.nombre not in lista_ing_utilizados]
                    opciones = [str(i + 1) for i in range(len(ing_disponibles))]

                    self.vista.mostrar_ingredientes_disponibles(ing_disponibles)
                    self.vista.refrescar_pantalla()

                    ins_num = self.vista.mostrar_seleccionar_insumo_prompt(opciones)
                    ing_obj = ing_disponibles[int(ins_num) - 1]

                    cantidad = self.vista.mostrar_ingresar_cantidad_ing_prompt()

                    unidad_medida = self.vista.mostrar_ingresar_unidad_medida_ing_prompt()

                    self.receta_actual.agregarIngrediente(ingrediente=ing_obj, cantidad=cantidad,
                                                          unidad_medida=unidad_medida)

                    self.formulario["ingredientes"].append(ing_obj.nombre)

                self.mostrar_detalles_receta()

            case "2":
                # modificar ingrediente
                opciones_idx = [str(ing) for ing in self.ing_idx]

                num_ing, cantidad, unidad_m = self.vista.mostrar_modificar_ingrediente_prompt(opciones_idx)

                if cantidad is not None and unidad_m is not None:
                    # busca el ing con el num y asigna los datos
                    self.receta_actual.lista_ingredientes[int(num_ing)-1].cantidad = cantidad
                    self.receta_actual.lista_ingredientes[int(num_ing) - 1].unidad_medida = unidad_m

                    nombre = self.receta_actual.lista_ingredientes[int(num_ing)-1].ingrediente.nombre

                    self.formulario["ingredientes"].append(nombre)

                self.mostrar_detalles_receta()

            case "3":
                #borra ingrediente
                opciones_idx = [str(ing) for ing in self.ing_idx]
                num_ing = self.vista.mostrar_borrar_ingrediente_prompt(opciones_idx)
                # debería validar aquí
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
                    lista_indices = [key for key in self.receta_actual.instrucciones]

                    if len(lista_indices) > 0:
                        idx = lista_indices[-1] + 1
                    else:
                        idx = 1

                    self.receta_actual.instrucciones[idx] = instruccion
                    self.agregar_edicion_instruccion({idx:instruccion})
                self.mostrar_detalles_receta()

            case "2":
                opciones = [str(idx) for idx in self.receta_actual.instrucciones]
                idx, instruccion = self.vista.mostrar_editar_instruccion_prompt(opciones)

                if instruccion is not None:
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
            if self.pagina_actual_lista_compras == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
                self.mostrar_lista_recetas()
            else:
                self.pagina_actual_lista_compras -= 1
                pagina, hay_sig_pag = self.paginar_lista_recetas(self.recetas_testeo, self.pagina_actual_lista_compras)
                self.mostrar_lista_recetas(pagina)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_recetas(self.recetas_testeo, self.pagina_actual_lista_compras)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
                self.mostrar_lista_recetas()
            else:
                self.pagina_actual_lista_compras += 1
                pagina, hay_sig_pag = self.paginar_lista_recetas(self.recetas_testeo, self.pagina_actual_lista_compras)
                self.mostrar_lista_recetas(pagina)

    def paginar_lista_recetas(self, items: list, num_pag: int):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 7

        idx_inicio = (num_pag - 1) * lineas_disp
        idx_final = idx_inicio + lineas_disp

        if idx_final < len(items) - 1:
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
                pagina, hay_sig_pag = self.paginar_lista_detalles(self.receta_actual.detalles,
                                                               self.pagina_actual_lista_detalles)
                self.mostrar_detalles_receta(pagina)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_detalles(self.receta_actual.detalles, self.pagina_actual_lista_detalles)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
                self.mostrar_detalles_receta()
            else:
                self.pagina_actual_lista_detalles += 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(self.receta_actual.detalles,
                                                               self.pagina_actual_lista_detalles)
                self.mostrar_detalles_receta(pagina)

    def paginar_lista_detalles(self, items: list, num_pag: int):
        lineas_disp = 11

        idx_inicio = (num_pag - 1) * lineas_disp
        idx_final = idx_inicio + lineas_disp

        if idx_final < len(items) - 1:
            prox_pag = True
        else:
            prox_pag = False

        return items[idx_inicio:idx_final], prox_pag

    def obtener_total_paginas_lista_compras(self, items: list):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 7

        return math.ceil(len(items) / lineas_disp)

    def obtener_total_paginas_detalles(self, items: list):
        lineas_disp = 11

        return math.ceil(len(items) / lineas_disp)
