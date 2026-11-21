from typing import List
from models.insumo import Insumo
from models.compra import Compra, DetalleCompra
from models.tipo_insumo import TipoInsumo
from models.marca import Marca
from models.proveedor import Proveedor
import mysql.connector
from mysql.connector import Error

class InsumoDAO:
    def __init__(self, db_connection):
        self.db = db_connection

    ''' FUNCIONES DE CONSULTA '''

    def obtener_tipos_insumo(self) -> List[TipoInsumo]:
        '''Obtiene una lista de todos los tipos de insumos disponibles.'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''SELECT clave cl, nombre nm FROM tipo_insumo;'''
                cursor.execute(sql)
                filas = cursor.fetchall()

                tipos_insumos: List[TipoInsumo] = []

                for fila in filas:
                    tipos_insumos.append(TipoInsumo(clave=fila['cl'],nombre=fila['nm']))
                
                return tipos_insumos
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar los insumos: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_tipo_insumo_por_nombre(self, nombre_tipo:str) -> TipoInsumo|None:
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''SELECT clave cl, nombre n FROM tipo_insumo WHERE nombre = %s;'''
                cursor.execute(sql, (nombre_tipo,))
                fila = cursor.fetchone()

                if fila is None:
                    return None

                tipo_insumo = TipoInsumo(clave=fila['cl'], nombre=fila['n'])

                return tipo_insumo
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar insumos: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_tipo_insumo_por_clave(self, clave_tipo:str) -> TipoInsumo|None:
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''SELECT clave cl, nombre n FROM tipo_insumo WHERE clave = %s;'''
                cursor.execute(sql, (clave_tipo,))
                fila = cursor.fetchone()

                if fila is None:
                    return None

                tipo_insumo = TipoInsumo(clave=fila['cl'], nombre=fila['n'])

                return tipo_insumo
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar insumos: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_insumos(self) -> list[Insumo]:
        '''Obtiene todos los insumos existentes en la BD'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                    SELECT
                    ins.num num,
                    ins.nombre nom,
                    ins.umbral umb,
                    ins.stock stock,
                    ins.tipo_insumo claveTipo,
                    ti.nombre nombreTipo,
                    ins.marca numMarca,
                    mc.nombre nombreMarca
                    FROM insumo ins
                    INNER JOIN tipo_insumo ti ON ins.tipo_insumo = ti.clave
                    INNER JOIN marca mc ON ins.marca = mc.num
                    ORDER BY ins.num;
                        '''
                cursor.execute(sql)
                filas = cursor.fetchall()
                insumos: List[Insumo] = []
                for fila in filas:
                    insumos.append(Insumo(
                        num=fila['num'],
                        nombre=fila['nom'],
                        umbral=fila['umb'],
                        stock=fila['stock'],
                        tipo_insumo=TipoInsumo(fila['claveTipo'],fila['nombreTipo']),
                        marca=Marca(fila['numMarca'],fila['nombreMarca'])
                    ))
                return insumos
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar los insumos: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_insumo_por_num(self, num_insumo:int) -> Insumo:
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                    SELECT
                    ins.num num,
                    ins.nombre nom,
                    ins.umbral umb,
                    ins.stock stock,
                    ins.tipo_insumo claveTipo,
                    ti.nombre nombreTipo,
                    ins.marca numMarca,
                    mc.nombre nombreMarca
                    FROM insumo ins
                    INNER JOIN tipo_insumo ti ON ins.tipo_insumo = ti.clave
                    INNER JOIN marca mc ON ins.marca = mc.num
                    WHERE ins.num = %s;
                        '''
                cursor.execute(sql, (num_insumo,))
                fila = cursor.fetchone()

                insumo = Insumo(
                    num=fila['num'],
                    nombre=fila['nom'],
                    umbral=fila['umb'],
                    stock=fila['stock'],
                    tipo_insumo=TipoInsumo(fila['claveTipo'], fila['nombreTipo']),
                    marca=Marca(fila['numMarca'], fila['nombreMarca']))

                return insumo
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar el insumo: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_insumo_por_nombre(self, nombre_insumo:str) -> Insumo|None:
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                    SELECT
                    ins.num num,
                    ins.nombre nom,
                    ins.umbral umb,
                    ins.stock stock,
                    ins.tipo_insumo claveTipo,
                    ti.nombre nombreTipo,
                    ins.marca numMarca,
                    mc.nombre nombreMarca
                    FROM insumo ins
                    INNER JOIN tipo_insumo ti ON ins.tipo_insumo = ti.clave
                    INNER JOIN marca mc ON ins.marca = mc.num
                    WHERE ins.nombre = %s;
                        '''
                cursor.execute(sql, (nombre_insumo,))
                fila = cursor.fetchone()

                if fila is None:
                    return fila

                insumo = Insumo(
                    num=fila['num'],
                    nombre=fila['nom'],
                    umbral=fila['umb'],
                    stock=fila['stock'],
                    tipo_insumo=TipoInsumo(fila['claveTipo'], fila['nombreTipo']),
                    marca=Marca(fila['numMarca'], fila['nombreMarca']))

                return insumo
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar el insumo: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_insumo_por_tipo_insumo(self, tipo_insumo_clave:str) -> List[Insumo]:
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                    SELECT
                    ins.num num,
                    ins.nombre nom,
                    ins.umbral umb,
                    ins.stock stock,
                    ins.tipo_insumo claveTipo,
                    ti.nombre nombreTipo,
                    ins.marca numMarca,
                    mc.nombre nombreMarca
                    FROM insumo ins
                    INNER JOIN tipo_insumo ti ON ins.tipo_insumo = ti.clave
                    INNER JOIN marca mc ON ins.marca = mc.num
                    WHERE ins.tipo_insumo = %s;
                        '''
                cursor.execute(sql, (tipo_insumo_clave,))
                filas = cursor.fetchall()

                lista_insumos: List[Insumo] = []

                for fila in filas:
                    lista_insumos.append(Insumo(
                        num=fila['num'],
                        nombre=fila['nom'],
                        umbral=fila['umb'],
                        stock=fila['stock'],
                        tipo_insumo=TipoInsumo(fila['claveTipo'], fila['nombreTipo']),
                        marca=Marca(fila['numMarca'], fila['nombreMarca'])))

                return lista_insumos
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar insumos: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_insumo_por_match_nombre(self, nombre_insumo:str) -> List[Insumo]:
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = f'''
                    SELECT
                    ins.num num,
                    ins.nombre nom,
                    ins.umbral umb,
                    ins.stock stock,
                    ins.tipo_insumo claveTipo,
                    ti.nombre nombreTipo,
                    ins.marca numMarca,
                    mc.nombre nombreMarca
                    FROM insumo ins
                    INNER JOIN tipo_insumo ti ON ins.tipo_insumo = ti.clave
                    INNER JOIN marca mc ON ins.marca = mc.num
                    WHERE ins.nombre LIKE('%{nombre_insumo}%')
                    ORDER BY ins.nombre;
                        '''
                cursor.execute(sql)
                filas = cursor.fetchall()

                lista_insumos: List[Insumo] = []

                for fila in filas:
                    lista_insumos.append(Insumo(
                        num=fila['num'],
                        nombre=fila['nom'],
                        umbral=fila['umb'],
                        stock=fila['stock'],
                        tipo_insumo=TipoInsumo(fila['claveTipo'], fila['nombreTipo']),
                        marca=Marca(fila['numMarca'], fila['nombreMarca'])))

                return lista_insumos
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar insumos: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_insumo_con_stock_bajo(self) -> List[Insumo]:
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = f'''
                    SELECT
                    ins.num num,
                    ins.nombre nom,
                    ins.umbral umb,
                    ins.stock stock,
                    ins.tipo_insumo claveTipo,
                    ti.nombre nombreTipo,
                    ins.marca numMarca,
                    mc.nombre nombreMarca
                    FROM insumo ins
                    INNER JOIN tipo_insumo ti ON ins.tipo_insumo = ti.clave
                    INNER JOIN marca mc ON ins.marca = mc.num
                    WHERE ins.stock < ins.umbral;
                        '''
                cursor.execute(sql)
                filas = cursor.fetchall()

                if not len(filas):
                    return []

                lista_insumos: List[Insumo] = []

                for fila in filas:
                    lista_insumos.append(Insumo(
                        num=fila['num'],
                        nombre=fila['nom'],
                        umbral=fila['umb'],
                        stock=fila['stock'],
                        tipo_insumo=TipoInsumo(fila['claveTipo'], fila['nombreTipo']),
                        marca=Marca(fila['numMarca'], fila['nombreMarca'])))

                return lista_insumos
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar insumos: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_insumo_por_marca(self, marca_num:str) -> List[Insumo]:
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                    SELECT
                    ins.num num,
                    ins.nombre nom,
                    ins.umbral umb,
                    ins.stock stock,
                    ins.tipo_insumo claveTipo,
                    ti.nombre nombreTipo,
                    ins.marca numMarca,
                    mc.nombre nombreMarca
                    FROM insumo ins
                    INNER JOIN tipo_insumo ti ON ins.tipo_insumo = ti.clave
                    INNER JOIN marca mc ON ins.marca = mc.num
                    WHERE ins.marca = %s;
                        '''
                cursor.execute(sql, (marca_num,))
                filas = cursor.fetchall()

                lista_insumos: List[Insumo] = []

                for fila in filas:
                    lista_insumos.append(Insumo(
                        num=fila['num'],
                        nombre=fila['nom'],
                        umbral=fila['umb'],
                        stock=fila['stock'],
                        tipo_insumo=TipoInsumo(fila['claveTipo'], fila['nombreTipo']),
                        marca=Marca(fila['numMarca'], fila['nombreMarca'])))

                return lista_insumos
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar insumos: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_marcas(self) -> List[Marca]:
        '''Obtiene una lista de todas las marcas disponibles.'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''SELECT num, nombre FROM marca ORDER BY num;'''
                cursor.execute(sql)
                filas = cursor.fetchall()

                marcas: List[Marca] = []

                for fila in filas:
                    marcas.append(Marca(num=fila['num'],nombre=fila['nombre']))
                
                return marcas
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar las marcas: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_id_insumo_por_nombre(self, nombre_insumo:str) -> Insumo:
            '''Obtiene un insumo por su nombre.'''
            connection = self.db.get_connection()
            try:
                with connection.cursor(dictionary=True) as cursor:
                    sql = '''SELECT 
                        ins.num num, 
                        ins.nombre nm, 
                        ins.umbral umb, 
                        ins.stock stock, 
                        ins.tipo_insumo numTipo,
                        ti.nombre nombreTipo,
                        ins.marca numMarca,
                        mc.nombre nombreMarca
                        FROM insumo ins
                        INNER JOIN tipo_insumo ti ON ins.tipo_insumo = ti.clave
                        INNER JOIN marca mc ON ins.marca = mc.num
                        WHERE ins.nombre = %s;'''
                    cursor.execute(sql,(nombre_insumo,))
                    fila = cursor.fetchone()
                    return Insumo(fila['num'],fila['nm'],fila['umb'],fila['stock'],
                                TipoInsumo(fila['numTipo'],fila['nombreTipo']),
                                Marca(fila['numMarca'],fila['nombreMarca']))
                
            except mysql.connector.Error as err:
                raise Error(f"DAO: Error al consultar insumo por su nombre: {err}")
            finally:
                if connection.is_connected():
                    connection.close()

    ''' FUNCIONES DE UPDATE '''

    def actualizar_insumo(self, insumo:Insumo):
        '''Actualiza propiedades simples de un insumo..'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:

                # actualiza los atributos basicos del menu
                sql_insumo = '''
                    UPDATE insumo ins
                    JOIN tipo_insumo ti ON ins.tipo_insumo = ti.clave
                    SET ins.nombre = %s, ins.umbral = %s, ins.tipo_insumo = %s
                    WHERE ins.num = %s;
                '''
                cursor.execute(sql_insumo, (insumo.nombre,
                                            insumo.umbral,
                                            insumo.tipo_insumo.clave,  # type: ignore
                                            insumo.num))

                connection.commit()

        except mysql.connector.Error as err:
            # si cualquiera de los updates, inserts o select fallo:
            connection.rollback()
            raise Error(f"DAO: Error en la transaccion al actualizar menu: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    ''' FUNCIONES DE REGISTROS '''

    def crear_tipo_insumo(self, tipo_insumo:TipoInsumo):
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:

                sql_insumo = '''
                             INSERT INTO tipo_insumo (clave, nombre)
                                 VALUES (%s, %s);
                             '''
                cursor.execute(sql_insumo, (tipo_insumo.clave, tipo_insumo.nombre))

                connection.commit()

        except mysql.connector.Error as err:
            connection.rollback()
            raise Error(f"DAO: Error al crear tipo de insumo: {err}")
        finally:
            if connection.is_connected():
                connection.close()
