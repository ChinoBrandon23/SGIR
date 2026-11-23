import time
from datetime import datetime
from typing import List
from models.insumo import Insumo
from models.compra import Compra, DetalleCompra
from models.tipo_insumo import TipoInsumo
from models.marca import Marca
from models.proveedor import Proveedor
import mysql.connector
from mysql.connector import Error

from utils.conversor_unidades import ConversorUnidades

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
                        DATE_FORMAT(com.fechaCreacion, '%d-%m-%Y') comFecha,
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
                        fecha_creacion=datetime.strptime(fila['comFecha'], "%d-%m-%Y").strftime("%d-%m-%Y"),
                        total_bruto=float(fila['totalCompra']),
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
                                DATE_FORMAT(lc.fechaCompra, '%d-%m-%Y') fechaCompra,
                                lc.cantidadComprada cantidadComprada,
                                lc.cantidadActual cantidadActual,
                                lc.unidadMedida unidadMedida,
                                DATE_FORMAT(lc.fechaCaducidad, '%d-%m-%Y') fechaCad,
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
                                umbral=float(fila['umbral']),
                                stock=float(fila['stock']),
                                tipo_insumo=TipoInsumo(fila['claveTipo'],fila['nombreTipo']),
                                marca=Marca(fila['numeroMarca'],fila['nombreMarca'])
                            ),
                            fecha_compra=datetime.strptime(fila['fechaCompra'], "%d-%m-%Y").strftime("%d-%m-%Y"),
                            cantidad_comprada=float(fila['cantidadComprada']),
                            cantidad_actual=float(fila['cantidadActual']),
                            unidad_medida=fila['unidadMedida'],
                            fecha_caducidad=datetime.strptime(fila['fechaCad'], "%d-%m-%Y").strftime("%d-%m-%Y"),
                            monto_unitario=float(fila['montoUnit']),
                            importe=float(fila['importe']))
                # regresamos una lista de compras con sus detalles
                return lista_compras
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar los insumos: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_compra_por_numero(self, num_compra:int) -> Compra:
        ''' Obtiene una compra completa por su numero'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                        SELECT
                        com.num numCompra,
                        com.total_bruto totalCompra,
                        DATE_FORMAT(com.fechaCreacion, '%d-%m-%Y') comFecha,
                        com.proveedor numProv,
                        prov.nombre nombreProv
                        FROM compra com
                        INNER JOIN proveedor prov ON com.proveedor = prov.num
                        WHERE com.num = %s;
                '''
                # obtenemos la compra simple
                cursor.execute(sql,(num_compra,))
                fila = cursor.fetchone()

                if not fila:
                    raise IndexError(f'DAO: No existe la compra {num_compra}')
                
                compra:Compra = Compra(
                        num=fila['numCompra'],
                        fecha_creacion=datetime.strptime(fila['comFecha'], "%d-%m-%Y").date(),
                        total_bruto=float(fila['totalCompra']),
                        proveedor=Proveedor(fila['numProv'],fila['nombreProv'])
                    )

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
                                DATE_FORMAT(lc.fechaCompra, '%d-%m-%Y') fechaCompra,
                                lc.cantidadComprada cantidadComprada,
                                lc.cantidadActual cantidadActual,
                                lc.unidadMedida unidadMedida,
                                DATE_FORMAT(lc.fechaCaducidad, '%d-%m-%Y') fechaCad,
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
                cursor.execute(sql_detalles,(num_compra,))
                filas = cursor.fetchall()
                for fila in filas:
                    compra.agregar_insumo_compra(
                        insumo=Insumo(
                            num=fila['numInsumo'],
                            nombre=fila['nombreInsumo'],
                            umbral=float(fila['umbral']),
                            stock=float(fila['stock']),
                            tipo_insumo=TipoInsumo(fila['claveTipo'],fila['nombreTipo']),
                            marca=Marca(fila['numeroMarca'],fila['nombreMarca'])
                        ),
                        fecha_compra=datetime.strptime(fila['fechaCompra'], "%d-%m-%Y").strftime("%d-%m-%Y"),
                        cantidad_comprada=float(fila['cantidadComprada']),
                        cantidad_actual=float(fila['cantidadActual']),
                        unidad_medida=fila['unidadMedida'],
                        fecha_caducidad=datetime.strptime(fila['fechaCad'], "%d-%m-%Y").strftime("%d-%m-%Y"),
                        monto_unitario=float(fila['montoUnit']),
                        importe=float(fila['importe']))
                # regresamos la compra completa
                return compra
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar los insumos: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_detalles_compras_por_insumo(self, insumo_id: int) -> List[DetalleCompra]:
        # pensada para el servicio inventario
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                    SELECT insumo           ins, \
                            cantidadActual   canAct, \
                            cantidadComprada canCom, \
                            unidadMedida     unidad_m, \
                            montoUnitario    monto, \
                            importe          imp, \
                            DATE_FORMAT(fechaCompra, '%d-%m-%Y')      fechaCom, \
                            DATE_FORMAT(fechaCaducidad, '%d-%m-%Y')   fechaCad
                    FROM lista_compra \
                    WHERE insumo = %s
                    '''

                cursor.execute(sql, (insumo_id,))
                filas = cursor.fetchall()
                lista_detalles_compra: List[DetalleCompra] = []

                for fila in filas:
                    lista_detalles_compra.append(DetalleCompra(
                        insumo=fila['ins'],
                        cantidad_actual=float(fila['canAct']),
                        cantidad_comprada=float(fila['canCom']),
                        unidad_medida=fila['unidad_m'],
                        importe=float(fila['imp']),
                        monto_unitario=float(fila['monto']),
                        fecha_caducidad=datetime.strptime(fila['fechaCad'], "%d-%m-%Y").strftime("%d-%m-%Y"),
                        fecha_compra=datetime.strptime(fila['fechaCom'], "%d-%m-%Y").strftime("%d-%m-%Y")))

                return lista_detalles_compra
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar los detalles de compra: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_proveedores(self) -> list[Proveedor]:
        '''Obtiene una lista de todas los proveedores disponibles.'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''SELECT num, nombre \
                        FROM proveedor \
                        ORDER BY num ASC;'''
                cursor.execute(sql)
                filas = cursor.fetchall()

                proveedores: list[Proveedor] = []

                for fila in filas:
                    proveedores.append(Proveedor(num=fila['num'], nombre=fila['nombre']))

                return proveedores
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar los proovedores: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_proveedor_por_nombre(self, nombre_prov:str) -> Proveedor|None:
        '''Obtiene una lista de todas los proveedores disponibles.'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''SELECT num, nombre
                        FROM proveedor
                        WHERE nombre = %s;'''
                cursor.execute(sql, (nombre_prov,))
                fila = cursor.fetchone()

                if fila is None:
                    return fila

                proveedor: Proveedor = Proveedor(num=fila['num'], nombre=fila['nombre'])

                return proveedor
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar los proovedores: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_compras_por_fecha_creacion(self, fecha_creacion:str):
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                      SELECT com.num                                    numCompra,
                             com.total_bruto                            totalCompra,
                             DATE_FORMAT(com.fechaCreacion, '%d-%m-%Y') comFecha,
                             com.proveedor                              numProv,
                             prov.nombre                                nombreProv
                      FROM compra com
                        INNER JOIN proveedor prov ON com.proveedor = prov.num
                          WHERE com.fechaCreacion = %s;
                      '''
                cursor.execute(sql, (fecha_creacion,))
                filas = cursor.fetchall()
                lista_compras: List[Compra] = []

                for fila in filas:
                    lista_compras.append(Compra(
                        num=fila['numCompra'],
                        fecha_creacion=datetime.strptime(fila['comFecha'], "%d-%m-%Y").strftime("%d-%m-%Y"),
                        total_bruto=float(fila['totalCompra']),
                        proveedor=Proveedor(fila['numProv'], fila['nombreProv'])
                    ))

                sql_detalles = '''
                               SELECT ins.num                                    numInsumo,
                                      ins.nombre                                 nombreInsumo,
                                      ins.umbral                                 umbral,
                                      ins.stock                                  stock,
                                      ti.clave                                   claveTipo,
                                      ti.nombre                                  nombreTipo,
                                      ma.num                                     numeroMarca,
                                      ma.nombre                                  nombreMarca,
                                      DATE_FORMAT(lc.fechaCompra, '%d-%m-%Y')    fechaCompra,
                                      lc.cantidadComprada                        cantidadComprada,
                                      lc.cantidadActual                          cantidadActual,
                                      lc.unidadMedida                            unidadMedida,
                                      DATE_FORMAT(lc.fechaCaducidad, '%d-%m-%Y') fechaCad,
                                      lc.montoUnitario                           montoUnit,
                                      lc.importe                                 importe
                               FROM insumo ins
                                        INNER JOIN marca ma ON ins.marca = ma.num
                                        INNER JOIN tipo_insumo ti ON ins.tipo_insumo = ti.clave
                                        INNER JOIN lista_compra lc ON lc.insumo = ins.num
                                        INNER JOIN compra com ON lc.compra = com.num
                               WHERE lc.compra = %s;
                               '''
                # obtenemos los detalles de cada compra y los agregamos a su respectiva compra
                for compra in lista_compras:
                    cursor.execute(sql_detalles, (compra.num,))
                    filas = cursor.fetchall()
                    for fila in filas:
                        compra.agregar_insumo_compra(
                            insumo=Insumo(
                                num=fila['numInsumo'],
                                nombre=fila['nombreInsumo'],
                                umbral=float(fila['umbral']),
                                stock=float(fila['stock']),
                                tipo_insumo=TipoInsumo(fila['claveTipo'], fila['nombreTipo']),
                                marca=Marca(fila['numeroMarca'], fila['nombreMarca'])
                            ),
                            fecha_compra=datetime.strptime(fila['fechaCompra'], "%d-%m-%Y").strftime("%d-%m-%Y"),
                            cantidad_comprada=float(fila['cantidadComprada']),
                            cantidad_actual=float(fila['cantidadActual']),
                            unidad_medida=fila['unidadMedida'],
                            fecha_caducidad=datetime.strptime(fila['fechaCad'], "%d-%m-%Y").strftime("%d-%m-%Y"),
                            monto_unitario=float(fila['montoUnit']),
                            importe=float(fila['importe']))
                # regresamos una lista de compras con sus detalles
                return lista_compras
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar los insumos: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_compras_por_proveedor(self, proveedor_num:int):
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                      SELECT com.num                                    numCompra,
                             com.total_bruto                            totalCompra,
                             DATE_FORMAT(com.fechaCreacion, '%d-%m-%Y') comFecha,
                             com.proveedor                              numProv,
                             prov.nombre                                nombreProv
                      FROM compra com
                               INNER JOIN proveedor prov ON com.proveedor = prov.num
                      WHERE com.proveedor = %s;
                      '''
                cursor.execute(sql, (proveedor_num,))
                filas = cursor.fetchall()
                lista_compras: List[Compra] = []

                for fila in filas:
                    lista_compras.append(Compra(
                        num=fila['numCompra'],
                        fecha_creacion=datetime.strptime(fila['comFecha'], "%d-%m-%Y").strftime("%d-%m-%Y"),
                        total_bruto=float(fila['totalCompra']),
                        proveedor=Proveedor(fila['numProv'], fila['nombreProv'])
                    ))

                sql_detalles = '''
                               SELECT ins.num                                    numInsumo,
                                      ins.nombre                                 nombreInsumo,
                                      ins.umbral                                 umbral,
                                      ins.stock                                  stock,
                                      ti.clave                                   claveTipo,
                                      ti.nombre                                  nombreTipo,
                                      ma.num                                     numeroMarca,
                                      ma.nombre                                  nombreMarca,
                                      DATE_FORMAT(lc.fechaCompra, '%d-%m-%Y')    fechaCompra,
                                      lc.cantidadComprada                        cantidadComprada,
                                      lc.cantidadActual                          cantidadActual,
                                      lc.unidadMedida                            unidadMedida,
                                      DATE_FORMAT(lc.fechaCaducidad, '%d-%m-%Y') fechaCad,
                                      lc.montoUnitario                           montoUnit,
                                      lc.importe                                 importe
                               FROM insumo ins
                                        INNER JOIN marca ma ON ins.marca = ma.num
                                        INNER JOIN tipo_insumo ti ON ins.tipo_insumo = ti.clave
                                        INNER JOIN lista_compra lc ON lc.insumo = ins.num
                                        INNER JOIN compra com ON lc.compra = com.num
                               WHERE lc.compra = %s;
                               '''
                for compra in lista_compras:
                    cursor.execute(sql_detalles, (compra.num,))
                    filas = cursor.fetchall()
                    for fila in filas:
                        compra.agregar_insumo_compra(
                            insumo=Insumo(
                                num=fila['numInsumo'],
                                nombre=fila['nombreInsumo'],
                                umbral=float(fila['umbral']),
                                stock=float(fila['stock']),
                                tipo_insumo=TipoInsumo(fila['claveTipo'], fila['nombreTipo']),
                                marca=Marca(fila['numeroMarca'], fila['nombreMarca'])
                            ),
                            fecha_compra=datetime.strptime(fila['fechaCompra'], "%d-%m-%Y").strftime("%d-%m-%Y"),
                            cantidad_comprada=float(fila['cantidadComprada']),
                            cantidad_actual=float(fila['cantidadActual']),
                            unidad_medida=fila['unidadMedida'],
                            fecha_caducidad=datetime.strptime(fila['fechaCad'], "%d-%m-%Y").strftime("%d-%m-%Y"),
                            monto_unitario=float(fila['montoUnit']),
                            importe=float(fila['importe']))
                # regresamos una lista de compras con sus detalles
                return lista_compras
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar los insumos: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    ''' FUNCIONES DE REGISTRO '''

    def registrar_compra(self, compra_nueva: Compra):
        '''Registra una compra en la BD'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:

                # registra el proveedor de la compra si no existe
                sql_proveedor = '''SELECT num, nombre \
                                FROM proveedor \
                                WHERE num = %s;'''
                cursor.execute(sql_proveedor, (compra_nueva.proveedor.num,))  # type: ignore
                proveedor = cursor.fetchone()
                proveedor_num: int = compra_nueva.proveedor.num  # type: ignore
                if not proveedor:
                    cursor.execute('INSERT INTO proveedor (nombre) VALUES (%s);',
                                (compra_nueva.proveedor.nombre,))  # type: ignore
                    proveedor_num = cursor.lastrowid

                # actualiza los atributos basicos la compra
                sql_compra = ''' \
                            INSERT INTO compra (fechaCreacion, total_bruto, proveedor) \
                            VALUES (%s, %s, %s);
                '''

                cursor.execute(sql_compra, (
                    compra_nueva.fecha_creacion,
                    compra_nueva.total_bruto,
                    proveedor_num
                ))
                compra_id = cursor.lastrowid
                compra_nueva.num = compra_id

                for detalle in compra_nueva.lista_compras:
                    sql_detalles_compra = ''' \
                                        INSERT INTO lista_compra (compra, insumo, montoUnitario, importe, \
                                                                    fechaCompra, fechaCaducidad, cantidadComprada, \
                                                                    cantidadActual, unidadMedida) \
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                        '''

                    cursor.execute(sql_detalles_compra, (
                        compra_nueva.num,
                        detalle.insumo.num,
                        detalle.monto_unitario,
                        detalle.importe,
                        detalle.fecha_compra,
                        detalle.fecha_caducidad,
                        detalle.cantidad_comprada,
                        detalle.cantidad_actual,
                        detalle.unidad_medida))

                    # valor inicial
                    cantidad_convertida_base = detalle.cantidad_comprada
                    ## estandarizar unidades
                    #try:
                    #    categoria = ConversorUnidades.obtener_categoria(detalle.unidad_medida)
                    #    if not categoria or categoria == None:
                    #        raise Exception('Unidad invalida.')
                    #    # evaluar que unidad estandar es
                    #    if categoria == 'MASA':
                    #        cantidad_convertida_base = ConversorUnidades.convertir(
                    #                cantidad=detalle.cantidad_comprada,
                    #                unidad_origen=detalle.unidad_medida,
                    #                unidad_destino='kg'
                    #            )
                    #        assert False, f'Origen:'
                    #    if categoria == 'VOLUMEN':
                    #        cantidad_convertida_base = ConversorUnidades.convertir(
                    #                cantidad=detalle.cantidad_comprada,
                    #                unidad_origen=detalle.unidad_medida,
                    #                unidad_destino='l'
                    #        )
                    #    if categoria == 'CONTEO':
                    #        cantidad_convertida_base = ConversorUnidades.convertir(
                    #                cantidad=detalle.cantidad_comprada,
                    #                unidad_origen=detalle.unidad_medida,
                    #                unidad_destino='pza'
                    #        )
                    #except ValueError as err:
                    #    raise ValueError(err)
                    ## actualiza el stock
                    sql_actualizar_stock = '''UPDATE insumo \
                                            SET stock = stock + %s \
                                            WHERE num = %s;'''

                    cursor.execute(sql_actualizar_stock, (
                        cantidad_convertida_base,
                        detalle.insumo.num
                    ))

                # si se llego hasta aqui sin lanzar excepcion, todo salio bien
                connection.commit()
                return cursor.lastrowid
            
        except ValueError as err:
                raise ValueError(f'DAO: Error con las unidades de medida.')
        except Exception as err:
            # si cualquiera de los updates, inserts o select fallo:
            connection.rollback()
            raise Error(f"DAO: Error en la transaccion al registrar compra.: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    '''FUNCIONES DE UPDATE'''

    def actualizar_compra_completa(self, compra_act: Compra):
        '''Actualiza una compra.'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:

                # valida si existe el proveedor en la BD por su numero
                proveedor_local: int = compra_act.proveedor.num  # type: ignore
                sql_proveedor = '''SELECT num, nombre
                                FROM proveedor
                                WHERE num = %s;''' # confiando en que el id local es el correspondiente a la bd
                cursor.execute(sql_proveedor, (proveedor_local,))  # type: ignore
                proveedor = cursor.fetchone()

                # valor inicial
                id_proveedor = compra_act.proveedor.num  # type: ignore
                # registra el proveedor de la compra si no existe
                if not proveedor:
                    cursor.execute('INSERT INTO proveedor (nombre) VALUES (%s);',
                                (compra_act.proveedor.nombre,))  # type: ignore
                    # entonces se modifica a el id del nuevo proveedor
                    id_proveedor = int(cursor.lastrowid) 

                # actualiza los atributos basicos de la compra
                sql_compra = '''
                            UPDATE compra
                            SET fechaCreacion = %s,
                                total_bruto   = %s,
                                proveedor     = %s
                            WHERE num = %s;
                '''
                cursor.execute(sql_compra, (
                    compra_act.fecha_creacion,
                    compra_act.total_bruto,
                    id_proveedor,
                    compra_act.num
                ))
                # consulta que insumos existen actualmente en la BD para esta compra
                sql_actuales = 'SELECT insumo FROM lista_compra WHERE compra = %s;'
                cursor.execute(sql_actuales, (compra_act.num,))
                # obtiene los numeros de insumo del menu en la BD en una lista
                insumos_num_bd = [fila['insumo'] for fila in cursor.fetchall()]

                # conjunto de ids que el usuario tiene ahora 
                ids_en_formulario = set()

                # iteracion de inserts y updates
                for detalle in compra_act.lista_compras:
                    ins_id = detalle.insumo.num
                    ids_en_formulario.add(ins_id)

                    # asignando a los insumos sus ids de la BD y no los locales
                    sql_buscar_id = '''SELECT num
                                        FROM insumo
                                        WHERE nombre = %s and marca = %s;'''
                    cursor.execute(sql_buscar_id, (detalle.insumo.nombre,detalle.insumo.marca.num))
                    fila = cursor.fetchone()
                    id_bd_ins = int(fila['num'])

                    if ins_id in insumos_num_bd:
                        # si ya existia en la BD, actualiza..
                        sql_update = '''
                                    UPDATE lista_compra li
                                    JOIN insumo ins ON li.insumo = ins.num
                                    SET li.unidadMedida = %s, li.montoUnitario = %s, 
                                        li.fechaCompra = %s, li.fechaCaducidad = %s, 
                                        ins.marca = %s, li.importe = %s
                                    WHERE li.compra = %s AND li.insumo=%s;
                        '''
                        valores = (
                            detalle.unidad_medida,
                            detalle.monto_unitario,
                            detalle.fecha_compra,
                            detalle.fecha_caducidad,
                            detalle.insumo.marca.num,  # type: ignore
                            detalle.importe,
                            compra_act.num,
                            id_bd_ins
                        )
                        cursor.execute(sql_update, valores)

                        # actualizar stock ya que se modifico la cantidad comprada del insumo de la compra
                    else:
                        # si el insumo no esta en la compra en la bd, se inserta
                        sql_insert = '''
                                    INSERT INTO lista_compra 
                                        (compra, insumo, montoUnitario, importe,
                                        fechaCompra, fechaCaducidad, cantidadComprada,
                                        cantidadActual, unidadMedida)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);'''
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

                        # actualiza el stock del insumo de este nuevo detalle-compra sumandole la cantidad comprada
                        sql_actualizar_stock = '''UPDATE insumo
                                                SET stock = stock + %s
                                                WHERE num = %s;'''
                        cursor.execute(sql_actualizar_stock, (
                            detalle.cantidad_comprada,
                            id_bd_ins
                        ))
                # ELIMINAR INSUMO DE COMPRA PENDIENTE
                ## delete de los platillos que el usuario elimino
                # for plat_id in platillos_num_bd:
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

    def crear_proveedor(self, proveedor:Proveedor):
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:

                sql_insumo = '''
                             INSERT INTO proveedor (nombre)
                             VALUES (%s);
                             '''
                cursor.execute(sql_insumo, (proveedor.nombre,))

                connection.commit()

        except mysql.connector.Error as err:
            connection.rollback()
            raise Error(f"DAO: Error al crear proveedor: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def eliminar_compra(self, num_compra:int):
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:

                # actualiza la lista de compras
                sql_lista_compra = '''
                                    DELETE
                                    FROM lista_compra
                                    WHERE compra = %s;
                                    '''
                cursor.execute(sql_lista_compra, (num_compra,))

                sql_menu = '''
                           DELETE
                           FROM compra
                           WHERE num = %s;
                           '''
                cursor.execute(sql_menu, (num_compra,))

                cursor.execute("ALTER TABLE compra AUTO_INCREMENT = 1")

                connection.commit()

        except mysql.connector.Error as err:
            # si cualquiera de los updates, inserts o select fallo
            connection.rollback()
            raise Error(f"DAO: Error en la transacción al eliminar compra: {err}")
        finally:
            if connection.is_connected():
                connection.close()
