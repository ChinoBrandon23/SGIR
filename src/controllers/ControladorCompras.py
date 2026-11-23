import copy
import datetime
import math
import time

from mysql.connector import Error
from Validaciones.validadorCompras import validadorCompras
from models.compra import Compra
from models.insumo import Insumo
from models.marca import Marca
from models.proveedor import Proveedor
from views.VistaCompras import VistaCompras

from services.compras_servicio import CompraServicio
from services.inventario_servicio import InventarioServicio


class ControladorCompras:
    def __init__(self, vista:VistaCompras, compra_servicio:CompraServicio, inventario_servicio:InventarioServicio, validador:validadorCompras):
        self.vista = vista
        self.servicio_compra = compra_servicio
        self.servicio_inventario = inventario_servicio
        self.validador = validador
        self.compra_actual = None
        self.formulario = {"insumos":[], "item_borrado":False}
        self.insumo_idx = {}

        self.pagina_actual_lista_compras = 1
        self.pagina_actual_lista_detalles = 1
        self.pagina_actual_lista_insumos = 1
        self.pagina_actual_lista_marcas = 1
        self.pagina_actual_lista_proveedores = 1
        self.pagina_actual_lista_tipos_insumo = 1

        self.proveedores_testeo = self.servicio_compra.obtener_proovedores()
        self.marcas_testeo = self.servicio_inventario.obtener_marcas()
        self.tipos_insumo_testeo = self.servicio_inventario.obtener_tipos_insumo()
        self.insumos_testeo = self.servicio_inventario.obtener_insumos()
        self.compras_testeo = None

        self.configurar_listeners()
        self.mostrar_lista_compras()

    def configurar_listeners(self):
        self.vista.input_menu_compras.agregar_escuchante(self.evaluar_seleccion_menu_compras)
        self.vista.input_abrir_detalles.agregar_escuchante(self.mostrar_detalles_compra)
        self.vista.input_menu_detalles.agregar_escuchante(self.evaluar_seleccion_menu_detalles)
        self.vista.input_menu_editar_compra.agregar_escuchante(self.evaluar_seleccion_menu_editar)
        self.vista.input_menu_editar_insumo.agregar_escuchante(self.evaluar_seleccion_editar_insumos)
        self.vista.input_menu_filtros.agregar_escuchante(self.evaluar_seleccion_busqueda_av)

        # Para cambiar de página
        self.vista.input_menu_compras.agregar_escuchante(self.cambiar_pagina_lista_compras)
        self.vista.input_menu_detalles.agregar_escuchante(self.cambiar_pagina_lista_detalles)
        self.vista.input_menu_editar_compra.agregar_escuchante(self.cambiar_pagina_lista_detalles)
        self.vista.input_menu_editar_insumo.agregar_escuchante(self.cambiar_pagina_lista_detalles)
        self.vista.input_seleccionar_tipo_insumo.agregar_escuchante(self.cambiar_pagina_lista_tipos_insumo)
        self.vista.input_seleccionar_insumo.agregar_escuchante(self.cambiar_pagina_lista_insumos)
        self.vista.input_seleccionar_marca.agregar_escuchante(self.cambiar_pagina_lista_marcas)
        self.vista.input_seleccionar_proveedor.agregar_escuchante(self.cambiar_pagina_lista_proveedores)

    def mostrar_lista_compras(self, lista_compras=None):
        """
        Conecta con la capa de servicios para obtener la lista de compras y crea un elemento de lista para cada una.
        """
        if self.compras_testeo is None:
            self.compras_testeo = self.servicio_compra.obtener_compras()

        self.vista.mostrar_todas_compras(self.pagina_actual_lista_compras,
                                        self.obtener_total_paginas_lista_compras(self.compras_testeo))

        if lista_compras is None:
            lista_compras, hay_prox_pag = self.paginar_lista_compras(self.compras_testeo,
                                                                    self.pagina_actual_lista_compras)

        if self.pagina_actual_lista_compras == 1:
            idx_ui = 0
        else:
            consola_size = self.vista.console.size[1]
            size_sin_prompt = consola_size - 6
            lineas_disp = size_sin_prompt - 7

            idx_ui = (self.pagina_actual_lista_compras - 1) * lineas_disp

        for compra in lista_compras:
            idx_ui += 1
            self.vista.crear_elemento_tabla_compras(compra, idx_ui)

        self.vista.refrescar_pantalla()
        self.vista.mostrar_menu_compras_prompt()

    def mostrar_detalles_compra(self, compra_num=None):
        if compra_num is None and self.compra_actual is None:
            self.vista.mostrar_abrir_detalles_prompt(self.servicio_compra.obtener_compras())

        if self.compra_actual is None:
            self.compra_actual = self.compras_testeo[int(compra_num)-1]

        self.mapear_detalle_insumo()

        # llama la función para crear la vista de tabla de detalles y le pasa los datos del formulario actual
        lista_compras, prox_pag = self.paginar_lista_detalles(self.compra_actual.lista_compras,
                                                               self.pagina_actual_lista_detalles)
        total_paginas_detalles = self.obtener_total_paginas_detalles(self.compra_actual.lista_compras)

        self.vista.mostrar_detalles_compra(self.compra_actual, lista_compras, self.pagina_actual_lista_detalles, total_paginas_detalles, datos_editados=copy.deepcopy(self.formulario),
                                        mapa_insumos=self.insumo_idx)

        compra_utilizada = False

        for detalle in self.compra_actual.lista_compras:
            if detalle.cantidad_actual != detalle.cantidad_comprada:
                compra_utilizada = True
                break

        if compra_utilizada:
            self.vista.crear_banda_opciones_detalles_edicion_des()
            self.vista.refrescar_pantalla()
            self.vista.mostrar_opciones_detalles_edicion_des_prompt()
        elif self.usuario_esta_editando():
            # si actualmente el formulario tiene info, muestra las opciones de edicion y su prompt
            self.vista.crear_banda_opciones_editar()
            self.vista.refrescar_pantalla()
            self.vista.mostrar_opciones_editar_prompt()
        else:
            # si no hay info en el formulario, entonces queremos que nos de las opciones normales
            self.vista.crear_banda_opciones_detalles()
            self.vista.refrescar_pantalla()
            self.vista.mostrar_opciones_detalles_prompt()

    def mostrar_formulario_registrar_compra(self):
        if self.compra_actual is None:
            self.vista.mostrar_crear_registro_compra(None, self.insumo_idx)
        else:
            self.vista.mostrar_crear_registro_compra(self.compra_actual, self.insumo_idx)
            self.vista.crear_banda_opciones_editar()
            self.vista.refrescar_pantalla()
            self.vista.mostrar_opciones_editar_prompt()

        self.vista.refrescar_pantalla()

    def guardar_editar_compra(self):
        if self.compra_actual.num == 0:
            try:
                self.servicio_compra.registrar_compra(self.compra_actual)
                compra_num = self.servicio_compra.obtener_compras()[-1].num
            except ValueError as err:
                self.vista.mostrar_mensaje_error_validacion(str(err))
        else:
            try:
                # llama al servicio para que valide, calcule y guarde en BD
                self.servicio_compra.actualizar_compra(self.compra_actual)
                compra_num = self.compra_actual.num
                # se refresca la lista de compras desde la BD
                self.compras_testeo = self.servicio_compra.obtener_compras()
            except ValueError as err:
                # si el servicio lanza un error de validacion
                self.vista.refrescar_pantalla()
                print(f'Error: {err}')
                time.sleep(2)
                self.mostrar_detalles_compra()

        self.cancelar_edicion_actual()
        self.compra_actual = self.servicio_compra.obtener_compra_por_numero(compra_num)
        self.compras_testeo = self.servicio_compra.obtener_compras()
        self.mostrar_detalles_compra()

    def cancelar_edicion_actual(self):
        # resetea formulario y receta actual
        self.compra_actual = None
        self.pagina_actual_lista_compras = 1
        self.pagina_actual_lista_detalles = 1
        self.pagina_actual_lista_insumos = 1
        self.pagina_actual_lista_marcas = 1
        self.pagina_actual_lista_proveedores = 1
        self.pagina_actual_lista_tipos_insumo = 1
        self.formulario = {"insumos":[], "item_borrado":False}

    def usuario_esta_editando(self):
        # checa si el usuario ha hecho cambios desde que entró a la vista de detalles
        if (len(self.formulario["insumos"]) > 0 or len(self.formulario.items()) > 2) or self.formulario["item_borrado"]:
            return True
        return False

    def agregar_edicion_insumos(self, detalle_comp):
        lista_ins_editados_nombre = [com.insumo.num for com in self.formulario["insumos"]]

        if detalle_comp.insumo.nombre in lista_ins_editados_nombre:
            # checa si un ingrediente ya fue editado antes y remueve esa edicion para agregar la nueva
            obj = [ins for ins in self.formulario["insumos"] if ins.insumo.num == detalle_comp.insumo.num][0]
            self.formulario["insumos"].remove(obj)

        self.formulario["insumos"].append(detalle_comp)

    def mapear_detalle_insumo(self):
        # toma los insumos de la lista de compra, itera sobre cada uno
        # y les asigna un número para mostrar en la tabla de la vista
        if self.compra_actual:
            self.insumo_idx = {}
            lista_insumo = self.compra_actual.lista_compras

            for i in range(len(lista_insumo)):
                self.insumo_idx[i + 1] = lista_insumo[i]

    def actualizar_total_bruto(self):
        total_actual = 0

        for detalle in self.compra_actual.lista_compras:
            total_actual = float(total_actual) + float(detalle.importe)

        if total_actual != self.compra_actual.total_bruto:
            self.compra_actual.total_bruto = total_actual
            self.formulario["total_bruto"] = total_actual

    def evaluar_seleccion_menu_compras(self, seleccion):
        match seleccion:
            case "1":
                # Aquí debería obtener la lista de todas las compras y pasarlas
                self.vista.mostrar_abrir_detalles_prompt(self.servicio_compra.obtener_compras())
            case "2":
                # Aquí crea el registro de una nueva compra
                lista_proveedores = self.servicio_compra.obtener_proovedores()

                pagina_prov, prox_pag = self.paginar_lista_detalles(lista_proveedores, self.pagina_actual_lista_proveedores)
                total_pag_prov = self.obtener_total_paginas_detalles(lista_proveedores)

                self.vista.mostrar_proveedores_disponibles(pagina_prov, self.pagina_actual_lista_proveedores, total_pag_prov)
                self.vista.refrescar_pantalla()

                opciones = [str(idx+1) for idx in range(len(lista_proveedores))]
                proveedor_num = self.vista.mostrar_prompt_registrar_compra(opciones)

                if proveedor_num:
                    if proveedor_num == "0":
                        nuevo_prov_nom = self.vista.mostrar_crear_proveedor_prompt()

                        if nuevo_prov_nom:
                            nuevo_prov = Proveedor(0, nuevo_prov_nom)
                            self.servicio_compra.crear_proveedor(nuevo_prov)
                            proveedor_obj = self.servicio_compra.obtener_proveedor_por_nombre(nuevo_prov.nombre)
                    else:
                        proveedor_obj = lista_proveedores[int(proveedor_num)-1]

                    # formateando al formato adecuado de día-mes-año
                    fecha_actual = datetime.date.strftime(datetime.date.today(), "%d-%m-%Y")

                    self.compra_actual = copy.deepcopy(Compra(0, fecha_actual, 0, proveedor=copy.deepcopy(proveedor_obj)))
                    self.mostrar_formulario_registrar_compra()

                    self.pagina_actual_lista_proveedores = 1
                    self.mostrar_detalles_compra()
                else:
                    self.pagina_actual_lista_proveedores = 1
                    self.mostrar_lista_compras()

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
                # volver a la vista de todas las compras
                self.cancelar_edicion_actual()
                self.mostrar_lista_compras()
            case "2":
                # abrir opciones de editar compra
                self.vista.crear_banda_opciones_editar()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_opciones_editar_prompt()
            case "3":
                #borrar compra
                borrar = self.vista.mostrar_prompt_eliminar_compra_prompt()
                if borrar:
                    self.servicio_compra.eliminar_compra(self.compra_actual)
                    self.compras_testeo = self.servicio_compra.obtener_compras()
                self.cancelar_edicion_actual()
                self.mostrar_lista_compras()
            case "m":
                # volver al menú principal
                self.cancelar_edicion_actual()

    def evaluar_seleccion_busqueda_av(self, seleccion):
        match seleccion:
            case "1":
                # buscar por fecha
                fecha = self.vista.mostrar_buscar_por_fecha_prompt()
                resultado_val_fecha = self.validador.validar_formato_fecha(fecha)

                while not resultado_val_fecha[0]:
                    self.vista.mostrar_mensaje_error_validacion(resultado_val_fecha[1])
                    fecha = self.vista.mostrar_buscar_por_fecha_prompt()
                    resultado_val_fecha = self.validador.validar_formato_fecha(fecha)

                try:
                    resultados_busqueda = self.servicio_compra.obtener_compras_por_fecha(fecha)
                    self.compras_testeo = resultados_busqueda
                except IndexError, Error:
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_mensaje_no_resultados_busqueda_av()
                finally:
                    self.mostrar_lista_compras()

            case "2":
                # buscar por proveedor
                lista_proveedores = self.servicio_compra.obtener_proovedores()

                pagina, prox_pag = self.paginar_lista_detalles(lista_proveedores, self.pagina_actual_lista_proveedores)
                total_pag = self.obtener_total_paginas_detalles(lista_proveedores)

                self.vista.mostrar_proveedores_disponibles(pagina, self.pagina_actual_lista_proveedores, total_pag)
                self.vista.refrescar_pantalla()

                opciones_prov = [str(idx+1) for idx in range(len(lista_proveedores))]
                seleccion = self.vista.mostrar_buscar_por_proveedor(opciones_prov)

                prov_num = lista_proveedores[int(seleccion)-1].num
                self.pagina_actual_lista_proveedores = 1
                # usa el prov_num para buscar compras por proveedor, y se asigna a self.compras_testeo como arriba
                try:
                    resultados_busqueda = self.servicio_compra.obtener_compras_por_proveedor(prov_num)
                except IndexError, Error:
                    resultados_busqueda = []

                if len(resultados_busqueda):
                    self.compras_testeo = resultados_busqueda
                else:
                    self.vista.refrescar_pantalla()
                    self.vista.mostrar_mensaje_no_resultados_busqueda_av()

                self.mostrar_lista_compras()

            case "3":
                # buscar todos (restaurar búsqueda)
                self.compras_testeo = self.servicio_compra.obtener_compras()

                self.mostrar_lista_compras()

            case "4":
                # volver a lista de compras
                # aquí no se hace nada
                self.mostrar_lista_compras()

    def evaluar_seleccion_menu_editar(self, seleccion):
        match seleccion:
            case "1":
                # abre opciones para editar proveedor
                lista_proveedores = self.servicio_compra.obtener_proovedores()

                pagina, prox_pag = self.paginar_lista_detalles(lista_proveedores, self.pagina_actual_lista_proveedores)
                total_pag = self.obtener_total_paginas_detalles(lista_proveedores)

                self.vista.mostrar_proveedores_disponibles(pagina, self.pagina_actual_lista_proveedores, total_pag)
                self.vista.refrescar_pantalla()

                opciones = [str(idx+1) for idx in range(len(lista_proveedores))]
                num_prov = self.vista.mostrar_editar_proveedor_prompt(opciones)

                #assert num_prov == 0, f'Hacer proveedor nuevo.'
                if num_prov == "0":
                    nuevo_prov_nom = self.vista.mostrar_crear_proveedor_prompt()
                    resultado_val_prov = self.validador.validar_nombre_proveedor(nuevo_prov_nom)

                    while not resultado_val_prov[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_prov[1])
                        nuevo_prov_nom = self.vista.mostrar_crear_proveedor_prompt()
                        resultado_val_prov = self.validador.validar_nombre_proveedor(nuevo_prov_nom)

                    if resultado_val_prov[1]:
                        proveedor = Proveedor(0, resultado_val_prov[1])
                        self.servicio_compra.crear_proveedor(proveedor)
                        proveedor_registrado = self.servicio_compra.obtener_proveedor_por_nombre(proveedor.nombre)
                        self.compra_actual.proveedor = proveedor_registrado
                        self.formulario["proveedor"] = proveedor.nombre

                elif num_prov:
                    proveedor_obj = lista_proveedores[int(num_prov)-1]
                    self.compra_actual.proveedor = copy.deepcopy(proveedor_obj)
                    self.formulario["proveedor"] = proveedor_obj.nombre

                self.pagina_actual_lista_proveedores = 1
                self.mostrar_detalles_compra()
            case "2":
                # agregar insumo
                lista_insumos_actuales = {det.insumo.nombre:det.insumo.marca.num for det in self.compra_actual.lista_compras}
                # 1. Numeramos del 1 al N solo los disponibles
                todos_insumos = self.servicio_inventario.obtener_insumos()
                lista_ins_disp = []

                for ins in todos_insumos:
                    if ins.nombre in lista_insumos_actuales:
                        if ins.marca.num != lista_insumos_actuales[ins.nombre]:
                            lista_ins_disp.append(ins)
                    elif ins.nombre not in lista_insumos_actuales:
                        lista_ins_disp.append(ins)

                # lista_ins_disp = [
                #     ins
                #     for ins in todos_insumos
                #     if (ins.nombre in lista_insumos_actuales and ins.marca != lista_insumos_actuales[ins.nombre]) or ins.nombre not in lista_insumos_actuales
                # ]
                idx_ins_disp = {i + 1: ins for i, ins in enumerate(lista_ins_disp)}
                opciones = [str(k) for k in idx_ins_disp.keys()]

                pagina, prox_pag = self.paginar_lista_detalles(lista_ins_disp, self.pagina_actual_lista_insumos)
                total_pag = self.obtener_total_paginas_detalles(lista_ins_disp)

                self.vista.mostrar_insumos_disponibles(pagina, self.pagina_actual_lista_insumos, total_pag)
                self.vista.refrescar_pantalla()

                num_insumo = self.vista.mostrar_seleccionar_insumo_prompt(opciones)
                self.pagina_actual_lista_insumos = 1
                insumo_obj = None

                # Si el usuario quiere crear un insumo, se desvía el flow de la creación de detalle compra
                # para crearlo de cero
                if num_insumo == "0":
                    nombre = self.vista.mostrar_crear_insumo_nombre_prompt()
                    resultado_val_nombre = self.validador.validar_nombre_insumo(nombre)

                    while not resultado_val_nombre[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_nombre[1])
                        nombre = self.vista.mostrar_crear_insumo_nombre_prompt()
                        resultado_val_nombre = self.validador.validar_nombre_insumo(nombre)

                    umbral = self.vista.mostrar_crear_insumo_umbral_prompt()
                    resultado_val_umbral = self.validador.validar_nombre_insumo(umbral)

                    while not resultado_val_umbral[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_umbral[1])
                        umbral = self.vista.mostrar_crear_insumo_umbral_prompt()
                        resultado_val_umbral = self.validador.validar_nombre_insumo(umbral)

                    nombre, umbral = resultado_val_nombre[1], resultado_val_umbral[1]

                    if nombre and umbral:
                        lista_marcas = self.servicio_inventario.obtener_marcas()
                        pagina, prox_pag = self.paginar_lista_detalles(lista_marcas, self.pagina_actual_lista_marcas)
                        total_pag = self.obtener_total_paginas_detalles(lista_marcas)

                        self.vista.mostrar_marcas_disponibles(pagina, self.pagina_actual_lista_marcas, total_pag)
                        self.vista.refrescar_pantalla()

                        marca = None

                        opciones_marca = [str(idx+1) for idx in range(len(lista_marcas))]
                        marca_num = self.vista.mostrar_seleccionar_marca_prompt(opciones_marca)

                        self.pagina_actual_lista_marcas = 1
                        # Aquí hay otra desviación para crear una marca nueva
                        if marca_num == "0":
                            marca_validada = False
                            nueva_marca_nom = ""

                            while not marca_validada:
                                nueva_marca_nom = self.vista.mostrar_crear_marca_prompt()
                                resultado_val_marca = self.validador.validar_nombre_marca(nueva_marca_nom)

                                while not resultado_val_marca[0]:
                                    self.vista.mostrar_mensaje_error_validacion(resultado_val_marca[1])
                                    nueva_marca_nom = self.vista.mostrar_crear_marca_prompt()
                                    resultado_val_marca = self.validador.validar_nombre_marca(nueva_marca_nom)

                                if self.servicio_inventario.marca_existe(resultado_val_marca[1]):
                                    self.vista.mostrar_mensaje_nombre_duplicado()
                                else:
                                    marca_validada = True
                                    nueva_marca_nom = resultado_val_marca[1]

                            self.servicio_inventario.crear_marca(nueva_marca_nom)
                            marca = self.servicio_inventario.obtener_marca_por_nombre(nueva_marca_nom)
                        else:
                            marca = lista_marcas[int(marca_num)-1]

                        lista_tipos_insumo = self.servicio_inventario.obtener_tipos_insumo()
                        dict_tipo_insumo = {i + 1: lista_tipos_insumo[i] for i in
                                            range(len(lista_tipos_insumo))}
                        opciones_tipo = [str(idx) for idx in dict_tipo_insumo]

                        pagina, prox_pag = self.paginar_lista_detalles(lista_tipos_insumo, self.pagina_actual_lista_tipos_insumo)
                        pag_total = self.obtener_total_paginas_detalles(lista_tipos_insumo)

                        self.vista.mostrar_tipos_insumo_disponibles(pagina, self.pagina_actual_lista_tipos_insumo, pag_total)
                        self.vista.refrescar_pantalla()

                        tipo_num = self.vista.mostrar_seleccionar_tipo_insumo_prompt(opciones_tipo)
                        tipo = None

                        self.pagina_actual_lista_tipos_insumo = 1
                        # Aquí se desvía para crear un nuevo tipo de insumo
                        if tipo_num == "0":
                            tipo_validado = False
                            nuevo_tipo_nom = ""

                            while not tipo_validado:
                                nuevo_tipo_nom = self.vista.mostrar_crear_tipo_insumo_prompt()
                                resultado_val_tipo_ins = self.validador.validar_nombre_tipo_ins(nuevo_tipo_nom)

                                while not resultado_val_tipo_ins[0]:
                                    self.vista.mostrar_mensaje_error_validacion(resultado_val_tipo_ins[1])
                                    nuevo_tipo_nom = self.vista.mostrar_crear_tipo_insumo_prompt()
                                    resultado_val_tipo_ins = self.validador.validar_nombre_tipo_ins(nuevo_tipo_nom)

                                if self.servicio_inventario.tipo_insumo_existe(resultado_val_tipo_ins[1]):
                                    self.vista.mostrar_mensaje_nombre_duplicado()
                                else:
                                    nuevo_tipo_nom = resultado_val_tipo_ins[1]
                                    tipo_validado = True

                            self.servicio_inventario.crear_tipo_insumo(nuevo_tipo_nom)
                            tipo = self.servicio_inventario.obtener_tipo_insumo_por_nombre(nuevo_tipo_nom)
                        else:
                            tipo = dict_tipo_insumo[int(tipo_num)]

                        # se asignan todos los valores escogidos y/o creados por el usuario
                        # dependiendo del caso a un obj insumo nuevo, el cual se agrega a la lista
                        # de testeo, el idx de este insumo nuevo se guarda para que al llegar al
                        # sig. if aquí debajo, se jale el dato y ahora sí lo use para crear
                        # un nuevo detalle de compra

                        # obtiene el del insumo en la BD
                        try:
                            self.servicio_inventario.crear_insumo(Insumo(0, nombre, umbral, 0, tipo, marca))
                            insumo_obj = self.servicio_inventario.obtener_insumo_por_nombre_marca(nombre, marca.nombre)
                        except ValueError:
                            self.vista.mostrar_mensaje_error_validacion("Error: Este insumo ya existe")
                            res = self.vista.mostrar_mensaje_solucionar_insumo_duplicado()

                            if res == "S":
                                insumo_obj = self.servicio_inventario.obtener_insumo_por_nombre_marca(nombre, marca.nombre)

                elif num_insumo:
                    insumo_obj = idx_ins_disp[int(num_insumo)]

                if insumo_obj:
                    # pide la fecha de compra
                    fecha_compra = self.vista.mostrar_agregar_insumo_fecha_com_prompt()
                    resultado_val_fecha_com = self.validador.validar_formato_fecha(fecha_compra)

                    validacion_congruencia = False
                    while not resultado_val_fecha_com[0] or not validacion_congruencia:
                        # la congruencia es que la fecha de caducidad no sea antes de hoy
                        try:
                            if not datetime.datetime.strptime(str(fecha_compra), "%d-%m-%Y").date() < datetime.date.today():
                                validacion_congruencia = True
                                continue
                            else:
                                self.vista.mostrar_mensaje_error_validacion("Error: La fecha de compra no puede ser anterior a hoy.")
                        except ValueError:
                            self.vista.mostrar_mensaje_error_validacion("Error: La fecha no es válida")
                            fecha_compra = self.vista.mostrar_agregar_insumo_fecha_com_prompt()
                            resultado_val_fecha_com = self.validador.validar_formato_fecha(fecha_compra)
                            continue

                        if not resultado_val_fecha_com[0]:
                            self.vista.mostrar_mensaje_error_validacion(resultado_val_fecha_com[1])
                        fecha_compra = self.vista.mostrar_agregar_insumo_fecha_com_prompt()
                        resultado_val_fecha_com = self.validador.validar_formato_fecha(fecha_compra)

                    fecha_compra = resultado_val_fecha_com[1]

                    # pide la cantidad del insumo
                    cantidad = self.vista.mostrar_agregar_insumo_cantidad_com_prompt()
                    resultado_val_cant_com = self.validador.validar_cantidad_insumo(cantidad)

                    while not resultado_val_cant_com[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_cant_com[1])
                        cantidad = self.vista.mostrar_agregar_insumo_cantidad_com_prompt()
                        resultado_val_cant_com = self.validador.validar_cantidad_insumo(cantidad)

                    cantidad = resultado_val_cant_com[1]

                    # pide la unidad de medida
                    unidad_medida = self.vista.mostrar_agregar_insumo_unidad_prompt()
                    resultado_val_unidad = self.validador.validar_unidad_medida(unidad_medida)

                    while not resultado_val_unidad[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_unidad[1])
                        unidad_medida = self.vista.mostrar_agregar_insumo_unidad_prompt()
                        resultado_val_unidad = self.validador.validar_unidad_medida(unidad_medida)

                    unidad_medida = resultado_val_unidad[1]

                    # pide el monto
                    monto_unitario = self.vista.mostrar_agregar_insumo_monto_prompt()
                    resultado_val_monto = self.validador.validar_monto_insumo(monto_unitario)

                    while not resultado_val_monto[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_monto[1])
                        monto_unitario = self.vista.mostrar_agregar_insumo_monto_prompt()
                        resultado_val_monto = self.validador.validar_monto_insumo(monto_unitario)

                    monto_unitario = resultado_val_monto[1]

                    # pide la fecha de caducidad
                    fecha_caducidad = self.vista.mostrar_agregar_insumo_fecha_cad_prompt()
                    resultado_val_caducidad = self.validador.validar_formato_fecha(fecha_caducidad)

                    validacion_congruencia = False
                    while not resultado_val_caducidad[0] or not validacion_congruencia:
                        try:
                            if not datetime.datetime.strptime(str(fecha_caducidad),
                                                              "%d-%m-%Y").date() < datetime.date.today():
                                validacion_congruencia = True
                                continue
                            else:
                                self.vista.mostrar_mensaje_error_validacion(
                                    "Error: La fecha de caducidad no puede ser anterior a hoy.")
                        except ValueError:
                            self.vista.mostrar_mensaje_error_validacion("Error: La fecha no es válida")
                            fecha_caducidad = self.vista.mostrar_agregar_insumo_fecha_cad_prompt()
                            resultado_val_caducidad = self.validador.validar_formato_fecha(fecha_caducidad)
                            continue

                        if not resultado_val_caducidad[0]:
                            self.vista.mostrar_mensaje_error_validacion(resultado_val_caducidad[1])
                        fecha_caducidad = self.vista.mostrar_agregar_insumo_fecha_cad_prompt()
                        resultado_val_caducidad = self.validador.validar_formato_fecha(fecha_caducidad)

                    fecha_caducidad = resultado_val_caducidad[1]

                    importe = float(monto_unitario) * float(cantidad)
                    self.compra_actual.agregar_insumo_compra(
                        insumo_obj,
                        float(cantidad),
                        float(cantidad),
                        unidad_medida,
                        float(importe),
                        float(monto_unitario),
                        fecha_caducidad,
                        fecha_compra,
                    )
                    self.agregar_edicion_insumos(
                        copy.deepcopy(self.compra_actual.lista_compras[-1])
                    )
                    self.actualizar_total_bruto()

                self.mostrar_detalles_compra()
            case "3":
                # Abre menú de editar insumo
                self.vista.crear_banda_opciones_editar_insumos()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_editar_insumos_menu_prompt()

            case "4":
                # remover insumo
                opciones = [str(idx) for idx in self.insumo_idx]
                num = self.vista.mostrar_remover_insumo_prompt(opciones)
                # debería validar aquí
                if num is not None:
                    # busca el nombre del platillo basado en el num ingresado,
                    # y lo borra del menú y actualiza el total de la compra
                    nombre = self.insumo_idx[int(num)].insumo.nombre
                    for detalle in self.compra_actual.lista_compras:
                        if detalle.insumo.nombre == nombre:
                            self.compra_actual.lista_compras.remove(detalle)
                            self.formulario["item_borrado"] = True
                            self.actualizar_total_bruto()
                self.mapear_detalle_insumo()
                self.mostrar_detalles_compra()

            case "5":
                # llama a la función para guardar receta
                self.guardar_editar_compra()

            case "6":
                # cancela la edición actual y vuelve a detalles
                if self.compra_actual.num in [menu.num for menu in self.compras_testeo]:
                    self.cancelar_edicion_actual()
                    self.mostrar_detalles_compra(self.vista.input_abrir_detalles.user_input)
                else:
                    self.cancelar_edicion_actual()
                    self.mostrar_lista_compras()

            case "m":
                # vuelve al menú
                self.cancelar_edicion_actual()

    def evaluar_seleccion_editar_insumos(self, seleccion):
        match seleccion:
            case "1":
                # editar cantidad comprada
                opciones = [str(idx) for idx in self.insumo_idx]
                num = self.vista.mostrar_editar_insumo_prompt(opciones)

                if num is not None:
                    cantidad = self.vista.mostrar_agregar_insumo_cantidad_com_prompt()
                    resultado_val_cant = self.validador.validar_cantidad_insumo(cantidad)

                    while not resultado_val_cant[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_cant[1])
                        cantidad = self.vista.mostrar_agregar_insumo_cantidad_com_prompt()
                        resultado_val_cant = self.validador.validar_cantidad_insumo(cantidad)

                    cantidad = resultado_val_cant[1]

                    for detalle in self.compra_actual.lista_compras:
                        if detalle.insumo.nombre == self.insumo_idx[int(num)].insumo.nombre:
                            # asigna la nueva cantidad comprada y recalcula el importe del insumo
                            detalle.cantidad_comprada = cantidad
                            detalle.importe = cantidad * float(detalle.monto_unitario)
                            self.agregar_edicion_insumos(copy.deepcopy(detalle))

                self.mostrar_detalles_compra()

            case "2":
                # editar unidad de medida
                opciones = [str(idx) for idx in self.insumo_idx]
                num = self.vista.mostrar_editar_insumo_prompt(opciones)

                if num is not None:
                    unidad = self.vista.mostrar_agregar_insumo_unidad_prompt()
                    resultado_val_unidad = self.validador.validar_unidad_medida(unidad)

                    while not resultado_val_unidad[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_unidad[1])
                        unidad = self.vista.mostrar_agregar_insumo_unidad_prompt()
                        resultado_val_unidad = self.validador.validar_unidad_medida(unidad)

                    unidad = resultado_val_unidad[1]

                    for detalle in self.compra_actual.lista_compras:
                        if detalle.insumo.nombre == self.insumo_idx[int(num)].insumo.nombre:
                            detalle.unidad_medida = unidad
                            self.agregar_edicion_insumos(copy.deepcopy(detalle))

                self.mostrar_detalles_compra()

            case "3":
                # editar monto unitario
                opciones = [str(idx) for idx in self.insumo_idx]
                num= self.vista.mostrar_editar_insumo_prompt(opciones)

                if num is not None:
                    monto_u = self.vista.mostrar_agregar_insumo_monto_prompt()
                    resultado_val_monto_u = self.validador.validar_monto_insumo(monto_u)

                    while not resultado_val_monto_u[0]:
                        self.vista.mostrar_mensaje_error_validacion(resultado_val_monto_u[1])
                        monto_u = self.vista.mostrar_agregar_insumo_monto_prompt()
                        resultado_val_monto_u = self.validador.validar_monto_insumo(monto_u)

                    monto_u = resultado_val_monto_u[1]

                    for detalle in self.compra_actual.lista_compras:
                        # asigna el nuevo monto unitario y actualiza el importe del insumo
                        if detalle.insumo.nombre == self.insumo_idx[int(num)].insumo.nombre:
                            detalle.monto_unitario = monto_u
                            detalle.importe = monto_u * float(detalle.cantidad_comprada)
                            self.agregar_edicion_insumos(copy.deepcopy(detalle))

                self.mostrar_detalles_compra()

            case "4":
                # editar fecha de compra
                opciones = [str(idx) for idx in self.insumo_idx]
                num = self.vista.mostrar_editar_insumo_prompt(opciones)

                if num is not None:
                    fecha_compra = self.vista.mostrar_agregar_insumo_fecha_com_prompt()
                    resultado_val_fecha_com = self.validador.validar_formato_fecha(fecha_compra)

                    validacion_congruencia = False
                    while not resultado_val_fecha_com[0] or not validacion_congruencia:
                        # la congruencia es que la fecha de caducidad no sea antes de hoy
                        try:
                            if not datetime.datetime.strptime(str(fecha_compra),
                                                              "%d-%m-%Y").date() < datetime.date.today():
                                validacion_congruencia = True
                                continue
                            else:
                                self.vista.mostrar_mensaje_error_validacion(
                                    "Error: La fecha de compra no puede ser anterior a hoy.")
                        except ValueError:
                            self.vista.mostrar_mensaje_error_validacion("Error: La fecha no es válida")
                            fecha_compra = self.vista.mostrar_agregar_insumo_fecha_com_prompt()
                            resultado_val_fecha_com = self.validador.validar_formato_fecha(fecha_compra)
                            continue

                        if not resultado_val_fecha_com[0]:
                            self.vista.mostrar_mensaje_error_validacion(resultado_val_fecha_com[1])
                        fecha_compra = self.vista.mostrar_agregar_insumo_fecha_com_prompt()
                        resultado_val_fecha_com = self.validador.validar_formato_fecha(fecha_compra)

                    fecha_compra = resultado_val_fecha_com[1]

                    for detalle in self.compra_actual.lista_compras:
                        if detalle.insumo.nombre == self.insumo_idx[int(num)].insumo.nombre:
                            detalle.fecha_compra = fecha_compra
                            self.agregar_edicion_insumos(copy.deepcopy(detalle))

                self.mostrar_detalles_compra()

            case "5":
                #editar fecha de caducidad
                opciones = [str(idx) for idx in self.insumo_idx]
                num = self.vista.mostrar_editar_insumo_prompt(opciones)

                if num is not None:
                    fecha_caducidad = self.vista.mostrar_agregar_insumo_fecha_cad_prompt()
                    resultado_val_caducidad = self.validador.validar_formato_fecha(fecha_caducidad)

                    validacion_congruencia = False
                    while not resultado_val_caducidad[0] or not validacion_congruencia:
                        try:
                            if not datetime.datetime.strptime(str(fecha_caducidad),
                                                              "%d-%m-%Y").date() < datetime.date.today():
                                validacion_congruencia = True
                                continue
                            else:
                                self.vista.mostrar_mensaje_error_validacion(
                                    "Error: La fecha de caducidad no puede ser anterior a hoy.")
                        except ValueError:
                            self.vista.mostrar_mensaje_error_validacion("Error: La fecha no es válida")
                            fecha_caducidad = self.vista.mostrar_agregar_insumo_fecha_cad_prompt()
                            resultado_val_caducidad = self.validador.validar_formato_fecha(fecha_caducidad)
                            continue

                        if not resultado_val_caducidad[0]:
                            self.vista.mostrar_mensaje_error_validacion(resultado_val_caducidad[1])
                        fecha_caducidad = self.vista.mostrar_agregar_insumo_fecha_cad_prompt()
                        resultado_val_caducidad = self.validador.validar_formato_fecha(fecha_caducidad)

                    fecha_caducidad = resultado_val_caducidad[1]

                    for detalle in self.compra_actual.lista_compras:
                        if detalle.insumo.nombre == self.insumo_idx[int(num)].insumo.nombre:
                            detalle.fecha_caducidad = fecha_caducidad
                            self.agregar_edicion_insumos(copy.deepcopy(detalle))

                self.mostrar_detalles_compra()
            case "6":
                # volver a menu editar principal
                self.vista.crear_banda_opciones_editar()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_opciones_editar_prompt()

    def cambiar_pagina_lista_compras(self, mov):
        if mov == ",":
            if self.pagina_actual_lista_compras == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
                self.mostrar_lista_compras()
            else:
                self.pagina_actual_lista_compras -= 1
                pagina, hay_sig_pag = self.paginar_lista_compras(self.compras_testeo,
                                                                self.pagina_actual_lista_compras)
                self.mostrar_lista_compras(pagina)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_compras(self.compras_testeo, self.pagina_actual_lista_compras)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
                self.mostrar_lista_compras()
            else:
                self.pagina_actual_lista_compras += 1
                pagina, hay_sig_pag = self.paginar_lista_compras(self.compras_testeo,
                                                                self.pagina_actual_lista_compras)
                self.mostrar_lista_compras(pagina)

    def paginar_lista_compras(self, items: list, num_pag: int):
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
                self.mostrar_detalles_compra()
            else:
                self.pagina_actual_lista_detalles -= 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(self.compra_actual.lista_compras,
                                                            self.pagina_actual_lista_detalles)
                self.mostrar_detalles_compra(pagina)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_detalles(self.compra_actual.lista_compras, self.pagina_actual_lista_detalles)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
                self.mostrar_detalles_compra()
            else:
                self.pagina_actual_lista_detalles += 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(self.compra_actual.lista_compras,
                                                            self.pagina_actual_lista_detalles)
                self.mostrar_detalles_compra(pagina)

    def cambiar_pagina_lista_proveedores(self, mov):
        lista_proveedores = self.servicio_compra.obtener_proovedores()

        if mov == ",":
            if self.pagina_actual_lista_proveedores == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
            else:
                self.pagina_actual_lista_proveedores -= 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(lista_proveedores,
                                                            self.pagina_actual_lista_proveedores)
                total_pag = self.obtener_total_paginas_detalles(lista_proveedores)
                self.vista.mostrar_proveedores_disponibles(pagina, self.pagina_actual_lista_proveedores, total_pag)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_detalles(lista_proveedores, self.pagina_actual_lista_proveedores)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
            else:
                self.pagina_actual_lista_proveedores += 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(lista_proveedores,
                                                            self.pagina_actual_lista_proveedores)
                total_pag = self.obtener_total_paginas_detalles(lista_proveedores)
                self.vista.mostrar_proveedores_disponibles(pagina, self.pagina_actual_lista_proveedores, total_pag)

    def cambiar_pagina_lista_marcas(self, mov):
        lista_marcas = self.servicio_inventario.obtener_marcas()

        if mov == ",":
            if self.pagina_actual_lista_marcas == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
            else:
                self.pagina_actual_lista_marcas -= 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(lista_marcas,
                                                            self.pagina_actual_lista_marcas)
                total_pag = self.obtener_total_paginas_detalles(lista_marcas)
                self.vista.mostrar_marcas_disponibles(pagina, self.pagina_actual_lista_marcas, total_pag)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_detalles(lista_marcas, self.pagina_actual_lista_marcas)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
            else:
                self.pagina_actual_lista_marcas += 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(lista_marcas,
                                                            self.pagina_actual_lista_marcas)
                total_pag = self.obtener_total_paginas_detalles(lista_marcas)
                self.vista.mostrar_marcas_disponibles(pagina, self.pagina_actual_lista_marcas, total_pag)

    def cambiar_pagina_lista_insumos(self, mov):
        lista_insumos_actuales = {det.insumo.nombre: det.insumo.marca.num for det in self.compra_actual.lista_compras}
        todos_insumos = self.servicio_inventario.obtener_insumos()
        lista_ins_disp = []

        for ins in todos_insumos:
            if ins.nombre in lista_insumos_actuales:
                if ins.marca.num != lista_insumos_actuales[ins.nombre]:
                    lista_ins_disp.append(ins)
            elif ins.nombre not in lista_insumos_actuales:
                lista_ins_disp.append(ins)

        if mov == ",":
            if self.pagina_actual_lista_insumos == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
            else:
                self.pagina_actual_lista_insumos -= 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(lista_ins_disp,
                                                            self.pagina_actual_lista_insumos)
                total_pag = self.obtener_total_paginas_detalles(lista_ins_disp)
                self.vista.mostrar_insumos_disponibles(pagina, self.pagina_actual_lista_insumos, total_pag)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_detalles(lista_ins_disp, self.pagina_actual_lista_insumos)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
            else:
                self.pagina_actual_lista_insumos += 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(lista_ins_disp,
                                                            self.pagina_actual_lista_insumos)
                total_pag = self.obtener_total_paginas_detalles(lista_ins_disp)
                self.vista.mostrar_insumos_disponibles(pagina, self.pagina_actual_lista_insumos, total_pag)

    def cambiar_pagina_lista_tipos_insumo(self, mov):
        lista_tipos_insumo = self.servicio_inventario.obtener_tipos_insumo()

        if mov == ",":
            if self.pagina_actual_lista_tipos_insumo == 1:
                self.vista.mostrar_mensaje_no_pagina_anterior()
            else:
                self.pagina_actual_lista_tipos_insumo -= 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(lista_tipos_insumo,
                                                            self.pagina_actual_lista_tipos_insumo)
                total_pag = self.obtener_total_paginas_detalles(lista_tipos_insumo)
                self.vista.mostrar_tipos_insumo_disponibles(pagina, self.pagina_actual_lista_tipos_insumo, total_pag)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_detalles(lista_tipos_insumo, self.pagina_actual_lista_tipos_insumo)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
            else:
                self.pagina_actual_lista_tipos_insumo += 1
                pagina, hay_sig_pag = self.paginar_lista_detalles(lista_tipos_insumo,
                                                            self.pagina_actual_lista_tipos_insumo)
                total_pag = self.obtener_total_paginas_detalles(lista_tipos_insumo)
                self.vista.mostrar_tipos_insumo_disponibles(pagina, self.pagina_actual_lista_tipos_insumo, total_pag)

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

    def obtener_total_paginas_lista_compras(self, items: list):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6
        lineas_disp = size_sin_prompt - 7

        total = math.ceil(len(items) / lineas_disp)

        if len(items) == 0:
            return 1

        return total

    def obtener_total_paginas_detalles(self, items: list):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6
        lineas_disp = size_sin_prompt - 18

        total = math.ceil(len(items) / lineas_disp)

        if len(items) == 0:
            return 1

        return total