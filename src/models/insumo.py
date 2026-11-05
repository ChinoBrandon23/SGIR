from typing import Optional
from datetime import datetime
#model imports
from models.tipo_insumo import TipoInsumo
from models.marca import Marca

class Insumo:
    def __init__(self, 
                num:int,
                nombre:str,
                umbral:float = 0,
                stock:float = 0,
                tipo_insumo: Optional[TipoInsumo] = None,
                marca: Optional[Marca] = None
                ):
        self._num = num
        self._nombre = nombre
        self._umbral = umbral 
        self._stock = stock

        #fk's
        self._tipo_insumo = tipo_insumo
        self._marca = marca

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
    def umbral(self) -> float:
        return self._umbral

    @umbral.setter
    def umbral(self, value):
        self._umbral = value

    @property
    def stock(self) -> float:
        return self._stock

    @stock.setter
    def stock(self, value):
        self._stock = value

    @property
    def tipo_insumo(self) -> TipoInsumo|None:
        return self._tipo_insumo

    @tipo_insumo.setter
    def tipo_insumo(self, value):
        self._tipo_insumo = value   

    @property
    def marca(self) -> Marca|None:
        return self._marca

    @marca.setter
    def marca(self, value):
        self._marca = value
