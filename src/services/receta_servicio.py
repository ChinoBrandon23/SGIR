from models.receta import Receta, IngredientesReceta
from models.ingrediente import Ingrediente
from daos.receta_dao import RecetaDAO

import mysql.connector
from mysql.connector import Error


from typing import List

class RecetaServicio:
    def __init__(self, receta_dao:RecetaDAO):
        self._receta_dao = receta_dao

    def obtener_recetas(self):
        '''Obtiene todas las receteas del sistema.'''
        lista_recetas: List[Receta] = []
        lista_recetas = self._receta_dao.obtener_recetas()  # pyright: ignore[reportAssignmentType]
        for receta in lista_recetas:
            receta.instrucciones = self._receta_dao.obtener_instrucion_receta_por_id(receta.num)
            for fila in self._receta_dao.obtener_ingredientes_receta(receta.num):  # pyright: ignore[reportOptionalIterable]
                receta.agregarIngrediente(
                    ingrediente=Ingrediente(fila['NumIngre'],fila['IngreNombre'],insumo=None,receta=None),
                    cantidad=fila['Cantidad'],
                    unidad_medida=fila['uniMedida']
                    )
        return lista_recetas

    def obtener_receta_por_id(self, num_receta:int):
        '''Obtener una receta por su numero.'''
        # evalua que receta exista
        try:
            self._receta_dao.obtener_receta_por_id(num_receta)
        except IndexError as indexError:
            raise IndexError(f'Servicio: {indexError}')  
        
        receta:Receta = self._receta_dao.obtener_receta_por_id(num_receta)
        receta.instrucciones = self._receta_dao.obtener_instrucion_receta_por_id(receta.num)
        for fila in self._receta_dao.obtener_ingredientes_receta(receta.num):  # pyright: ignore[reportOptionalIterable]
            receta.agregarIngrediente(
                ingrediente=Ingrediente(fila['NumIngre'],fila['IngreNombre'],insumo=None,receta=None),
                cantidad=fila['Cantidad'],
                unidad_medida=fila['uniMedida']
                )
        return receta

    def obtener_ingrediente_por_id(self, num_ing:int):
        try:
            return self._receta_dao.obtener_ingrediente_por_id(num_ing)
        except IndexError as ie:
            raise IndexError(f'Servicio: No existe el ingrediente. {ie}')

    def obtener_ingrediente_por_nombre(self, nombre_ing:str):
        try:
            return self._receta_dao.obtener_ingrediente_por_nombre(nombre_ing)
        except IndexError as ie:
            raise IndexError(f'Servicio: No existe el ingrediente. {ie}')
    
    def crear_receta(self, receta:Receta):
        '''Crear una receta.'''

        # evalua que la receta no exista
        if self._receta_dao.obtener_receta_por_id(receta.num):
            # la receta existe y hay que impedir creacion
            raise ValueError('Servicio: El numero de receta es invalido. La receta ya existe.')
        
        self._receta_dao.crear_receta_vacia(receta=receta)

        if receta.lista_ingredientes:
            # llama funcion del dao para agregar ingredientes de la receta
            for lista_ingrediente in receta.lista_ingredientes:
                self._receta_dao.agregar_ingrediente_a_receta(receta.num,lista_ingrediente)
            
        if receta.instrucciones:
            # llama funcion del dao para agregar instrucciones a la receta
            for num,instruccion in receta.instrucciones.items():
                self._receta_dao.agregar_instruccion_a_receta(receta.num,num,instruccion)

    def actualizar_receta(self,receta:Receta):

        '''actualiza una receta completa, incluyendo su lista de ingredientes e instrucciones.'''

        # evalua que la receta exista
        try:
            self._receta_dao.obtener_receta_por_id(receta.num)
        except IndexError as indexError:
            raise IndexError(f'Servicio: {indexError}')  

        # actualiza recetas vacias
        self._receta_dao.actualizar_receta(receta=receta)


        # obtiene lista ingredientes de la receta en la BD, para comparar
        lista_ing_receta_bd = self._receta_dao.obtener_ingredientes_receta(receta.num)
        
        # si no hay ningun ingrediente en la receta en la BD, entonces ninguno existe en la BD y hay que crearlos
        if not lista_ing_receta_bd:
            # agrega todos los ingredientes a la receta
            for li in receta.lista_ingredientes:
                self._receta_dao.agregar_ingrediente_a_receta(receta.num,li)
        else:
            for lista_ingrediente in receta.lista_ingredientes:
                # validando que el ingrediente exista en la BD, no se puede agregar un ingrediente que no existe
                if not self.obtener_ingrediente_por_id(lista_ingrediente.ingrediente.num):
                    continue # si no existe entonces pasamos a la siguiente iteracion
                for registro in lista_ing_receta_bd:
                    # para poder actualizar, primero se evalua si el ingrediente existe en la lista de ing de la receta en la BD
                    if lista_ingrediente.ingrediente.num == int(registro['NumIngre']):
                        
                        self._receta_dao.actualizar_ingrediente_receta(
                            num_receta=receta.num,
                            ingrediente_receta=lista_ingrediente
                        )
                    #else:
                    #    print(f'aqui toy -------{lista_ingrediente.ingrediente.num}--{registro['NumIngre']}')
                    #    ''' si el ingrediente no existe en la receta actual, entonces, hay que agregarla'''
                    #    self._receta_dao.agregar_ingrediente_a_receta(receta.num,lista_ingrediente)

        # obtiene todas instrucciones de la receta en la BD para comparar 
        instrucciones_actuales:dict[int,str] = self._receta_dao.obtener_instrucion_receta_por_id(receta.num)

        for num,instruccion in receta.instrucciones.items():
            # evalua que la instruccion exista
            if not instrucciones_actuales.get(num) == None:
                self._receta_dao.actualizar_instruccion_receta(
                    num_receta=receta.num,
                    num_instruccion=num,
                    instruccion_nueva=instruccion
                    )
            else:
                '''si la instruccion no existe en el diccionario de instruciones...
                    de la receta actual, entonces, hay que crearla'''
                self._receta_dao.agregar_instruccion_a_receta(receta.num,num,instruccion)

    def borrar_receta(self, num_receta:int):
        '''Borra la receta por numero. Solo usar si es estrictamente necesario.'''
        # valida que la receta exista en la BD
        try:
            self._receta_dao.obtener_receta_por_id(num_receta)
        except IndexError as ie:
            raise IndexError(f'Servicio: La receta no existe. {ie}\n')

        # valida que la receta no sea la receta de un ingrediente
        if self._receta_dao.es_receta_de_ingrediente(num_receta):
            raise ValueError('Servicio: No se puede eliminar una receta, la cual es receta de un ingrediente.\n')

        # si se pasan las validaciones, se realiza la eliminacion.
        try:
            # retorna la cantidad de filas afectadas. 
            return self._receta_dao.borrar_receta(num_receta)
        except mysql.connector.Error as e:
            raise ValueError(f'Servicio: {e}\n')

