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

    ''' FUNCIONES DE UPDATE '''

    def actualizar_insumo(self, menu:Menu):
        '''Actualiza propiedades simples de un insumo..'''
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
                # obtiene los numeros de platillo del menu en la BD en una lista 
                platillos_num_bd = [fila['platillo'] for fila in cursor.fetchall()]

                # conjunto de ids que el usuario tiene ahora en el menu (nuevos platillos)
                ids_en_formulario = set()

                # iteracion de inserts y updates
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
                # si se llego hasta aqui sin lanzar excepcion, todo salio bien:)
                connection.commit()

        except mysql.connector.Error as err:
            # si cualquiera de los updates, inserts o select fallo:
            connection.rollback()
            raise Error(f"DAO: Error en la transaccion al actualizar menu: {err}")
        finally:
            if connection.is_connected():
                connection.close()