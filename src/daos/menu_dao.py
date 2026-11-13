from models.menu import Menu, DetalleMenu
from models.platillo import Platillo
from models.categoria import Categoria
from models.receta import Receta


from datetime import date,datetime
from typing import List

import mysql.connector
from mysql.connector import Error


class MenuDAO:    
    def __init__(self, db_manager):
        self.db = db_manager 

    '''funciones de consulta'''
    def obtener_platillo_por_numero(self, num_platillo:int):
        '''Obtiene un platillo por su numero. Hueco'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                    SELECT p.num
                    FROM platillo p
                    WHERE p.num = %s;
                '''
                cursor.execute(sql,(num_platillo,))
                return cursor.fetchone()
                
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error generico de mysql menus: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_menu_por_numero(self, num_menu:int) -> Menu:
        '''obtiene un menu por su numero, justamente con sus platillos.'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                    SELECT 
                    m.num numMenu,
                    m.nombre nombreMenu,
                    m.cantidadPlatillos cantPlatillos,
                    m.fechaInicial fechaInicial,
                    m.fechaFinal fechaFinal
                    FROM menu m
                    WHERE m.num = %s;
                '''
                cursor.execute(sql,(num_menu,))
                fila = cursor.fetchone()
                lista_menus: List[Menu] = []
                menu = Menu(
                        num=fila['numMenu'],
                        nombre=fila['nombreMenu'],
                        cantidad_platillos=fila['cantPlatillos'],
                        fecha_inicial=fila['fechaInicial'],
                        fecha_final=fila['fechaFinal']
                        )
                try:
                    # agregando sus respectivos platillos al menu
                    for detalleMenu in self.obtener_platillos_de_menu(num_menu):
                        menu.agregar_platillo(detalleMenu.platillo,detalleMenu.precio)
                except mysql.connector.Error as err:
                    raise Error(f'DAO: Error generico en la BD: {err}')
                return menu
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error generico de mysql menus: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_menus_disponibles(self, fecha_actual:date) -> List[Menu]:
        '''Retorna los menus disponibles segun la fecha actual. (Sin los platillos).'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                    SELECT 
                    m.num numMenu,
                    m.nombre nombreMenu,
                    m.cantidadPlatillos cantPlatillos,
                    m.fechaInicial fechaInicial,
                    m.fechaFinal fechaFinal
                    FROM menu m
                    WHERE %s BETWEEN m.fechaInicial AND m.fechaFinal;
                '''
                cursor.execute(sql,(fecha_actual,))
                filas = cursor.fetchall()
                lista_menus: List[Menu] = []

                for fila in filas:
                    lista_menus.append(Menu(
                                    num=fila['numMenu'],
                                    nombre=fila['nombreMenu'],
                                    cantidad_platillos=fila['cantPlatillos'],
                                    fecha_inicial=fila['fechaInicial'],
                                    fecha_final=fila['fechaFinal']
                                    ))
                return lista_menus
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error generico de mysql menus: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_menus(self) -> List[Menu]:
        '''Retorna todos los menus de la BD. (Sin los platillos).'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                    SELECT 
                    m.num numMenu,
                    m.nombre nombreMenu,
                    m.cantidadPlatillos cantPlatillos,
                    m.fechaInicial fechaInicial,
                    m.fechaFinal fechaFinal
                    FROM menu m
                '''
                cursor.execute(sql)
                filas = cursor.fetchall()
                lista_menus: List[Menu] = []

                for fila in filas:
                    lista_menus.append(Menu(
                                    num=fila['numMenu'],
                                    nombre=fila['nombreMenu'],
                                    cantidad_platillos=fila['cantPlatillos'],
                                    fecha_inicial=fila['fechaInicial'],
                                    fecha_final=fila['fechaFinal']
                                    ))
                return lista_menus
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error generico de mysql menus: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_platillos(self) -> List[Platillo]:
        '''Retorna todos los platillos de la BD.'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                    SELECT
                    p.num numPlatillo,
                    p.nombre nombrePlatillo,
                    cat.clave claveCat,
                    cat.nombre nombreCat,
                    p.receta numReceta
                    FROM platillo p
                    INNER JOIN categoria cat ON p.categoria = cat.clave;
                '''
                cursor.execute(sql)
                filas = cursor.fetchall()
                lista_platillos: List[Platillo] = []

                for fila in filas:
                    lista_platillos.append(Platillo(
                                num=fila['numPlatillo'],
                                nombre=fila['nombrePlatillo'],
                                categoria=Categoria(clave=fila['claveCat'],nombre=fila['nombreCat']),
                                receta=Receta(fila['numReceta'],'',0,{})))
                return lista_platillos
        except mysql.connector.Error as err:
            raise Error(f"DAO: {err}")
        finally:
            if connection.is_connected():
                connection.close()
    
    def obtener_platillos_de_menu(self, num_menu:int) -> List[DetalleMenu]:
        '''Retorna los platillos de un menu.'''
        # num, nombre platillo, claveCategoria, nombre categoria, num receta, precio
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                    SELECT
                    p.num numPlatillo,
                    p.nombre nombrePlatillo,
                    cat.clave claveCat,
                    cat.nombre nombreCat,
                    p.receta numReceta,
                    mp.precio precioPlat
                    FROM menu_platillo mp
                    INNER JOIN menu m ON mp.menu = m.num
                    INNER JOIN platillo p ON mp.platillo = p.num
                    INNER JOIN categoria cat ON p.categoria = cat.clave
                    WHERE m.num = %s;
                '''
                cursor.execute(sql,(num_menu,))
                filas = cursor.fetchall()
                lista_platillos: List[DetalleMenu] = []

                for fila in filas:
                    lista_platillos.append(DetalleMenu(
                        platillo=Platillo(
                                num=fila['numPlatillo'],
                                nombre=fila['nombrePlatillo'],
                                categoria=Categoria(clave=fila['claveCat'],nombre=fila['nombreCat']),
                                receta=Receta(fila['numReceta'],'',0,{})),
                        precio=fila['precioPlat']))
                return lista_platillos
        except mysql.connector.Error as err:
            raise Error(f"DAO: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    ''' funciones de actualizacion '''
    def actualizar_menu(self, menu_actualizado:Menu):
        '''Actualiza el registro de un menu. Sin platillos'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                # nombre, vigencia, platillos
                sql = '''
                        UPDATE menu
                        SET 
                        menu.nombre = %s, 
                        menu.fechaInicial = %s, 
                        menu.fechaFinal = %s,
                        menu.cantidadPlatillos = %s
                        WHERE menu.num = %s;
                        '''
                valores = (
                    menu_actualizado.nombre,
                    menu_actualizado.fecha_inicial,
                    menu_actualizado.fecha_final,
                    menu_actualizado.cantidad_platillos,
                    menu_actualizado.num
                )
                cursor.execute(sql,valores)
                connection.commit()
                
        except mysql.connector.Error as err:
            connection.rollback()
            # manejo de errores de base de datos
            raise Error(f"DAO: Error al actualizar el menu: {err}")

        finally:
            # devuelve el pool, incluso si hubo un error o un return antes
            if connection.is_connected():
                connection.close()

    def actualizar_platillo_de_menu(self, num_menu:int, platillo_actualizado:DetalleMenu):
        '''Actualiza el platillo de un menu'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                # nombre, vigencia, platillos
                sql = '''
                        UPDATE menu_platillo mp
                        SET 
                        mp.precio = %s
                        WHERE mp.menu = %s AND mp.platillo = %s;
                        '''
                valores = (
                    platillo_actualizado.precio,
                    num_menu,
                    platillo_actualizado.platillo.num
                )
                cursor.execute(sql,valores)
                connection.commit()

        except mysql.connector.Error as err:
            connection.rollback()
            raise Error(f"DAO: Error al actualizar el platillo {platillo_actualizado.platillo.nombre} del menu: {err}") 
        finally:
            if connection.is_connected():
                connection.close()

    def agregar_platillo_menu(self, num_menu:int, platillo_nuevo:DetalleMenu):
        '''Agrega un platillo a un menu'''
        pass










