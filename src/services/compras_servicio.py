
import mysql.connector
from mysql.connector import Error
from daos.insumo_dao import InsumoDAO
from daos.compra_dao import CompraDAO
from models.insumo import Insumo
from models.compra import Compra
from models.proveedor import Proveedor

from datetime import date, datetime
from typing import List

class CompraServicio:
    def __init__(self, compra_dao:CompraDAO, insumo_dao:InsumoDAO):
        self._compra_dao = compra_dao
        self._insumo_dao = insumo_dao


    def registrar_compra(self, compra_nueva:Compra):
        importes:List[float] = []

        # evaluar fechas
        #convirtiendo fecha a date
        fecha_creacion = datetime.strptime(str(compra_nueva.fecha_creacion), "%d-%m-%Y").date()
        # convirtiendo a formato anglosajon, (btw que palabra poco comun)
        #fecha_creacion_ev = fecha_creacion.strftime("%Y-%m-%d")
        hoy = date.today()

        # validando que la fecha de creacion sea "hoy"
        if fecha_creacion < hoy:
            raise ValueError(f'La fecha de creacion de la compra no puede ser anterior a hoy.')
        
        # formateando fecha de creacion
        compra_nueva.fecha_creacion = self._formatear_a_iso(compra_nueva.fecha_creacion) # type: ignore

        # validaciones
        if not compra_nueva.proveedor:
            raise ValueError("La compra debe tener un proveedor asignado.")
            
        if not compra_nueva.lista_compras or len(compra_nueva.lista_compras) == 0:
            raise ValueError("La compra debe contener al menos un insumo agregado.")

        for detalle_compra in compra_nueva.lista_compras:
            # validaciones
            # fecha_compra_ev = datetime.strptime(str(detalle_compra.fecha_compra), "%Y-%m-%d").date()
            # fecha_cad_ev = datetime.strptime(str(detalle_compra.fecha_caducidad), "%Y-%m-%d").date()
            detalle_compra.fecha_compra = datetime.strptime(detalle_compra.fecha_compra, '%d-%m-%Y')  # type: ignore
            detalle_compra.fecha_caducidad = datetime.strptime(detalle_compra.fecha_caducidad, '%d-%m-%Y')

            detalle_compra.fecha_compra = datetime.strftime(detalle_compra.fecha_compra, '%Y-%m-%d') # type: ignore
            detalle_compra.fecha_caducidad = datetime.strftime(detalle_compra.fecha_caducidad, '%Y-%m-%d')  # type: ignore

            # if fecha_compra_ev < hoy:
            #     raise ValueError(f"La fecha de compra para {detalle_compra.insumo.nombre} no puede ser anterior a hoy.")
            # if fecha_cad_ev < hoy:
            #     raise ValueError(f"La fecha de caducidad para {detalle_compra.insumo.nombre} no puede ser anterior a hoy.")
            # if detalle_compra.cantidad_comprada <= 0:
            #     raise ValueError(f"Servicio: La cantidad de {detalle_compra.insumo.nombre} debe ser mayor a 0.")
            # if detalle_compra.monto_unitario <= 0:
            #     raise ValueError(f"Servicio: El precio unitario de {detalle_compra.insumo.nombre} debe ser mayor a 0.")
            # if not ConversorUnidades.es_valida(detalle_compra.unidad_medida):
            #     raise ValueError(f'Unidad de medida ingresada invalida para el insumo {detalle_compra.insumo.nombre}.')

            # formatear fecha
            #detalle_compra.fecha_caducidad = self._formatear_a_iso(detalle_compra.fecha_caducidad) # type: ignore
            #detalle_compra.fecha_compra = self._formatear_a_iso(detalle_compra.fecha_compra) # type: ignore

            # calcular importes de cada detalle compra, que es precio unitario por cantidad comprada
            detalle_compra.importe = self._calcular_importe(detalle_compra.monto_unitario,detalle_compra.cantidad_comprada)
            # agregar a lista de importes para posterior suma
            importes.append(detalle_compra.importe)
            # calculando la cantidad actual inicial, la cual es igual a la cantidad comprada
            detalle_compra.cantidad_actual = detalle_compra.cantidad_comprada
            # agregando stock nuevo al insumo
            #self._abastecer_insumo(detalle_compra.insumo,detalle_compra.cantidad_comprada)

        # calculando total bruto
        compra_nueva.total_bruto = self._calcular_total_bruto(importes)
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

        # # evaluar fechas
        # #convirtiendo fecha a date
        # fecha_creacion = datetime.strptime(str(compra_act.fecha_creacion), "%d-%m-%Y").date()
        # # convirtiendo a formato anglosajon, (btw que palabra poco comun)
        # #fecha_creacion_ev = fecha_creacion.strftime("%Y-%m-%d")
        # hoy = date.today()
        #
        # # validando que la fecha de creacion sea "hoy"
        # if fecha_creacion < hoy:
        #     raise ValueError(f'La fecha de creacion de la compra no puede ser anterior a hoy.')
        #
        # # formateando fecha de creacion
        # compra_act.fecha_creacion = self._formatear_a_iso(compra_act.fecha_creacion) # type: ignore
        compra_act.fecha_creacion = datetime.strptime(str(compra_act.fecha_creacion), "%d-%m-%Y")
        for detalle_compra in compra_act.lista_compras:
            # detalle_compra.fecha_compra = datetime.strptime(str(detalle_compra.fecha_compra), "%Y-%m-%d").date()
            # detalle_compra.fecha_caducidad = datetime.strptime(str(detalle_compra.fecha_caducidad), "%Y-%m-%d").date()
            detalle_compra.fecha_compra = datetime.strptime(str(detalle_compra.fecha_compra), "%d-%m-%Y")
            detalle_compra.fecha_caducidad = datetime.strptime(str(detalle_compra.fecha_caducidad), "%d-%m-%Y")


            # esto ya se va a validar en el controlador
            # if fecha_compra_ev < hoy:
            #     raise ValueError(f"La fecha de compra para {detalle_compra.insumo.nombre} no puede ser anterior a hoy.")
            # if fecha_cad_ev < hoy:
            #     raise ValueError(f"La fecha de caducidad para {detalle_compra.insumo.nombre} no puede ser anterior a hoy.")
            # if detalle_compra.cantidad_comprada <= 0:
            #     raise ValueError(f"Servicio: La cantidad de {detalle_compra.insumo.nombre} debe ser mayor a 0.")
            # if detalle_compra.monto_unitario <= 0:
            #     raise ValueError(f"Servicio: El precio unitario de {detalle_compra.insumo.nombre} debe ser mayor a 0.")
            # if not ConversorUnidades.es_valida(detalle_compra.unidad_medida):
            #     raise ValueError(f'Unidad de medida ingresada invalida para el insumo {detalle_compra.insumo.nombre}.')
            
            # recalcular importes de cada detalle compra, que es precio unitario por cantidad comprada
            detalle_compra.importe = self._calcular_importe(detalle_compra.monto_unitario,detalle_compra.cantidad_comprada)
            # agregar a lista de importes para posterior suma
            importes.append(detalle_compra.importe)
        
        # actualizando total bruto
        compra_act.total_bruto = self._calcular_total_bruto(importes)
        try:
            return self._compra_dao.actualizar_compra_completa(compra_act)
        except Error as err:
            raise ValueError(f"Servicio: Error en base de datos al actualizar compra: {err}")

    def crear_proveedor(self, proveedor:Proveedor):
        try:
            self._compra_dao.crear_proveedor(proveedor=proveedor)
        except mysql.connector.Error as err:
            raise Error(f'Error al crear proveedor en la BD - {err}')

    def eliminar_compra(self, num_compra:int):
        try:
            self._compra_dao.eliminar_compra(num_compra=num_compra)
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