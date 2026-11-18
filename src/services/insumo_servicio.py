import random

import mysql.connector
from mysql.connector import Error
from daos.insumo_dao import InsumoDAO
from daos.compra_dao import CompraDAO
from models.marca import Marca
from models.tipo_insumo import TipoInsumo
from models.insumo import Insumo
from models.compra import Compra, DetalleCompra

from typing import List

class InsumoServicio:
    def __init__(self, insumo_dao:InsumoDAO, compra_dao:CompraDAO):
        self._insumo_dao = insumo_dao
        self._compra_dao = compra_dao

    def obtener_compras(self) -> List[Compra]:
        try:
            return self._compra_dao.obtener_compras()
        except mysql.connector.Error as err:
            raise IndexError(f'Servicio: Error al obtener las compras. {err}')

    def obtener_detalles_compra_por_insumo(self, insumo_num):
        try:
            return self._compra_dao.obtener_detalles_compras_por_insumo(insumo_num)
        except mysql.connector.Error as err:
            raise IndexError(f'Servicio: Error al obtener los detalles de compras. {err}')

    def obtener_insumo_por_nombre(self, nombre_ins:str):
        pass

    def obtener_insumo_por_num(self, num_insumo:int) -> Insumo:
        try:
            return self._insumo_dao.obtener_insumo_por_num(num_insumo)
        except mysql.connector.Error as err:
            raise IndexError(f'Servicio: Error al obtener insumo. {err}')

    def obtener_insumos(self) -> List[Insumo]:
        ''' Obtiene todos los insumos.'''
        try:
            return self._insumo_dao.obtener_insumos()
        except mysql.connector.Error as err:
            raise IndexError(f'Servicio: Error al consultar insumos. {err}')

    def obtener_tipos_insumo(self) -> List[TipoInsumo]:
        try:
            return self._insumo_dao.obtener_tipos_insumo()
        except mysql.connector.Error as err:
            raise IndexError(f"Servicio: Error al consultar los tipos insumos: {err}")

    def obtener_insumos_por_tipo_insumo(self, tipo_insumo_clave:str) -> List[Insumo]:
        try:
            return self._insumo_dao.obtener_insumo_por_tipo_insumo(tipo_insumo_clave)
        except mysql.connector.Error as err:
            raise IndexError(f'Servicio: Error al consultar insumos. {err}')

    def obtener_insumos_por_match_nombre(self, nombre_insumo:str) -> List[Insumo]:
        try:
            return self._insumo_dao.obtener_insumo_por_match_nombre(nombre_insumo)
        except mysql.connector.Error as err:
            raise IndexError(f'Servicio: Error al consultar insumos. {err}')

    def obtener_insumos_con_stock_bajo(self) -> List[Insumo]:
        try:
            return self._insumo_dao.obtener_insumo_con_stock_bajo()
        except mysql.connector.Error as err:
            raise IndexError(f'Servicio: Error al consultar insumos. {err}')

    def obtener_insumos_por_marca(self, marca_num:str) -> List[Insumo]:
        try:
            return self._insumo_dao.obtener_insumo_por_marca(marca_num)
        except mysql.connector.Error as err:
            raise IndexError(f'Servicio: Error al consultar insumos. {err}')

    def obtener_marcas(self) -> List[Marca]:
            try:
                return self._insumo_dao.obtener_marcas()
            except mysql.connector.Error as err:
                raise IndexError(f"Servicio: Error al consultar las marcas: {err}")
        
    def actualizar_insumo(self, insumo_act:Insumo):
        try:
            self._insumo_dao.actualizar_insumo(insumo=insumo_act)
        except mysql.connector.Error as err:
            raise IndexError(f'Servicio: Error al actualizar insumo. {err}')

    def eliminar_insumo(self):
        # pensando si usar o no
        pass

    def obtener_tipo_insumo_por_clave(self, clave:str):
        try:
            return self._insumo_dao.obtener_tipo_insumo_por_clave(clave)
        except mysql.connector.Error as err:
            raise IndexError(f"Servicio: Error al obtener de tipo insumo: {err}")

    def obtener_tipo_insumo_por_nombre(self, nombre:str):
        try:
            return self._insumo_dao.obtener_tipo_insumo_por_nombre(nombre)
        except mysql.connector.Error as err:
            raise IndexError(f"Servicio: Error al obtener de tipo insumo: {err}")

    def tipo_insumo_existe(self, nombre_tipo:str):
        try:
            tipo_insumo = self._insumo_dao.obtener_tipo_insumo_por_nombre(nombre_tipo)
            if tipo_insumo:
                return True
            return False

        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Error al obtener tipo de insumo: {err}\n')

    def crear_tipo_insumo(self, nombre_tipo:str):
        try:
            # verifica si ya existe el tipo de insumo
            if self.tipo_insumo_existe(nombre_tipo):
                raise ValueError(f'Servicio: Error tipo de insumo ya existe')

            # por default se genera clave utilizando los primeros 3 caracteres del nombre
            clave = nombre_tipo[:3]

            # verifica si la clave del tipo de insumo existe en la bd
            tipo_insumo_por_clave = self.obtener_tipo_insumo_por_clave(clave)

            while tipo_insumo_por_clave:
                # genera nueva clave
                clave = "".join(random.choices(nombre_tipo.split(), k=3))
                tipo_insumo_por_clave = self.obtener_tipo_insumo_por_clave(clave)

            self._insumo_dao.crear_tipo_insumo(tipo_insumo=TipoInsumo(clave, nombre_tipo))
        except mysql.connector.Error as err:
            raise IndexError(f'Servicio: Error al crear tipo de insumo. {err}')
