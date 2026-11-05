from typing import Optional
from datetime import datetime

#model imports
from models.insumo import Insumo
from models.tipo_merma import TipoMerma

class Merma:
    def __init__(self, 
                num:int,
                descripcion:str,
                fecha: Optional[str|datetime],
                unidad_medida:str,
                cantidad:float,
                insumo:Insumo,
                tipo_merma:TipoMerma
                ):
        self._num = num
        self._fecha = fecha
        self._descripcion = descripcion
        self._cantidad = cantidad
        self._unidad_medida = unidad_medida
        #fks
        self._insumo = insumo
        self._tipo_merma = tipo_merma

    @property
    def num(self) -> int:
        return self._num

    @num.setter
    def num(self, value):
        self._num = value

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @descripcion.setter
    def descripcion(self, value):
        self._descripcion = value


    @property
    def fecha(self) -> str|datetime|None:
        return self._fecha

    @fecha.setter
    def fecha(self, value):
        self._fecha = value

    @property
    def unidad_medida(self) -> str:
        return self._unidad_medida

    @unidad_medida.setter
    def unidad_medida(self, value):
        self._unidad_medida = value

    @property
    def cantidad(self) -> float:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, value):
        self._cantidad = value

    @property
    def insumo(self) -> Insumo:
        return self._insumo 

    @insumo.setter
    def insumo(self, value):
        self._insumo = value

    @property
    def tipo_merma(self) -> TipoMerma:
        return self._tipo_merma 

    @tipo_merma.setter
    def tipo_merma(self, value):
        self._tipo_merma = value
