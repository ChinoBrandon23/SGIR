
import mysql.connector
from mysql.connector import Error
from daos.insumo_dao import InsumoDAO
from daos.compra_dao import CompraDAO
from models.marca import Marca
from models.tipo_insumo import TipoInsumo
from models.insumo import Insumo
from models.compra import Compra, DetalleCompra
from models.proveedor import Proveedor

from datetime import date, datetime
from typing import List

class CompraServicio:
    def __init__(self, compra_dao:CompraDAO, insumo_dao:InsumoDAO):
        self._compra_dao = compra_dao
        self._insumo_dao = insumo_dao

    #def registrar_compra(self, fecha_creacion:date, proveedor:Proveedor, detalles_compra:DetalleCompra):
    def registrar_compra(self, compra_nueva:Compra):
        importes:List[float] = []


        # validaciones
        if not compra_nueva.proveedor:
            raise ValueError("Servicio: La compra debe tener un proveedor asignado.")
            
        if not compra_nueva.lista_compras or len(compra_nueva.lista_compras) == 0:
            raise ValueError("Servicio: La compra debe contener al menos un insumo.")

        for detalle_compra in compra_nueva.lista_compras:
            # validaciones
            if detalle_compra.cantidad_comprada <= 0:
                raise ValueError(f"Servicio: La cantidad de {detalle_compra.insumo.nombre} debe ser mayor a 0.")
            if detalle_compra.monto_unitario <= 0:
                raise ValueError(f"Servicio: El precio unitario de {detalle_compra.insumo.nombre} debe ser mayor a 0.")

            # formatear fecha
            detalle_compra.fecha_caducidad = datetime.strptime(str(detalle_compra.fecha_caducidad), '%d-%m-%Y').strftime('%Y-%m-%d')
            detalle_compra.fecha_compra = datetime.strptime(str(detalle_compra.fecha_compra), '%d-%m-%Y').strftime('%Y-%m-%d')

            # calcular importes de cada detalle compra, que es precio unitario por cantidad comprada
            detalle_compra.importe = self._calcular_importe(detalle_compra.monto_unitario,detalle_compra.cantidad_comprada)
            # agregar a lista de importes para posterior suma
            importes.append(detalle_compra.importe)
            # calculando la cantidad actual inicial, la cual es igual a la cantidad comprada
            detalle_compra.cantidad_actual = detalle_compra.cantidad_comprada
            # agregando stock nuevo al insumo
            #self._abastecer_insumo(detalle_compra.insumo,detalle_compra.cantidad_comprada)

        # formateando fecha
        compra_nueva.fecha_creacion = datetime.strptime(str(compra_nueva.fecha_creacion), '%d-%m-%Y').strftime('%Y-%m-%d')

        compra_nueva.total_bruto = self._calcular_total_bruto(importes)

        try:
            return self._compra_dao.registrar_compra(compra_nueva)
        except Error as err:
            raise ValueError(f"Servicio: Error en base de datos al registrar compra: {err}")

    def _calcular_importe(self, monto_unit:float, cantidad:float) -> float:
        return monto_unit * cantidad


    def _calcular_total_bruto(self, importes:List[float]) -> float:
        return sum(importes)

    def obtener_proovedores(self) -> List[Proveedor]:
        try:
            return self._compra_dao.obtener_proveedores()
        except mysql.connector.Error as err:
            raise IndexError(f'Servicio: Error al obtener los proovedores. {err}')

    def obtener_compras(self) -> List[Compra]:
        '''Obtiene la lista de todas las compras y sus detalles, que hay en la BD.'''
        try:
            return self._compra_dao.obtener_compras()
        except mysql.connector.Error as err:
            raise IndexError(f'Servicio: Error al obtener las compras. {err}')

    def obtener_compra_por_nombre(self, nombre_ins:str):
        pass

    def actualizar_compra(self, compra:Compra):
        '''Actualiza una compra.'''
        pass


    def eliminar_compra(self):
        # pensando si usar o no
        pass
