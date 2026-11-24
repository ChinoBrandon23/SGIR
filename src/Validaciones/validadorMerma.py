from datetime import datetime

from utils.conversor_unidades import ConversorUnidades


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

    def validar_formato_fecha(self, fecha: str):
        fecha_limpia = fecha.strip()

        if not fecha_limpia:
            return False, "Error: La fecha no puede estar vacía."

        # Verificar que la fecha sea valida
        formato = "%d-%m-%Y"

        try:
            fecha_limpia = datetime.strptime(fecha_limpia, formato).strftime("%d-%m-%Y")
        except ValueError:
            return False, "Error: La fecha no es valida."

        return True, fecha_limpia

    def validar_unidad_medida(self, unidad: str):
        # Verificar que la unidad de medida sea válida y de un largo adecuado
        if ConversorUnidades.es_valida(unidad):
            unidad_limpia = ConversorUnidades.normalizar(unidad)

            if not (1 <= len(unidad_limpia) <= 15):
                return False, "Error: La unidad de medida tiene un largo inválido (debe tener entre 1 y 15 caracteres)."
        else:
            return False, f"Error: {unidad} no es una unidad reconocida en el sistema."

        return True, unidad_limpia

    def validar_cantidad_insumo(self, cantidad: str):
        cantidad = cantidad.strip()

        try:
            cantidad = float(cantidad)
        except ValueError:
            return False, "Error: La cantidad debe ser un valor numérico."

        if cantidad < 1:
            return False, "Error: La cantidad no puede ser menor a 1."

        return True, cantidad

    def validar_descripcion_merma(self, descripcion:str):
        descripcion = descripcion.strip()

        if len(descripcion) > 50:
            return False, "Error: La descripción excede el largo adecuado de 50 caracteres."

        return True, descripcion

    def validar_nombre_tipo_merma(self, nombre:str):
        nombre = nombre.strip()

        if len(nombre) > 20:
            return False, "Error: El nombre excede la cantidad de caractéres permitidos de 20"

        if len(nombre) == 0:
            return False, "Error: El nombre no puede estar vacío"

        return True, nombre.capitalize()

    def validar_rango_fecha(self, fecha_inicial, fecha_final):
        formato = "%d-%m-%Y"

        if datetime.strptime(fecha_inicial, formato) > datetime.strptime(fecha_final, formato):
            return False, "Error: La fecha inicial no puede ser después de la fecha final."

        return True, (fecha_inicial, fecha_final)