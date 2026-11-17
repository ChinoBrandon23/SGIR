
import mysql.connector
from mysql.connector import Error
from daos.insumo_dao import InsumoDAO
from daos.compra_dao import CompraDAO
from models.marca import Marca
from models.tipo_insumo import TipoInsumo
from models.insumo import Insumo
from models.compra import Compra, DetalleCompra

from typing import List

class CompraServicio:
    def __init__(self, compra_dao:CompraDAO, insumo_dao:InsumoDAO):
        self._compra_dao = compra_dao
        self._insumo_dao = insumo_dao

    ''' FUNCIONES DE CONSULTA '''

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
