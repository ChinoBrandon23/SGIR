from __future__ import annotations  # Para evitar referencias circulares
from typing import TYPE_CHECKING
from typing import List
if TYPE_CHECKING:
    #model imports
    from models.ingrediente import Ingrediente
    from models.receta import IngredientesReceta

class Receta:
    def __init__(self, num:int, nombre:str, num_porciones:int, instrucciones:dict[int,str]):
        self._num = num
        self._nombre = nombre
        self._num_porciones = num_porciones

        #diccionario para las instrucciones {numeroIntruccion:"instruccion"}
        self._instrucciones = instrucciones

        #lista para almacenar los ingredientes de la receta
        self._lista_ingredientes: List[IngredientesReceta] = []  

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
    def num_porciones(self) -> int:
        return self._num_porciones

    @num_porciones.setter
    def num_porciones(self, value):
        self._num_porciones = value

    @property
    def instrucciones(self) -> dict[int,str]:
        return self._instrucciones

    @instrucciones.setter
    def instrucciones(self, value):
        self._instrucciones = value

    @property
    def lista_ingredientes(self) -> List[IngredientesReceta]:
        return self._lista_ingredientes 

    @lista_ingredientes.setter
    def lista_ingredientes(self, value):
        self._lista_ingredientes = value

    #metodo para agregar ingrediente a la receta, usando el submodelo IngredientesReceta
    def agregarIngrediente(self, ingrediente:Ingrediente, cantidad:float, unidad_medida:str):
        nuevo_ingrediente = IngredientesReceta(ingrediente, cantidad, unidad_medida)
        self._lista_ingredientes.append(nuevo_ingrediente)



#Sub-clase para encapsular los ingredientes de la receta, puede llamarse tambien DetalleReceta.
class IngredientesReceta:
    def __init__(self, ingrediente:Ingrediente, cantidad:float, unidad_medida:str):
        self._ingrediente = ingrediente 
        self._cantidad = cantidad
        self._unidad_medida = unidad_medida

    @property
    def ingrediente(self) -> Ingrediente:
        return self._ingrediente

    @property
    def cantidad(self) -> float:
        return self._cantidad

    @property
    def unidad_medida(self) -> str:
        return self._unidad_medida



'''

from Ingrediente import Ingrediente
from Insumo import Insumo
#EJEMPLO DE USO
receta1 = Receta(1, "Receta de Pizza", 4, {1: "Mezclar los ingredientes", 2: "Amasar la masa", 3: "Hornear la pizza"}) 

for num, instruccion in receta1.instrucciones.items():
    print(f"Instrucción {num}: {instruccion}")

Ingrediente1 = Ingrediente(1, "Harina",Insumo(1, "Harina de Trigo", fecha_compra="2026-01-01", fecha_caducidad="2026-01-01", precio_unitario=2.0, umbral=5, stock=10, unidad_medida="kg", tipo_insumo=None, marca=None))
receta1.agregarIngrediente(Ingrediente1, 2, "taza")
receta1.agregarIngrediente(Ingrediente(2, "Levadura", Insumo(2, "Levadura", fecha_compra="2026-01-01", fecha_caducidad="2026-01-01", precio_unitario=1.0, umbral=5, stock=10, unidad_medida="kg", tipo_insumo=None, marca=None)), 1, "cucharada")

for ingrediente_receta in receta1._lista_ingredientes:
    print('')
    print('Ingrediente:', ingrediente_receta.ingrediente.nombre)
    print('Cantidad:', ingrediente_receta.cantidad)
    print('Unidad de Medida:', ingrediente_receta.unidad_medida)
'''