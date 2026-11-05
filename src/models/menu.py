from typing import List, Optional
from datetime import date, datetime
#imports de los modelos
from models.platillo import Platillo

class Menu:
    #Modelo principal
    def __init__(self,
                num:int,
                nombre:str,
                cantidad_platillos:int = 0,
                fecha_inicial: Optional[str|date] = None,
                fecha_final: Optional[str|date] = None
                ):
        self._num = num
        self._nombre = nombre
        self._cantidad_platillos = cantidad_platillos 
        self._fecha_inicial = fecha_inicial
        self._fecha_final = fecha_final

        # Aquí estara la lista de sub-modelos (tabla intermedia)
        self._detalles:List[DetalleMenu] = [] #en una lista se guardaran los objetos de la clase DetalleMenu

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
    def cantidad_platillos(self) -> int:
        return self._cantidad_platillos

    @cantidad_platillos.setter
    def cantidad_platillos(self, value):
        self._cantidad_platillos = value

    @property
    def detalles(self) -> List[DetalleMenu]:
        return self._detalles

    @detalles.setter
    def detalles(self, value):
        self._detalles = value

    @property
    def fecha_inicial(self) -> str|date|None:
        return self._fecha_inicial

    @fecha_inicial.setter
    def fecha_inicial(self, value):
        self._nombre = value

    @property
    def fecha_final(self) -> str|date|None:
        return self._fecha_final

    @fecha_final.setter
    def fecha_final(self, value):
        self._nombre = value

    def agregar_platillo(self, platillo:Platillo, precio:float):
        """metodo agreagacion para instanciar y guardar el detalle del menu"""
        nuevo_detalle = DetalleMenu(platillo, precio)
        self._detalles.append(nuevo_detalle)


class DetalleMenu:
    #Sub-modelo para encapsular la tabla intermedia MENU_PLATILLO
    def __init__(self, platillo:Platillo, precio:float):
        self._platillo = platillo 
        self._precio = precio

    @property
    def platillo(self) -> Platillo:
        return self._platillo

    @property
    def precio(self) -> float:
        return self._precio