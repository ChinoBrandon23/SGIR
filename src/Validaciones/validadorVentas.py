from datetime import datetime

class ValidadorVentas:

    def ingreso_venta(self, fecha: str, monto: str, comensales: str):

        #Eliminar espacios al incio y al final
        fecha_limpia = fecha.strip()
        monto_limpio = monto.strip()
        comensales_limpio = comensales.strip()

        if not fecha_limpia or not monto_limpio or not comensales_limpio:
            return False, "Error: Ninguno de los campos puede estar vacios."

        #Verificar que el dia y el mes sean numeros validos
        formato = "%d/%m/%Y"
        try:
            fecha_venta = datetime.strptime(fecha_limpia, formato)
        except ValueError:
            return False, "Error: La fecha es invalida."

        #la venta sea mayor a 0
        try:
            comensales = int(comensales_limpio)
            if comensales <= 0:
                return False, "Error: El numero de comensales debe ser mayor a 0."
        except ValueError:
            return False, "Error: el numero de comensales debe ser un numero entero."

        return True, {
            "fecha": fecha_limpia,
            "monto": monto,
            "comensales": comensales
        }

    def validar_formato_fecha(self, fecha: str):
        fecha_limpia = fecha.strip()

        if not fecha_limpia:
            return False, "Error: La fecha del ticket no puede estar vacía."

        # Verificar que la fecha sea valida
        formato = "%d-%m-%Y"

        try:
            fecha_limpia = datetime.strptime(fecha_limpia, formato).strftime("%d-%m-%Y")
        except ValueError:
            return False, "Error: La fecha no es valida."

        return True, fecha_limpia

    def validar_num_comensales(self, num_comensales: str):
        num_comensales = num_comensales.strip()

        try:
            num_comensales = int(num_comensales)
        except ValueError:
            return False, "Error: El número de comensales debe ser un valor numérico."

        if num_comensales < 1:
            return False, "Error: El número de comensales debe ser de al menos 1."

        return True, num_comensales

    def validar_cantidad_consumo(self, cantidad: str):
        num_comensales = cantidad.strip()

        try:
            num_comensales = float(num_comensales)
        except ValueError:
            return False, "Error: La cantidad de platillos consumidos debe ser un valor numérico."

        if num_comensales < 1:
            return False, "Error: El número de platillos consumidos debe ser de al menos 1."

        return True, num_comensales

    def validar_rango_fecha(self, fecha_inicial, fecha_final):
        fecha_inicial = fecha_inicial.strip()
        fecha_final = fecha_final.strip()

        if not fecha_inicial:
            return False, "Error: La fecha inicial no puede estar vacía."

        if not fecha_final:
            return False, "Error: La fecha final no puede estar vacía."

        formato = "%d-%m-%Y"
        try:
            fecha_inicial = datetime.strptime(fecha_inicial, formato).strftime("%d-%m-%Y")
        except ValueError:
            return False, "Error: La fecha inicial no es valida."

        try:
            fecha_final = datetime.strptime(fecha_final, formato).strftime("%d-%m-%Y")
        except ValueError:
            return False, "Error: La fecha final no es valida."

        if datetime.strptime(fecha_inicial, formato) > datetime.strptime(fecha_final, formato):
            return False, "Error: La fecha inicial no puede ser después de la fecha final."

        return True, (fecha_inicial, fecha_final)