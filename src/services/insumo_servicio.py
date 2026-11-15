
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
