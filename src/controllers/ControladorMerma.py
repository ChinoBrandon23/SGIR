import copy
import random
import datetime

from models.insumo import Insumo
from models.marca import Marca
from models.merma import Merma
from models.tipo_insumo import TipoInsumo
from models.tipo_merma import TipoMerma
from views.VistaMerma import VistaMerma


class ControladorMerma:
    def __init__(self, vista:VistaMerma, servicio=None):
        self.vista = vista
        self.servicio = servicio
        self.merma_actual = None
        self.formulario = {}

        self.insumos_testeo = self.crear_insumos_testeo()
        self.tipos_merma_testeo = self.crear_tipos_merma_testeo()
        self.merma_testeo = self.crear_mermas_testeo()

        self.configurar_listeners()
        self.mostrar_lista_mermas()

    def configurar_listeners(self):
        self.vista.input_menu_merma.agregar_escuchante(self.evaluar_seleccion_menu_merma)
        self.vista.input_abrir_detalles.agregar_escuchante(self.mostrar_detalles_merma)
        self.vista.input_menu_detalles.agregar_escuchante(self.evaluar_seleccion_menu_detalles)
        self.vista.input_menu_editar_merma.agregar_escuchante(self.evaluar_seleccion_menu_editar)

    def crear_tipos_merma_testeo(self):
        tipo1 = TipoMerma("EXPI", "Expirado")
        tipo2 = TipoMerma("DEVO", "Devolución")

        return [tipo1, tipo2]

    def crear_insumos_testeo(self):
        marca1 = Marca(1, "El Rosal")
        marca2 = Marca(2, "Tradi-Pan")

        tipo1 = TipoInsumo("HARI", "Harinas")
        tipo2 = TipoInsumo("PANA", "Panadería")

        insumo1 = Insumo(1, "Harina de Trigo", umbral=5, stock=10, tipo_insumo=tipo1, marca=marca1)
        insumo2 = Insumo(2, "Levadura", umbral=5, stock=10, tipo_insumo=tipo2, marca=marca2)

        return [insumo1, insumo2]

    def crear_mermas_testeo(self):
        descripcion1 = "Error de etiquetado"
        descripcion2 = "Queja del servicio"

        fecha = datetime.date.today()
        fecha = datetime.date.strftime(fecha, "%d-%m-%Y")

        merma1 = Merma(1, descripcion1, fecha, "gramos", 50, self.insumos_testeo[0], self.tipos_merma_testeo[0])
        merma2 = Merma(2, descripcion2, fecha, "gramos", 100, self.insumos_testeo[1], self.tipos_merma_testeo[1])

        return [merma1, merma2]

    def mostrar_lista_mermas(self):
        """
        Conecta con la capa de servicios para obtener la lista de platillos y crea un elemento de lista para cada una.
        """

        self.vista.mostrar_toda_merma()

        for merma in self.merma_testeo:
            self.vista.crear_elemento_tabla_merma(merma)

        self.vista.refrescar_pantalla()
        self.vista.mostrar_menu_merma_prompt()

    def mostrar_detalles_merma(self, merma_num=None):
        if self.merma_actual is None:
            # Si no tenemos una merma actual, busca la merma por el num pasado como arg
            # idealmente con un servicio pero por ahora uso un loop para testeo
            for merma in self.merma_testeo:
                if str(merma.num) == merma_num:
                    # La receta encontrada se convierte en la nueva receta actual
                    self.merma_actual = copy.deepcopy(merma)
                    break

        # llama la función para crear la vista de detalles y le pasa los datos del formulario actual
        self.vista.mostrar_detalles_merma(self.merma_actual, datos_editados=self.formulario)

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

    def mostrar_formulario_registrar_merma(self):
        if self.merma_actual is None:
            self.vista.mostrar_registrar_merma(None)
        else:
            self.vista.mostrar_registrar_merma(self.merma_actual)
            self.vista.crear_banda_opciones_editar()
            self.vista.refrescar_pantalla()
            self.vista.mostrar_opciones_editar_prompt()

        self.vista.refrescar_pantalla()

    def crear_tipo_merma(self, nombre:str):
        # aquí debería llamar a algún servicio
        nombre_lista = nombre.split()
        codigo = ""

        for i in range(4):
            codigo += random.choice(nombre_lista)

        tipo = TipoMerma(codigo, nombre)
        self.tipos_merma_testeo.append(tipo)

        return tipo

    def guardar_editar_merma(self):
        # Cambia los datos del formulario en el objeto actual
        # para testeo, aquí debería llamar a un servicio

        lista_num = [merma.num for merma in self.merma_testeo]

        if self.merma_actual.num in lista_num:
            idx = lista_num.index(self.merma_actual.num)
            self.merma_testeo.pop(idx)
            self.merma_testeo.insert(idx, copy.deepcopy(self.merma_actual))
        else:
            self.merma_testeo.append(copy.deepcopy(self.merma_actual))
        # resetea el formulario porque la info ya se guardó y vuelve a la vista de detalles
        # esta debería jalar de nuevo el dato, el cual debería estar actualizado ya

        merma_actual_num = str(self.merma_actual.num)
        self.cancelar_edicion_actual()
        self.mostrar_detalles_merma(merma_actual_num)

    def cancelar_edicion_actual(self):
        # resetea formulario y platillo actual
        self.merma_actual = None
        self.formulario = {}

    def usuario_esta_editando(self):
        # checa si el usuario ha hecho cambios desde que entró a la vista de detalles
        if len(self.formulario.items()) > 0:
            return True
        return False

    def evaluar_seleccion_menu_merma(self, seleccion):
        match seleccion:
            case "1":
                # Aquí debería obtener la lista de todos los platillos y pasarla
                self.vista.mostrar_abrir_detalles_prompt(self.merma_testeo)
            case "2":
                # Aquí registra merma
                self.mostrar_formulario_registrar_merma()
                self.vista.refrescar_pantalla()

                fecha = self.vista.mostrar_editar_fecha_prompt()
                cantidad = self.vista.mostrar_editar_cantidad_prompt()
                unidad_m = self.vista.mostrar_editar_unidad_medida_prompt()

                opciones_ins = [str(insumo.num) for insumo in self.insumos_testeo]
                self.vista.mostrar_insumos_disponibles(self.insumos_testeo)
                self.vista.refrescar_pantalla()

                num_ins = self.vista.mostrar_prompt_registrar_insumo_merma(opciones_ins)
                insumo_merma = None

                if num_ins != "0":
                    for insumo in self.insumos_testeo:
                        if insumo.num == int(num_ins):
                            insumo_merma = insumo

                    opciones_tipo_mer = [str(idx+1) for idx in range(len(self.tipos_merma_testeo))]
                    self.vista.mostrar_tipos_merma_disponibles(self.tipos_merma_testeo)
                    self.vista.refrescar_pantalla()

                    num_tipo_mer = self.vista.mostrar_editar_tipo_merma_prompt(opciones_tipo_mer)
                    tipo_merma = self.tipos_merma_testeo[int(num_tipo_mer)-1]

                    if num_ins is not None:
                        # debería llamar al servicio para registrar una merma nueva
                        idx = len(self.merma_testeo) + 1
                        self.merma_actual = Merma(idx, "", fecha, unidad_m, cantidad, insumo_merma, tipo_merma)
                        self.mostrar_formulario_registrar_merma()

                self.mostrar_lista_mermas()

            case "3":
                # aquí debería haber filtros de búsqueda
                pass

            case "m":
                # cancela la edicion actual antes de volver al menu
                self.cancelar_edicion_actual()

    def evaluar_seleccion_menu_detalles(self, seleccion):
        match seleccion:
            case "1":
                # volver a la vista de todas las mermas
                self.cancelar_edicion_actual()
                self.mostrar_lista_mermas()
            case "2":
                # abrir opciones de editar merma
                self.vista.crear_banda_opciones_editar()
                self.vista.refrescar_pantalla()
                self.vista.mostrar_opciones_editar_prompt()
            case "3":
                borrar = self.vista.mostrar_prompt_eliminar_merma_prompt()
                if borrar:
                    for merma in self.merma_testeo:
                        if merma.num == self.merma_actual.num:
                            self.merma_testeo.remove(merma)
                            break

                self.cancelar_edicion_actual()
                self.mostrar_lista_mermas()
            case "m":
                # volver al menú principal
                self.cancelar_edicion_actual()

    def evaluar_seleccion_menu_editar(self, seleccion):
        match seleccion:
            case "1":
                # abre prompt para cambiar la descripción
                descripcion = self.vista.mostrar_editar_descripcion_prompt()
                descripcion = descripcion.strip()
                # checa que haya una respuesta del usuario y si es así lo debe validar
                if descripcion is not None:
                    self.merma_actual.descripcion = descripcion
                    self.formulario["descripcion"] = descripcion

                self.mostrar_detalles_merma()

            case "2":
                # abre prompt para cambiar la fecha de la merma
                fecha = self.vista.mostrar_editar_fecha_prompt()

                # checa que haya un valor y luego valída y asigna
                if fecha:
                    fecha = datetime.date.strptime(fecha, "%d-%m-%Y")
                    fecha = datetime.date.strftime(fecha, "%d-%m-%Y")

                    self.merma_actual.fecha = fecha
                    self.formulario["fecha"] = fecha

                self.mostrar_detalles_merma()

            case "3":
                # abre opciones para editar unidad de medida
                cantidad = self.vista.mostrar_editar_cantidad_prompt()

                if cantidad is not None:
                    self.merma_actual.cantidad = cantidad
                    self.formulario["cantidad"] = cantidad

                self.mostrar_detalles_merma()

            case "4":
                # abre opciones para editar unidad de medida
                cantidad = self.vista.mostrar_editar_unidad_medida_prompt()

                if cantidad is not None:
                    self.merma_actual.unidad_medida = cantidad
                    self.formulario["unidad_medida"] = cantidad

                self.mostrar_detalles_merma()

            case "5":
                # abre opciones para editar tipo de merma
                opciones = [str(idx + 1) for idx in range(len(self.tipos_merma_testeo))]
                self.vista.mostrar_tipos_merma_disponibles(self.tipos_merma_testeo)
                self.vista.refrescar_pantalla()

                cantidad = self.vista.mostrar_editar_tipo_merma_prompt(opciones)

                if cantidad == "0":
                    # crear tipo
                    nombre_tipo = self.vista.mostrar_crear_tipo_insumo_prompt()
                    self.crear_tipo_merma(nombre_tipo)
                    self.merma_actual.tipo_merma = self.merma_testeo[-1]
                    self.formulario["tipo"] = self.merma_testeo[-1]

                if cantidad is not None:
                    tipo = self.tipos_merma_testeo[int(cantidad) - 1]
                    self.merma_actual.tipo_merma = tipo
                    self.formulario["tipo"] = tipo

                self.mostrar_detalles_merma()

            case "6":
                # llama a la función para guardar registro
                self.guardar_editar_merma()

            case "7":
                # cancela la edición actual y vuelve a detalles
                if self.merma_actual.num in [merma.num for merma in self.merma_testeo]:
                    self.cancelar_edicion_actual()
                    self.mostrar_detalles_merma(self.vista.input_abrir_detalles.user_input)
                else:
                    self.cancelar_edicion_actual()
                    self.mostrar_lista_mermas()

            case "m":
                # vuelve al menú
                self.cancelar_edicion_actual()
