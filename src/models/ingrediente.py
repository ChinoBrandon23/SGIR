from __future__ import annotations  # Para resolver referencias circulares
from typing import TYPE_CHECKING
from typing import Optional
#model imports
from models.insumo import Insumo

if TYPE_CHECKING:
    from models.receta import Receta


class Ingrediente:
    def __init__(self,
                num:int,
                nombre:str,
                insumo: Optional[Insumo] = None,
                receta: Optional[Receta] = None
                ):
        self._num = num
        self._nombre = nombre
        #fk
        self._insumo = insumo
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
    def insumo(self) -> Insumo|None:
        return self._insumo

    @insumo.setter
    def insumo(self, value):
        self._insumo = value

    @property
    def receta(self) -> Receta|None:
        return self._receta

    @receta.setter
    def receta(self, value):
        self._receta = value

'''
from Insumo import Insumo
from Marca import Marca
from TipoInsumo import TipoInsumo

#ejemplo uso

tomate_fisico = Insumo(1, "Tomate Verde", 
    fecha_compra="2023-01-01", fecha_caducidad="2023-01-10", precio_unitario=10.0, 
    umbral=5, stock=10, unidad_medida="kg", tipo_insumo=TipoInsumo(1, "Vegetal"), 
    marca=Marca(1, "Marca A"))
tomate_ingrediente = Ingrediente(1, "Tomate Verde", insumo=tomate_fisico)

cantidad_requeridad = 0.5  #0.5 kg de tomate
stock_actual = tomate_ingrediente.insumo.stock
nuevo_stock = stock_actual - cantidad_requeridad

print(f"Se uso {tomate_ingrediente.nombre} en la cocina.")
print(f"El stock de '{tomate_ingrediente.insumo.nombre}' bajó a {nuevo_stock}kg  de {stock_actual}kg.")
'''