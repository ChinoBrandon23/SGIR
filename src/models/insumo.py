from typing import Optional
from datetime import datetime
#model imports
from models.tipo_insumo import TipoInsumo
from models.marca import Marca

class Insumo:
    def __init__(self, 
                num:int,
                nombre:str,
                unidad_medida:str,
                fecha_caducidad: Optional[str|datetime] = None,
                fecha_compra: Optional[str|datetime] = None,
                precio_unitario:float=0.0,
                umbral:float = 0,
                stock:float = 0,
                tipo_insumo: Optional[TipoInsumo] = None,
                marca: Optional[Marca] = None
                ):
        self._num = num
        self._nombre = nombre
        self._fecha_compra = fecha_compra  
        self._fecha_caducidad = fecha_caducidad
        self._unidad_medida = unidad_medida
        self._precio_unitario = precio_unitario  
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
    def fecha_compra(self) -> str|datetime|None:
        return self._fecha_compra

    @fecha_compra.setter
    def fecha_compra(self, value):
        self._fecha_compra = value

    @property
    def fecha_caducidad(self) -> str|datetime|None:
        return self._fecha_caducidad

    @fecha_caducidad.setter
    def fecha_caducidad(self, value):
        self._fecha_caducidad = value

    @property
    def precio_unitario(self) -> float:
        return self._precio_unitario

    @precio_unitario.setter
    def precio_unitario(self, value):
        self._precio_unitario = value

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
    def unidad_medida(self) -> str:
        return self._unidad_medida

    @unidad_medida.setter
    def unidad_medida(self, value):
        self._unidad_medida = value

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

    

'''
from TipoInsumo import TipoInsumo
from Marca import Marca

tomate = Insumo(1, "Tomate Verde", fecha_compra="2023-10-01", fecha_caducidad="2023-10-15", precio_unitario=2.5, umbral=5, stock=10, unidad_medida="kg", tipo_insumo=TipoInsumo(1, "Vegetal"), marca=Marca(1, "Marca A"))
print(tomate.stock)

''' 
