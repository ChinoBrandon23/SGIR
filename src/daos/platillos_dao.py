import time

from models.platillo import Platillo
from models.categoria import Categoria
from models.receta import Receta

from typing import List

import mysql.connector
from mysql.connector import Error


class PlatillosDAO:
    def __init__(self, db_manager):
        self.db = db_manager

    '''funciones de consulta'''

    def obtener_platillo_por_numero(self, num_platillo: int) -> Platillo|None:
        '''Obtiene un platillo por su numero'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                      SELECT p.num platNum, 
                             p.nombre nombrePlat, 
                             p.categoria cat, 
                          cat.nombre nombreCat,
                             p.receta recetaNum,
                            r.nombre nombreRec,
                            r.numPorciones numPorciones
                      FROM platillo p
                    INNER JOIN receta as r on p.receta = r.num
                          INNER JOIN categoria as cat on p.categoria = cat.clave
                      WHERE p.num = %s;
                      '''
                cursor.execute(sql, (num_platillo,))

                fila = cursor.fetchone()

                if fila is None:
                    return fila

                platillo = Platillo(num=fila['platNum'],
                                    nombre=fila['nombrePlat'],
                                    categoria=Categoria(clave=fila['cat'],
                                                        nombre=fila['nombreCat']),
                                    receta=Receta(num=fila['recetaNum'],
                                                  nombre=fila['nombreRec'],
                                                  num_porciones=fila['numPorciones'],
                                                  instrucciones={})
                                    )

                return platillo

        except mysql.connector.Error as err:
            raise Error(f"DAO: Error generico de mysql platillos: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_platillos(self) -> List[Platillo]:
        '''Retorna todos los platillos de la BD.'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                      SELECT p.num platNum, 
                             p.nombre nombrePlat, 
                             p.categoria cat, 
                          cat.nombre nombreCat,
                             p.receta recetaNum,
                            r.nombre nombreRec,
                            r.numPorciones numPorciones
                      FROM platillo p
                        INNER JOIN receta as r on p.receta = r.num
                          INNER JOIN categoria as cat on p.categoria = cat.clave
                          WHERE p.receta IS NOT NULL
                          ORDER BY p.num;
                      '''
                cursor.execute(sql)
                filas = cursor.fetchall()
                lista_platillos: List[Platillo] = []

                for fila in filas:
                    lista_platillos.append(Platillo(num=fila['platNum'],
                                        nombre=fila['nombrePlat'],
                                        categoria=Categoria(clave=fila['cat'],
                                                            nombre=fila['nombreCat']),
                                        receta=Receta(num=fila['recetaNum'],
                                                      nombre=fila['nombreRec'],
                                                      num_porciones=fila['numPorciones'],
                                                      instrucciones={})
                                        ))
                return lista_platillos
        except mysql.connector.Error as err:
            raise Error(f"DAO: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_platillos_por_match_nombre(self, nombre:str):
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = f'''
                      SELECT p.num          platNum,
                             p.nombre       nombrePlat,
                             p.categoria    cat,
                             cat.nombre     nombreCat,
                             p.receta       recetaNum,
                             r.nombre       nombreRec,
                             r.numPorciones numPorciones
                      FROM platillo p
                               INNER JOIN receta as r on p.receta = r.num
                               INNER JOIN categoria as cat on p.categoria = cat.clave
                        WHERE p.nombre LIKE('%{nombre}%')
                      ORDER BY p.nombre;
                      '''
                cursor.execute(sql)
                filas = cursor.fetchall()
                lista_platillos: List[Platillo] = []

                for fila in filas:
                    lista_platillos.append(Platillo(num=fila['platNum'],
                                                    nombre=fila['nombrePlat'],
                                                    categoria=Categoria(clave=fila['cat'],
                                                                        nombre=fila['nombreCat']),
                                                    receta=Receta(num=fila['recetaNum'],
                                                                  nombre=fila['nombreRec'],
                                                                  num_porciones=fila['numPorciones'],
                                                                  instrucciones={})
                                                    ))
                return lista_platillos
        except mysql.connector.Error as err:
            raise Error(f"DAO: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_platillos_por_categoria(self, clave_cat:str):
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                      SELECT p.num          platNum,
                             p.nombre       nombrePlat,
                             p.categoria    cat,
                             cat.nombre     nombreCat,
                             p.receta       recetaNum,
                             r.nombre       nombreRec,
                             r.numPorciones numPorciones
                      FROM platillo p
                               INNER JOIN receta as r on p.receta = r.num
                               INNER JOIN categoria as cat on p.categoria = cat.clave
                        WHERE p.categoria = %s
                      ORDER BY p.num;
                      '''
                cursor.execute(sql, (clave_cat,))
                filas = cursor.fetchall()
                lista_platillos: List[Platillo] = []

                for fila in filas:
                    lista_platillos.append(Platillo(num=fila['platNum'],
                                                    nombre=fila['nombrePlat'],
                                                    categoria=Categoria(clave=fila['cat'],
                                                                        nombre=fila['nombreCat']),
                                                    receta=Receta(num=fila['recetaNum'],
                                                                  nombre=fila['nombreRec'],
                                                                  num_porciones=fila['numPorciones'],
                                                                  instrucciones={})
                                                    ))
                return lista_platillos
        except mysql.connector.Error as err:
            raise Error(f"DAO: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_platillo_por_nombre(self, nombre) -> Platillo|None:
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                      SELECT p.num          platNum,
                             p.nombre       nombrePlat,
                             p.categoria    cat,
                             cat.nombre     nombreCat,
                             p.receta       recetaNum,
                             r.nombre       nombreRec,
                             r.numPorciones numPorciones
                      FROM platillo p
                               INNER JOIN receta as r on p.receta = r.num
                               INNER JOIN categoria as cat on p.categoria = cat.clave
                      WHERE p.nombre = %s;
                      '''
                cursor.execute(sql, (nombre,))

                fila = cursor.fetchone()

                if fila is None:
                    return fila

                platillo = Platillo(num=fila['platNum'],
                                    nombre=fila['nombrePlat'],
                                    categoria=Categoria(clave=fila['cat'],
                                                        nombre=fila['nombreCat']),
                                    receta=Receta(num=fila['recetaNum'],
                                                  nombre=fila['nombreRec'],
                                                  num_porciones=fila['numPorciones'],
                                                  instrucciones={})
                                    )

                return platillo

        except mysql.connector.Error as err:
            raise Error(f"DAO: Error generico de mysql platillos: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_categorias(self) -> List[Categoria]:
        '''Retorna todas las categorias de la BD.'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                      SELECT clave clave, nombre nombre
                      FROM categoria;
                      '''
                cursor.execute(sql)
                filas = cursor.fetchall()
                lista_categorias: List[Categoria] = []

                for fila in filas:
                    lista_categorias.append(Categoria(
                        clave=fila['clave'],
                        nombre=fila['nombre']))
                return lista_categorias
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error genérico de mysql categorías: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_categoria_por_nombre(self, nombre) -> Categoria|None:
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                      SELECT clave clave,
                             nombre nombre
                      FROM categoria
                      WHERE nombre = %s;
                      '''
                cursor.execute(sql, (nombre,))

                fila = cursor.fetchone()

                if fila is None:
                    return fila

                categoria_obj = Categoria(clave=fila['clave'], nombre=fila['nombre'])

                return categoria_obj

        except mysql.connector.Error as err:
            raise Error(f"DAO: Error genérico de mysql categorías: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_categoria_por_clave(self, clave) -> Categoria|None:
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                      SELECT clave clave,
                             nombre nombre  
                      FROM categoria
                      WHERE clave = %s;
                      '''
                cursor.execute(sql, (clave,))

                fila = cursor.fetchone()

                if fila is None:
                    return fila

                categoria_obj = Categoria(clave=fila['clave'], nombre=fila['nombre'])

                return categoria_obj

        except mysql.connector.Error as err:
            raise Error(f"DAO: Error genérico de mysql categorías: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_ventas_platillo(self, num_platillo):
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                      SELECT venta  venta,
                             platillo platillo,
                          importe importe,
                          cantidadPlatillos cantidadP
                      FROM consumo
                      WHERE platillo = %s;
                      '''
                cursor.execute(sql, (num_platillo,))

                filas = cursor.fetchall()

                return filas

        except mysql.connector.Error as err:
            raise Error(f"DAO: Error genérico de mysql categorías: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    ''' funciones de creacion '''

    def crear_platillo(self, platillo: Platillo):
        '''Inserta un nuevo registro de platillo'''
        connection = self.db.get_connection()

        try:
            with connection.cursor(dictionary=True) as cursor:
                query = '''
                        INSERT INTO platillo (nombre, categoria, receta)
                        VALUES (%s, %s, %s);
                        '''
                cursor.execute(query, (platillo.nombre, platillo.categoria.clave, platillo.receta.num))
                connection.commit()

        except mysql.connector.Error as err:
            connection.rollback()
            raise Error(f"Error al insertar el platillo: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def crear_categoria(self, categoria: Categoria):
        '''Inserta un nuevo registro de categoría'''
        connection = self.db.get_connection()

        try:
            with connection.cursor(dictionary=True) as cursor:
                query = '''
                        INSERT INTO categoria (clave, nombre)
                        VALUES (%s, %s);
                        '''
                cursor.execute(query, (categoria.clave, categoria.nombre))
                connection.commit()

        except mysql.connector.Error as err:
            connection.rollback()
            raise Error(f"Error al insertar la categoría: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    ''' funciones de actualizacion '''

    def actualizar_platillo(self, platillo:Platillo):
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                      UPDATE platillo
                      SET nombre = %s,
                          categoria = %s,
                          receta = %s
                      WHERE num = %s;
                      '''
                valores = (
                    platillo.nombre,
                    platillo.categoria.clave,
                    platillo.receta.num,
                    platillo.num
                )
                cursor.execute(sql, valores)
                connection.commit()

        except mysql.connector.Error as err:
            connection.rollback()
            raise Error(f"Error al actualizar el platillo: {err}")

        finally:
            if connection.is_connected():
                connection.close()

    def desactivar_platillo(self, num_platillo) -> None:
        # cambia la receta base a none y ya
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                      UPDATE platillo
                      SET receta = null
                      WHERE num = %s;
                      '''
                cursor.execute(sql, (num_platillo,))

        except mysql.connector.Error as err:
            raise Error(f"DAO: Error generico de mysql platillos: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def borrar_platillo(self, num_platillo) -> None:
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql_menu_platillo = '''
                        DELETE FROM menu_platillo WHERE platillo = %s;
                        '''
                cursor.execute(sql_menu_platillo, (num_platillo,))

                sql_platillo = '''DELETE FROM platillo WHERE num = %s;'''
                cursor.execute(sql_platillo, (num_platillo,))

                connection.commit()

        except mysql.connector.Error as err:
            raise Error(f"DAO: Error generico de mysql platillos: {err}")
        finally:
            if connection.is_connected():
                connection.close()
