from models.tipo_insumo import TipoInsumo
from models.marca import Marca
from models.insumo import Insumo
from models.ingrediente import Ingrediente
from models.receta import Receta,IngredientesReceta

from typing import List

import mysql.connector
from mysql.connector import Error


class RecetaDAO:    
    def __init__(self, db_manager):
        self.db = db_manager # clase que hace crea las conexiones
    '''funciones de consulta'''

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
                sql = "SELECT num NumReceta, nombre NomReceta, numPorciones NumPor FROM receta"
                cursor.execute(sql)
                filas = cursor.fetchall()
                
                lista_recetas: List[Receta] = []
                # mapeando recetas a una lista
                for fila in filas:
                    nueva_receta = Receta(
                        num=fila['NumReceta'],
                        nombre=fila['NomReceta'],
                        num_porciones=fila['NumPor'],
                        instrucciones=self.obtener_instrucion_receta_por_id(fila['NumReceta']))
                    filitas:dict = self.obtener_ingredientes_receta(fila['NumReceta'])

                    for filita in filitas:
                        nueva_receta.agregarIngrediente(
                            ingrediente=Ingrediente(filita['NumIngre'],filita['IngreNombre'],insumo=None,receta=None),
                            cantidad=filita['Cantidad'],
                            unidad_medida=filita['uniMedida']
                            )                    
                    lista_recetas.append(nueva_receta)

                    #r.num NumReceta,
                    #i.num NumIngre,
                    #i.nombre IngreNombre,
                    #li.cantidad Cantidad,
                    #li.unidadMedida uniMedida

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

    def obtener_ingredientes_receta(self, num_receta:int):
        '''obtiene todo los ingredientes de una receta'''
    #nombre, cantidad, unidad de medida
        connection = self.db.get_connection()
        try:
            # 'with' cierra automáticamente el cursor al terminar de usarse
            with connection.cursor(dictionary=True) as cursor:
                sql = '''SELECT 
                            r.num NumReceta,
                            i.num NumIngre,
                            i.nombre IngreNombre,
                            li.cantidad Cantidad,
                            li.unidadMedida uniMedida
                        FROM lista_ingredientes li
                        INNER JOIN receta AS r ON li.receta = r.num
                        INNER JOIN ingrediente AS i ON li.ingrediente = i.num
                        WHERE r.num = %s;'''
                cursor.execute(sql,(num_receta,))

                return cursor.fetchall()
            
        except mysql.connector.Error as err:
            # manejo de errores de base de datos
            print(f"Error al obtener recetas: {err}")
        finally:
            # devuelve el pool, incluso si hubo un error o un return antes
            if connection.is_connected():
                connection.close()

        #return self._tabla_ingredientes
        pass

    '''funciones de registro'''

    def crear_receta_vacia(self, receta:Receta):
        '''Inserta un nuevo registo de una receta sin instrucciones ni ingredientes.'''
        connection = self.db.get_connection()

        try:
            # 'with' cierra automáticamente el cursor al terminar de usarse
            with connection.cursor(dictionary=True) as cursor:
                query = '''
                        INSERT INTO receta (nombre,numPorciones) 
                        VALUES (%s,%s);
                        '''
                cursor.execute(query,(receta.nombre,receta.num_porciones))
                connection.commit()
                
                return connection.lastrowid()

        except mysql.connector.Error as err:
            # si hay fallo, se revierte la query ejecutada
            connection.rollback()
            raise Error(f"Error al insertar la receta: {err}")

        finally:
            # devuelve el pool, incluso si hubo un error o un return antes
            if connection.is_connected():
                connection.close()
        
        #nombre receta, num porciones, ingredientes (nombre, cantidad, unidadMedida)
        #instrucciones(num,intruccion)


    def agregar_ingrediente_a_receta(self, num_receta:int, ingrediente_receta:IngredientesReceta):
        
        '''Agrega un ingrediente a una receta.'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                query = '''
                        INSERT INTO lista_ingredientes (ingrediente,receta,cantidad,unidadMedida) VALUES 
                        (%s, %s, %s,%s);
                        '''
                valores = (
                    ingrediente_receta.ingrediente.num,
                    num_receta,
                    ingrediente_receta.cantidad,
                    ingrediente_receta.unidad_medida
                )
                cursor.execute(query,valores)
                connection.commit()
                return connection.lastrowid()

        except mysql.connector.Error as err:
            # si hay fallo, se revierte la query ejecutada
            connection.rollback()
            raise Error(f"Error al insertar la receta: {err}")

        finally:
            # devuelve el pool, incluso si hubo un error o un return antes
            if connection.is_connected():
                connection.close()

    def agregar_instruccion_a_receta(self, num_receta:int, num_instruccion:int, instruccion:str):
            '''Agrega una instruccion a una receta.'''
            connection = self.db.get_connection()
            try:
                with connection.cursor(dictionary=True) as cursor:
                    query = '''
                            INSERT INTO instrucciones (num, receta, instruccion) VALUES (%s, %s, %s);
                            '''
                    valores = (
                        num_instruccion,
                        num_receta,
                        instruccion
                    )
                    cursor.execute(query,valores)
                    connection.commit()
                    return connection.lastrowid()

            except mysql.connector.Error as err:
                # si hay fallo, se revierte la query ejecutada
                connection.rollback()
                raise Error(f"Error al insertar la instruccion: {err}")

            finally:
                # devuelve el pool, incluso si hubo un error o un return antes
                if connection.is_connected():
                    connection.close()