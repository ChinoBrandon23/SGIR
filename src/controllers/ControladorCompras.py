import copy
import datetime
import math
import time

from models.compra import Compra
from models.insumo import Insumo
from models.marca import Marca
from models.proveedor import Proveedor
from models.tipo_insumo import TipoInsumo
from views.VistaCompras import VistaCompras


class ControladorCompras:
    def __init__(self, vista:VistaCompras, servicio=None):
        self.vista = vista
        self.servicio = servicio
        self.compra_actual = None
        self.formulario = {"insumos":[], "item_borrado":False}
        self.insumo_idx = {}

        self.pagina_actual_lista_compras = 1
        self.pagina_actual_lista_detalles = 1

        self.proveedores_testeo = self.crear_proveedores_testeo()
        self.marcas_testeo = self.crear_marcas_testeo()
        self.tipos_insumo_testeo = self.crear_tipos_insumo_testeo()
        self.insumos_testeo = self.crear_insumos_testeo()
        self.compras_testeo = self.crear_compras_testeo()

        self.configurar_listeners()
        self.mostrar_lista_compras()

    def configurar_listeners(self):
        self.vista.input_menu_compras.agregar_escuchante(self.evaluar_seleccion_menu_compras)
        self.vista.input_abrir_detalles.agregar_escuchante(self.mostrar_detalles_compra)
        self.vista.input_menu_detalles.agregar_escuchante(self.evaluar_seleccion_menu_detalles)
        self.vista.input_menu_editar_compra.agregar_escuchante(self.evaluar_seleccion_menu_editar)
        self.vista.input_menu_editar_insumo.agregar_escuchante(self.evaluar_seleccion_editar_insumos)
        self.vista.input_cambiar_pagina.agregar_escuchante(self.cambiar_pagina_lista_compras)

    def crear_proveedores_testeo(self):
        proveedor1 = Proveedor(1, "Calimax")
        proveedor2 = Proveedor(2, "Central de abastos")

        return [proveedor1, proveedor2]

    def crear_marcas_testeo(self):
        marca1 = Marca(1, "El Rosal")
        marca2 = Marca(2, "Tradi-Pan")

        return [marca1, marca2]

    def crear_tipos_insumo_testeo(self):
        tipo1 = TipoInsumo("HARI", "Harinas")
        tipo2 = TipoInsumo("PANA", "Panadería")

        return [tipo1, tipo2]

    def crear_insumos_testeo(self):
        insumo1 = Insumo(1, "Harina de Trigo", umbral=5, stock=10, tipo_insumo=self.tipos_insumo_testeo[0], marca=self.marcas_testeo[0])
        insumo2 = Insumo(2, "Levadura", umbral=5, stock=10, tipo_insumo=self.tipos_insumo_testeo[1], marca=self.marcas_testeo[1])

        return [insumo1, insumo2]

    def crear_compras_testeo(self):
        fecha1 = datetime.date.strptime("04-11-2027", "%d-%m-%Y")
        fecha1 = datetime.date.strftime(fecha1, "%d-%m-%Y")

        fecha2 = datetime.date.strptime("31-12-2027", "%d-%m-%Y")
        fecha2 = datetime.date.strftime(fecha2, "%d-%m-%Y")

        compra1 = Compra(1, fecha1, proveedor=self.proveedores_testeo[0])
        compra2 = Compra(2, fecha2, proveedor=self.proveedores_testeo[1])

        compra1.agregar_insumo_compra(self.insumos_testeo[0], 10, "kilos", 500, 50, fecha2, fecha1)
        compra1.agregar_insumo_compra(self.insumos_testeo[1], 20, "kilos", 750, 37.5, fecha2, fecha1)

        compra1.total_bruto = 500 + 750

        return [compra1, compra2]

    def mostrar_lista_compras(self, lista_compras=None):
        """
        Conecta con la capa de servicios para obtener la lista de compras y crea un elemento de lista para cada una.
        """

        self.vista.mostrar_todas_compras(self.pagina_actual_lista_compras,
                                         self.obtener_total_paginas(self.compras_testeo))

        if lista_compras is None:
            lista_compras, hay_prox_pag = self.paginar_lista_compras(self.compras_testeo,
                                                                     self.pagina_actual_lista_compras)

        for compra in lista_compras:
            self.vista.crear_elemento_tabla_compras(compra)

        self.vista.refrescar_pantalla()
        self.vista.mostrar_menu_compras_prompt()

    def mostrar_detalles_compra(self, compra_num=None):
        if self.compra_actual is None:
            # Si no tenemos un menú actual, busca el menú por el num pasado como arg
            # idealmente con un servicio pero por ahora uso un loop para testeo
            for compra in self.compras_testeo:
                if str(compra.num) == compra_num:
                    # El menú encontrado se convierte en el nuevo menú actual
                    self.compra_actual = copy.deepcopy(compra)
                    break

        self.mapear_detalle_insumo()
        self.actualizar_total_bruto()
        # llama la función para crear la vista de tabla de detalles y le pasa los datos del formulario actual
        self.vista.mostrar_detalles_compra(self.compra_actual, datos_editados=copy.deepcopy(self.formulario),
                                           mapa_insumos=self.insumo_idx)

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
        # Cambia los datos del formulario en el objeto actual
        # para testeo, aquí debería llamar a un servicio
        lista_num = [compra.num for compra in self.compras_testeo]

        if self.compra_actual.num in lista_num:
            idx = lista_num.index(self.compra_actual.num)
            self.compras_testeo.pop(idx)
            self.compras_testeo.insert(idx, copy.deepcopy(self.compra_actual))
        else:
            self.compras_testeo.append(copy.deepcopy(self.compra_actual))
        # resetea el formulario porque la info ya se guardó y vuelve a la vista de detalles
        # esta debería jalar de nuevo el dato, el cual debería estar actualizado ya
        menu_actual_num = str(self.compra_actual.num)
        self.cancelar_edicion_actual()
        self.mostrar_detalles_compra(menu_actual_num)

    def cancelar_edicion_actual(self):
        # resetea formulario y receta actual
        self.compra_actual = None
        self.formulario = {"insumos":[], "item_borrado":False}

    def usuario_esta_editando(self):
        # checa si el usuario ha hecho cambios desde que entró a la vista de detalles
        if (len(self.formulario["insumos"]) > 0 or len(self.formulario.items()) > 2) or self.formulario["item_borrado"]:
            return True
        return False

    def agregar_edicion_insumos(self, detalle_comp):
        lista_ins_editados_nombre = [com.insumo.nombre for com in self.formulario["insumos"]]

        if detalle_comp.insumo.nombre in lista_ins_editados_nombre:
            # checa si un ingrediente ya fue editado antes y remueve esa edicion para agregar la nueva
            obj = [ins for ins in self.formulario["insumos"] if ins.insumo.nombre == detalle_comp.insumo.nombre][0]
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
            total_actual += detalle.importe

        if total_actual != self.compra_actual.total_bruto:
            self.compra_actual.total_bruto = total_actual
            self.formulario["total_bruto"] = total_actual

    def evaluar_seleccion_menu_compras(self, seleccion):
        match seleccion:
            case "1":
                # Aquí debería obtener la lista de todas las compras y pasarlas
                self.vista.mostrar_abrir_detalles_prompt(self.compras_testeo)
            case "2":
                # Aquí crea el registro de una nueva compra
                self.vista.mostrar_proveedores_disponibles(self.proveedores_testeo)
                self.vista.refrescar_pantalla()

                proveedor_num = self.vista.mostrar_prompt_registrar_compra()

                if proveedor_num == "0":
                    nuevo_prov_nom = self.vista.mostrar_crear_proveedor_prompt()

                    if nuevo_prov_nom:
                        idx = len(self.proveedores_testeo) + 1
                        self.proveedores_testeo.append(Proveedor(idx, nuevo_prov_nom))
                        proveedor_num = idx

                if proveedor_num:
                    # debería llamar al servicio para crear un menú nuevo
                    num = len(self.compras_testeo) + 1
                    for prov in self.proveedores_testeo:
                        if prov.num == int(proveedor_num):
                            # formateando al formato adecuado de día-mes-año
                            fecha_actual = datetime.date.strftime(datetime.date.today(), "%d-%m-%Y")

                            self.compra_actual = copy.deepcopy(Compra(num, fecha_actual, 0, proveedor=copy.deepcopy(prov)))
                            self.mostrar_formulario_registrar_compra()

                self.mostrar_detalles_compra()
            case "3":
                # aquí debería haber filtros de búsqueda
                pass
            case "4":
                self.vista.refrescar_pantalla()
                self.vista.mostrar_prompt_cambiar_pagina()
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
                # borrar compra
                borrar = self.vista.mostrar_prompt_eliminar_compra_prompt()
                if borrar:
                    for compra in self.compras_testeo:
                        if compra.num == self.compra_actual.num:
                            self.compras_testeo.remove(compra)
                            break

                self.cancelar_edicion_actual()
                self.mostrar_lista_compras()
            case "m":
                # volver al menú principal
                self.cancelar_edicion_actual()

    def evaluar_seleccion_menu_editar(self, seleccion):
        match seleccion:
            case "1":
                # abre opciones para editar proveedor
                self.vista.mostrar_proveedores_disponibles(self.proveedores_testeo)
                self.vista.refrescar_pantalla()

                opciones = [str(proveedor.num) for proveedor in self.proveedores_testeo]
                num_prov = self.vista.mostrar_editar_proveedor_prompt(opciones)

                if num_prov:
                    for prov in self.proveedores_testeo:
                        if prov.num == int(num_prov):
                            self.compra_actual.proveedor = copy.deepcopy(prov)
                            self.formulario["proveedor"] = prov.nombre

                self.mostrar_detalles_compra()
            case "2":
                # agregar insumo
                lista_insumos_actuales = [det.insumo.nombre for det in self.compra_actual.lista_compras]
                idx_ins_disp = {i + 1: self.insumos_testeo[i] for i in range(len(self.insumos_testeo)) if
                                self.insumos_testeo[i].nombre not in lista_insumos_actuales}

                # hago una lista de solo los índices de los insumos disponibles para pasarla a la vista como
                # opciones válidas de input para el usuario
                # hago otra lista con solo los nombres de los insumos para pasarla a la función que va a mostrar al
                # usuario los insumos disponibles
                opciones = [str(i) for i in idx_ins_disp]
                lista_ins_disp = [idx_ins_disp[idx] for idx in idx_ins_disp]

                self.vista.mostrar_insumos_disponibles(lista_ins_disp)
                self.vista.refrescar_pantalla()

                # pedir resto de detalles
                num_insumo = self.vista.mostrar_seleccionar_insumo_prompt(opciones)

                # Si el usuario quiere crear un insumo, se desvía el flow de la creación de detalle compra
                # para crearlo de cero
                if num_insumo == "0":
                    nombre, umbral = self.vista.mostrar_crear_insumo_prompt()

                    if nombre and umbral:
                        self.vista.mostrar_marcas_disponibles(self.marcas_testeo)
                        self.vista.refrescar_pantalla()

                        marca = None

                        opciones_marca = [str(marca.num) for marca in self.marcas_testeo]
                        marca_num = self.vista.mostrar_seleccionar_marca_prompt(opciones_marca)

                        # Aquí hay otra desviación para crear una marca nueva
                        if marca_num == "0":
                            nueva_marca_nom = self.vista.mostrar_crear_marca_prompt()
                            idx = len(self.marcas_testeo) + 1
                            marca = Marca(idx, nueva_marca_nom)
                            self.marcas_testeo.append(marca)
                        else:
                            for marca_obj in self.marcas_testeo:
                                if marca_obj.num == int(marca_num):
                                    marca = marca_obj

                        dict_tipo_insumo = {i + 1: self.tipos_insumo_testeo[i] for i in
                                            range(len(self.tipos_insumo_testeo))}
                        opciones_tipo = [str(idx) for idx in dict_tipo_insumo]

                        self.vista.mostrar_tipos_insumo_disponibles(self.tipos_insumo_testeo)
                        self.vista.refrescar_pantalla()

                        tipo_num = self.vista.mostrar_seleccionar_tipo_insumo_prompt(opciones_tipo)
                        tipo = None

                        # Aquí se desvía para crear un nuevo tipo de insumo
                        if tipo_num == "0":
                            nuevo_tipo_nom = self.vista.mostrar_crear_tipo_insumo_prompt()
                            tipo = TipoInsumo(nuevo_tipo_nom[:3], nuevo_tipo_nom)
                            self.tipos_insumo_testeo.append(tipo)

                        else:
                            for idx, tipo_obj in dict_tipo_insumo.items():
                                if idx == tipo_num:
                                    tipo = dict_tipo_insumo[idx]

                        idx_insumo = len(self.insumos_testeo) + 1
                        # se asignan todos los valores escogidos y/o creados por el usuario
                        # dependiendo del caso a un obj insumo nuevo, el cual se agrega a la lista
                        # de testeo, el idx de este insumo nuevo se guarda para que al llegar al
                        # sig. if aquí debajo, se jale el dato y ahora sí lo use para crear
                        # un nuevo detalle de compra
                        nuevo_insumo = Insumo(idx_insumo, nombre, umbral, 0, tipo, marca)
                        self.insumos_testeo.append(copy.deepcopy(nuevo_insumo))

                        num_insumo = idx_insumo

                if num_insumo:
                    for insumo in self.insumos_testeo:
                        if insumo.num == int(num_insumo):
                            monto_unitario, fecha_compra, fecha_caducidad, cantidad, unidad_medida = self.vista.mostrar_agregar_insumo_prompt()

                            # digamos que los inputs de fecha están validados, entonces primero toma cada str
                            # y lo pasa a tipo date, luego el tipo date se pasa al formato adecuado de día-mes-año

                            fecha_caducidad = datetime.date.strptime(fecha_caducidad, "%d-%m-%Y")
                            fecha_caducidad = datetime.date.strftime(fecha_caducidad, "%d-%m-%Y")

                            fecha_compra = datetime.date.strptime(fecha_compra, "%d-%m-%Y")
                            fecha_compra = datetime.date.strftime(fecha_compra, "%d-%m-%Y")

                            importe = float(monto_unitario) * float(cantidad)

                            self.compra_actual.agregar_insumo_compra(insumo, float(cantidad), unidad_medida,
                                                                    float(importe), float(monto_unitario),
                                                                    fecha_caducidad, fecha_compra)
                            self.agregar_edicion_insumos(copy.deepcopy(self.compra_actual.lista_compras[-1]))

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
                # editar cantidad
                opciones = [str(idx) for idx in self.insumo_idx]
                num, cantidad = self.vista.mostrar_editar_cantidad_insumo_prompt(opciones)

                if num and cantidad:
                    for detalle in self.compra_actual.lista_compras:
                        if detalle.insumo.nombre == self.insumo_idx[int(num)].insumo.nombre:
                            # asigna la nueva cantidad y recalcula el importe del insumo
                            detalle.cantidad = float(cantidad)
                            detalle.importe = float(cantidad) * detalle.monto_unitario
                            self.agregar_edicion_insumos(copy.deepcopy(detalle))

                self.mostrar_detalles_compra()

            case "2":
                # editar unidad de medida
                opciones = [str(idx) for idx in self.insumo_idx]
                num, unidad = self.vista.mostrar_editar_unidad_medida_prompt(opciones)

                if num and unidad:
                    for detalle in self.compra_actual.lista_compras:
                        if detalle.insumo.nombre == self.insumo_idx[int(num)].insumo.nombre:
                            detalle.unidad_medida = unidad
                            self.agregar_edicion_insumos(copy.deepcopy(detalle))

                self.mostrar_detalles_compra()

            case "3":
                # editar monto unitario
                opciones = [str(idx) for idx in self.insumo_idx]
                num, monto_u = self.vista.mostrar_editar_monto_unitario_prompt(opciones)

                if num and monto_u:
                    for detalle in self.compra_actual.lista_compras:
                        # asigna el nuevo monto unitario y actualiza el importe del insumo
                        if detalle.insumo.nombre == self.insumo_idx[int(num)].insumo.nombre:
                            detalle.monto_unitario = float(monto_u)
                            detalle.importe = float(monto_u) * detalle.cantidad
                            self.agregar_edicion_insumos(copy.deepcopy(detalle))

                self.mostrar_detalles_compra()

            case "4":
                # editar fecha de compra
                opciones = [str(idx) for idx in self.insumo_idx]
                num, fecha = self.vista.mostrar_editar_fecha_compra_prompt(opciones)

                # digamos que el input fecha está validado, entonces primero toma ese str
                # y lo pasa a tipo date, luego ese tipo date se pasa al formato adecuado de día-mes-año
                fecha = datetime.date.strptime(fecha, "%d-%m-%Y")
                fecha = datetime.date.strftime(fecha, "%d-%m-%Y")

                if num and fecha:
                    for detalle in self.compra_actual.lista_compras:
                        if detalle.insumo.nombre == self.insumo_idx[int(num)].insumo.nombre:
                            detalle.fecha_compra = fecha
                            self.agregar_edicion_insumos(copy.deepcopy(detalle))

                self.mostrar_detalles_compra()

            case "5":
                #editar fecha de caducidad
                opciones = [str(idx) for idx in self.insumo_idx]
                num, fecha = self.vista.mostrar_editar_fecha_caducidad_prompt(opciones)

                # digamos que el input fecha está validado, entonces primero toma ese str
                # y lo pasa a tipo date, luego ese tipo date se pasa al formato adecuado de día-mes-año
                fecha = datetime.date.strptime(fecha, "%d-%m-%Y")
                fecha = datetime.date.strftime(fecha, "%d-%m-%Y")

                if num and fecha:
                    for detalle in self.compra_actual.lista_compras:
                        if detalle.insumo.nombre == self.insumo_idx[int(num)].insumo.nombre:
                            detalle.fecha_caducidad = fecha
                            self.agregar_edicion_insumos(copy.deepcopy(detalle))

                self.mostrar_detalles_compra()

            case "6":
                # editar marca
                marca = None

                opciones_insumo = [str(idx) for idx in self.insumo_idx]
                opciones_marca = [str(marca.num) for marca in self.marcas_testeo]

                num = self.vista.mostrar_editar_insumo_prompt(opciones_insumo)

                self.vista.mostrar_marcas_disponibles(self.marcas_testeo)
                self.vista.refrescar_pantalla()

                marca_num = self.vista.mostrar_editar_marca_prompt(opciones_marca)

                # Desviación para crear una marca nueva
                if marca_num == "0":
                    nueva_marca_nom = self.vista.mostrar_crear_marca_prompt()
                    idx = len(self.marcas_testeo) + 1
                    marca = Marca(idx, nueva_marca_nom)
                    self.marcas_testeo.append(marca)
                else:
                    for marca_obj in self.marcas_testeo:
                        if marca_obj.num == int(marca_num):
                            marca = marca_obj

                # si tenemos marca, ya sea nueva o no, ahora se asigna al detalleCompra correcto
                if marca:
                    for detalle in self.compra_actual.lista_compras:
                        if detalle.insumo.nombre == self.insumo_idx[int(num)].insumo.nombre:
                            detalle.insumo.marca = marca
                            self.agregar_edicion_insumos(copy.deepcopy(detalle))

                self.mostrar_detalles_compra()
            case "7":
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

        if idx_final < len(items) - 1:
            prox_pag = True
        else:
            prox_pag = False

        return items[idx_inicio:idx_final], prox_pag

    def obtener_total_paginas(self, items: list):
        consola_size = self.vista.console.size[1]
        size_sin_prompt = consola_size - 6

        lineas_disp = size_sin_prompt - 7

        return math.ceil(len(items) / lineas_disp)
