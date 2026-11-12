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

    def obtener_receta_por_id(self, num_receta:int):
        '''obtiene una receta por su numero.'''
        #nombre, cantidad, unidad de medida
        connection = self.db.get_connection()
        try:
            # 'with' cierra automáticamente el cursor al terminar de usarse
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                        SELECT num NumReceta, nombre NomReceta, numPorciones NumPor 
                        FROM receta 
                        WHERE num = %s;'''
                cursor.execute(sql,(num_receta,))
                respuesta = cursor.fetchone()
                if not respuesta:
                    raise IndexError('DAO:  No existe la receta en la BD.')
                receta = Receta(
                        num=respuesta['NumReceta'],
                        nombre=respuesta['NomReceta'],
                        num_porciones=respuesta['NumPor'],
                        instrucciones={}
                    )
                return receta
        except mysql.connector.Error as err:
            # manejo de errores de base de datos
            raise Error(f"Error generico de mysql receta: {err}")
        finally:
            # devuelve el pool, incluso si hubo un error o un return antes
            if connection.is_connected():
                connection.close()

    def obtener_ingrediente_por_id(self, num_ing:int):
        '''obtiene un ingrediente por su numero.'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                        SELECT num, nombre, receta numReceta, insumo numInsumo   
                        FROM ingrediente
                        WHERE num = %s;'''
                cursor.execute(sql,(num_ing,))
                respuesta = cursor.fetchone()
                if not respuesta:
                    raise IndexError('DAO:  No existe la receta en la BD.')
                ingrediente = Ingrediente(
                        num=respuesta['num'],
                        nombre=respuesta['nombre'],
                        receta=Receta(respuesta['numReceta'],'',0,{}), # objeto hueco
                        insumo=Insumo(respuesta['numInsumo'],'',0,0,None,None) # objeto hueco
                    )
                return ingrediente
        except mysql.connector.Error as err:
            raise Error(f"Error generico de mysql ingrediente: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_ingrediente_por_nombre(self, nombre_ing:str):
        '''obtiene un ingrediente por su numero.'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                        SELECT num, nombre, receta numReceta, insumo numInsumo   
                        FROM ingrediente
                        WHERE nombre = %s;'''
                cursor.execute(sql,(nombre_ing,))
                respuesta = cursor.fetchone()
                if not respuesta:
                    raise IndexError('DAO:  No existe la receta en la BD.')
                ingrediente = Ingrediente(
                        num=respuesta['num'],
                        nombre=respuesta['nombre'],
                        receta=Receta(respuesta['numReceta'],'',0,{}), # objeto hueco
                        insumo=Insumo(respuesta['numInsumo'],'',0,0,None,None) # objeto hueco
                    )
                return ingrediente
        except mysql.connector.Error as err:
            raise Error(f"Error generico de mysql ingrediente: {err}")
        finally:
            if connection.is_connected():
                connection.close()

    def obtener_recetas(self):
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
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
                        instrucciones={})
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
        """Obtiene todas las instrucciones de una receta."""
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
            raise Error(f"Error al obtener instruccion: {err}")

        finally:
            # devuelve el pool, incluso si hubo un error o un return antes
            if connection.is_connected():
                connection.close()

    def obtener_ingredientes_receta(self, num_receta:int):
        '''obtiene todo los ingredientes de una receta'''
    #nombre, cantidad, unidad de medida
        connection = self.db.get_connection()
        try:
            # 'with' cierra automáticamente el cursor al terminar de usarse
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                        SELECT 
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
            raise Error(f"Error al obtener recetas: {err}")
        finally:
            # devuelve el pool, incluso si hubo un error o un return antes
            if connection.is_connected():
                connection.close()

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
                
                #return connection.lastrowid()

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
                #return connection.lastrowid()

        except mysql.connector.Error as err:
            # si hay fallo, se revierte la query ejecutada
            connection.rollback()
            raise Error(f"Error al insertar la  el ingrediente a la receta: {err}")

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
                    #return connection.lastrowid()

            except mysql.connector.Error as err:
                # si hay fallo, se revierte la query ejecutada
                connection.rollback()
                raise Error(f"Error al insertar la instruccion a la receta: {err}")

            finally:
                # devuelve el pool, incluso si hubo un error o un return antes
                if connection.is_connected():
                    connection.close()

    '''funciones de actualizacion'''

    def actualizar_receta(self,receta:Receta):
        '''Actualiza el registro de una receta segun su numero'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                        UPDATE receta
                        SET nombre = %s, numPorciones = %s
                        WHERE num = %s;
                        '''
                valores = (
                    receta.nombre,
                    receta.num_porciones,
                    receta.num
                )
                cursor.execute(sql,valores)
                connection.commit()
                
        except mysql.connector.Error as err:
            connection.rollback()
            # manejo de errores de base de datos
            raise Error(f"Error al actualizar la receta: {err}")

        finally:
            # devuelve el pool, incluso si hubo un error o un return antes
            if connection.is_connected():
                connection.close()

    def actualizar_ingrediente_receta(self, num_receta:int, ingrediente_receta:IngredientesReceta):
        '''Actualiza una lista de ingredientes de una receta. (objeto IngredienteReceta)'''
        connection = self.db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                        UPDATE lista_ingredientes li
                        INNER JOIN ingrediente ing ON li.ingrediente = ing.num
                        INNER JOIN receta r ON li.receta = r.num
                        SET li.cantidad = %s
                        WHERE r.num = %s;'''
                valores = (
                    ingrediente_receta.cantidad,
                    num_receta
                )
                cursor.execute(sql,valores)
                connection.commit()
                return cursor.rowcount > 0
        except mysql.connector.Error as err:
            connection.rollback()
            # manejo de errores de base de datos
            raise Error(f"DAOL Error al insertar al actualizar ingrediente de la receta: {err}")
        finally:
            # devuelve el pool, incluso si hubo un error o un return antes
            if connection.is_connected():
                connection.close()

    def actualizar_instruccion_receta(self, num_receta:int,num_instruccion:int, instruccion_nueva:str):
            '''Actualiza la lista de instrucciones de una receta.'''
            connection = self.db.get_connection()
            try:
                with connection.cursor(dictionary=True) as cursor:
                    sql = '''
                            UPDATE instrucciones ins
                            INNER JOIN receta r ON ins.receta = r.num
                            SET ins.instruccion = %s
                            WHERE r.num = %s AND ins.num = %s;'''
                    valores = (
                        instruccion_nueva,
                        num_receta,
                        num_instruccion,
                    )
                    cursor.execute(sql,valores)
                    connection.commit()
                    #devuele el numero de filas que se actualizaron
                    return cursor.rowcount > 0

            except mysql.connector.Error as err:
                connection.rollback()
                # manejo de errores de base de datos
                raise Error(f"Error al actualizar instruccion de la receta: {err}")
            finally:
                # devuelve el pool, incluso si hubo un error o un return antes
                if connection.is_connected():
                    connection.close()


    ''' FUNCIONES DE BORRADO '''

    def borrar_receta(self, num_receta:int):
        '''solo usar si es necesario. Solo si es una receta que necesita forzosamente ser eliminada.'''
        connection = self.db.get_connection()

        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                        DELETE FROM lista_ingredientes WHERE receta = %s;
                        DELETE FROM instrucciones WHERE receta = %s;
                        UPDATE platillo 
                        SET receta = NULL WHERE receta = %s;
                        DELETE FROM receta WHERE num = %s;
                        '''
                cursor.execute(sql,(num_receta,))
                connection.commit()
                # devuele el numero de filas que se actualizaron
                return cursor.rowcount > 0
        except mysql.connector.Error as err:
            connection.rollback()
            raise Error(f"DAO: Error al tratar de eliminar la receta.: {err}")
        finally:
            if connection.is_connected():
                connection.close()


    def es_receta_de_ingrediente(self, num_receta:int):
        '''Valida que la receta no sea de un ingrediente.'''
        connection = self.db.get_connection()

        # validando que la receta no sea la receta de un ingrediente
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = '''
                        SELECT 
                        i.num Ingrediente
                        FROM ingrediente i
                        INNER JOIN receta r ON i.receta = r.num
                        WHERE r.num = %s'''
                cursor.execute(sql,(num_receta,))
                respuesta = cursor.fetchone()

                ''' si es True, significa que se encontro un valor, y por ende, 
                es receta de un ingrediente, asi que 
                ''' 
                if respuesta:
                    return True
                else:
                    return False

        except mysql.connector.Error as err:
            connection.rollback()
            # manejo de errores de base de datos
            raise Error(f"Error al validar receta: {err}")
        finally:
            if connection.is_connected():
                connection.close()
