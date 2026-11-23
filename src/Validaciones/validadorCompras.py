import datetime
import time

from utils.conversor_unidades import ConversorUnidades


class validadorCompras:
        UNIDADES_VALIDAS = {
        "kilo", "kilos", "kg", "gramo", "gramos", "g", 
        "litro", "litros", "lt", "ml", "pieza", "piezas", 
        "taza", "tazas", "cucharada", "cucharadas"
        }

        def validar_formato_fecha(self, fecha: str):
            fecha_limpia = fecha.strip()

            if not fecha_limpia:
                return False, "Error: La fecha del ticket no puede estar vacia."

            #Verificar que la fecha sea valida
            formato = "%d-%m-%Y"

            try:
                fecha_limpia = datetime.datetime.strptime(fecha_limpia, formato).strftime("%d-%m-%Y")
            except ValueError:
                return False, "Error: La fecha no es valida."

            return True, fecha_limpia

        def validar_nombre_insumo(self, nombre:str):
            nombre = nombre.strip()

            if len(nombre) > 35:
                return False, "Error: El nombre del insumo debe ser de 35 caractéres máximo."

            if not nombre.replace(" ", "").isalnum():
                return False, "Error: El nombre no puede contener caractéres especiales."

            return True, nombre.capitalize()

        def validar_nombre_proveedor(self, nombre:str):
            nombre = nombre.strip()

            if len(nombre) > 30:
                return False, "Error: El nombre del insumo debe ser de 30 caractéres máximo."

            if not nombre.replace(" ", "").isalnum():
                return False, "Error: El nombre no puede contener caractéres especiales."

            return True, nombre.capitalize()

        def validar_umbral(self, umbral:str):
            umbral = umbral.strip()

            try:
                umbral = float(umbral)
            except ValueError:
                return False, "Error: El umbral debe ser un valor numérico."

            if umbral < 1:
                return False, "Error: El umbral no puede ser menor a 1."

            return True, umbral

        def validar_nombre_marca(self, marca_nombre:str):
            marca_nombre = marca_nombre.strip().lower()

            if len(marca_nombre) > 20:
                return False, "Error: El nombre de la marca debe ser de 20 caractéres máximo."

            if not marca_nombre.replace(" ", "").isalnum():
                return False, "Error: El nombre de la marca no debe contener caractéres especiales."

            return True, marca_nombre.capitalize()

        def validar_nombre_tipo_ins(self, nombre_tipo:str):
            nombre_tipo = nombre_tipo.strip().lower()

            if len(nombre_tipo) > 20:
                return False, "Error: El nombre de la marca debe ser de 20 caractéres máximo."

            if not nombre_tipo.replace(" ", "").isalnum():
                return False, "Error: El nombre de la marca no debe contener caractéres especiales."

            return True, nombre_tipo.capitalize()

        def validar_cantidad_insumo(self, cantidad:str):
            cantidad = cantidad.strip()

            try:
                cantidad = float(cantidad)
            except ValueError:
                return False, "Error: La cantidad debe ser un valor numérico."

            if cantidad < 1:
                return False, "Error: La cantidad no puede ser menor a 1."

            return True, cantidad

        def validar_unidad_medida(self, unidad: str):
            # Verificar que la unidad de medida sea válida y de un largo adecuado
            if ConversorUnidades.es_valida(unidad):
                unidad_limpia = ConversorUnidades.normalizar(unidad)

                if not (1 <= len(unidad_limpia) <= 15):
                    return False, "Error: La unidad de medida tiene un largo inválido (debe tener entre 1 y 15 caracteres)."
            else:
                return False, f"Error: {unidad} no es una unidad reconocida en el sistema."

            return True, unidad_limpia

        def validar_monto_insumo(self, monto: str):
            monto = monto.strip()

            try:
                monto = float(monto)
            except ValueError:
                return False, "Error: El monto debe ser un valor numérico."

            if monto < 0:
                return False, "Error: El monto no puede ser menor a 0."

            return True, monto


        def insumo_comprado(self, insumo: str, cantidad: str, unidad: str, fecha: str, monto: str):

            insumo_limpio = insumo.strip()
            cantidad_limpia = cantidad.strip()
            unidad_limpia = unidad.strip()
            fecha_limpia = fecha.strip()
            monto_limpio = monto.strip()

            if not all([insumo_limpio, cantidad_limpia,unidad_limpia,fecha_limpia,monto_limpio]):
                return False, "Error: Ningun campo del insumo puede quedar vacio."

            #Verificar espacios en blancos
            if " " in insumo_limpio:
                return False, "Error: El insimo no acepta espacios en blanco."

            if " " in unidad_limpia:
                return False, "Error: La unidad de medida no acepta espacios en blancos."

            #La cantiadd sea mayor a 0
            try:
                cantidad = float(cantidad_limpia)
                if cantidad <= 0:
                    return False, "Error: la cantidad comprada debe ser mayor a 0."
            except ValueError:
                return False, f"Error: la cantidad {cantidad_limpia} no es un numero valido."

            #Unidad de medida y largo correcto.
            if len(unidad_limpia) > 10:
                return False, "Error: La unidad de medida excede el limite de 10 caracteres."

            if unidad_limpia not in self.UNIDADES_VALIDAS:
                return False, "Error: La unidad de medida no es reconocida."

            #Verificar fecha
            formato = "%d/%m/%Y"
            try:
                datetime.strptime(fecha_limpia,formato)
            except ValueError:
                return False, "Error: La fecha ingresada no es valida."

            #Monto unitario mayor a 0
            try:
                monto = float(monto_limpio)
                if monto <= 0:
                    return False, "Error: El monto unitario debe ser mayor a 0."
            except ValueError:
                return False, "Error: El monto unitario no es un numero valido."

            return True, {
                "insumo": insumo_limpio.capitalize(),
                "cantidad": cantidad,
                "unidad" : unidad_limpia,
                "fecha" : fecha_limpia,
                "monto_unitario" : monto
            }