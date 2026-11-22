import datetime
import time

from models.menu import Menu, DetalleMenu
from models.platillo import Platillo
from daos.menu_dao import MenuDAO


from datetime import date

import mysql.connector
from mysql.connector import Error

from typing import List

class MenuServicio:
    def __init__(self, menu_dao:MenuDAO):
        self._menu_dao = menu_dao

    ''' funciones de evaluacion '''

    def menu_existe(self,num_menu:int) -> bool:
        try:
            menu = self._menu_dao.obtener_menu_por_numero(num_menu)
            # evalua que el menu especificado exista
            if not menu:
                return False
            return True

        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrio un error: {err}\n')

    def obtener_platillos_invalidos_menu(self, menu: Menu, fecha_inicial: date, fecha_final: date):
        try:
            platillos_disponibles = self.obtener_platillos_disponibles(fecha_inicial, fecha_final)
            platillos_disponibles_idx = [plat.num for plat in platillos_disponibles]

            platillos_invalidos = []

            for detalle in menu.detalles:
                if detalle.platillo.num not in platillos_disponibles_idx:
                    platillos_invalidos.append(detalle.platillo)

            return platillos_invalidos
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error {err}\n')

    def platillo_existe(self, num_platillo:int) -> bool:
        try:
            if self._menu_dao.obtener_platillo_por_numero(num_platillo):
                return True
        except mysql.connector.Error as err:
            raise Error(f'Servicio: Error en la BD: {err}')
        return False

    ''' funcione de consulta'''

    def obtener_platillos(self) -> List[Platillo]:
        try:
            return self._menu_dao.obtener_platillos()
        except mysql.connector.Error as err:
            raise Error(f'Error en la BD. {err}')

    def obtener_platillos_disponibles(self, fecha_inicial, fecha_final) -> List[Platillo]:
        try:
            # ahora se convierte al formato que mysql usa y se pasa de nuevo a str
            fecha_inicial_formateada = datetime.datetime.strftime(fecha_inicial, '%Y-%m-%d') # type: ignore
            fecha_final_formateada = datetime.datetime.strftime(fecha_final, '%Y-%m-%d') # type: ignore

            return self._menu_dao.obtener_platillos_disponibles(fecha_inicial, fecha_final)
        except mysql.connector.Error as err:
            raise Error(f'Error en la BD. {err}')

    def obtener_menu_por_id(self,num_menu:int) -> Menu:
        try:
            menu = self._menu_dao.obtener_menu_por_numero(num_menu)
            # evalua que el menu especificado exista
            if not menu:
                raise IndexError(f'Servicio: Menu con numero {num_menu} no existe.')
            return menu
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrio un error: {err}\n')

    def obtener_menu_por_nombre(self, nombre_menu: str) -> Menu:
        try:
            menu = self._menu_dao.obtener_menu_por_nombre(nombre_menu)
            if not menu:
                raise IndexError(f'Servicio: El menú "{nombre_menu}" no existe.')
            return menu
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al obtener menú por nombre: {err}\n')
    
    def obtener_menus_disponibles(self, fecha_actual:date) -> List[Menu]:
        '''Obtiene los menus disponibles de una fecha. (Con platillos y precios)'''
        try:
            menus = self._menu_dao.obtener_menus_disponibles(fecha_actual)
            # evalua que haya menus en la fecha especificada
            if not menus:
                raise IndexError(f'Servicio: No hay menus disponibles para la fecha.')

            # creando el lista de objetos menu con sus respectivos platillos
            try:
                for menu in menus:
                    platillos = self._menu_dao.obtener_platillos_de_menu(menu.num)    
                    for detalleMenu in platillos:
                        menu.agregar_platillo(platillo=detalleMenu.platillo,precio=detalleMenu.precio)     
                return menus
            except mysql.connector.Error as err:
                raise ValueError(f'Servicio: Ocurrio un error: {err}\n')
            
        except mysql.connector.Error as err:
            raise ValueError(f'Ocurrio un error: {err}')

    def obtener_menus(self) -> List[Menu]:
        '''Obtiene todos los menus de la BD. (Con platillos y precios)'''
        try:
            menus = self._menu_dao.obtener_menus()
            # evalua que haya menus en la fecha especificada
            if not menus:
                raise IndexError(f'Servicio: No hay menus disponibles.')
            # creando el lista de objetos menu con sus respectivos platillos
            try:
                for menu in menus:
                    platillos = self._menu_dao.obtener_platillos_de_menu(menu.num)    
                    for detalleMenu in platillos:
                        menu.agregar_platillo(platillo=detalleMenu.platillo,precio=detalleMenu.precio)     
                return menus
            except mysql.connector.Error as err:
                raise ValueError(f'Servicio: Ocurrio un error: {err}\n')
            
        except mysql.connector.Error as err:
            raise ValueError(f'Ocurrio un error: {err}')

    def obtener_menus_por_rango_fecha(self, fecha_inicial:str, fecha_final:str) -> List[Menu]:
        try:
            # obtengo el objeto date a partir del str basado en el formato en que lo ingresó el usuario
            fecha_inicial = datetime.datetime.strptime(fecha_inicial, '%d-%m-%Y') # type: ignore
            fecha_final = datetime.datetime.strptime(fecha_final, '%d-%m-%Y') # type: ignore

            # ahora se convierte al formato que mysql usa y se pasa de nuevo a str
            fecha_inicial_formateada = datetime.datetime.strftime(fecha_inicial, '%Y-%m-%d') # type: ignore
            fecha_final_formateada = datetime.datetime.strftime(fecha_final, '%Y-%m-%d') # type: ignore

            menus = self._menu_dao.obtener_menus_disponibles_por_rango_fecha(fecha_inicial_formateada, fecha_final_formateada)

            if not menus:
                raise IndexError(f'Servicio: No hay menus disponibles en el rango.')

            try:
                for menu in menus:
                    platillos = self._menu_dao.obtener_platillos_de_menu(menu.num)
                    for detalleMenu in platillos:
                        menu.agregar_platillo(platillo=detalleMenu.platillo, precio=detalleMenu.precio)
                return menus
            except mysql.connector.Error as err:
                raise ValueError(f'Servicio: Ocurrio un error al obtener platillos: {err}\n')

        except mysql.connector.Error as err:
            raise ValueError(f'Ocurrio un error al buscar menús por rango de fecha: {err}')

    def obtener_menus_por_match_nombre(self, insumo_nombre:str) -> List[Menu]:
        try:
            menus = self._menu_dao.obtener_menus_disponibles_por_match_nombre(insumo_nombre)

            if not menus:
                raise IndexError(f'Servicio: No hay menus disponibles en el rango.')

            try:
                for menu in menus:
                    platillos = self._menu_dao.obtener_platillos_de_menu(menu.num)
                    for detalleMenu in platillos:
                        menu.agregar_platillo(platillo=detalleMenu.platillo, precio=detalleMenu.precio)
                return menus
            except mysql.connector.Error as err:
                raise ValueError(f'Servicio: Ocurrio un error al obtener platillos: {err}\n')

        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al obtener menús por nombre: {err}\n')

    def obtener_platillos_de_un_menu(self, num_menu:int) -> List[DetalleMenu]:
        ''' Retorna los platillos de un menu '''
        try:
            # evalua que el menu especificado exista
            if not self._menu_dao.obtener_menu_por_numero(num_menu):
                raise IndexError(f'Servicio: Menu con numero {num_menu} no existe.')
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrio un error: {err}\n')
        
        try:
            respuesta = self._menu_dao.obtener_platillos_de_menu(num_menu)                
            return respuesta
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrio un error: {err}\n')

    '''funciones de creacion'''

    def crear_menu(self, nuevo_menu: Menu):
        try:
            self._menu_dao.crear_menu(menu=nuevo_menu)
            nuevo_num = self.obtener_menu_por_nombre(nuevo_menu.nombre).num
            nuevo_menu.num = nuevo_num
            self.actualizar_menu(nuevo_menu)

        except mysql.connector.Error as err:
            raise Error(f'Error en crear menu en la BD - {err}')

    ''' funciones de actualizacion'''

    def actualizar_menu(self, menu:Menu):
        ''' Actualiza un menu y sus platillos.'''
        # actualizamos el numero de platilos del menu
        menu.cantidad_platillos = self.calcular_num_platillos(menu)
        
        # actualiza menu completo
        try:
            self._menu_dao.actualizar_menu_completo(menu=menu)
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Error al actualizar menu. {err}\n')

    ''' funciones de eliminacion'''

    def eliminar_menu(self, num_menu:int):
        try:
            self._menu_dao.eliminar_menu(num_menu)
        except mysql.connector.Error as err:
            raise Error(f'Error en la al eliminar menu de la BD - {err}')

    '''funciones de calculo'''

    def calcular_num_platillos(self, menu:Menu) -> int:
        '''calcula el numero de platillos disponibles de un menu'''
        return len(menu.detalles)





