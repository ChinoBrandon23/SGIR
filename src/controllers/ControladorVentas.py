import copy
import datetime
import time

from models.categoria import Categoria
from models.ingrediente import Ingrediente
from models.insumo import Insumo
from models.platillo import Platillo
from models.receta import Receta
from models.venta import Venta
from views.VistaVentas import VistaVentas


class ControladorVentas:
    def __init__(self, vista:VistaVentas, servicio=None):
        self.vista = vista
        self.servicio = servicio
        self.venta_actual = None
        self.formulario = {"consumo":[], "item_borrado":False}
        self.consumo_idx = {}

        self.categorias_testeo = self.crear_categorias_testeo()
        self.platillos_testeo = self.crear_platillos_testeo()
        self.ventas_testeo = self.crear_ventas_testeo()

        self.configurar_listeners()
        self.mostrar_lista_ventas()

    def configurar_listeners(self):
        self.vista.input_menu_ventas.agregar_escuchante(self.evaluar_seleccion_menu_ventas)
        self.vista.input_abrir_detalles.agregar_escuchante(self.mostrar_detalles_venta)
        self.vista.input_menu_detalles.agregar_escuchante(self.evaluar_seleccion_menu_detalles)
        self.vista.input_menu_editar.agregar_escuchante(self.evaluar_seleccion_menu_editar)
        self.vista.input_menu_editar_consumo.agregar_escuchante(self.evaluar_seleccion_menu_editar_consumo)

    def crear_categorias_testeo(self):
        categoria1 = Categoria("PFUE", "Platillo fuerte")
        categoria2 = Categoria("ENTR", "Entrada")
        categoria3 = Categoria("POST", "Postre")
        categoria4 = Categoria("BEBI", "Bebida")

        return [categoria1, categoria2, categoria3, categoria4]

    def crear_platillos_testeo(self):
        receta1 = Receta(2, "Receta de Pizza", 4,
                         {1: "Mezclar los ingredientes", 2: "Amasar la masa", 3: "Hornear la pizza"})

        Ingrediente1 = Ingrediente(1, "Harina", Insumo(1, "Harina de Trigo", umbral=5,
                                                       stock=10, tipo_insumo=None, marca=None))
        receta1.agregarIngrediente(Ingrediente1, 2, "taza")
        receta1.agregarIngrediente(Ingrediente(2, "Levadura", Insumo(2, "Levadura", umbral=5, stock=10,
                                                                     tipo_insumo=None, marca=None)), 1, "cucharada")
        receta2 = Receta(1, "Pasta en salsa de tomate", 10, {})



        platillo1 = Platillo(num=1, nombre="Pasta en salsa de tomate", categoria=self.categorias_testeo[0], receta=receta2)
        platillo2 = Platillo(num=2, nombre="Pizza de peperoni", categoria=self.categorias_testeo[0], receta=receta1)

        return [platillo1, platillo2]

    def crear_ventas_testeo(self):
        fecha = datetime.date.today()
        fecha = datetime.date.strftime(fecha, "%d-%m-%Y")

        venta1 = Venta(1, fecha, 3, 500)
        venta2 = Venta(2, fecha, 1, 400)


        venta1.agregar_consumo(self.platillos_testeo[0], 300, 2)
        venta1.agregar_consumo(self.platillos_testeo[1], 200, 1)

        venta2.agregar_consumo(self.platillos_testeo[1], 400, 2)

        return [venta1, venta2]

    def mostrar_lista_ventas(self):
        """
        Conecta con la capa de servicios para obtener la lista de ventas y crea un elemento de lista para cada una.
        """

        self.vista.mostrar_todas_ventas()

        for venta in self.ventas_testeo:
            self.vista.crear_elemento_tabla_ventas(venta)

        self.vista.refrescar_pantalla()
        self.vista.mostrar_menu_ventas_prompt()

    def mostrar_detalles_venta(self, venta_num=None):
        if self.venta_actual is None:
            # Si no tenemos una venta actual, busca la venta por el num pasado como arg
            # idealmente con un servicio pero por ahora uso un loop para testeo
            for venta in self.ventas_testeo:
                if str(venta.num) == venta_num:
                    # La receta encontrada se convierte en la nueva receta actual
                    self.venta_actual = copy.deepcopy(venta)
                    break

        self.mapear_detalle_venta()
        # llama la función para crear la vista de detalles y le pasa los datos del formulario actual
        self.vista.mostrar_detalles_venta(self.venta_actual, copy.deepcopy(self.formulario), self.consumo_idx)

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
        # Cambia los datos del formulario en el objeto actual
        # para testeo, aquí debería llamar a un servicio

        lista_num = [venta.num for venta in self.ventas_testeo]

        if self.venta_actual.num in lista_num:
            idx = lista_num.index(self.venta_actual.num)
            self.ventas_testeo.pop(idx)
            self.ventas_testeo.insert(idx, copy.deepcopy(self.venta_actual))
        else:
            self.ventas_testeo.append(copy.deepcopy(self.venta_actual))
        # resetea el formulario porque la info ya se guardó y vuelve a la vista de detalles
        # esta debería jalar de nuevo el dato, el cual debería estar actualizado ya

        venta_actual_num = str(self.venta_actual.num)
        self.cancelar_edicion_actual()
        self.mostrar_detalles_venta(venta_actual_num)

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

        time.sleep(5)

    def evaluar_seleccion_menu_ventas(self, seleccion):
        match seleccion:
            case "1":
                # Aquí debería obtener la lista de todas las ventas y pasarla
                self.vista.mostrar_abrir_detalles_prompt(self.ventas_testeo)
            case "2":
                # Aquí crea venta
                self.mostrar_formulario_crear_venta()
                fecha, num_comensales = self.vista.mostrar_prompt_crear_venta()
                if fecha and num_comensales:
                    # debería llamar al servicio para crear una venta nueva
                    idx = len(self.platillos_testeo) + 1
                    fecha = datetime.date.strptime(fecha, "%d-%m-%Y")
                    fecha = datetime.date.strftime(fecha, "%d-%m-%Y")

                    self.venta_actual = Venta(idx, fecha, int(num_comensales), 0)
                    self.formulario["nueva_venta"] = copy.deepcopy(self.venta_actual)
                    self.mostrar_detalles_venta()
                else:
                    self.mostrar_lista_ventas()
            case "3":
                # aquí debería haber filtros de búsqueda
                pass
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
                borrar = self.vista.mostrar_prompt_eliminar_venta_prompt()
                if borrar:
                    for venta in self.ventas_testeo:
                        if venta.num == self.venta_actual.num:
                            self.platillos_testeo.remove(venta)
                            break

                self.cancelar_edicion_actual()
                self.mostrar_lista_ventas()
            case "m":
                # volver al menú principal
                self.cancelar_edicion_actual()

    def evaluar_seleccion_menu_editar(self, seleccion):
        match seleccion:
            case "1":
                # abre prompt para editar la fecha de venta
                fecha = self.vista.mostrar_editar_fecha_prompt()
                # checa que haya una respuesta del usuario y si es así lo debe validar
                if fecha is not None:
                    fecha = datetime.date.strptime(fecha, "%d-%m-%Y")
                    fecha = datetime.date.strftime(fecha, "%d-%m-%Y")

                    self.venta_actual.fecha = fecha
                    self.formulario["fecha"] = fecha

                self.mostrar_detalles_venta()

            case "2":
                # abre prompt para editar el num de comensales
                num_comensales = self.vista.mostrar_editar_comensales_prompt()

                # checa que haya un valor y luego valída y asigna
                if num_comensales:
                    self.venta_actual.numero_comensales = int(num_comensales)
                    self.formulario["comensales"] = int(num_comensales)

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
                if self.venta_actual.num in [venta.num for venta in self.ventas_testeo]:
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

                lista_platillos_actuales = [pl.platillo.nombre for pl in self.venta_actual.detalles]
                idx_plat_disp = {i + 1: self.platillos_testeo[i] for i in range(len(self.platillos_testeo)) if
                                 self.platillos_testeo[i].nombre not in lista_platillos_actuales}

                opciones = [str(i) for i in idx_plat_disp]
                lista_plat_disp = [idx_plat_disp[idx] for idx in idx_plat_disp]

                self.vista.mostrar_platillos_disponibles(lista_plat_disp)

                num_platillo, cantidad = self.vista.mostrar_agregar_consumo_prompt(opciones)

                if num_platillo and cantidad:
                    platillo = idx_plat_disp[int(num_platillo)]

                    self.venta_actual.agregar_consumo((copy.deepcopy(platillo)), 200, int(cantidad))
                    self.agregar_edicion_consumo((self.venta_actual.detalles[-1]))
                    self.actualizar_monto_total_venta()

                self.mostrar_detalles_venta()
            case "2":
                # editar cantidad
                opciones = [str(idx) for idx in self.consumo_idx]
                num, cantidad = self.vista.mostrar_editar_cantidad_prompt(opciones)
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
                        cons.cantidad_platillos = int(cantidad)
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

                        self.venta_actual.remove(cons)
                        self.formulario["item_borrado"] = True
                        self.actualizar_monto_total_venta()

                self.mostrar_detalles_venta()

            case "4":
                # volver a la vista anterior
                self.vista.crear_banda_opciones_editar()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_opciones_editar_prompt()
