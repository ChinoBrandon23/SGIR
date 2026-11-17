
import mysql.connector
from mysql.connector import Error
from daos.insumo_dao import InsumoDAO
from models.marca import Marca
from models.tipo_insumo import TipoInsumo
from models.insumo import Insumo
from models.compra import Compra, DetalleCompra

from typing import List

class InsumoServicio:
    def __init__(self, insumo_dao:InsumoDAO):
        self._insumo_dao = insumo_dao


    def obtener_insumos(self) -> List[Compra]:
        try:
            return self._insumo_dao.obtener_compras()
        except mysql.connector.Error as err:
            raise IndexError(f'Servicio: Error al obtener los insumos. {err}')

    def obtener_insumo_por_nombre(self, nombre_ins:str):
        pass

    def obtener_tipos_insumo(self) -> List[TipoInsumo]:
        try:
            return self._insumo_dao.obtener_tipos_insumo()
        except mysql.connector.Error as err:
            raise IndexError(f"Servicio: Error al consultar los tipos insumos: {err}")

    def actualizar_insumo(self, insumo_act:Insumo):
        try:
            self._insumo_dao.actualizar_insumo(insumo=insumo_act)
        except mysql.connector.Error as err:
            raise IndexError(f'Servicio: Error al actualizar insumo. {err}')

    def eliminar_insumo(self):
        # pensando si usar o no
        pass
