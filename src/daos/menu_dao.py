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

    ''' funciones de creacion '''

    def crear_menu(self, menu:Menu) -> Menu:
        '''Crea un menu en la BD y regresa el menu de la actualizado de la BD.'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:

                # actualiza los atributos basicos del menu
                sql_menu = '''
                    INSERT INTO menu (nombre, fechaInicial, fechaFinal, cantidadPlatillos)
                    VALUES (%s, %s, %s, %s);
                '''
                cursor.execute(sql_menu, (
                    menu.nombre,
                    menu.fecha_inicial,
                    menu.fecha_final,
                    menu.cantidad_platillos,
                ))
                # si se llego hasta aqui sin lanzar excepcion, todo salio bien
                connection.commit()
                menu.num = cursor.lastrowid
                return menu.num

        except mysql.connector.Error as err:
            # si cualquiera de los updates, inserts o select fallo:
            connection.rollback()
            raise Error(f"DAO: Error en la transaccion al crear menu: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    ''' funciones de actualizacion '''
    def actualizar_menu_completo(self, menu:Menu):
        '''Actualiza el encabezado del menu y sincroniza todos sus platillos en una sola transaccion.'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:

                # actualiza los atributos basicos del menu
                sql_menu = '''
                    UPDATE menu
                    SET nombre = %s, fechaInicial = %s, fechaFinal = %s, cantidadPlatillos = %s
                    WHERE num = %s;
                '''
                cursor.execute(sql_menu, (
                    menu.nombre,
                    menu.fecha_inicial,
                    menu.fecha_final,
                    menu.cantidad_platillos,
                    menu.num
                ))

                # consulta que platillos existen actualmente en la BD para este menu
                sql_actuales = 'SELECT platillo FROM menu_platillo WHERE menu = %s;'
                cursor.execute(sql_actuales, (menu.num,))
                platillos_num_bd = [fila['platillo'] for fila in cursor.fetchall()]

                # conjunto de ids que el usuario tiene ahora en el menu
                ids_en_formulario = set()

                # iteracion de inserts y updates (sobre la misma conexion y cursor)
                for detalle in menu.detalles:
                    plat_id = detalle.platillo.num
                    ids_en_formulario.add(plat_id)

                    if plat_id in platillos_num_bd:
                        # si ya existia en la BD, se actualiza el precio
                        sql_update = '''
                            UPDATE menu_platillo 
                            SET precio = %s 
                            WHERE menu = %s AND platillo = %s;
                        '''
                        cursor.execute(sql_update, (detalle.precio, menu.num, plat_id))
                    else:
                        # si es nuevo en el menu, se inserta
                        sql_insert = '''
                            INSERT INTO menu_platillo (menu, platillo, precio) 
                            VALUES (%s, %s, %s);
                        '''
                        cursor.execute(sql_insert, (menu.num, plat_id, detalle.precio))

                # delete de los platillos que el usuario elimino
                for plat_id in platillos_num_bd:
                    if plat_id not in ids_en_formulario:
                        sql_delete = '''
                            DELETE FROM menu_platillo 
                            WHERE menu = %s AND platillo = %s;
                        '''
                        cursor.execute(sql_delete, (menu.num, plat_id))

                # solo un commit para todo
                # si se llego hasta aqui sin lanzar excepcion, todo salio bien
                connection.commit()

        except mysql.connector.Error as err:
            # si cualquiera de los updates, inserts o select fallo:
            connection.rollback()
            raise Error(f"DAO: Error en la transaccion al actualizar menu: {err}")
        finally:
            if connection.is_connected():
                connection.close()


    ''' funciones de eliminacion '''

    def eliminar_menu(self, num_menu:int):
        '''Elimina menu de la BD por su numero.'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:

                # actualiza los atributos basicos del menu
                sql_menu_platillo = '''
                    DELETE FROM menu_platillo WHERE menu = %s;
                '''
                cursor.execute(sql_menu_platillo,(num_menu,))    
                # si se llego hasta aqui sin lanzar excepcion, todo salio bien
                sql_menu = '''
                    DELETE FROM menu WHERE num = %s;
                '''
                cursor.execute(sql_menu,(num_menu,))   

                # reiniciar el autoinrement al siguiente disponible 
                cursor.execute("ALTER TABLE menu AUTO_INCREMENT = 1")

                connection.commit()

        except mysql.connector.Error as err:
            # si cualquiera de los updates, inserts o select fallo:
            connection.rollback()
            raise Error(f"DAO: Error en la transaccion al eliminar menu: {err}")
        finally:
            if connection.is_connected():
                connection.close()

