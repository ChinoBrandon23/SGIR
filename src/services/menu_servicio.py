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

    def menu_existe(self,num_menu:int) -> bool:
        try:
            menu = self._menu_dao.obtener_menu_por_numero(num_menu)
            # evalua que el menu especificado exista
            if not menu:
                return False
            return True

        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrio un error: {err}\n')

    def platillo_existe(self, num_platillo:int) -> bool:
        try:
            if self._menu_dao.obtener_platillo_por_numero(num_platillo):
                return True
        except mysql.connector.Error as err:
            raise Error(f'Servicio: Error en la BD: {err}')
        return False

    ''' funcione de consulta'''
    def obtener_platillos(self):
        try:
            return self._menu_dao.obtener_platillos()
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

    def obtener_platillos_de_un_menu(self, num_menu:int) -> List[DetalleMenu]:
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





