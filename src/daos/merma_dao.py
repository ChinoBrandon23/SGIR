from typing import List

import mysql.connector
from mysql.connector import Error

from models.insumo import Insumo
from models.marca import Marca
from models.merma import Merma
from models.tipo_insumo import TipoInsumo
from models.tipo_merma import TipoMerma


class MermaDAO:
    def __init__(self, db_connection):
        self.db = db_connection

    ''' METODOS DE CONSULTA '''

    def _consultar_mermas(self, condicion: str = "", parametros: tuple = ()) -> List[Merma]:
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = f"""
                    SELECT
                        me.num numMerma,
                        me.descripcion descripcion,
                        me.fecha fecha,
                        me.unidadMedida unidadMedida,
                        me.cantidad cantidad,
                        ins.num numInsumo,
                        ins.nombre nombreInsumo,
                        ins.umbral umbral,
                        ins.stock stock,
                        ti.clave claveTipoInsumo,
                        ti.nombre nombreTipoInsumo,
                        ma.num numMarca,
                        ma.nombre nombreMarca,
                        tm.clave claveTipoMerma,
                        tm.nombre nombreTipoMerma
                    FROM merma me
                    INNER JOIN insumo ins ON me.insumo = ins.num
                    INNER JOIN tipo_insumo ti ON ins.tipo_insumo = ti.clave
                    INNER JOIN marca ma ON ins.marca = ma.num
                    INNER JOIN tipo_merma tm ON me.tipo_merma = tm.clave
                    {condicion}
                    ORDER BY me.fecha, me.num;
                """
                cursor.execute(sql, parametros)
                filas = cursor.fetchall()

                return [
                    Merma(
                        num=fila["numMerma"],
                        descripcion=fila["descripcion"],
                        fecha=fila["fecha"],
                        unidad_medida=fila["unidadMedida"],
                        cantidad=float(fila["cantidad"]),
                        insumo=Insumo(
                            num=fila["numInsumo"],
                            nombre=fila["nombreInsumo"],
                            umbral=float(fila["umbral"]),
                            stock=float(fila["stock"]),
                            tipo_insumo=TipoInsumo(
                                fila["claveTipoInsumo"], fila["nombreTipoInsumo"]
                            ),
                            marca=Marca(fila["numMarca"], fila["nombreMarca"]),
                        ),
                        tipo_merma=TipoMerma(
                            fila["claveTipoMerma"], fila["nombreTipoMerma"]
                        ),
                    )
                    for fila in filas
                ]
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar las mermas: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_mermas(self) -> List[Merma]:
        """Obtiene todas las mermas con su insumo y tipo asociados."""
        return self._consultar_mermas()

    def obtener_merma_por_numero(self, num_merma: int) -> Merma | None:
        """Obtiene una merma por su número."""
        mermas = self._consultar_mermas("WHERE me.num = %s", (num_merma,))
        return mermas[0] if mermas else None

    def obtener_merma_por_nombre(self, nombre_merma: int) -> Merma | None:
        """Obtiene una merma por su nombre."""
        mermas = self._consultar_mermas("WHERE me.nombre = %s", (nombre_merma,))
        return mermas[0] if mermas else None

    def obtener_mermas_por_rango_fecha(self, fecha_inicial: str, fecha_final: str) -> List[Merma]:
        """Obtiene las mermas registradas dentro de un rango de fechas inclusivo."""
        return self._consultar_mermas(
            "WHERE me.fecha BETWEEN %s AND %s",
            (fecha_inicial, fecha_final),
        )

    def obtener_mermas_por_tipo(self, tipo_merma_clave: str) -> List[Merma]:
        """Obtiene las mermas correspondientes a un tipo."""
        return self._consultar_mermas(
            "WHERE me.tipo_merma = %s", (tipo_merma_clave,)
        )

    def obtener_mermas_por_insumo(self, num_insumo: int) -> List[Merma]:
        """Obtiene las mermas asociadas a un insumo."""
        return self._consultar_mermas("WHERE me.insumo = %s", (num_insumo,))

    def obtener_tipos_merma(self) -> List[TipoMerma]:
        """Obtiene todos los tipos de merma disponibles."""
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    "SELECT clave, nombre FROM tipo_merma ORDER BY nombre;"
                )
                filas = cursor.fetchall()
                return [
                    TipoMerma(fila["clave"], fila["nombre"])
                    for fila in filas
                ]
        except mysql.connector.Error as err:
            raise Error(f"DAO: Error al consultar los tipos de merma: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    ''' METODOS DE CREACION '''
    def registrar_merma(self, merma:Merma) -> int:
        '''Registra una merma.'''
        # fecha, cantidad merma, unidad medida, insumo mermado, tipo merma -> (uno existento o 0 para nuevo)
        # 1. Validar que la fecha no pueda ser mayor a hoy
        # 2. validar que la fecha no sea mayor a 1 pasada semana
        # 3. validar la cantidad de la merma, p.e. debe ser mayor e igual a 0
        # 3. validar unidad de medida
        # 4. validar que el insumo seleccionado exista buscando por su nombre en la bd y que el dao regrese un num
            #(no se puede registrar una merma de un insumo inexistente)
        # 5. validar que el tipo de merma exista, si no, crear uno. (esto va en el dao creo)
        # 6. logica para convertir la cantidad a la unidad base y para que ese sea la nueva cantidad que se descontara del insumo
        # 7. try: registrar merma dao. 
        # 8. buscar el detalle insumo con la fecha mas antigua
        # 9. mermar en el dao
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:

                # registra el proveedor de la compra si no existe
                sql_reg_merma = '''
                                INSERT INTO merma (descripcion, fecha, unidadMedida, cantidad, insumo, tipo_merma)
                                VALUES (%s,%s,%s,%s,%s,%s);'''
                cursor.execute(sql_reg_merma, (
                    '', # descripcion inicia en ''
                    merma.fecha,
                    merma.unidad_medida,
                    merma.cantidad,
                    merma.insumo,
                    merma.tipo_merma
                )) 
                
                sql_mermar_insumo = '''
                                    UPDATE insumo
                                    SET stock = stock - %s
                                    WHERE num = %s;
                                    '''
                cursor.execute(sql_mermar_insumo, (
                    merma.cantidad, # cantidad previamente convertida e el servicio
                    merma.insumo.num 
                ))

                # si se llego hasta aqui sin lanzar excepcion, todo salio bien
                connection.commit()
                return cursor.lastrowid
            
        except Exception as err:
            # si cualquiera de los updates, inserts o select fallo:
            connection.rollback()
            raise Error(f"DAO: Error en la transaccion al registrar la merma. {err}")
        finally:
            if connection.is_connected():
                connection.close()
    











