from typing import Optional
#model imports
from models.categoria import Categoria
from models.receta import Receta

class Platillo:
    def __init__(
            self,
            num:int, 
            nombre:str, 
            categoria: Optional[Categoria] = None, 
            receta: Optional[Receta] = None
        ):
    
        self._num = num
        self._nombre = nombre
        #fk's
        self._categoria = categoria
        self._receta = receta

    @property
    def num(self) -> int:
        return self._num

    @num.setter
    def num(self, value):
        self._num = value

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, value):
        self._nombre = value

    @property
    def categoria(self) -> Categoria|None:
        return self._categoria

    @categoria.setter
    def categoria(self, value):
        self._categoria = value
    
    @property
    def receta(self) -> Receta|None:
        return self._receta    

    @receta.setter
    def receta(self, value):
        self._receta = value   
