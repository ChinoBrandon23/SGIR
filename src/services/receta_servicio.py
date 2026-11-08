from models.receta import Receta

from daos.receta_dao import RecetaDAO

class RecetaServicio:
    def __init__(self, receta_dao:RecetaDAO):
        self._receta_dao = receta_dao

    def obtener_recetas(self):
        return self._receta_dao.obtener_recetas()
        '''queda pendiente formar el objeto aqui y no en el dao, similar a crear_receta()'''

    def crear_receta(self, receta:Receta):
        '''Crear una receta.'''
        self._receta_dao.crear_receta_vacia(receta=receta)

        if receta.lista_ingredientes:
            # llama funcion del dao para agregar ingredientes de la receta
            for lista_ingrediente in receta.lista_ingredientes:
                self._receta_dao.agregar_ingrediente_a_receta(receta.num,lista_ingrediente)
            
        if receta.lista_ingredientes:
            # llama funcion del dao para agregar instrucciones a la receta
            for num,instruccion in receta.instrucciones.items():
                self._receta_dao.agregar_instruccion_a_receta(receta.num,num,instruccion)

