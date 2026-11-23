import time
from datetime import datetime

from daos.insumo_dao import InsumoDAO
from daos.platillos_dao import PlatillosDAO
from daos.receta_dao import RecetaDAO
from daos.venta_dao import VentaDAO
from models.ingrediente import Ingrediente
from models.platillo import Platillo
from models.venta import Venta

import mysql.connector


class VentaServicio:
    def __init__(self, venta_dao:VentaDAO, insumo_dao:InsumoDAO, receta_dao:RecetaDAO, platillo_dao:PlatillosDAO):
        self._venta_dao = venta_dao
        self._insumo_dao = insumo_dao
        self._receta_dao = receta_dao
        self._platillo_dao = platillo_dao

    def obtener_ventas(self) -> list[Venta]:
        try:
            lista_ventas = self._venta_dao.obtener_ventas()

            for venta in lista_ventas:
                for consumo in venta.detalles:
                    filas = self._receta_dao.obtener_ingredientes_receta(consumo.platillo.receta.num)

                    for fila in filas:
                        consumo.platillo.receta.agregarIngrediente(
                            ingrediente=Ingrediente(fila['NumIngre'], fila['IngreNombre'],
                                                    insumo=self._insumo_dao.obtener_insumo_por_num(fila['NumInsumo']) if fila['NumInsumo'] else None,
                                                    receta=self._receta_dao.obtener_receta_por_id(fila['NumRecetaIngrediente']) if fila['NumRecetaIngrediente'] else None),
                                                    cantidad=fila['Cantidad'],
                                                    unidad_medida=fila['uniMedida'])
            return lista_ventas
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al obtener ventas: {err}\n')

    def obtener_venta_por_num(self) -> list[Venta]:
        try:
            lista_ventas = self._venta_dao.obtener_ventas()

            for venta in lista_ventas:
                for consumo in venta.detalles:
                    filas = self._receta_dao.obtener_ingredientes_receta(consumo.platillo.receta.num)

                    for fila in filas:
                        consumo.platillo.receta.agregarIngrediente(
                            ingrediente=Ingrediente(fila['NumIngre'], fila['IngreNombre'],
                                                    insumo=self._insumo_dao.obtener_insumo_por_num(fila['NumInsumo']) if fila['NumInsumo'] else None,
                                                    receta=self._receta_dao.obtener_receta_por_id(fila['NumRecetaIngrediente']) if fila['NumRecetaIngrediente'] else None),
                                                    cantidad=fila['Cantidad'],
                                                    unidad_medida=fila['uniMedida'])
            return lista_ventas
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al obtener ventas: {err}\n')

    def obtener_ventas_por_rango_fecha(self, fecha_inicial, fecha_final) -> list[Venta]:
        try:
            fecha_inicial_datetime = datetime.strptime(fecha_inicial, '%d-%m-%Y')
            fecha_inicial = datetime.strftime(fecha_inicial_datetime, '%Y-%m-%d')

            fecha_final_datetime = datetime.strptime(fecha_final, '%d-%m-%Y')
            fecha_final = datetime.strftime(fecha_final_datetime, '%Y-%m-%d')

            lista_ventas = self._venta_dao.obtener_ventas_por_rango_fecha(fecha_inicial, fecha_final)

            for venta in lista_ventas:
                for consumo in venta.detalles:
                    filas = self._receta_dao.obtener_ingredientes_receta(consumo.platillo.receta.num)

                    for fila in filas:
                        consumo.platillo.receta.agregarIngrediente(
                            ingrediente=Ingrediente(fila['NumIngre'], fila['IngreNombre'],
                                                    insumo=self._insumo_dao.obtener_insumo_por_num(fila['NumInsumo']) if fila['NumInsumo'] else None,
                                                    receta=self._receta_dao.obtener_receta_por_id(fila['NumRecetaIngrediente']) if fila['NumRecetaIngrediente'] else None),
                                                    cantidad=fila['Cantidad'],
                                                    unidad_medida=fila['uniMedida'])
            return lista_ventas

        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al obtener venta: {err}\n')

    def obtener_platillos_conflicto_fecha(self, consumos_actuales:list[Platillo], fecha_venta) -> list[Platillo]:
        try:
            platillos_conflicto: list[Platillo] = []

            lista_platillos_disp = self.obtener_platillos_disponibles_por_fecha(fecha_venta)

            if lista_platillos_disp:
                lista_platillos_disp_nombres = [platillo.nombre for platillo in lista_platillos_disp]

                for consumo in consumos_actuales:
                    if consumo.platillo.nombre not in lista_platillos_disp_nombres:
                        platillos_conflicto.append(consumo.platillo)
                return platillos_conflicto
            else:
                return [cons.platillo for cons in consumos_actuales]

        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al obtener los platillos: {err}\n')

    def obtener_platillos_disponibles_por_fecha(self, fecha):
        try:
            venta_fecha_datetime = datetime.strptime(fecha, '%d-%m-%Y')
            fecha = datetime.strftime(venta_fecha_datetime, '%Y-%m-%d')

            lista_platillos = self._venta_dao.obtener_platillos_disponibles_por_fecha(fecha)

            if lista_platillos:
                for platillo in lista_platillos:
                    filas = self._receta_dao.obtener_ingredientes_receta(platillo.receta.num)
                    for fila in filas:
                        platillo.receta.agregarIngrediente(
                            ingrediente=Ingrediente(fila['NumIngre'], fila['IngreNombre'],
                                                    insumo=self._insumo_dao.obtener_insumo_por_num(fila['NumInsumo']) if fila[
                                                        'NumInsumo'] else None,
                                                    receta=self._receta_dao.obtener_receta_por_id(
                                                        fila['NumRecetaIngrediente']) if fila[
                                                        'NumRecetaIngrediente'] else None),
                            cantidad=fila['Cantidad'],
                            unidad_medida=fila['uniMedida'])
                return lista_platillos
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al obtener venta: {err}\n')

    def obtener_ultima_venta(self):
        # como las ventas no tienen nombre, esta función se creó para poder obtener una venta recién creada,
        # cuando el sistema no tiene el número de venta para buscarlo con él
        try:
            venta = self._venta_dao.obtener_ultima_venta_registrada()

            for consumo in venta.detalles:
                filas = self._receta_dao.obtener_ingredientes_receta(consumo.platillo.receta.num)

                for fila in filas:
                    consumo.platillo.receta.agregarIngrediente(
                        ingrediente=Ingrediente(fila['NumIngre'], fila['IngreNombre'],
                                                insumo=self._insumo_dao.obtener_insumo_por_num(fila['NumInsumo']) if
                                                fila['NumInsumo'] else None,
                                                receta=self._receta_dao.obtener_receta_por_id(
                                                    fila['NumRecetaIngrediente']) if fila[
                                                    'NumRecetaIngrediente'] else None),
                        cantidad=fila['Cantidad'],
                        unidad_medida=fila['uniMedida'])

            return venta
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al obtener venta: {err}\n')

    def obtener_precio_venta_platillo(self, fecha_venta, num_platillo) -> float:
        try:
            venta_fecha_datetime = datetime.strptime(fecha_venta, '%d-%m-%Y')
            fecha_venta = datetime.strftime(venta_fecha_datetime, '%Y-%m-%d')

            return self._venta_dao.obtener_precio_platillo_por_fecha(fecha_venta, num_platillo)
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al obtener venta: {err}\n')

    def registrar_venta(self, venta:Venta):
        try:
            venta_fecha_datetime = datetime.strptime(venta.fecha, '%d-%m-%Y')
            venta.fecha = datetime.strftime(venta_fecha_datetime, '%Y-%m-%d')
            self._venta_dao.crear_venta(venta)

            num_registro_venta = self.obtener_ultima_venta().num
            venta.num = num_registro_venta

            self._venta_dao.registrar_consumo(venta)
            self._venta_dao.descontar_consumo(venta)

            for consumo in venta.detalles:
                lista_ingredientes = consumo.platillo.receta.lista_ingredientes

                for ingredienteDetalle in lista_ingredientes:
                    # actualiza el stock de cada insumo de la venta
                    if ingredienteDetalle.ingrediente.insumo:
                        insumo_id = ingredienteDetalle.ingrediente.insumo
                        self._insumo_dao.actualizar_stock_insumo(insumo_id)
                    else:
                        # si el ingrediente es una receta, va a otro loop
                        for ing in ingredienteDetalle.ingrediente.receta.lista_ingredientes:
                            insumo_id = ing.ingrediente.insumo
                            self._insumo_dao.actualizar_stock_insumo(insumo_id)
        except mysql.connector.Error as err:
            raise ValueError(f'Servicio: Ocurrió un error al obtener ventas: {err}\n')