import copy
import datetime
import time

from models.categoria import Categoria
from models.ingrediente import Ingrediente
from models.insumo import Insumo
from models.menu import Menu
from models.platillo import Platillo
from models.receta import Receta
from views.VistaMenus import VistaMenus


class ControladorMenus:
    def __init__(self, vista:VistaMenus, servicio=None):
        self.vista = vista
        self.servicio = servicio
        self.menu_actual = None
        self.formulario = {"platillos":[], "item_borrado":False}
        self.platillo_idx = {}

        self.platillos_testeo = self.crear_platillos_testeo()
        self.menus_testeo = self.crear_menus_testeo()

        self.configurar_listeners()
        self.mostrar_lista_menus()

    def configurar_listeners(self):
        self.vista.input_menu_menus.agregar_escuchante(self.evaluar_seleccion_menu_recetas)
        self.vista.input_abrir_detalles.agregar_escuchante(self.mostrar_detalles_menu)
        self.vista.input_menu_detalles.agregar_escuchante(self.evaluar_seleccion_menu_detalles)
        self.vista.input_menu_editar_menu.agregar_escuchante(self.evaluar_seleccion_menu_editar)
        self.vista.input_menu_editar_platillo.agregar_escuchante(self.evaluar_seleccion_editar_platillos)

    def crear_platillos_testeo(self):
        receta1 = Receta(2, "Receta de Pizza", 4,
                         {1: "Mezclar los ingredientes", 2: "Amasar la masa", 3: "Hornear la pizza"})

        Ingrediente1 = Ingrediente(1, "Harina", Insumo(1, "Harina de Trigo", umbral=5,
                                                       stock=10, tipo_insumo=None, marca=None))
        receta1.agregarIngrediente(Ingrediente1, 2, "taza")
        receta1.agregarIngrediente(Ingrediente(2, "Levadura", Insumo(2, "Levadura", umbral=5, stock=10,
                                                                     tipo_insumo=None, marca=None)), 1, "cucharada")
        receta2 = Receta(1, "Pasta en salsa de tomate", 10, {})

        categoria1 = Categoria("PFUE", "Platillo fuerte")
        categoria2 = Categoria("ENTR", "Entrada")
        categoria3 = Categoria("POST", "Postre")
        categoria4 = Categoria("BEBI", "Bebida")

        platillo1 = Platillo(num=1, nombre="Pasta en salsa de tomate", categoria=categoria1,
                             receta=receta2)
        platillo2 = Platillo(num=2, nombre="Pizza de peperoni", categoria=categoria1, receta=receta1)

        return [platillo1, platillo2]

    def crear_menus_testeo(self):
        fecha_inicio = datetime.date.today()
        fecha_final = datetime.date.strptime("31-12-2027", "%d-%m-%Y")

        menu1 = Menu(1, "Menú 2025", 0, fecha_inicio, fecha_final)
        menu2 = Menu(2, "Menú 2026", 2, fecha_inicio, fecha_final)

        for platillo in self.platillos_testeo:
            menu2.agregar_platillo(platillo, 150)

        return [menu1, menu2]

    def mostrar_lista_menus(self):
        """
        Conecta con la capa de servicios para obtener la lista de recetas y crea un elemento de lista para cada una.
        """

        self.vista.mostrar_todos_menus()

        for menu in self.menus_testeo:
            self.vista.crear_elemento_tabla_menus(menu)

        self.vista.refrescar_pantalla()
        self.vista.mostrar_menu_menus_prompt()

    def mostrar_detalles_menu(self, menu_num=None):
        if self.menu_actual is None:
            # Si no tenemos un menú actual, busca el menú por el num pasado como arg
            # idealmente con un servicio pero por ahora uso un loop para testeo
            for menu in self.menus_testeo:
                if str(menu.num) == menu_num:
                    # El menú encontrado se convierte en el nuevo menú actual
                    self.menu_actual = copy.deepcopy(menu)
                    break

        self.mapear_detalle_platillo()
        # llama la función para crear la vista de tabla de detalles y le pasa los datos del formulario actual
        self.vista.mostrar_detalles_menu(self.menu_actual, datos_editados=copy.deepcopy(self.formulario), mapa_platillos=self.platillo_idx)

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
            self.vista.mostrar_crear_menu(None, self.platillo_idx)
        else:
            self.vista.mostrar_crear_menu(self.menu_actual, self.platillo_idx)
            self.vista.crear_banda_opciones_editar()
            self.vista.refrescar_pantalla()
            self.vista.mostrar_opciones_editar_prompt()

        self.vista.refrescar_pantalla()

    def guardar_editar_menu(self):
        # Cambia los datos del formulario en el objeto actual
        # para testeo, aquí debería llamar a un servicio
        lista_num = [menu.num for menu in self.menus_testeo]

        if self.menu_actual.num in lista_num:
            idx = lista_num.index(self.menu_actual.num)
            self.menus_testeo.pop(idx)
            self.menus_testeo.insert(idx, copy.deepcopy(self.menu_actual))
        else:
            self.menus_testeo.append(copy.deepcopy(self.menu_actual))
        # resetea el formulario porque la info ya se guardó y vuelve a la vista de detalles
        # esta debería jalar de nuevo el dato, el cual debería estar actualizado ya
        menu_actual_num = str(self.menu_actual.num)
        self.cancelar_edicion_actual()
        self.mostrar_detalles_menu(menu_actual_num)

    def asignar_vigencia(self, fecha_inicial, fecha_final):
        # debería validar el formato de la fecha y usar un servicio y eso
        formato = "%d-%m-%Y"

        self.menu_actual.fecha_inicial = datetime.date.strptime(fecha_inicial, formato)
        self.menu_actual.fecha_final = datetime.date.strptime(fecha_final, formato)

        self.formulario["vigencia"] = True

    def cancelar_edicion_actual(self):
        # resetea formulario y receta actual
        self.menu_actual = None
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

    def mapear_detalle_platillo(self):
        # toma los platillos del menú itera sobre cada uno y les asigna un número para mostrar en la tabla de la vista
        if self.menu_actual:
            self.platillo_idx = {}
            lista_platillo = self.menu_actual.detalles

            for i in range(len(lista_platillo)):
                # agregando al dict los ingredientes originales de la receta
                self.platillo_idx[i + 1] = lista_platillo[i].platillo.nombre

    def evaluar_seleccion_menu_recetas(self, seleccion):
        match seleccion:
            case "1":
                # Aquí debería obtener la lista de todos los menús y pasarlos
                self.vista.mostrar_abrir_detalles_prompt(self.menus_testeo)
            case "2":
                # Aquí crea menú
                self.mostrar_formulario_crear_menu()
                nombre = self.vista.mostrar_prompt_crear_menu()

                if nombre:
                    # debería llamar al servicio para crear un menú nuevo
                    num = len(self.menus_testeo) + 1
                    self.menu_actual = copy.deepcopy(Menu(num, nombre, 0, datetime.date.today(), datetime.date.today()))
                    self.mostrar_formulario_crear_menu()
                else:
                    self.mostrar_lista_menus()
            case "3":
                # aquí debería haber filtros de búsqueda
                pass
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
                if borrar:
                    for menu in self.menus_testeo:
                        if menu.nombre == self.menu_actual.nombre:
                            self.menus_testeo.remove(menu)
                            break

                self.cancelar_edicion_actual()
                self.mostrar_lista_menus()
            case "m":
                # volver al menú principal
                self.cancelar_edicion_actual()

    def evaluar_seleccion_menu_editar(self, seleccion):
        match seleccion:
            case "1":
                # abre prompt para cambiar el nombre del menú
                nombre = self.vista.mostrar_editar_nombre_prompt()
                # checa que haya una respuesta del usuario y si es así lo debe validar
                if nombre is not None:
                    self.formulario["nombre"] = nombre
                    self.menu_actual.nombre = nombre
                self.mostrar_detalles_menu()

            case "2":
                # abre prompt para cambiar la vigencia del menú
                self.vista.refrescar_pantalla()
                f_inicial, f_final = self.vista.mostrar_editar_vigencia_prompt()

                if f_inicial is not None and f_final is not None:
                    self.asignar_vigencia(f_inicial, f_final)
                self.mostrar_detalles_menu()

            case "3":
                # abre opciones para editar platillos
                self.vista.crear_banda_opciones_editar_platillos()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_editar_platillos_menu_prompt()

            case "4":
                # llama a la función para guardar receta
                self.guardar_editar_menu()
            case "5":
                # cancela la edición actual y vuelve a detalles
                if self.menu_actual.num in [menu.num for menu in self.menus_testeo]:
                    self.cancelar_edicion_actual()
                    self.mostrar_detalles_menu(self.vista.input_abrir_detalles.user_input)
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
                lista_platillos_actuales = [pl.platillo.nombre for pl in self.menu_actual.detalles]
                idx_plat_disp = {i + 1: self.platillos_testeo[i] for i in range(len(self.platillos_testeo)) if
                                 self.platillos_testeo[i].nombre not in lista_platillos_actuales}

                # hago una lista de solo los índices de los platillos disponibles para pasarla a la vista como
                # opciones válidas de input para el usuario
                # hago otra lista con solo los nombres de los platillos para pasarla a la función que va a mostrar al
                # usuario los platillos disponibles
                opciones = [str(i) for i in idx_plat_disp]
                lista_plat_disp = [idx_plat_disp[idx] for idx in idx_plat_disp]

                self.vista.mostrar_platillos_disponibles(lista_plat_disp)
                self.vista.refrescar_pantalla()

                num_platillo, precio = self.vista.mostrar_agregar_platillo_prompt(opciones)

                if num_platillo and precio:
                    nombre = idx_plat_disp[int(num_platillo)].nombre

                    for plat in self.platillos_testeo:
                        if plat.nombre == nombre:
                            self.menu_actual.agregar_platillo(plat, float(precio))
                            self.agregar_edicion_platillos(copy.deepcopy(self.menu_actual.detalles[-1]))
                            self.menu_actual.cantidad_platillos += 1

                self.mostrar_detalles_menu()

            case "2":
                # modificar precio
                # digamos que aquí se valida el precio
                opciones = [str(idx) for idx in self.platillo_idx]
                lista_platillos = [detalle.platillo for detalle in self.menu_actual.detalles]

                self.vista.mostrar_platillos_disponibles(lista_platillos)
                self.vista.refrescar_pantalla()

                num, precio = self.vista.mostrar_editar_precio_platillo_prompt(opciones)

                if num and precio:
                    nombre = self.platillo_idx[int(num)]
                    for plDetalles in self.menu_actual.detalles:
                        if plDetalles.platillo.nombre == nombre:
                            plDetalles.precio = precio
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
