import random
import time

import mysql.connector

from daos.platillos_dao import PlatillosDAO
from models.categoria import Categoria
from models.platillo import Platillo


class PlatillosServicio:
    def __init__(self, platillos_dao:PlatillosDAO):
        self._platillos_dao = platillos_dao

    ''' funciones de evaluación '''

    def platillo_existe(self, num_platillo) -> bool:
        try:
            if self.obtener_platillo_por_num(num_platillo):
                return True
            else:
                return False
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al obtener platillo: {err}\n')

    ''' funciones de consulta '''

    def obtener_platillos(self) -> list[Platillo]:
        try:
            return self._platillos_dao.obtener_platillos()
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al obtener los platillos: {err}\n')

    def obtener_platillo_por_num(self, num_platillo):
        try:
            return self._platillos_dao.obtener_platillo_por_numero(num_platillo)
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al obtener platillo: {err}\n')

    def obtener_platillos_match_nombre(self, nombre_platillo) -> list[Platillo]:
        try:
            return self._platillos_dao.obtener_platillos_por_match_nombre(nombre_platillo)
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al obtener platillos: {err}\n')

    def obtener_platillo_por_nombre(self, nombre_platillo):
        try:
            return self._platillos_dao.obtener_platillo_por_nombre(nombre_platillo)
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al obtener platillo: {err}\n')

    def obtener_categorias(self) -> list[Categoria]:
        try:
            return self._platillos_dao.obtener_categorias()
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al obtener categorías: {err}\n')

    def obtener_platillos_por_categoria(self, categoria_clave:str) -> list[Platillo]:
        try:
            return self._platillos_dao.obtener_platillos_por_categoria(categoria_clave)
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al obtener platillos: {err}\n')

    def obtener_categoria_por_nombre(self, nombre_cat:str):
        try:
            return self._platillos_dao.obtener_categoria_por_nombre(nombre_cat)
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al obtener categoría: {err}\n')

    def obtener_categoria_por_clave(self, clave:str):
        try:
            return self._platillos_dao.obtener_categoria_por_clave(clave)
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al obtener categoría: {err}\n')

    ''' funciones de actualización '''

    def actualizar_platillo(self, platillo:Platillo):
        try:
            self._platillos_dao.actualizar_platillo(platillo)
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al actualizar el platillo: {err}\n')

    ''' funciones de registro '''

    def crear_platillo(self, platillo:Platillo):
        try:
            if self._platillos_dao.obtener_platillo_por_nombre(platillo.nombre):
                # platillo ya existe
                raise ValueError(f"Servicio: Error el platillo ya existe")

            self._platillos_dao.crear_platillo(platillo)
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al actualizar el platillo: {err}\n')

    def crear_categoria(self, categoria_nombre:str):
        try:
            if self.obtener_categoria_por_nombre(categoria_nombre):
                # platillo ya existe
                raise ValueError(f"Servicio: Error la categoría ya existe")

            # generar clave
            clave = categoria_nombre[:3]

            # verifica si la clave del tipo de insumo existe en la bd
            categoria_por_clave = self.obtener_categoria_por_clave(clave)

            while categoria_por_clave:
                # genera nueva clave
                clave = "".join(random.choices(categoria_nombre.split(), k=3))
                categoria_por_clave = self.obtener_categoria_por_clave(clave)

            categoria_obj = Categoria(clave=clave, nombre=categoria_nombre)

            self._platillos_dao.crear_categoria(categoria_obj)
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al crear la categoría: {err}\n')

    ''' funciones de borrado '''

    def borrar_platillo(self, num_platillo):
        try:
            # evalua si el platillo ha sido registrado en una venta, de ser así, no lo va a borrar
            # sino solo va a quitar la receta base para 'desactivarlo' pero seguirá en la bd para
            # referencias de ventas
            if len(self._platillos_dao.obtener_ventas_platillo(num_platillo)):
                self._platillos_dao.desactivar_platillo(num_platillo)
            else:
                # borra definitivamente el platillo porque su eliminación no altera ningún otro registro
                self._platillos_dao.borrar_platillo(num_platillo)
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al borrar el platillo: {err}\n')