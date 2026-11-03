from typing import List, Optional
from datetime import datetime
#imports de los modelos
from models.menu import DetalleMenu
from models.platillo import Platillo

class Menu:
    #Modelo principal
    def __init__(self,
                num:int,
                nombre:str,
                cantidad_platillos:int = 0,
                fecha_inicial: Optional[str|datetime] = None, 
                fecha_final: Optional[str|datetime] = None
                ):
        self._num = num
        self._nombre = nombre
        self._cantidad_platillos = cantidad_platillos 
        self._fecha_inicial = fecha_inicial
        self._fecha_final = fecha_final

        # Aquí estara la lista de sub-modelos (tabla intermedia)
        self._detalles:List[DetalleMenu] = [] #en una lista se guardaran los objetos de la clase DetalleMenu

    @property
    def num(self):
        return self._num

    @num.setter
    def num(self, value):
        self._num = value

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, value):
        self._nombre = value

    @property
    def cantidad_platillos(self):
        return self._cantidad_platillos

    @cantidad_platillos.setter
    def cantidad_platillos(self, value):
        self._cantidad_platillos = value

    @property
    def detalles(self):
        return self._detalles

    @property
    def fecha_inicial(self):
        return self._fecha_inicial

    @fecha_inicial.setter
    def fecha_inicial(self, value):
        self._nombre = value

    @property
    def fecha_final(self):
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
        self._platillo = platillo # Objeto Platillo
        self._precio = precio

    @property
    def platillo(self):
        return self._platillo

    @property
    def precio(self):
        return self._precio


'''
from Platillo import Platillo
menu = Menu(1,'navidad',4)
pizza_p = Platillo(1,'Pizza de Peperonni')

menu.agregar_platillo(pizza_p,400,'10-12-2026','26-12-2026')

#Aqui se imprimen los detalles de los platillos del Menu
for detalleM in menu.detalles:
    print(detalleM.platillo.nombre)
    print(detalleM.precio)
    print(detalleM.fecha_inicial)
    print(detalleM.fecha_final)'''

