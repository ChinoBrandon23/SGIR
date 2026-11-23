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

    def obtener_insumo_por_nombre(self, nombre_insumo:str) -> List[Insumo]|None:
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
                filas = cursor.fetchall()
                lista_insumos:List[Insumo] = []

                if filas is None or not len(filas):
                    return None

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

    def obtener_marcas_disponibles_insumo(self, insumo_nombre:str) -> List[Marca]:
        '''Obtiene las marcas que un insumo puede tener para no resultar en dos insumos o más con el
        mismo nombre y marcar (duplicados)'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''SELECT m.num, m.nombre
                         FROM marca m
                        INNER JOIN insumo ins ON m.num = ins.marca
                        WHERE ins.nombre != %s
                         ORDER BY num;'''
                cursor.execute(sql)
                filas = cursor.fetchall()

                marcas: List[Marca] = []

                for fila in filas:
                    marcas.append(Marca(num=fila['num'], nombre=fila['nombre']))

                return marcas
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar las marcas: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_marcas_disponibles_insumo(self, insumo_nombre:str) -> List[Marca]:
        '''Obtiene las marcas que un insumo puede tener para no resultar en dos insumos o más con el
        mismo nombre y marcar (duplicados)'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''SELECT m.num, m.nombre
                         FROM marca m
                        INNER JOIN insumo ins ON m.num = ins.marca
                        WHERE ins.nombre != %s
                         ORDER BY num;'''
                cursor.execute(sql)
                filas = cursor.fetchall()

                marcas: List[Marca] = []

                for fila in filas:
                    marcas.append(Marca(num=fila['num'], nombre=fila['nombre']))

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

    def obtener_marca_por_nombre(self, nombre_marca:str) -> Marca|None:
        '''Obtiene una lista de todas las marcas disponibles.'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''SELECT num, nombre
                         FROM marca 
                         WHERE nombre = %s;'''
                cursor.execute(sql, (nombre_marca,))
                fila = cursor.fetchone()

                if fila is None:
                    return fila

                marca: Marca = Marca(fila['num'],fila['nombre'])

                return marca
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar las marcas: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_insumo_por_nombre_marca(self, nombre_insumo:str, nombre_marca:str) -> Insumo|None:
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''SELECT ins.num         num,
                                ins.nombre      nm,
                                ins.umbral      umb,
                                ins.stock       stock,
                                ins.tipo_insumo numTipo,
                                ti.nombre       nombreTipo,
                                ins.marca       numMarca,
                                mc.nombre       nombreMarca
                         FROM insumo ins
                                  INNER JOIN tipo_insumo ti ON ins.tipo_insumo = ti.clave
                                  INNER JOIN marca mc ON ins.marca = mc.num
                         WHERE ins.nombre = %s AND mc.nombre = %s;'''
                cursor.execute(sql, (nombre_insumo, nombre_marca))
                fila = cursor.fetchone()

                if fila is None:
                    return fila

                return Insumo(fila['num'], fila['nm'], fila['umb'], fila['stock'],
                              TipoInsumo(fila['numTipo'], fila['nombreTipo']),
                              Marca(fila['numMarca'], fila['nombreMarca']))
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar los proovedores: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_marca_por_nombre(self, nombre_marca:str) -> Marca|None:
        '''Obtiene una lista de todas las marcas disponibles.'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''SELECT num, nombre
                         FROM marca 
                         WHERE nombre = %s;'''
                cursor.execute(sql, (nombre_marca,))
                fila = cursor.fetchone()

                if fila is None:
                    return fila

                marca: Marca = Marca(fila['num'],fila['nombre'])

                return marca
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar las marcas: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_insumo_nombre_marca(self, nombre_insumo:str, nombre_marca:str) -> Insumo|None:
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''SELECT ins.num         num,
                                ins.nombre      nm,
                                ins.umbral      umb,
                                ins.stock       stock,
                                ins.tipo_insumo numTipo,
                                ti.nombre       nombreTipo,
                                ins.marca       numMarca,
                                mc.nombre       nombreMarca
                         FROM insumo ins
                                  INNER JOIN tipo_insumo ti ON ins.tipo_insumo = ti.clave
                                  INNER JOIN marca mc ON ins.marca = mc.num
                         WHERE ins.nombre = %s AND mc.nombre = %s;'''
                cursor.execute(sql, (nombre_insumo, nombre_marca))
                fila = cursor.fetchone()

                if fila is None:
                    return fila

                return Insumo(fila['num'], fila['nm'], fila['umb'], fila['stock'],
                              TipoInsumo(fila['numTipo'], fila['nombreTipo']),
                              Marca(fila['numMarca'], fila['nombreMarca']))
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar los proovedores: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def crear_marca(self, nombre_marca:str):
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:

                sql_insumo = '''
                             INSERT INTO marca (nombre)
                                 VALUES (%s);
                             '''
                cursor.execute(sql_insumo, (nombre_marca,))

                connection.commit()

        except mysql.connector.Error as err:
            connection.rollback()
            raise Error(f"DAO: Error al crear tipo de insumo: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def crear_insumo(self, insumo:Insumo):
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:

                sql_insumo = '''
                             INSERT INTO insumo (nombre, umbral, stock, tipo_insumo, marca)
                             VALUES (%s, %s, %s, %s, %s); \
                             '''
                cursor.execute(sql_insumo, (insumo.nombre, insumo.umbral, insumo.stock, insumo.tipo_insumo.clave, insumo.marca.num))

                connection.commit()

        except mysql.connector.Error as err:
            connection.rollback()
            raise Error(f"DAO: Error al crear tipo de insumo: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def crear_ingrediente_de_insumo(self, insumo:Insumo):
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                # checa si ya existe un ingrediente del mismo nombre, ignorando la marca
                sql_ya_existe_ing = '''
                                    SELECT ing.num, ing.nombre, ing.receta numReceta, ing.insumo numInsumo
                                    FROM ingrediente AS ing
                                             INNER JOIN insumo ins ON ing.insumo = ins.num
                                    WHERE ins.nombre = %s;'''
                cursor.execute(sql_ya_existe_ing, (insumo.nombre,))
                ingrediente_existente = cursor.fetchone()

                if not ingrediente_existente:
                    # crea uno y lo vincula al insumo registrado
                    sql_crear_ingrediente = '''
                                            INSERT INTO ingrediente (nombre, receta, insumo)
                                            VALUES (%s, null, %s); \
                                            '''
                    cursor.execute(sql_crear_ingrediente,
                                   (insumo.nombre, insumo.num))

                connection.commit()

        except mysql.connector.Error as err:
            connection.rollback()
            raise Error(f"DAO: Error al crear tipo de insumo: {err}")
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

    def actualizar_stock_insumo(self, insumo:Insumo):
        '''Actualiza el stock en base a los datos de lista_compras'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql_lista_compras = '''
                                SELECT cantidadActual
                                FROM lista_compra
                                WHERE insumo = %s
                '''
                cursor.execute(sql_lista_compras, (insumo.num,))
                resultados = cursor.fetchall()
                suma_total = 0

                for res in resultados:
                    suma_total += res['cantidadActual']

                sql_insumo = '''
                    UPDATE insumo ins
                    JOIN tipo_insumo ti ON ins.tipo_insumo = ti.clave
                    SET ins.nombre = %s, ins.umbral = %s, ins.tipo_insumo = %s, ins.stock = %s
                    WHERE ins.num = %s;
                '''
                cursor.execute(sql_insumo, (insumo.nombre,
                                            insumo.umbral,
                                            insumo.tipo_insumo.clave,
                                            suma_total,# type: ignore
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

    def crear_marca(self, nombre_marca:str):
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:

                sql_insumo = '''
                             INSERT INTO marca (nombre)
                                 VALUES (%s);
                             '''
                cursor.execute(sql_insumo, (nombre_marca,))

                connection.commit()

        except mysql.connector.Error as err:
            connection.rollback()
            raise Error(f"DAO: Error al crear tipo de insumo: {err}")
        finally:
            if connection.is_connected():
                connection.close()


