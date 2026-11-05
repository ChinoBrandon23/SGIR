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
