import time
from datetime import datetime
from decimal import Decimal
from typing import List

import mysql.connector
from mysql.connector import Error

from models.categoria import Categoria
from models.ingrediente import Ingrediente
from models.insumo import Insumo
from models.platillo import Platillo
from models.receta import Receta
from models.venta import Venta, Consumo
from utils.conversor_unidades import ConversorUnidades


class VentaDAO:
    def __init__(self, db_manager):
        self.db = db_manager

    def obtener_ventas(self) -> list[Venta]:
        ''' obtiene las ventas y su consumo asociado '''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql_ventas = '''
                      SELECT num numVenta, 
                             numComensales comensales, 
                             DATE_FORMAT(fecha, '%d-%m-%Y') fechaVenta, 
                             montoTotal montoVenta
                      FROM venta;
                      '''
                cursor.execute(sql_ventas)
                filas = cursor.fetchall()

                ventas_lista: list[Venta] = []

                for fila in filas:
                    ventas_lista.append(Venta(num=fila["numVenta"],
                                              numero_comensales=fila["comensales"],
                                              fecha=datetime.strptime(fila["fechaVenta"], "%d-%m-%Y").strftime("%d-%m-%Y"),
                                              monto_total=(fila["montoVenta"])))

                for venta in ventas_lista:
                    sql_consumo = '''
                                  SELECT cons.venta ventaNum,
                                         cons.platillo platNum,
                                         cons.importe importe,
                                         cons.cantidadPlatillos cantPlat,
                                        plat.nombre nomPlat,
                                        plat.categoria catPlat,
                                        plat.receta recNum,
                                        rec.nombre recNom,
                                        rec.numPorciones numPorc
                                  FROM consumo cons
                                  INNER JOIN platillo plat on cons.platillo = plat.num  
                                  INNER JOIN receta rec on plat.receta = rec.num
                                  WHERE cons.venta = %s;
                                  '''
                    cursor.execute(sql_consumo, (venta.num,))

                    filas = cursor.fetchall()

                    for fila in filas:
                        venta.detalles.append(Consumo(
                            platillo=Platillo(fila["platNum"], fila["nomPlat"], None,
                                              receta=Receta(fila["recNum"], fila["recNom"], fila["numPorc"], {})),
                            importe=fila["importe"],
                            cantidad_platillos=fila["cantPlat"]
                        ))

                return ventas_lista

        except mysql.connector.Error as err:
            raise Error(f"DAO: Error generico de mysql ventas: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_ventas_por_rango_fecha(self, fecha_inicial, fecha_final) -> list[Venta]:
        ''' obtiene las ventas y su consumo asociado cuando estas hayan sido en un rango de tiempo específico'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql_ventas = '''
                      SELECT num numVenta, 
                             numComensales comensales, 
                             DATE_FORMAT(fecha, '%d-%m-%Y') fechaVenta, 
                             montoTotal montoVenta
                      FROM venta
                      WHERE fecha BETWEEN %s and %s;
                      '''
                cursor.execute(sql_ventas, (fecha_inicial, fecha_final))
                filas = cursor.fetchall()

                ventas_lista: list[Venta] = []

                for fila in filas:
                    ventas_lista.append(Venta(num=fila["numVenta"],
                                              numero_comensales=fila["comensales"],
                                              fecha=datetime.strptime(fila["fechaVenta"], "%d-%m-%Y").strftime("%d-%m-%Y"),
                                              monto_total=fila["montoVenta"]))

                for venta in ventas_lista:
                    sql_consumo = '''
                                  SELECT cons.venta ventaNum,
                                         cons.platillo platNum,
                                         cons.importe importe,
                                         cons.cantidadPlatillos cantPlat,
                                        plat.nombre nomPlat,
                                        plat.categoria catPlat,
                                        plat.receta recNum,
                                        rec.nombre recNom,
                                        rec.numPorciones numPorc
                                  FROM consumo cons
                                  INNER JOIN platillo plat on cons.platillo = plat.num  
                                  INNER JOIN receta rec on plat.receta = rec.num
                                  WHERE cons.venta = %s;
                                  '''
                    cursor.execute(sql_consumo, (venta.num,))

                    filas = cursor.fetchall()

                    for fila in filas:
                        venta.detalles.append(Consumo(
                            platillo=Platillo(fila["platNum"], fila["nomPlat"], None,
                                              receta=Receta(fila["recNum"], fila["recNom"], fila["numPorc"], {})),
                            importe=fila["importe"],
                            cantidad_platillos=fila["cantPlat"]
                        ))

                return ventas_lista

        except mysql.connector.Error as err:
            raise Error(f"DAO: Error generico de mysql ventas: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_ultima_venta_registrada(self) -> Venta:
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql_ventas = '''
                             SELECT num                            numVenta,
                                    numComensales                  comensales,
                                    DATE_FORMAT(fecha, '%d-%m-%Y') fechaVenta,
                                    montoTotal                     montoVenta
                             FROM venta
                             ORDER BY numVenta desc;
                             '''
                cursor.execute(sql_ventas)
                fila = cursor.fetchall()[0]

                venta = Venta(num=fila["numVenta"],
                               numero_comensales=fila["comensales"],
                               fecha=datetime.strptime(fila["fechaVenta"], "%d-%m-%Y").strftime(
                                                  "%d-%m-%Y"),
                               monto_total=fila["montoVenta"])

                sql_consumo = '''
                              SELECT cons.venta             ventaNum,
                                     cons.platillo          platNum,
                                     cons.importe           importe,
                                     cons.cantidadPlatillos cantPlat,
                                     plat.nombre            nomPlat,
                                     plat.categoria         catPlat,
                                     plat.receta            recNum,
                                     rec.nombre             recNom,
                                     rec.numPorciones       numPorc
                              FROM consumo cons
                                       INNER JOIN platillo plat on cons.platillo = plat.num
                                       INNER JOIN receta rec on plat.receta = rec.num
                              WHERE cons.venta = %s;
                              '''
                cursor.execute(sql_consumo, (venta.num,))

                filas = cursor.fetchall()

                for fila in filas:
                    venta.detalles.append(Consumo(
                        platillo=Platillo(fila["platNum"], fila["nomPlat"], None,
                                          receta=Receta(fila["recNum"], fila["recNom"], fila["numPorc"], {})),
                        importe=fila["importe"],
                        cantidad_platillos=fila["cantPlat"]
                    ))

                return venta

        except mysql.connector.Error as err:
            raise Error(f"DAO: Error generico de mysql ventas: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_venta_por_num(self, num_venta:int) -> Venta:
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql_ventas = '''
                             SELECT num                            numVenta,
                                    numComensales                  comensales,
                                    DATE_FORMAT(fecha, '%d-%m-%Y') fechaVenta,
                                    montoTotal                     montoVenta
                             FROM venta
                             WHERE num = %s;
                             '''
                cursor.execute(sql_ventas, (num_venta,))
                fila = cursor.fetchall()[0]

                venta = Venta(num=fila["numVenta"],
                              numero_comensales=fila["comensales"],
                              fecha=datetime.strptime(fila["fechaVenta"], "%d-%m-%Y").strftime(
                                  "%d-%m-%Y"),
                              monto_total=fila["montoVenta"])

                sql_consumo = '''
                              SELECT cons.venta             ventaNum,
                                     cons.platillo          platNum,
                                     cons.importe           importe,
                                     cons.cantidadPlatillos cantPlat,
                                     plat.nombre            nomPlat,
                                     plat.categoria         catPlat,
                                     plat.receta            recNum,
                                     rec.nombre             recNom,
                                     rec.numPorciones       numPorc
                              FROM consumo cons
                                       INNER JOIN platillo plat on cons.platillo = plat.num
                                       INNER JOIN receta rec on plat.receta = rec.num
                              WHERE cons.venta = %s; \
                              '''
                cursor.execute(sql_consumo, (venta.num,))

                filas = cursor.fetchall()

                for fila in filas:
                    venta.detalles.append(Consumo(
                        platillo=Platillo(fila["platNum"], fila["nomPlat"], None,
                                          receta=Receta(fila["recNum"], fila["recNom"], fila["numPorc"], {})),
                        importe=fila["importe"],
                        cantidad_platillos=fila["cantPlat"]
                    ))

                return venta

        except mysql.connector.Error as err:
            raise Error(f"DAO: Error generico de mysql ventas: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_platillos_disponibles_por_fecha(self, fecha) -> Platillo|None:
        '''Retorna todos los platillos que están activos en un menú en la fecha especificada'''
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
                                INNER JOIN menu_platillo as mp on p.num = mp.platillo
                                INNER JOIN menu as m on mp.menu = m.num
                      WHERE %s BETWEEN m.fechaInicial and m.fechaFinal;
                      '''
                cursor.execute(sql, (fecha,))
                filas = cursor.fetchall()
                lista_platillos: List[Platillo] = []

                if filas is None:
                    return None

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

    def obtener_precio_platillo_por_fecha(self, fecha, num_platillo):
        '''Retorna todos los platillos que están activos en un menú en la fecha especificada'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                      SELECT mp.precio precio
                        FROM platillo p
                        INNER JOIN menu_platillo as mp on p.num = mp.platillo
                        INNER JOIN menu as m on mp.menu = m.num
                      WHERE %s BETWEEN m.fechaInicial and m.fechaFinal and p.num = %s;
                      '''
                cursor.execute(sql, (fecha, num_platillo))
                res = cursor.fetchone()

                return float(res['precio'])
        except mysql.connector.Error as err:
            raise Error(f"DAO: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def crear_venta(self, venta:Venta):
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                # registra venta
                sql_venta = '''
                           INSERT INTO venta (numComensales, fecha, montoTotal)
                           VALUES (%s, %s, %s);
                           '''
                cursor.execute(sql_venta, (venta.numero_comensales, venta.fecha, venta.monto_total))

                connection.commit()

        except mysql.connector.Error as err:
            connection.rollback()
            raise Error(f"DAO: Error en al crear venta: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def descontar_consumo(self, venta:Venta):
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                conversor = ConversorUnidades()
                for consumo in venta.detalles:
                    for ing_detalle in consumo.platillo.receta.lista_ingredientes:
                        nombre_insumo = ing_detalle.ingrediente.insumo.nombre

                        # esto quiere decir que los ingredientes son basados en receta, lo que requiere
                        # de otro loop para descontar cada insumo de la receta del ingrediente
                        if nombre_insumo is None:
                            sql_ingredientes_rec_ing = '''
                                  SELECT
                                         li.cantidad     cantidad,
                                         li.unidadMedida uniMedida,
                                         ins.nombre      InsumoNombre,
                                         i.receta        NumRecetaIngrediente,
                                        r.numPorciones numPorc
                                  FROM lista_ingredientes li
                                           INNER JOIN receta AS r ON li.receta = r.num
                                           INNER JOIN ingrediente AS i ON li.ingrediente = i.num
                                           INNER JOIN insumo AS ins ON i.insumo = ins.num
                                  WHERE li.receta = %s;'''

                            cursor.execute(sql_ingredientes_rec_ing, (nombre_insumo,))
                            filas_ing = cursor.fetchall()

                            for fila in filas_ing:
                                nombre_insumo = fila['InsumoNombre']

                                cantidad_por_porcion_ing = float(fila['cantidad'] / fila['numPorc'])
                                cantidad_total_por_ing_completo = float(ing_detalle.cantidad) * cantidad_por_porcion_ing
                                cantidad_a_descontar = cantidad_total_por_ing_completo * cant_platillos
                                unidad_medida = fila['uniMedida']
                                cant_platillos = consumo.cantidad_platillos

                                while cantidad_a_descontar != 0:
                                    # checa el stock del insumo
                                    sql_detalle_compra = '''
                                                         SELECT ins.num        insNum,
                                                                compra         com,
                                                                cantidadActual cantAct,
                                                                unidadMedida   unidad
                                                         FROM lista_compra li
                                                                  INNER JOIN insumo ins on ins.num = li.insumo
                                                         WHERE ins.nombre = %s
                                                         ORDER BY fechaCaducidad;
                                                         '''
                                    cursor.execute(sql_detalle_compra, (nombre_insumo,))
                                    res = cursor.fetchall()[0]

                                    if res:
                                        # convierte la cantidad del ingrediente a la cantidad para la unidad de medida del insumo
                                        cantidad_a_descontar = conversor.convertir(cantidad_a_descontar, unidad_medida,
                                                                                   res['unidad'])
                                        cantidad_actual = float(res['cantAct'])

                                        if cantidad_actual >= cantidad_a_descontar:
                                            # el detalle de compra tiene stock suficiente, descuenta la cant actual y la cantidad restante a descontar se pone en 0
                                            cantidad_actual -= cantidad_a_descontar
                                            cantidad_a_descontar = 0
                                        else:
                                            # el detalle de compra no tiene stock suficiente, se descuenta la cant actual a lo que resta de la cantidad
                                            # y actualiza la cant act a 0
                                            cantidad_a_descontar -= cantidad_actual
                                            cantidad_actual = 0

                                        sql_actualiza_stock = '''
                                                              UPDATE lista_compra
                                                              SET cantidadActual = %s
                                                              WHERE insumo = %s
                                                                and compra = %s;
                                                              '''

                                        cursor.execute(sql_actualiza_stock, (cantidad_actual, res['insNum'], res['com']))
                                    else:
                                        # no hubo resultados del query
                                        raise ValueError(f"Error: No hay insumos disponibles para completar la venta")

                        # se dividen la cant de los ingredientes entre la cantidad de porciones que rinde la receta
                        # para ver cuánto se gasta por cada platillo, se divide entre la porción usada
                        # y se multiplica por la cantidad de platillos vendida
                        cant_platillos = consumo.cantidad_platillos
                        cantidad_ing = float(ing_detalle.cantidad) / int(ing_detalle.ingrediente.receta.num_porciones)
                        cantidad_a_descontar = (cantidad_ing / consumo.platillo.receta.num_porciones) * cant_platillos
                        unidad_medida = ing_detalle.unidad_medida

                        while cantidad_a_descontar != 0:
                            # checa el stock del insumo
                            sql_detalle_compra = '''
                                                 SELECT ins.num        insNum,
                                                        compra         com,
                                                        cantidadActual cantAct,
                                                        unidadMedida   unidad
                                                 FROM lista_compra li
                                                          INNER JOIN insumo ins on ins.num = li.insumo
                                                 WHERE ins.nombre = %s
                                                 ORDER BY fechaCaducidad;
                                                 '''
                            cursor.execute(sql_detalle_compra, (nombre_insumo,))
                            res = cursor.fetchall()[0]

                            if res:
                                # convierte la cantidad del ingrediente a la cantidad para la unidad de medida del insumo
                                cantidad_a_descontar = conversor.convertir(cantidad_a_descontar, unidad_medida, (res['unidad']))
                                cantidad_actual = float(res['cantAct'])

                                if cantidad_actual >= cantidad_a_descontar:
                                    # el detalle de compra tiene stock suficiente, descuenta la cant actual y la cantidad restante a descontar se pone en 0
                                    cantidad_actual -= cantidad_a_descontar
                                    cantidad_a_descontar = 0
                                else:
                                    # el detalle de compra no tiene stock suficiente, se descuenta la cant actual a lo que resta de la cantidad
                                    # y actualiza la cant act a 0
                                    cantidad_a_descontar -= cantidad_actual
                                    cantidad_actual = 0

                                sql_actualiza_stock = '''
                                                      UPDATE lista_compra
                                                      SET cantidadActual = %s
                                                      WHERE insumo = %s
                                                        and compra = %s;
                                                      '''

                                cursor.execute(sql_actualiza_stock, (cantidad_actual, res['insNum'], res['com']))
                            else:
                                # no hubo resultados del query
                                raise ValueError(f"Error: No hay insumos disponibles para completar la venta")
                connection.commit()

        except mysql.connector.Error as err:
            connection.rollback()
            raise Error(f"DAO: Error en al actualizar el consumo: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def registrar_consumo(self, venta: Venta):
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                for consumo in venta.detalles:
                    sql_consumo = '''
                                  INSERT INTO consumo (venta, platillo, importe, cantidadPlatillos)
                                  VALUES (%s, %s, %s, %s);
                                  '''
                    cursor.execute(sql_consumo,
                                   (venta.num, consumo.platillo.num, consumo.importe, consumo.cantidad_platillos))

                connection.commit()

        except mysql.connector.Error as err:
            # si cualquiera de los updates, inserts o select fallo:
            connection.rollback()
            raise Error(f"DAO: Error en la transaccion al crear consumo: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def actualizar_venta(self, venta:Venta):
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:

                # actualiza los atributos básicos del menu
                sql_venta = '''
                           UPDATE venta
                           SET numComensales = %s,
                               fecha = %s,
                               montoTotal = %s
                           WHERE num = %s;
                           '''

                cursor.execute(sql_venta, (venta.numero_comensales, venta.fecha, venta.monto_total, venta.num))

                for consumo in venta.detalles:
                    sql_consumo = '''
                               UPDATE consumo
                               SET venta = %s,
                                   platillo = %s,
                                   importe = %s,
                                   cantidadPlatillos = %s
                               WHERE venta = %s;
                               '''
                    cursor.execute(sql_consumo, (venta.num, consumo.platillo.num, consumo.importe, consumo.cantidad_platillos, venta.num))

                connection.commit()

        except mysql.connector.Error as err:
            # si cualquiera de los updates, inserts o select fallo:
            connection.rollback()
            raise Error(f"DAO: Error en la transaccion al actualizar venta: {err}")
        finally:
            if connection.is_connected():
                connection.close()