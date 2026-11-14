import copy
import datetime
import math
import time

from models.compra import DetalleCompra
from models.insumo import Insumo
from models.marca import Marca
from models.tipo_insumo import TipoInsumo
from views.VistaInventario import VistaInventario


class ControladorInventario:

    def __init__(self, vista:VistaInventario, servicio=None):
        self.vista = vista
        self.servicio = servicio
        self.insumo_actual = None
        self.detalles_insumo_actual = []
        self.formulario = {}

        self.pagina_actual_lista_inventario = 1
        self.pagina_actual_lista_detalles = 1

        self.marcas_testeo = self.crear_marcas_testeo()
        self.tipos_insumo_testeo = self.crear_tipos_insumo_testeo()
        self.insumos_testeo = self.crear_insumos_testeo()

        # esto era para testear paginado
        # for i in range(25):
        #     self.insumos_testeo.append(Insumo(2, "Levadura", umbral=1, stock=6, tipo_insumo=self.tipos_insumo_testeo[1],
        #                  marca=self.marcas_testeo[1]))

        self.detalle_compra_testeo = self.crear_detalle_compra_testeo()

        self.configurar_listeners()
        self.mostrar_lista_insumos()

    def configurar_listeners(self):
        self.vista.input_menu_inventario.agregar_escuchante(self.evaluar_seleccion_menu_inventario)
        self.vista.input_abrir_detalles.agregar_escuchante(self.mostrar_detalles_insumo)
        self.vista.input_menu_detalles.agregar_escuchante(self.evaluar_seleccion_menu_detalles)
        self.vista.input_menu_editar_inventario.agregar_escuchante(self.evaluar_seleccion_menu_editar)
        self.vista.input_cambiar_pagina.agregar_escuchante(self.cambiar_pagina_lista_inventario)

    def crear_detalle_compra_testeo(self):
        fecha1 = datetime.date.strptime("04-11-2027", "%d-%m-%Y")
        fecha1 = datetime.date.strftime(fecha1, "%d-%m-%Y")

        fecha2 = datetime.date.strptime("31-12-2027", "%d-%m-%Y")
        fecha2 = datetime.date.strftime(fecha2, "%d-%m-%Y")

        fecha_hoy = datetime.date.strftime(datetime.date.today(), "%d-%m-%Y")

        detalle1 = DetalleCompra(self.insumos_testeo[0], 10, "kilos", 500, 50, fecha1, fecha_hoy)
        detalle2 = DetalleCompra(self.insumos_testeo[0], 5, "kilos", 495, 49.5, fecha2, fecha_hoy)
        detalle3 = DetalleCompra(self.insumos_testeo[1], 500, "gramos", 150, 0.3, fecha1, fecha_hoy)

        return [detalle1, detalle2, detalle3]

    def crear_marcas_testeo(self):
        marca1 = Marca(1, "El Rosal")
        marca2 = Marca(2, "Tradi-Pan")

        return [marca1, marca2]

    def crear_tipos_insumo_testeo(self):
        tipo1 = TipoInsumo("HARI", "Harinas")
        tipo2 = TipoInsumo("PANA", "Panadería")

        return [tipo1, tipo2]

    def crear_insumos_testeo(self):
        insumo1 = Insumo(1, "Harina de Trigo", umbral=5, stock=10, tipo_insumo=self.tipos_insumo_testeo[0],
                         marca=self.marcas_testeo[0])
        insumo2 = Insumo(2, "Levadura", umbral=1, stock=6, tipo_insumo=self.tipos_insumo_testeo[1],
                         marca=self.marcas_testeo[1])

        return [insumo1, insumo2]

    def mostrar_lista_insumos(self, lista_insumos=None):
        """
        Conecta con la capa de servicios para obtener la lista de insumos y crea un elemento de lista para cada una.
        """
        self.vista.mostrar_todos_insumos(self.pagina_actual_lista_inventario,
                                         self.obtener_total_paginas(self.insumos_testeo))

        if lista_insumos is None:
            lista_insumos, hay_prox_pag = self.paginar_lista_inventario(self.insumos_testeo, self.pagina_actual_lista_inventario)

        for insumo in lista_insumos:
            self.vista.crear_elemento_tabla_insumos(insumo, alerta_stock=False)

        self.vista.refrescar_pantalla()
        self.vista.mostrar_menu_insumos_prompt()

    def mostrar_detalles_insumo(self, insumo_num=None):
        if self.insumo_actual is None:
            # Si no tenemos un insumo actual, busca el menú por el num pasado como arg
            # idealmente con un servicio pero por ahora uso un loop para testeo
            for insumo in self.insumos_testeo:
                if str(insumo.num) == insumo_num:
                    # El menú encontrado se convierte en el nuevo insumo actual
                    self.insumo_actual = copy.deepcopy(insumo)
                    break

            # teniendo ahora el insumo a ver, hay que obtener la lista de los detalles de compra para este insumo
            for detalle in self.detalle_compra_testeo:
                if detalle.insumo.num == self.insumo_actual.num:
                    self.detalles_insumo_actual.append(detalle)

        # llama la función para crear la vista de tabla de detalles y le pasa los datos del formulario actual
        self.vista.mostrar_detalles_insumo(self.insumo_actual, datos_editados=copy.deepcopy(self.formulario),
                                           lista_detalles=self.detalles_insumo_actual)

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
        # Cambia los datos del formulario en el objeto actual
        # para testeo, aquí debería llamar a un servicio
        lista_num = [insumo.num for insumo in self.insumos_testeo]

        if self.insumo_actual.num in lista_num:
            idx = lista_num.index(self.insumo_actual.num)
            self.insumos_testeo.pop(idx)
            self.insumos_testeo.insert(idx, copy.deepcopy(self.insumo_actual))
        else:
            self.insumos_testeo.append(copy.deepcopy(self.insumo_actual))
        # resetea el formulario porque la info ya se guardó y vuelve a la vista de detalles
        # esta debería jalar de nuevo el dato, el cual debería estar actualizado ya
        insumo_actual_num = str(self.insumo_actual.num)
        self.cancelar_edicion_actual()
        self.mostrar_detalles_insumo(insumo_actual_num)

    def cancelar_edicion_actual(self):
        # resetea formulario e insumo actual
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
                self.vista.mostrar_abrir_detalles_prompt(self.insumos_testeo)
            case "2":
                # aquí debería haber filtros de búsqueda
                pass
            case "3":
                self.vista.refrescar_pantalla()
                self.vista.mostrar_prompt_cambiar_pagina()
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
            case "3":
                # comentado en lo que veo si se van a borrar insumos y cómo
                # borrar = self.vista.mostrar_prompt_eliminar_insumo_prompt()
                # if borrar:
                #     for insumo in self.insumos_testeo:
                #         if insumo.nombre == self.insumo_actual.nombre:
                #             self.insumos_testeo.remove(insumo)
                #             break

                self.cancelar_edicion_actual()
                self.mostrar_lista_insumos()
            case "m":
                # volver al menú principal
                self.cancelar_edicion_actual()

    def evaluar_seleccion_menu_editar(self, seleccion):
        match seleccion:
            case "1":
                # abre prompt para cambiar el nombre del insumo
                nombre = self.vista.mostrar_editar_nombre_prompt()
                # checa que haya una respuesta del usuario y si es así lo debe validar
                if nombre is not None:
                    self.formulario["nombre"] = nombre
                    self.insumo_actual.nombre = nombre
                self.mostrar_detalles_insumo()

            case "2":
                # abre prompt para cambiar el umbral del insumo
                self.vista.refrescar_pantalla()
                umbral = self.vista.mostrar_editar_umbral_prompt()

                if umbral is not None:
                    self.insumo_actual.umbral = umbral
                    self.formulario["umbral"] = umbral
                self.mostrar_detalles_insumo()

            case "3":
                # abre prompt para editar tipo de insumo
                dict_tipo_insumo = {i + 1: self.tipos_insumo_testeo[i] for i in
                                    range(len(self.tipos_insumo_testeo))}

                opciones_tipo = [str(idx) for idx in dict_tipo_insumo]

                self.vista.mostrar_tipos_insumo_disponibles(self.tipos_insumo_testeo)
                self.vista.refrescar_pantalla()

                tipo_num = self.vista.mostrar_editar_tipo_insumo_prompt(opciones_tipo)
                tipo = None

                # Aquí se desvía para crear un nuevo tipo de insumo
                if tipo_num == "0":
                    nuevo_tipo_nom = self.vista.mostrar_crear_tipo_insumo_prompt()
                    tipo = TipoInsumo(nuevo_tipo_nom[:3], nuevo_tipo_nom)
                    self.tipos_insumo_testeo.append(copy.deepcopy(tipo))
                else:
                    for idx, tipo_obj in dict_tipo_insumo.items():
                        if idx == int(tipo_num):
                            tipo = dict_tipo_insumo[idx]

                if tipo:
                    self.insumo_actual.tipo_insumo = tipo
                    self.formulario["tipo_insumo"] = (copy.deepcopy(tipo))

                self.mostrar_detalles_insumo()
            case "4":
                # llama a la función para guardar
                self.guardar_editar_menu()
            case "5":
                # cancela la edición actual y vuelve a detalles
                if self.insumo_actual.num in [menu.num for menu in self.insumos_testeo]:
                    self.cancelar_edicion_actual()
                    self.mostrar_detalles_insumo(self.vista.input_abrir_detalles.user_input)
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
                pagina, hay_sig_pag = self.paginar_lista_inventario(self.insumos_testeo, self.pagina_actual_lista_inventario)
                self.mostrar_lista_insumos(pagina)

        elif mov == ".":
            pagina, sig_pag  = self.paginar_lista_inventario(self.insumos_testeo, self.pagina_actual_lista_inventario)
            if sig_pag is False:
                self.vista.mostrar_mensaje_no_pagina_siguiente()
                self.mostrar_lista_insumos()
            else:
                self.pagina_actual_lista_inventario += 1
                pagina, hay_sig_pag = self.paginar_lista_inventario(self.insumos_testeo, self.pagina_actual_lista_inventario)
                self.mostrar_lista_insumos(pagina)

    def paginar_lista_inventario(self, items: list, num_pag: int):
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
