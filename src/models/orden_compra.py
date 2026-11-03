from typing import List, Optional
from datetime import datetime

#model imports
from models.insumo import Insumo
from models.estado_orden import EstadoOrden
from models.proveedor import Proveedor
from models.orden_compra import DetalleCompra

class OrdenCompra:
    def __init__(self,
                num:int,
                fecha_creacion: Optional[str|datetime],
                fecha_cierre: Optional[str|datetime],
                total_bruto:float = 0.0,
                estado_orden: Optional[EstadoOrden] = None,
                proveedor: Optional[Proveedor] = None
                ):
        self._num = num
        self._fecha_creacion = fecha_creacion
        self._fecha_cierre = fecha_cierre
        self._total_bruto = total_bruto
        self._estado_orden = estado_orden
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
    def fecha_creacion(self) -> str|datetime|None:
        return self._fecha_creacion

    @fecha_creacion.setter
    def fecha_creacion(self, value):
        self._fecha_creacion = value

    @property
    def fecha_cierre(self) -> str|datetime|None:
        return self._fecha_cierre

    @fecha_cierre.setter
    def fecha_cierre(self, value):
        self._fecha_cierre = value

    @property
    def total_bruto(self) -> float:
        return self._total_bruto

    @total_bruto.setter
    def total_bruto(self, value):
        self._total_bruto = value

    @property
    def estado_orden(self) -> EstadoOrden|None:
        return self._estado_orden

    @estado_orden.setter
    def estado_orden(self, value):
        self._estado_orden = value

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
                importe:float = 0.0
                ):
        #metodo de agregacion para  guardar el detalle de la orden de compra, es decir, una nueva compra de insumo
        nueva_compra = DetalleCompra(insumo,cantidad, unidad_medida, importe)
        self._lista_compras.append(nueva_compra)

#Es la talba Lista_Compra
class DetalleCompra:
    def __init__(self,
                insumo:Insumo,
                cantidad:float,
                unidad_medida:str,
                importe:float = 0.0
                ):
        self._insumo = insumo
        self._cantidad = cantidad
        self._unidad_medida = unidad_medida
        self._importe = importe

    @property
    def num(self) -> int:
        return self._num

    @num.setter
    def num(self, value):
        self._num = value

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

'''

# EJEPLO DE USO
from Insumo import Insumo
from TipoInsumo import TipoInsumo
from Marca import Marca

tomate = Insumo(1, "Tomate Verde", fecha_compra="2023-10-01", fecha_caducidad="2023-10-15", precio_unitario=2.5, umbral=5, stock=10, unidad_medida="kg", tipo_insumo=TipoInsumo(1, "Vegetal"), marca=Marca(1, "Marca A"))
orden1 = OrdenCompra(1, "2026-10-25", "2026-10-26", total_bruto=0, estado_orden="TERMINADO", proveedor="Walmart")

orden1.agregar_insumo_compra("Tomate Verde", 10, "kg", 100.0)
orden1.agregar_insumo_compra("Cebolla", 5, "kg", 50.0)
orden1.agregar_insumo_compra("Lechuga", 3, "kg", 30.0)

orden1.total_bruto = sum(detalle.importe for detalle in orden1._lista_compras)
print(f"Orden de Compra #{orden1.num} con proveedor '{orden1.proveedor}' tiene un total bruto de {orden1.total_bruto}")

stock_antes = tomate.stock
# abastecer el insumo ejemplo
tomate.stock += orden1._lista_compras[0].cantidad  # Se agregan 10 kg de tomate al stock
print(f"El stock de '{tomate.nombre}' ahora es de {tomate.stock} {tomate.unidad_medida}. (antes: {stock_antes} {tomate.unidad_medida})")

'''