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