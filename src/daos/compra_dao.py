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

    def obtener_proveedores(self) -> list[Proveedor]:
            '''Obtiene una lista de todas los proveedores disponibles.'''
            connection = self.db.get_connection()
            try:
                with connection.cursor(dictionary=True) as cursor:
                    sql = '''SELECT num, nombre FROM proveedor ORDER BY num ASC;'''
                    cursor.execute(sql)
                    filas = cursor.fetchall()
    
                    proveedores: list[Proveedor] = []
    
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

                # registra el proveedor de la compra si no existe
                sql_proveedor = '''SELECT num, nombre FROM proveedor WHERE num = %s;'''
                cursor.execute(sql_proveedor,(compra_nueva.proveedor.num,)) # type: ignore
                proveedor = cursor.fetchone()
                proveedor_num:int = compra_nueva.proveedor.num # type: ignore
                if not proveedor:
                    cursor.execute('INSERT INTO proveedor (nombre) VALUES (%s);',
                                (compra_nueva.proveedor.nombre,)) # type: ignore
                    proveedor_num = cursor.lastrowid
                
                # actualiza los atributos basicos la compra
                sql_compra = '''
                    INSERT INTO compra (fechaCreacion, total_bruto, proveedor)
                    VALUES (%s,%s,%s);
                '''
                
                cursor.execute(sql_compra, (
                    compra_nueva.fecha_creacion,
                    compra_nueva.total_bruto,
                    proveedor_num
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


                    # actualiza el stock
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


    '''FUNCIONES DE UPDATE'''
    def actualizar_compra_completa(self, compra_act:Compra):
        '''Actualiza una compra.'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:

                # actualiza los atributos basicos de la compra
                sql_compra = '''
                    UPDATE compra
                    SET fechaCreacion = %s, total_bruto = %s, proveedor = %s
                    WHERE num = %s;
                '''
                cursor.execute(sql_compra, (
                    compra_act.fecha_creacion,
                    compra_act.total_bruto,
                    compra_act.proveedor,
                    compra_act.num
                ))

                # consulta que insumos existen actualmente en la BD para esta compra
                sql_actuales = 'SELECT insumo FROM lista_compra WHERE compra = %s;'
                cursor.execute(sql_actuales, (compra_act.num,))
                # obtiene los numeros de platillo del menu en la BD en una lista 
                insumos_num_bd = [fila['insumo'] for fila in cursor.fetchall()]

                # conjunto de ids que el usuario tiene ahora en el menu (nuevos platillos)
                ids_en_formulario = set()

                # iteracion de inserts y updates
                for detalle in compra_act.lista_compras:
                    ins_id = detalle.insumo.num
                    ids_en_formulario.add(ins_id)

                    # asignando a los insumos sus ids de la BD y no los locales
                    sql_buscar_id = '''SELECT num FROM insumo WHERE nombre = %s;'''
                    cursor.execute(sql_buscar_id,(detalle.insumo.nombre,))
                    fila = cursor.fetchone()
                    id_bd_ins  = int(fila['num'])

                    if ins_id in insumos_num_bd:
                        # si ya existia en la BD, actualiza..
                        # cant comprada, unidad med, monto_unit, fecha compra, fecha caduciidad, marca
                        sql_update = '''
                            UPDATE lista_compra li
                            JOIN insumo ins ON li.insumo = ins.num
                            SET li.unidadMedida = %s, 
                            li.montoUnitario = %s, li.fechaCompra = %s, li.fechaCaducidad = %s, ins.marca = %s
                            WHERE li.compra = %s AND li.insumo=%s;
                        '''
                        valores = (
                            detalle.unidad_medida,
                            detalle.monto_unitario,
                            detalle.fecha_compra,
                            detalle.fecha_caducidad,
                            detalle.insumo.marca.num,  # type: ignore
                            compra_act.num,
                            id_bd_ins
                        )
                        cursor.execute(sql_update, valores)

                        #actualizar stock ya que se modifico la cantidad comprada del insumo de la compra
                    else:
                        # si es nuevo el insumo, se inserta
                        sql_insert = '''
                            INSERT INTO lista_compra (compra,insumo,montoUnitario,importe,
                            fechaCompra,fechaCaducidad,cantidadComprada,
                            cantidadActual,unidadMedida)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);
                            '''
                        cursor.execute(sql_insert, (
                            compra_act.num,
                            id_bd_ins,
                            detalle.monto_unitario,
                            detalle.importe,
                            detalle.fecha_compra,
                            detalle.fecha_caducidad,
                            detalle.cantidad_comprada,
                            detalle.cantidad_actual,
                            detalle.unidad_medida
                        ))

                        # actualiza el stock
                        sql_actualizar_stock = '''UPDATE insumo SET stock = stock + %s WHERE num = %s;'''
                        cursor.execute(sql_actualizar_stock,(
                            detalle.cantidad_comprada,
                            id_bd_ins
                        ))
                # ELIMINAR INSUMO DE COMPRA PENDIENTE
                ## delete de los platillos que el usuario elimino
                #for plat_id in platillos_num_bd:
                #    if plat_id not in ids_en_formulario:
                #        sql_delete = '''
                #            DELETE FROM menu_platillo 
                #            WHERE menu = %s AND platillo = %s;
                #        '''
                #        cursor.execute(sql_delete, (menu.num, plat_id))

                # solo un commit para todo
                # si se llego hasta aqui sin lanzar excepcion, todo salio bien:)
                connection.commit()

        except Exception as err:
            # si cualquiera de los updates, inserts o select fallo:
            connection.rollback()
            raise Error(f"DAO: Error en la transaccion al actualizar compra: {err}")
        finally:
            if connection.is_connected():
                connection.close()