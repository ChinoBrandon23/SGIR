from datetime import datetime

class validadorMerma:

    UNIDADES_VALIDAS = {
        "kilo", "kilos", "kg", "gramo", "gramos", "g", 
        "litro", "litros", "lt", "ml", "pieza", "piezas", 
        "taza", "tazas", "cucharada", "cucharadas"
        }


    def registro_merma(self, tipo_merma: str, descripcion: str, fecha: str, cantidad: str, unidad: str):
    
    #Eliminar espacios al incio y al final
        tipo_limpio = tipo_merma.strip()
        descripcion_limpia = descripcion.strip()
        fecha_limpia = fecha.strip()
        cantidad_limpia = cantidad.strip()
        unidad_limpia = unidad.strip()

        if not tipo_limpio or not descripcion_limpia or not fecha_limpia or not cantidad_limpia or not unidad_limpia:
                return False, "Error: Ningun campo puede quedar vacio."

        #Evita espacios en blanco
        if " " in tipo_limpio:
                return False, "Error: El tipo de merma no acepta espacios en blanco."

        if len(tipo_limpio) > 20:
            return False, "Error: El tipo de merma excede el largo permitido de 20 caracteres"

        if len(descripcion_limpia) > 50:
            return False, "Error: La descripcion excede el largo adecuado de 50 caracteres."

        #Validar fecha
        formato = "%d/%m/Y"
        try:
            fecha_merma = datetime.strptime(fecha_limpia, formato)
        except ValueError:
            return False, "Error: La fecha es invalida."

        #Validar cantidad
        try:
            cantidad = float(cantidad_limpia)
            if cantidad <= 0:
                return False, "Error: La cantidad debe ser mayor a 0."
        except  ValueError:
            return False, f"Error: La cantidad {cantidad_limpia} no es un numero valido."

        #Validar unidades de medidas
        if len(unidad_limpia) > 10:
            return False, "Error: La unidad de medida excede el largo correcto de 10 caracteres."

        if unidad_limpia not in self.UNIDADES_VALIDAS:
            return False, f"Error: {unidad_limpia} no es una unidad reconocida."

        return True, {
            "tipo": tipo_limpio,
            "descripcion": descripcion_limpia.capitalize(),
            "fecha": fecha_limpia,
            "cantidad": cantidad,
            "unidad": unidad_limpia
        }
