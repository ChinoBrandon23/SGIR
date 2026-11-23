
import mysql.connector
from mysql.connector import Error
from daos.insumo_dao import InsumoDAO
from daos.compra_dao import CompraDAO
from models.insumo import Insumo
from models.compra import Compra
from models.marca import Marca
from models.proveedor import Proveedor

from datetime import date, datetime
from typing import List

from models.tipo_insumo import TipoInsumo
from utils.conversor_unidades import ConversorUnidades


class CompraServicio:
    def __init__(self, compra_dao:CompraDAO, insumo_dao:InsumoDAO):
        self._compra_dao = compra_dao
        self._insumo_dao = insumo_dao


    def registrar_compra(self, compra_nueva:Compra):
        importes:List[float] = []

        # evaluar fechas
        fecha_creacion_formateada = datetime.strptime(str(compra_nueva.fecha_creacion), "%d-%m-%Y").date()
        fecha_creacion_formateada = self._formatear_a_iso(fecha_creacion_formateada)
        fecha_creacion_formateada = datetime.strptime(str(fecha_creacion_formateada), "%Y-%m-%d").date()

        compra_nueva.fecha_creacion = str(fecha_creacion_formateada)

        hoy = date.today()
        # validando que la fecha de creacion sea "hoy"
        if fecha_creacion_formateada < hoy:
            raise ValueError(f'La fecha de creacion de la compra no puede ser anterior a hoy.')
        # validaciones
        if not compra_nueva.proveedor:
            raise ValueError("La compra debe tener un proveedor asignado.")
            
        if not compra_nueva.lista_compras or len(compra_nueva.lista_compras) == 0:
            raise ValueError("La compra debe contener al menos un insumo agregado.")

        for detalle_compra in compra_nueva.lista_compras:
            # formanteando fechas
            fecha_compra_ev = datetime.strptime(str(detalle_compra.fecha_compra), "%d-%m-%Y").date()
            fecha_compra_ev = self._formatear_a_iso(fecha_compra_ev)
            fecha_compra_ev = datetime.strptime(str(fecha_compra_ev), "%Y-%m-%d").date()
            detalle_compra.fecha_compra = str(fecha_compra_ev)
            # formatenado fechas
            fecha_caducidad_ev = datetime.strptime(str(detalle_compra.fecha_caducidad), "%d-%m-%Y").date()
            fecha_caducidad_ev = self._formatear_a_iso(fecha_caducidad_ev)
            fecha_caducidad_ev = datetime.strptime(str(fecha_caducidad_ev), "%Y-%m-%d").date()
            detalle_compra.fecha_caducidad = str(fecha_caducidad_ev)

            if fecha_compra_ev < hoy:
                raise ValueError(f"La fecha de compra para {detalle_compra.insumo.nombre} no puede ser anterior a hoy.")
            if fecha_caducidad_ev < hoy:
                raise ValueError(f"La fecha de caducidad para {detalle_compra.insumo.nombre} no puede ser anterior a hoy.")
            if detalle_compra.cantidad_comprada <= 0:
                raise ValueError(f"Servicio: La cantidad de {detalle_compra.insumo.nombre} debe ser mayor a 0.")
            if detalle_compra.monto_unitario <= 0:
                raise ValueError(f"Servicio: El precio unitario de {detalle_compra.insumo.nombre} debe ser mayor a 0.")
            if not ConversorUnidades.es_valida(detalle_compra.unidad_medida):
                raise ValueError(f'Unidad de medida ingresada invalida para el insumo {detalle_compra.insumo.nombre}.')

            # calcular importes de cada detalle compra, que es precio unitario por cantidad comprada
            detalle_compra.importe = self._calcular_importe(detalle_compra.monto_unitario,detalle_compra.cantidad_comprada)
            detalle_compra.importe = round(detalle_compra.importe, 2)
            '''Convirtiendo unidad'''
            # determinamos la unidad base para este insumo ('kg', 'l' o 'pza')
            unidad_base = ConversorUnidades.obtener_unidad_base(detalle_compra.unidad_medida)
            # si el usuario ingreso algo diferente a la base (p.e. 'g' en vez de 'kg')
            if ConversorUnidades.normalizar(detalle_compra.unidad_medida) != unidad_base:
                # 400 g -> 0.4 kg
                cantidad_convertida = ConversorUnidades.convertir(
                cantidad=detalle_compra.cantidad_comprada,
                unidad_origen=detalle_compra.unidad_medida,
                unidad_destino=unidad_base,
                decimales=2
            )
                # asignamos los valores 'base' para la BD
                detalle_compra.cantidad_comprada = cantidad_convertida
                # calculando la cantidad actual inicial, la cual es igual a la cantidad comprada
                detalle_compra.cantidad_actual = cantidad_convertida
                detalle_compra.unidad_medida = unidad_base

                # el precio unitario se 'escala' a la unidad base p.e. : $20 / 0.4 kg = $50.00/kg:
                detalle_compra.monto_unitario = round(detalle_compra.importe / cantidad_convertida, 4)

                #assert False, f'Cantidad Comprada: {detalle_compra.cantidad_comprada} - Unidad medida: {detalle_compra.unidad_medida} - Importe {detalle_compra.importe} Monto Unitario {detalle_compra.monto_unitario}'

            else:
                # si ya venia en kg o l, solo se normaliza el texto
                detalle_compra.unidad_medida = unidad_base
                detalle_compra.cantidad_actual = detalle_compra.cantidad_comprada

            # agregar a lista de importes para posterior suma
            importes.append(detalle_compra.importe)

        # calculando total bruto
        compra_nueva.total_bruto = self._calcular_total_bruto(importes)
        #assert False
        try:
            return self._compra_dao.registrar_compra(compra_nueva)
        except Error as err:
            raise ValueError(f"Error en base de datos al registrar compra: {err}")

    def _calcular_importe(self, monto_unit:float, cantidad:float) -> float:
        return monto_unit * cantidad

    def _calcular_total_bruto(self, importes:List[float]) -> float:
        return sum(importes)

    def obtener_proovedores(self) -> list[Proveedor]:
        try:
            return self._compra_dao.obtener_proveedores()
        except mysql.connector.Error as err:
            raise IndexError(f'Servicio: Error al obtener los proovedores. {err}')

    def obtener_proveedor_por_nombre(self, nombre_prov) -> Proveedor|None:
        try:
            return self._compra_dao.obtener_proveedor_por_nombre(nombre_prov)
        except mysql.connector.Error as err:
            raise IndexError(f'Servicio: Error al obtener el proveedor. {err}')

    def obtener_compras(self) -> List[Compra]:
        '''Obtiene la lista de todas las compras y sus detalles, que hay en la BD.'''
        try:
            return self._compra_dao.obtener_compras()
        except mysql.connector.Error as err:
            raise IndexError(f'Servicio: Error al obtener las compras. {err}')

    def obtener_compra_por_numero(self, num_compra:int) -> Compra:
        try:
            return self._compra_dao.obtener_compra_por_numero(num_compra)
        except IndexError as err:
            raise IndexError(f'Servicio: No existe la compra con numero {num_compra}. {err}')
        except mysql.connector.Error as err:
            raise IndexError(f'Servicio: Error al obtener compra numero {num_compra}. {err}')

    def obtener_compras_por_fecha(self, fecha:str):
        try:
            # convirtiendo al formato que usa mysql
            fecha = datetime.strptime(fecha, '%d-%m-%Y')
            fecha = datetime.strftime(fecha, '%Y-%m-%d')

            return self._compra_dao.obtener_compras_por_fecha_creacion(fecha)
        except mysql.connector.Error as err:
            raise IndexError(f'Servicio: Error al obtener las compras. {err}')

    def obtener_compras_por_proveedor(self, prov_num):
        try:
            return self._compra_dao.obtener_compras_por_proveedor(prov_num)
        except mysql.connector.Error as err:
            raise IndexError(f'Servicio: Error al obtener las compras. {err}')

    def obtener_insumo_por_nombre(self, nombre_insumo:str) -> Insumo:
        try:
            return self._insumo_dao.obtener_id_insumo_por_nombre(nombre_insumo)
        except mysql.connector.Error as err:
            raise IndexError(f'Error al consultar numero de insumo por el nombre. {err}')

    def actualizar_compra(self, compra_act:Compra):
        '''Actualiza una compra completa.'''
        importes:List[float] = []

        # evaluar fechas
        fecha_creacion_formateada = datetime.strptime(str(compra_act.fecha_creacion), "%d-%m-%Y").date()
        fecha_creacion_formateada = self._formatear_a_iso(fecha_creacion_formateada)
        fecha_creacion_formateada = datetime.strptime(str(fecha_creacion_formateada), "%Y-%m-%d").date()

        compra_act.fecha_creacion = str(fecha_creacion_formateada)

        hoy = date.today()

        # validando que la fecha de creacion sea "hoy"
        if fecha_creacion_formateada < hoy:
            raise ValueError(f'La fecha de creacion de la compra no puede ser anterior a hoy.')

        for detalle_compra in compra_act.lista_compras:
            # formanteando fechas
            fecha_compra_ev = datetime.strptime(str(detalle_compra.fecha_compra), "%d-%m-%Y").date()
            fecha_compra_ev = self._formatear_a_iso(fecha_compra_ev)
            fecha_compra_ev = datetime.strptime(str(fecha_compra_ev), "%Y-%m-%d").date()
            detalle_compra.fecha_compra = str(fecha_compra_ev)

            # formatenado fechas
            fecha_caducidad_ev = datetime.strptime(str(detalle_compra.fecha_caducidad), "%d-%m-%Y").date()
            fecha_caducidad_ev = self._formatear_a_iso(fecha_caducidad_ev)
            fecha_caducidad_ev = datetime.strptime(str(fecha_caducidad_ev), "%Y-%m-%d").date()
            detalle_compra.fecha_caducidad = str(fecha_caducidad_ev)

            if fecha_compra_ev < hoy:
                raise ValueError(f"La fecha de compra para {detalle_compra.insumo.nombre} no puede ser anterior a hoy.")
            if fecha_caducidad_ev < hoy:
                raise ValueError(f"La fecha de caducidad para {detalle_compra.insumo.nombre} no puede ser anterior a hoy.")
            if detalle_compra.cantidad_comprada <= 0:
                raise ValueError(f"Servicio: La cantidad de {detalle_compra.insumo.nombre} debe ser mayor a 0.")
            if detalle_compra.monto_unitario <= 0:
                raise ValueError(f"Servicio: El precio unitario de {detalle_compra.insumo.nombre} debe ser mayor a 0.")
            if not ConversorUnidades.es_valida(detalle_compra.unidad_medida):
                raise ValueError(f'Unidad de medida ingresada invalida para el insumo {detalle_compra.insumo.nombre}.')

            # calcular importes de cada detalle compra, que es precio unitario por cantidad comprada
            detalle_compra.importe = self._calcular_importe(detalle_compra.monto_unitario,detalle_compra.cantidad_comprada)
            detalle_compra.importe = round(detalle_compra.importe,2)

            '''Convirtiendo unidad'''
            # determinamos la unidad base para este insumo ('kg', 'l' o 'pza')
            unidad_base = ConversorUnidades.obtener_unidad_base(detalle_compra.unidad_medida)
            # si el usuario ingreso algo diferente a la base (p.e. 'g' en vez de 'kg')
            if ConversorUnidades.normalizar(detalle_compra.unidad_medida) != unidad_base:
                # 400 g -> 0.4 kg
                cantidad_convertida = ConversorUnidades.convertir(
                cantidad=detalle_compra.cantidad_comprada,
                unidad_origen=detalle_compra.unidad_medida,
                unidad_destino=unidad_base,
                decimales=2
            )
                # asignamos los valores 'base' para la BD
                detalle_compra.cantidad_comprada = cantidad_convertida
                # calculando la cantidad actual inicial, la cual es igual a la cantidad comprada
                detalle_compra.cantidad_actual = cantidad_convertida
                detalle_compra.unidad_medida = unidad_base

                # el precio unitario se 'escala' a la unidad base p.e. : $20 / 0.4 kg = $50.00/kg:
                detalle_compra.monto_unitario = round(detalle_compra.importe / cantidad_convertida, 4)

            else:
                # si ya venia en kg o l, solo se normaliza el texto
                detalle_compra.unidad_medida = unidad_base
                detalle_compra.cantidad_actual = detalle_compra.cantidad_comprada

            importes.append(detalle_compra.importe)

        # actualizando total bruto
        compra_act.total_bruto = self._calcular_total_bruto(importes)
        try:
            return self._compra_dao.actualizar_compra_completa(compra_act)
        except Error as err:
            raise ValueError(f"Servicio: Error en base de datos al actualizar compra: {err}")

    def registrar_nuevo_insumo(self, nombre: str, umbral: float, tipo_insumo: TipoInsumo, marca: Marca) -> Insumo:
        """
        Valida y crea un nuevo insumo durante el proceso de compra.
        Regla del nombre: debe tener al menos 2 palabras 'generico' + 'especifico' o la 'marca')."""
        # 1 - validacio de nombre limpio
        nombre_limpio = " ".join(nombre.strip().split())
        if not nombre_limpio:
            raise ValueError("El nombre del insumo no debe estar vacio.")

        palabras = nombre_limpio.split()
        if len(palabras) < 2:
            raise ValueError(
                "Formato invalido: El nombre del insumo debe tener una parte generica y una especifica. "
                "P.e.: 'Leche Deslactosada Lala' o 'Harina Trigo XMarca')."
            )

        # 2 - validar que no exista un insumo con ese mismo nombre (es sensible a las mayusculas y minusculas)
        insumo_existente = self._insumo_dao.obtener_insumo_por_nombre(nombre_limpio)
        if insumo_existente:
            raise ValueError(f"Ya existe un insumo registrado con el nombre '{nombre_limpio}'.")

        # 3 validacion el umbral
        try:
            umbral_float = float(umbral)
            if umbral_float < 0:
                raise ValueError("El umbral del insumo no puede ser negativo.")
        except (ValueError, TypeError):
            raise ValueError("El umbral debe ser un valor numerco valido.")

        # 4 - validacion de TipoInsumo y Marca
        if not tipo_insumo or not tipo_insumo.clave:
            raise ValueError("Debe asignarse un tipo de insumo valido.")
        if not marca or not marca.num:
            raise ValueError("Debe asignarse una marca valida.")

        # 5. - crear el objeto con stock inicial en 0 (se abastece con las compras)
        nuevo_insumo = Insumo(
            num=0,
            nombre=nombre_limpio.title(),  # hacemos que todo sea mayuscula en la bd
            umbral=umbral_float,
            stock=0.0, # tiene stock 0 por defecto
            tipo_insumo=tipo_insumo,
            marca=marca
        )

        try:
            insumo_guardado = self._compra_dao.crear_insumo(insumo=nuevo_insumo)
            return insumo_guardado
        except Error as err:
            raise ValueError(f"Servicio: No se pudo registrar el nuevo insumo: {err}")

    def registrar_nuevo_insumo(self, nombre: str, umbral: float, tipo_insumo: TipoInsumo, marca: Marca) -> Insumo:
        """
        Valida y crea un nuevo insumo durante el proceso de compra.
        Regla del nombre: debe tener al menos 2 palabras 'generico' + 'especifico' o la 'marca')."""
        # 1 - validacio de nombre limpio
        nombre_limpio = " ".join(nombre.strip().split())
        if not nombre_limpio:
            raise ValueError("El nombre del insumo no debe estar vacio.")

        palabras = nombre_limpio.split()
        if len(palabras) < 2:
            raise ValueError(
                "Formato invalido: El nombre del insumo debe tener una parte generica y una especifica. "
                "P.e.: 'Leche Deslactosada Lala' o 'Harina Trigo XMarca')."
            )

        # 2 - validar que no exista un insumo con ese mismo nombre (es sensible a las mayusculas y minusculas)
        insumo_existente = self._insumo_dao.obtener_insumo_por_nombre(nombre_limpio)
        if insumo_existente:
            raise ValueError(f"Ya existe un insumo registrado con el nombre '{nombre_limpio}'.")

        # 3 validacion el umbral
        try:
            umbral_float = float(umbral)
            if umbral_float < 0:
                raise ValueError("El umbral del insumo no puede ser negativo.")
        except (ValueError, TypeError):
            raise ValueError("El umbral debe ser un valor numerco valido.")

        # 4 - validacion de TipoInsumo y Marca
        if not tipo_insumo or not tipo_insumo.clave:
            raise ValueError("Debe asignarse un tipo de insumo valido.")
        if not marca or not marca.num:
            raise ValueError("Debe asignarse una marca valida.")

        # 5. - crear el objeto con stock inicial en 0 (se abastece con las compras)
        nuevo_insumo = Insumo(
            num=0,
            nombre=nombre_limpio.title(),  # hacemos que todo sea mayuscula en la bd
            umbral=umbral_float,
            stock=0.0, # tiene stock 0 por defecto
            tipo_insumo=tipo_insumo,
            marca=marca
        )

        try:
            insumo_guardado = self._compra_dao.crear_insumo(insumo=nuevo_insumo)
            return insumo_guardado
        except Error as err:
            raise ValueError(f"Servicio: No se pudo registrar el nuevo insumo: {err}")

    def crear_proveedor(self, proveedor:Proveedor):
        try:
            self._compra_dao.crear_proveedor(proveedor=proveedor)
        except mysql.connector.Error as err:
            raise Error(f'Error al crear proveedor en la BD - {err}')

    def eliminar_compra(self, compra:Compra):
        try:
            self._compra_dao.eliminar_compra(num_compra=compra.num)
            for detalle in compra.lista_compras:
                self._insumo_dao.actualizar_stock_insumo(detalle.insumo)
        except mysql.connector.Error as err:
            raise Error(f'Error al eliminar la compra - {err}')

    ''' FUNCIONALIDAD '''
    def _formatear_a_iso(self, fecha:date) -> str:
        """Asegura que la fecha termine en formato y-m-d para mysql."""
        if not fecha:
            return None
        if isinstance(fecha, (date, datetime)):
            return fecha.strftime('%Y-%m-%d')
        fecha_str = str(fecha).strip()
        # si ya tiene guiones estilo YYYY-MM-DD...
        if len(fecha_str) == 10 and fecha_str[4] == '-' and fecha_str[7] == '-':
            return fecha_str
        # Si viene en formato dd-mm-yyyy:
        try:
            return datetime.strptime(fecha_str, '%d-%m-%Y').strftime('%Y-%m-%d')
        except ValueError:
            return fecha_str