import random
from datetime import date, datetime, timedelta
from typing import List

import mysql.connector
from utils.conversor_unidades import ConversorUnidades
from mysql.connector import Error

from daos.merma_dao import MermaDAO
from daos.insumo_dao import InsumoDAO
from models.merma import Merma
from models.tipo_merma import TipoMerma
from models.insumo import Insumo
from models.tipo_insumo import TipoInsumo
from models.marca import Marca



class MermaServicio:
    def __init__(self, merma_dao: MermaDAO, insumo_dao:InsumoDAO):
        self._merma_dao = merma_dao
        self._insumo_dao = insumo_dao

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


    def registar_merma(self, merma:Merma) -> int:
        '''Registra una merma de un insumo'''
        # fecha, cantidad merma, unidad medida, insumo mermado, tipo merma -> (uno existento o 0 para nuevo)
        # 1. Validar que la fecha no pueda ser mayor a hoy
        # 2. validar que la fecha no sea mayor a 1 pasada semana
        # 3. validar la cantidad de la merma, p.e. debe ser mayor e igual a 0
        # 3. validar unidad de medida
        # 4. validar que el insumo seleccionado exista buscando por su nombre en la bd y que el dao regrese un num
            #(no se puede registrar una merma de un insumo inexistente)
        # 5. validar que el tipo de merma exista, si no, crear uno. (esto va en el dao creo)
        # 6. logica para convertir la cantidad a la unidad base y para que ese sea la nueva cantidad que se descontara del insumo
        # 7. try: registrar merma dao. 
        if not merma.fecha or len(str(merma.fecha)) == 0:
            raise ValueError('La merma debe tener una fecha')

        hoy = date.today()
        hace_7_dias = hoy - timedelta(days=7)
        fecha_ev:date =  datetime.strptime(self._formatear_fecha(merma.fecha), "%Y-%m-%d").date()
        merma.fecha = str(fecha_ev)

        if fecha_ev > hoy:
            raise ValueError('La fecha de la merma no puede pasar de hoy.')

        if not hace_7_dias < fecha_ev:
            raise ValueError('La fecha de la merma no puede ser de hace mas de 7 dias.')
        
        if not merma.cantidad or float(merma.cantidad) <= 0:
            raise ValueError('La merma debe ser mayor a 0.')

        if not merma.unidad_medida or not ConversorUnidades.es_valida(merma.unidad_medida):
            raise ValueError('La unidad de medida no es valida.')

        if not merma.tipo_merma or merma.tipo_merma.nombre == '' or not merma.tipo_merma.clave:
            raise ValueError('La merma debe tener un tipo.')

        # obtienen los detalle_compra/lista_compra con el mismo nombre, lo que implica que son del mismo insumo aunque con diferente marca
        #try:
        #    insumos = self._insumo_dao.obtener_insumo_por_nombre(merma.insumo.nombre)
        #    if not insumos or len(insumos) == 0:
        #        raise ValueError('El insumo seleccionado para mermar no existe.')
        #    #if len(insumos) > 1:
        #    #    raise IndexError('Insumo duplicado con el mismo nombre.')
        #except mysql.connector.Error as err:
        #    raise IndexError(f"Error al consultar el insumo: {err}")
        
        # elige el insumo con la fecha de caducidad mas antigua -----------------------------
        # 3. Validar existencia del insumo en BD
        insumo_bd = self._insumo_dao.obtener_insumo_por_num(merma.insumo.num)
        if not insumo_bd:
            raise ValueError('El insumo seleccionado para mermar no existe en la base de datos.')
        # convertir cantidad a la unidad canónica ('kg', 'l' o 'pza')
        unidad_base = ConversorUnidades.obtener_unidad_base(merma.unidad_medida)
        cantidad_convertida = ConversorUnidades.convertir(
            cantidad=float(merma.cantidad),
            unidad_origen=merma.unidad_medida,
            unidad_destino=unidad_base,
            decimales=4
        )
        # validar que no se intente mermar mas de lo que hay en stock 
        if insumo_bd.stock < cantidad_convertida:
            raise ValueError(
                f"Stock insuficiente: Intentas mermar {cantidad_convertida} {unidad_base}, "
                f"pero solo hay {insumo_bd.stock} {unidad_base} disponibles en el stock."
            )
        # llamar al dao
        try:
            return self._merma_dao.registrar_merma(merma=merma,cantidad=cantidad_convertida)
        except Error as err:
            raise ValueError(f"Servicio: Error al registrar la merma: {err}")

        except Exception as err:
            raise IndexError('Error al registrar la nueva merma.')


    def editar_merma(self, merma: Merma) -> bool:
        '''Actualiza una merma.'''
        if not merma.descripcion or len(merma.descripcion.strip()) == 0:
            raise ValueError('Debe ingresar una descripcion del motivo de la merma.')
        fecha_ev = datetime.strptime(self._formatear_fecha(merma.fecha), "%Y-%m-%d").date()
        merma.fecha = str(fecha_ev)
        hoy = date.today()
        if fecha_ev > hoy:
            raise ValueError('La fecha no puede ser posterior a hoy.')
        if fecha_ev < (hoy - timedelta(days=7)):
            raise ValueError('La fecha no puede ser anterior a 7 días.')
        try:
            return self._merma_dao.actualizar_merma(merma)
        except Error as err:
            raise ValueError(f"Servicio: Error al editar la merma: {err}")

    def crear_tipo_merma(self, nombre_tipo_merma:str):
        try:
            # verifica si ya existe el tipo de insumo
            if self._merma_dao.obtener_tipo_merma_por_nombre(nombre_tipo_merma):
                raise ValueError(f'Servicio: Error tipo de insumo ya existe')

            # por default se genera clave utilizando los primeros 3 caracteres del nombre
            clave = nombre_tipo_merma[:3]

            # verifica si la clave del tipo de insumo existe en la bd
            tipo_merma_por_clave = self._merma_dao.obtener_tipo_merma_por_clave(clave)

            while tipo_merma_por_clave:
                # genera nueva clave
                clave = "".join(random.choices(nombre_tipo_merma.split(), k=3))
                tipo_merma_por_clave = self._merma_dao.obtener_tipo_merma_por_clave(clave)

            self._merma_dao.registrar_tipo_merma(TipoMerma(clave, nombre_tipo_merma))
        except Error as err:
            raise ValueError(f"Servicio: Error al crear el tipo de merma: {err}")

    def obtener_tipo_merma_por_nombre(self, nombre_tipo_merma:str):
        try:
            return self._merma_dao.obtener_tipo_merma_por_nombre(nombre_tipo_merma)
        except Error as err:
            raise ValueError(f"Servicio: Error al obtener el tipo de merma: {err}")

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