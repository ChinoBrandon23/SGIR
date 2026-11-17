from typing import List
from models.insumo import Insumo
from models.compra import Compra, DetalleCompra
from models.tipo_insumo import TipoInsumo
from models.marca import Marca
from models.proveedor import Proveedor
import mysql.connector
from mysql.connector import Error


class CompraDAO:
    def __init__(self, db_connection):
        self.db = db_connection

    ''' FUNCIONES DE CONSULTA '''

    def obtener_compras(self) -> List[Compra]:
        ''' Obtiene todos los insumos de la BD junto con su informacion de compra.
        Es decir las compras completas.'''
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

    def obtener_proveedores(self) -> List[Proveedor]:
            '''Obtiene una lista de todas los proveedores disponibles.'''
            connection = self.db.get_connection()
            try:
                with connection.cursor(dictionary=True) as cursor:
                    sql = '''SELECT num, nombre FROM proveedor;'''
                    cursor.execute(sql)
                    filas = cursor.fetchall()
    
                    proveedores: List[Proveedor] = []
    
                    for fila in filas:
                        proveedores.append(Proveedor(num=fila['num'],nombre=fila['nombre']))
                    
                    return proveedores
            except mysql.connector.Error as err:
                raise Error(f"DAO: Error al consultar los proovedores: {err}")
            finally:
                if connection.is_connected():
                    connection.close()

    ''' FUNCIONES DE REGISTRO '''
    def registrar_compra(self, compra_nueva:Compra):
        '''Registra una compra en la BD'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:

                # actualiza los atributos basicos la compra
                sql_compra = '''
                    INSERT INTO compra (fechaCreacion, total_bruto, proveedor)
                    VALUES (%s,%s,%s);
                '''
                cursor.execute(sql_compra, (
                    compra_nueva.fecha_creacion,
                    compra_nueva.total_bruto,
                    compra_nueva.proveedor.num # type: ignore
                ))
                compra_id = cursor.lastrowid
                compra_nueva.num = compra_id

                for detalle in compra_nueva.lista_compras:
                    sql_detalles_compra = '''
                        INSERT INTO lista_compra (compra,insumo,montoUnitario,importe,
                        fechaCompra,fechaCaducidad,cantidadComprada,
                        cantidadActual,unidadMedida)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);
                        '''

                    cursor.execute(sql_detalles_compra,(
                    compra_nueva.num,
                    detalle.insumo.num,
                    detalle.monto_unitario,
                    detalle.importe,
                    detalle.fecha_compra,
                    detalle.fecha_caducidad,
                    detalle.cantidad_comprada,
                    detalle.cantidad_actual,
                    detalle.unidad_medida))

                    sql_actualizar_stock = '''UPDATE insumo SET stock = stock + %s WHERE num = %s;'''

                    cursor.execute(sql_actualizar_stock,(
                        detalle.cantidad_comprada,
                        detalle.insumo.num
                    ))


                # si se llego hasta aqui sin lanzar excepcion, todo salio bien
                connection.commit()
                return compra_nueva
        except Exception as err:
            # si cualquiera de los updates, inserts o select fallo:
            connection.rollback()
            raise Error(f"DAO: Error en la transaccion al registrar compra.: {err}")
        finally:
            if connection.is_connected():
                connection.close()
