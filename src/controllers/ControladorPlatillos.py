import copy
import random
import time

from models.categoria import Categoria
from models.ingrediente import Ingrediente
from models.insumo import Insumo
from models.platillo import Platillo
from models.receta import Receta
from views.VistaPlatillos import VistaPlatillos


class ControladorPlatillos:
    def __init__(self, vista:VistaPlatillos, servicio=None):
        self.vista = vista
        self.servicio = servicio
        self.platillo_actual = None
        self.formulario = {}

        self.recetas_testeo = None
        self.categorias_testeo = self.crear_categorias_testeo()
        self.platillos_testeo = self.crear_platillos_testeo()

        self.configurar_listeners()
        self.mostrar_lista_platillos()

    def configurar_listeners(self):
        self.vista.input_menu_platillos.agregar_escuchante(self.evaluar_seleccion_menu_recetas)
        self.vista.input_abrir_detalles.agregar_escuchante(self.mostrar_detalles_platillo)
        self.vista.input_menu_detalles.agregar_escuchante(self.evaluar_seleccion_menu_detalles)
        self.vista.input_menu_editar_platillo.agregar_escuchante(self.evaluar_seleccion_menu_editar)

    def crear_categorias_testeo(self):
        categoria1 = Categoria("PFUE", "Platillo fuerte")
        categoria2 = Categoria("ENTR", "Entrada")
        categoria3 = Categoria("POST", "Postre")
        categoria4 = Categoria("BEBI", "Bebida")

        return [categoria1, categoria2, categoria3, categoria4]

    def crear_platillos_testeo(self):
        receta1 = Receta(2, "Receta de Pizza", 4,
                         {1: "Mezclar los ingredientes", 2: "Amasar la masa", 3: "Hornear la pizza"})

        Ingrediente1 = Ingrediente(1, "Harina", Insumo(1, "Harina de Trigo", fecha_compra="2026-01-01",
                                                       fecha_caducidad="2026-01-01", precio_unitario=2.0, umbral=5,
                                                       stock=10, unidad_medida="kg", tipo_insumo=None, marca=None))
        receta1.agregarIngrediente(Ingrediente1, 2, "taza")
        receta1.agregarIngrediente(Ingrediente(2, "Levadura", Insumo(2, "Levadura", fecha_compra="2026-01-01",
                                                                     fecha_caducidad="2026-01-01",
                                                                     precio_unitario=1.0, umbral=5, stock=10,
                                                                     unidad_medida="kg", tipo_insumo=None,
                                                                     marca=None)), 1, "cucharada")
        receta2 = Receta(1, "Pasta en salsa de tomate", 10, {})



        platillo1 = Platillo(num=1, nombre="Pasta en salsa de tomate", categoria=self.categorias_testeo[0], receta=receta2)
        platillo2 = Platillo(num=2, nombre="Pizza de peperoni", categoria=self.categorias_testeo[0], receta=receta1)

        self.recetas_testeo = [receta1, receta2]

        return [platillo1, platillo2]

    def mostrar_lista_platillos(self):
        """
        Conecta con la capa de servicios para obtener la lista de platillos y crea un elemento de lista para cada una.
        """

        self.vista.mostrar_todos_platillos()

        for platillo in self.platillos_testeo:
            self.vista.crear_elemento_tabla_platillos(platillo)

        self.vista.refrescar_pantalla()
        self.vista.mostrar_menu_platillos_prompt()

    def mostrar_detalles_platillo(self, platillo_num=None):
        if self.platillo_actual is None:
            # Si no tenemos un platillo actual, busca el platillo por el num pasado como arg
            # idealmente con un servicio pero por ahora uso un loop para testeo
            for platillo in self.platillos_testeo:
                if str(platillo.num) == platillo_num:
                    # La receta encontrada se convierte en la nueva receta actual
                    self.platillo_actual = copy.deepcopy(platillo)
                    break

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

    def crear_categoria(self, nombre:str):
        # aquí debería llamar a algún servicio
        nombre_lista = nombre.split()
        codigo = ""

        for i in range(4):
            codigo += random.choice(nombre_lista)

        categoria = Categoria(codigo, nombre)
        self.categorias_testeo.append(categoria)

        return categoria

    def guardar_editar_platillo(self):
        # Cambia los datos del formulario en el objeto actual
        # para testeo, aquí debería llamar a un servicio

        lista_num = [platillo.num for platillo in self.platillos_testeo]

        if self.platillo_actual.num in lista_num:
            idx = lista_num.index(self.platillo_actual.num)
            self.platillos_testeo.pop(idx)
            self.platillos_testeo.insert(idx, copy.deepcopy(self.platillo_actual))
        else:
            self.platillos_testeo.append(copy.deepcopy(self.platillo_actual))
        # resetea el formulario porque la info ya se guardó y vuelve a la vista de detalles
        # esta debería jalar de nuevo el dato, el cual debería estar actualizado ya

        platillo_actual_num = str(self.platillo_actual.num)
        self.cancelar_edicion_actual()
        self.mostrar_detalles_platillo(platillo_actual_num)

    def cancelar_edicion_actual(self):
        # resetea formulario y platillo actual
        self.platillo_actual = None
        self.formulario = {}

    def usuario_esta_editando(self):
        # checa si el usuario ha hecho cambios desde que entró a la vista de detalles
        if "nombre" in self.formulario or "categoria" is self.formulario or "receta" in self.formulario:
            return True
        return False

    def evaluar_seleccion_menu_recetas(self, seleccion):
        match seleccion:
            case "1":
                # Aquí debería obtener la lista de todos los platillos y pasarla
                self.vista.mostrar_abrir_detalles_prompt(self.platillos_testeo)
            case "2":
                # Aquí crea platillo
                self.mostrar_formulario_crear_platillo()
                nombre = self.vista.mostrar_prompt_crear_platillo()
                if nombre is not None:
                    # debería llamar al servicio para crear un platillo nuevo
                    num = len(self.platillos_testeo) + 1
                    self.platillo_actual = Platillo(num, nombre)
                    self.mostrar_formulario_crear_platillo()
                else:
                    self.mostrar_lista_platillos()
            case "3":
                # aquí debería haber filtros de búsqueda
                pass
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
                    for platillo in self.platillos_testeo:
                        if platillo.nombre == self.platillo_actual.nombre:
                            self.platillos_testeo.remove(platillo)
                            break

                self.cancelar_edicion_actual()
                self.mostrar_lista_platillos()
            case "m":
                # volver al menú principal
                self.cancelar_edicion_actual()

    def evaluar_seleccion_menu_editar(self, seleccion):
        match seleccion:
            case "1":
                # abre prompt para cambiar el nombre del platillo
                nombre = self.vista.mostrar_editar_nombre_prompt()
                # checa que haya una respuesta del usuario y si es así lo debe validar
                if nombre is not None:
                    self.platillo_actual.nombre = nombre
                    self.formulario["nombre"] = nombre

                self.mostrar_detalles_platillo()

            case "2":
                # abre prompt para cambiar la categoria
                self.vista.mostrar_categorias_disponibles(self.categorias_testeo)
                self.vista.refrescar_pantalla()
                opciones = [str(i + 1) for i in range(len(self.categorias_testeo))]
                categoria_num = self.vista.mostrar_editar_categoria_prompt(opciones)

                if categoria_num == "0":
                    self.vista.refrescar_pantalla()
                    nombre_cat = self.vista.mostrar_crear_categoria_prompt()

                    if nombre_cat is not None:
                        categoria = self.crear_categoria(nombre_cat)
                        self.platillo_actual.categoria = categoria
                        self.formulario["categoria"] = categoria

                # checa que haya un valor y luego valída y asigna
                elif categoria_num is not None:
                    categoria = [self.categorias_testeo[i] for i in range(len(self.categorias_testeo)) if i == int(categoria_num)-1][0]
                    self.platillo_actual.categoria = categoria
                    self.formulario["categoria"] = categoria

                self.mostrar_detalles_platillo()

            case "3":
                # abre opciones para editar receta base
                self.vista.mostrar_recetas_disponibles(self.recetas_testeo)
                self.vista.refrescar_pantalla()
                opciones = [str(receta.num) for receta in self.recetas_testeo]
                num_receta = self.vista.mostrar_editar_receta_base_prompt(opciones)

                if num_receta is not None:
                    receta = [self.recetas_testeo[i] for i in range(len(self.categorias_testeo)) if i == int(num_receta)-1][0]
                    self.platillo_actual.receta = receta
                    self.formulario["receta"] = receta

                self.mostrar_detalles_platillo()
            case "4":
                # llama a la función para guardar platillo
                self.guardar_editar_platillo()

            case "5":
                # cancela la edición actual y vuelve a detalles
                if self.platillo_actual.num in [platillo.num for platillo in self.platillos_testeo]:
                    self.cancelar_edicion_actual()
                    self.mostrar_detalles_platillo(self.vista.input_abrir_detalles.user_input)
                else:
                    self.cancelar_edicion_actual()
                    self.mostrar_lista_platillos()
            case "m":
                # vuelve al menú
                self.cancelar_edicion_actual()
