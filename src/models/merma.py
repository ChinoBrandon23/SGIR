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
    def num(self):
        return self._num

    @num.setter
    def num(self, value):
        self._num = value

    @property
    def descripcion(self):
        return self._descripcion

    @descripcion.setter
    def descripcion(self, value):
        self._descripcion = value


    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, value):
        self._fecha = value

    @property
    def unidad_medida(self):
        return self._unidad_medida

    @unidad_medida.setter
    def unidad_medida(self, value):
        self._unidad_medida = value

    @property
    def cantidad(self):
        return self._cantidad

    @cantidad.setter
    def cantidad(self, value):
        self._cantidad = value

    @property
    def insumo(self):
        return self._insumo 

    @insumo.setter
    def insumo(self, value):
        self._insumo = value

    @property
    def tipo_merma(self):
        return self._tipo_merma 

    @tipo_merma.setter
    def tipo_merma(self, value):
        self._tipo_merma = value



'''

from Insumo import Insumo
from Marca import Marca
from TipoInsumo import TipoInsumo
from Ingrediente import Ingrediente
from TipoMerma import TipoMerma

#ejemplo uso
tomate_fisico = Insumo(1, "Tomate Verde", 
    fecha_compra="2023-01-01", fecha_caducidad="2023-01-10", precio_unitario=10.0, 
    umbral=5, stock=10, unidad_medida="kg", tipo_insumo=TipoInsumo(1, "Vegetal"), 
    marca=Marca(1, "Marca A"))
tomate_ingrediente = Ingrediente(1, "Tomate Verde", insumo=tomate_fisico)

merma1 = Merma(1, "Merma de tomate por mal estado", "2026-10-26", "kg", 2, insumo=tomate_ingrediente.insumo, tipo_merma=TipoMerma(1, "CADUCIDAD"))

print(f"Se registro una merma de {merma1.cantidad} {merma1.unidad_medida} de '{merma1.insumo.nombre}' debido a '{merma1.tipo_merma.nombre}' el dia {merma1.fecha}.")

'''