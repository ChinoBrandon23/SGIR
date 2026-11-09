from typing import List, Optional
from datetime import date
#imports de modelos
from models.platillo import Platillo

class Venta:
    def __init__(self,
                num:int,
                fecha: Optional[str|date],
                numero_comensales:int,
                monto_total:float = 0.0):
        self._num = num
        self._fecha = fecha
        self._numero_comensales = numero_comensales
        self._monto_total = monto_total
        # Aqui esta la lista de objetos Consumo
        self._detalles: List[Consumo] = []

    @property
    def num(self):
        return self._num

    @num.setter
    def num(self, valor):
        self._num = valor

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, fecha):
        self._fecha = fecha

    @property
    def numero_comensales(self):
        return self._numero_comensales

    @numero_comensales.setter
    def numero_comensales(self, num):
        self._numero_comensales = num

    @property
    def monto_total(self):
        return self._monto_total

    @monto_total.setter
    def monto_total(self, monto):
        self._monto_total = monto

    @property
    def detalles(self):
        return self._detalles

    @detalles.setter
    def detalles(self, value):
        self._detalles = value

    def agregar_consumo(self, platillo:Platillo, importe:float, cantidad_platillos:int):
        nuevo_detalle = Consumo(platillo, importe, cantidad_platillos)
        self._detalles.append(nuevo_detalle)


#sub-clase consumo (es una tabla intermedia en el DB)
class Consumo:
    def __init__(self, platillo:Platillo, importe:float, cantidad_platillos:int):
        #self._venta = venta
        self._platillo = platillo
        self._importe = importe
        self._cantidad_platillos = cantidad_platillos

    @property
    def platillo(self):
        return self._platillo

    @platillo.setter
    def platillo(self, platillo):
        self._platillo = platillo

    @property
    def importe(self):
        return self._importe

    @importe.setter
    def importe(self, cantidad):
        self._importe = cantidad

    @property
    def cantidad_platillos(self):
        return self._cantidad_platillos

    @cantidad_platillos.setter
    def cantidad_platillos(self, value):
        self._cantidad_platillos = value

        
'''

#EJEMPLO TEMPORAL DE USO DE LA CLASE VENTA Y CONSUMO
from Platillo import Platillo
from Menu import DetalleMenu
from Menu import Menu
from Platillo import Platillo

#creando menu y platillos de ejemplo
menu = Menu(1,'navidad',4)
pizza_p = Platillo(1,'Pizza de Peperonni',"Categoria 1", "Receta 1")
platillo2 = Platillo(2, "Platillo 1", "Categoria 2", "Receta 2")
platillo3 = Platillo(3, "Platillo 2", "Categoria 3", "Receta 3")

menu.agregar_platillo(pizza_p,400,'10-12-2026','26-12-2026')
menu.agregar_platillo(platillo2,100,'10-12-2026','26-12-2026')
menu.agregar_platillo(platillo3,150,'10-12-2026','26-12-2026')



precio_pizza = 0
precio_platillo2 = 0
precio_platillo3 = 0
cantidad_pizza = 2
cantidad_platillo2 = 1
cantidad_platillo3 = 1

for detalle in menu.detalles:
    if detalle.platillo.num == pizza_p.num:
        precio_pizza = detalle.precio
        break   
for detalle in menu.detalles:
    if detalle.platillo.num == platillo2.num:
        precio_platillo2 = detalle.precio
        break  
for detalle in menu.detalles:
    if detalle.platillo.num == platillo3.num:
        precio_platillo3 = detalle.precio
        break   


#iniciando una venta de ejemplo
venta = Venta(1, "2023-07-15", 4, 0)

#agregando consumos a venta

venta.agregar_consumo(pizza_p, precio_pizza*cantidad_pizza, 2)
venta.agregar_consumo(platillo2, precio_platillo2*cantidad_platillo2, 1)
venta.agregar_consumo(platillo3, precio_platillo3*cantidad_platillo3, 1)

for consum in venta.detalles:
    venta.monto_total += consum.importe

venta.monto_total = venta.detalles[0].importe + venta.detalles[1].importe + venta.detalles[2].importe

print("Monto:", venta.monto_total) 


'''