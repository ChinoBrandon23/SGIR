from typing import List, Optional
from datetime import datetime, date

#model imports
from models.insumo import Insumo
from models.proveedor import Proveedor
from src.models.compra import DetalleCompra

class Compra:
    def __init__(self,
                num:int,
                fecha_creacion: Optional[str|date],
                total_bruto:float = 0.0,
                proveedor: Optional[Proveedor] = None
                ):
        self._num = num
        self._fecha_creacion = fecha_creacion
        self._total_bruto = total_bruto
        self._proveedor = proveedor

        #Lista para almacenar los detalles de la orden de compra
        self._lista_compras: List[DetalleCompra] = []  

    @property
    def num(self) -> int:
        return self._num

    @num.setter
    def num(self, value):
        self._num = value

    @property
    def fecha_creacion(self) -> str|date|None:
        return self._fecha_creacion

    @fecha_creacion.setter
    def fecha_creacion(self, value):
        self._fecha_creacion = value

    @property
    def total_bruto(self) -> float:
        return self._total_bruto

    @total_bruto.setter
    def total_bruto(self, value):
        self._total_bruto = value

    @property
    def proveedor(self) -> Proveedor|None:
        return self._proveedor

    @proveedor.setter
    def proveedor(self, value):
        self._proveedor = value

    def agregar_insumo_compra(
                self,
                insumo:Insumo,
                cantidad:float, 
                unidad_medida:str,
                importe:float,
                monto_unitario:float,
                fecha_caducidad: Optional[date|str],
                fecha_compra: Optional[date|str],
                ):
        #metodo de agregacion para  guardar el detalle de la orden de compra, es decir, una nueva compra de insumo
        nueva_compra = DetalleCompra(insumo,
                                    cantidad, 
                                    unidad_medida,
                                    importe,
                                    monto_unitario,
                                    fecha_caducidad,
                                    fecha_compra
                                    )
        self._lista_compras.append(nueva_compra)

#Es la talba Lista_Compra
class DetalleCompra:
    def __init__(self,
                insumo:Insumo,
                cantidad:float,
                unidad_medida:str,
                importe:float = 0.0,
                monto_unitario:float=0.0,
                fecha_caducidad: Optional[str|date] = None,
                fecha_compra: Optional[str|date] = None
                ):
        self._insumo = insumo
        self._cantidad = cantidad
        self._unidad_medida = unidad_medida
        self._importe = importe
        self._monto_unitario = monto_unitario  
        self._fecha_compra = fecha_compra  
        self._fecha_caducidad = fecha_caducidad


    @property
    def insumo(self) -> Insumo:
        return self._insumo

    @insumo.setter
    def insumo(self, value):
        self._insumo = value

    @property
    def cantidad(self) -> float:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, value):
        self._cantidad = value

    @property
    def unidad_medida(self) -> str:
        return self._unidad_medida

    @unidad_medida.setter
    def unidad_medida(self, value):
        self._unidad_medida = value

    @property
    def importe(self) -> float:
        return self._importe

    @importe.setter
    def importe(self, value):
        self._importe = value

    @property
    def fecha_compra(self) -> str|date|None:
        return self._fecha_compra

    @fecha_compra.setter
    def fecha_compra(self, value):
        self._fecha_compra = value

    @property
    def fecha_caducidad(self) -> str|date|None:
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

