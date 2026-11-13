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
        pass

    ''' funciones de actualizacion'''
    def actualizar_menu(self, menu:Menu):
        ''' Actualiza un menu y sus platillos '''
        # actualizamos el numero de platilos del menu
        menu.cantidad_platillos = self.calcular_num_platillos(menu)
        
        # actualiza solo menu sin platillos
        try:
            self._menu_dao.actualizar_menu_completo(menu=menu)
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Error al actualizar menu. {err}\n')

        ## obtenemos los platillos de este menu en la BD
        #try:
        #    platillos_bd = self._menu_dao.obtener_platillos_de_menu(menu.num)
        #except mysql.connector.Error as err:
        #    raise Error(f'Servicio: Error en la BD: {err}')
#
        ## crear lista de numeros de platillos para comparar
        #lista_numero_platillos_bd: List[int] = []
        #for detallePlat in platillos_bd:
        #    lista_numero_platillos_bd.append(detallePlat.platillo.num)
#
        ## iteramos para saber cuales platillos son nuevos y cuales no
        #for numPlat in lista_numero_platillos_bd:
        #    for detalleMenu in menu.detalles:
        #        if not detalleMenu.platillo.num in lista_numero_platillos_bd:
        #            # significa que el platillo no existe en el menu y hay que agregarlo
        #            try:
        #                if not self.platillo_existe(detalleMenu.platillo.num):
        #                    raise ValueError(f'El platillo {detalleMenu.platillo.num} que se desea agregar al menu, no existe.')
        #                self._menu_dao.agregar_platillo_menu(menu.num,detalleMenu)
        #            except mysql.connector.Error as err:
        #                raise Error(f'Servicio: Error en la BD. {err}\n')
#
        #        if detalleMenu.platillo.num in lista_numero_platillos_bd:
        #            # significa que el platillo si esta en menu y hay que actualizar
        #            try:
        #                self._menu_dao.actualizar_platillo_de_menu(menu.num,detalleMenu)
        #            except mysql.connector.Error as err:
        #                raise Error(f'Servicio: Error en la BD. {err}\n')
        #

    '''funciones de calculo'''

    def calcular_num_platillos(self, menu:Menu) -> int:
        '''calcula el numero de platillos disponibles de un menu'''
        return len(menu.detalles)





