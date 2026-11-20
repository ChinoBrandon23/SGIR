from datetime import datetime

class validadorCompras:
        UNIDADES_VALIDAS = {
        "kilo", "kilos", "kg", "gramo", "gramos", "g", 
        "litro", "litros", "lt", "ml", "pieza", "piezas", 
        "taza", "tazas", "cucharada", "cucharadas"
        }

        def ticket_compra(self, fecha: str):

            fecha_limpia = fecha.strip()

            if not fecha_limpia:
                return False, "Error: La fecha del ticket no puede estar vacia."

            #Verificar que la fecha sea valida
            formato = "%d/%m/%Y"
            try:
                datetime.strptime(fecha_limpia, formato)
            except ValueError:
                return False, "Error: La fecha no es valida."

            return True, fecha_limpia

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