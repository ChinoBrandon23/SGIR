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

    def obtener_compras(self) -> List[Compra]:
        ''' Obtiene todos los insumos de la BD junto con su informacion de compra.'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                        SELECT
                        com.num numCompra,
                        com.total_bruto totalCompra,
                        com.fechaCreacion comFecha,
                        com.proveedor numProv,
                        prov.nombre nombreProv
                        FROM compra com
                        INNER JOIN proveedor prov ON com.proveedor = prov.num;
                '''
                # obtenemos todas las compras simples
                cursor.execute(sql)
                filas = cursor.fetchall()
                lista_compras: List[Compra] = []

                for fila in filas:
                    lista_compras.append(Compra(
                        num=fila['numCompra'],
                        fecha_creacion=fila['comFecha'],
                        total_bruto=fila['totalCompra'],
                        proveedor=Proveedor(fila['numProv'],fila['nombreProv'])
                    ))

                sql_detalles = '''
                                SELECT
                                ins.num numInsumo,
                                ins.nombre nombreInsumo,
                                ins.umbral umbral,
                                ins.stock stock,
                                ti.clave claveTipo,
                                ti.nombre nombreTipo,
                                ma.num numeroMarca,
                                ma.nombre nombreMarca,
                                lc.fechaCompra fechaCompra,
                                lc.cantidadComprada cantidadComprada,
                                lc.cantidadActual cantidadActual,
                                lc.unidadMedida unidadMedida,
                                lc.fechaCaducidad fechaCad,
                                lc.montoUnitario montoUnit,
                                lc.importe importe
                                FROM insumo ins
                                INNER JOIN marca ma ON ins.marca = ma.num
                                INNER JOIN tipo_insumo ti ON ins.tipo_insumo = ti.clave
                                INNER JOIN lista_compra lc ON lc.insumo = ins.num
                                INNER JOIN compra com ON lc.compra = com.num
                                WHERE lc.compra = %s;
                                '''
                # obtenemos los detalles de cada compra y los agregamos a su respectiva compra
                for compra in lista_compras:
                    cursor.execute(sql_detalles,(compra.num,))
                    filas = cursor.fetchall()
                    for fila in filas:
                        compra.agregar_insumo_compra(
                            insumo=Insumo(
                                num=fila['numInsumo'],
                                nombre=fila['nombreInsumo'],
                                umbral=fila['umbral'],
                                stock=fila['stock'],
                                tipo_insumo=TipoInsumo(fila['claveTipo'],fila['nombreTipo']),
                                marca=Marca(fila['numeroMarca'],fila['nombreMarca'])
                            ),
                            fecha_compra=fila['fechaCompra'],
                            cantidad_comprada=fila['cantidadComprada'],
                            cantidad_actual=fila['cantidadActual'],
                            unidad_medida=fila['unidadMedida'],
                            fecha_caducidad=fila['fechaCad'],
                            monto_unitario=fila['montoUnit'],
                            importe=fila['importe'])
                # regresamos una lista de compras con sus detalles
                return lista_compras
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar los insumos: {err}")
        finally:
            if connection.is_connected():
                connection.close()

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

    def obtener_insumos(self) -> List[Insumo]:
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
                    INNER JOIN marca mc ON ins.marca = mc.num;
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

    def obtener_marcas(self) -> List[Marca]:
        '''Obtiene una lista de todas las marcas disponibles.'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''SELECT num, nombre FROM marca;'''
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


