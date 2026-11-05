from models.tipo_insumo import TipoInsumo
from models.marca import Marca
from models.insumo import Insumo
from models.ingrediente import Ingrediente
from models.receta import Receta

from typing import List

import mysql.connector

class RecetaDAO:    
    def __init__(self, db_manager):
        self.db = db_manager # clase que hace crea las conexiones

    def buscar_por_id(self, num_insumo:int):
        pass
    
    def buscar_por_nombre(self, nombre_insumo:str):
        #for receta in self._tabla_recetas:
        #    if receta.nombre == nombre_insumo:
        #        return receta
        #return False
        pass
        
    def obtener_recetas(self):
        """Obtiene una receta por su id."""
        connection = self.db.get_connection()

        try:
            # 'with' cierra automáticamente el cursor al terminar de usarse
            with connection.cursor(dictionary=True) as cursor:
                #sql = "SELECT r.num, r.nombre, r.numPorciones FROM receta AS r WHERE r.num = %s"
                sql = "SELECT num, nombre, numPorciones FROM receta"
                cursor.execute(sql)
                filas = cursor.fetchall()

                sql2 = '''
                    SELECT
                    i.num,
                    i.instruccion
                    FROM receta AS r
                    INNER JOIN instrucciones AS i ON i.receta = r.num
                    WHERE r.num = 1;
                                '''
                cursor.execute(sql2)
                filas_instrucciones = cursor.fetchall()

                lista_recetas: List[Receta] = []
                # mapeando recetas a una lista
                for fila in filas:
                    nueva_receta = Receta(
                        num=fila['num'],
                        nombre=fila['nombre'],
                        num_porciones=fila['numPorciones'],
                        instrucciones=self.obtener_instrucion_receta_por_id(fila['num']))
                    lista_recetas.append(nueva_receta)
                return lista_recetas

        except mysql.connector.Error as err:
            # manejo de errores de base de datos
            print(f"Error al obtener recetas: {err}")

        finally:
            # devuelve el pool, incluso si hubo un error o un return antes
            if connection.is_connected():
                connection.close()

    def obtener_instrucion_receta_por_id(self, num_receta:int):
        """Obtiene una instruccion por su id."""
        connection = self.db.get_connection()

        try:
            # 'with' cierra automáticamente el cursor al terminar de usarse
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                    SELECT
                    i.num,
                    i.instruccion
                    FROM receta AS r
                    INNER JOIN instrucciones AS i ON i.receta = r.num
                    WHERE r.num = %s;
                                '''

                # mapeando instruccion
                cursor.execute(sql, (num_receta,))                
                filas = cursor.fetchall()
                respuesta: dict[int,str] = {}

                for fila in filas:
                    respuesta[fila['num']] = fila['instruccion']
                return respuesta

        except mysql.connector.Error as err:
            # manejo de errores de base de datos
            print(f"Error al obtener instruccion: {err}")

        finally:
            # devuelve el pool, incluso si hubo un error o un return antes
            if connection.is_connected():
                connection.close()

    def buscar_ingrediente_por_id(self, num_ingrediente:int):
        pass
        #"""Simula un SELECT * FROM receta WHERE num = ?"""
        #for ingrediente in self._tabla_ingredientes:
        #    if ingrediente.num == num_ingrediente:
        #        return ingrediente
        #return False

    def obtener_todos_ingredientes(self):
        #return self._tabla_ingredientes
        pass

