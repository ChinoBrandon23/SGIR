from datetime import date, datetime
from typing import List

import mysql.connector
from mysql.connector import Error

from daos.merma_dao import MermaDAO
from models.merma import Merma
from models.tipo_merma import TipoMerma


class MermaServicio:
    def __init__(self, merma_dao: MermaDAO):
        self._merma_dao = merma_dao

    def obtener_mermas(self) -> List[Merma]:
        try:
            return self._merma_dao.obtener_mermas()
        except mysql.connector.Error as err:
            raise Error(f"Servicio: Error al obtener las mermas: {err}")

    def obtener_merma_por_numero(self, num_merma: int) -> Merma | None:
        try:
            return self._merma_dao.obtener_merma_por_numero(num_merma)
        except mysql.connector.Error as err:
            raise Error(
                f"Servicio: Error al obtener la merma número {num_merma}: {err}"
            )

    def obtener_mermas_por_rango_fecha(
        self, fecha_inicial: str | date | datetime, fecha_final: str | date | datetime
    ) -> List[Merma]:
        fecha_inicial_iso = self._formatear_fecha(fecha_inicial)
        fecha_final_iso = self._formatear_fecha(fecha_final)
        if fecha_inicial_iso > fecha_final_iso:
            raise ValueError("La fecha inicial no puede ser posterior a la fecha final.")

        try:
            return self._merma_dao.obtener_mermas_por_rango_fecha(
                fecha_inicial_iso, fecha_final_iso
            )
        except mysql.connector.Error as err:
            raise Error(f"Servicio: Error al consultar mermas por fecha: {err}")

    def obtener_mermas_por_tipo(self, tipo_merma_clave: str) -> List[Merma]:
        try:
            return self._merma_dao.obtener_mermas_por_tipo(tipo_merma_clave)
        except mysql.connector.Error as err:
            raise Error(f"Servicio: Error al consultar mermas por tipo: {err}")

    def obtener_mermas_por_insumo(self, num_insumo: int) -> List[Merma]:
        try:
            return self._merma_dao.obtener_mermas_por_insumo(num_insumo)
        except mysql.connector.Error as err:
            raise Error(f"Servicio: Error al consultar mermas por insumo: {err}")

    def obtener_tipos_merma(self) -> List[TipoMerma]:
        try:
            return self._merma_dao.obtener_tipos_merma()
        except mysql.connector.Error as err:
            raise Error(f"Servicio: Error al obtener los tipos de merma: {err}")

    @staticmethod
    def _formatear_fecha(fecha: str | date | datetime) -> str:
        if isinstance(fecha, (date, datetime)):
            return fecha.strftime("%Y-%m-%d")

        fecha_limpia = fecha.strip()
        for formato in ("%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(fecha_limpia, formato).strftime("%Y-%m-%d")
            except ValueError:
                continue
        raise ValueError(
            f"Formato de fecha no válido: {fecha!r}. Use DD-MM-AAAA o AAAA-MM-DD."
        )