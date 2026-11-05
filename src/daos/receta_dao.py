from models.tipo_insumo import TipoInsumo
from models.marca import Marca
from models.insumo import Insumo
from models.ingrediente import Ingrediente
from models.receta import Receta

import mysql.connector

class RecetaDAO:    
    def __init__(self, db_manager):
        self.db = db_manager # clase que hace crea las conexiones

    def buscar_por_id(self, num_insumo:int):
        """Obtiene una receta por su id."""
        connection = self.db.get_connection()

        try:
            # 'with' cierra automáticamente el cursor al terminar de usarse
            with connection.cursor(dictionary=True) as cursor:
                sql = "SELECT r.num, r.nombre, r.numPorciones FROM receta AS r WHERE r.num = %s"
                cursor.execute(sql,num_insumo)
                result_set = cursor.fetchall()
                print(result_set)

        except mysql.connector.Error as err:
            # manejo de errores de base de datos
            print(f"Error al obtener insumos: {err}")
            return []

        finally:
            # devuelve el pool, incluso si hubo un error o un return antes
            if connection.is_connected():
                connection.close()

        #for receta in self._tabla_recetas:
        #    if receta.num == num_insumo:
        #        return receta
        #return False
    
    def buscar_por_nombre(self, nombre_insumo:str):
        #for receta in self._tabla_recetas:
        #    if receta.nombre == nombre_insumo:
        #        return receta
        #return False
        pass
        
    def obtener_todos(self):
        """Simula un SELECT * FROM receta"""
        #return self._tabla_recetas
        pass

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

