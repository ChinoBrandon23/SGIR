from datetime import datetime

class validadorMenu:

    def crear_menu( self, nombre: str, fecha_inicio: str, fecha_fin: str, platillos: list) -> tuple [bool, any]:

        #Quitar espacios al inicio y final
        nombre_limpio = nombre.strip()
        fecha_inicio_limpio = fecha_inicio.strip()
        fecha_fin_limpia = fecha_fin.strip()

        #El nombre sea de un largo correcto
        if not (5 <= len(nombre_limpio) <= 25):
            return False, "El nombre del menu tiene un largo invalido. Debe tener entre 5 a 25 caracteres."

        #Verificar que un mismo platillo no se agregue mas de una vez
        if len(platillos)  != len(set(platillos)):
            return False,"Error: Hay platillos duplicados. Un mismo platillo no se puede agragar mas de una vez."

        #Verificar formato, dias/mes
        formato = "%d/%m/%Y"
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_limpio, formato)
            fecha_fin = datetime.strptime(fecha_fin_limpia, formato)
        except ValueError:
            return False, "Error: la fecha es invalida (DD/MM/YY)"

        #Verifica que la fecha de inicio y final no sean pasadas
        hoy = datetime.now().replace(hour=0, minute=0,second=0,microsecond=0)
        if fecha_inicio < hoy:
            return False, "Error: la fecha inicio no puede ser  una fecha pasada."

        if fecha_fin < hoy:
            return False, "Error: La fecha final no puede ser una fecha pasada."

        return True, {
            "nombre": nombre_limpio.capitalize(),
            "fecha_inicio": fecha_inicio_limpio,
            "fecha_fin": fecha_fin_limpia,
            "platillos": platillos
        }

    #Validar el precio ingresado por cada platillo
    def precio_platillo(self, precio_str: str) -> tuple[bool, any]:

        precio_limpio = precio_str.strip()

        #Verificar que sea un dato numerico
        try:
            precio = float(precio_limpio)
        except ValueError:
            return False,f"Error: el valor {precio_limpio} no es numerico."

        #Verifica que sea >0
        if precio <= 0:
            return False, "Error: El precio por platillo debe ser mayor a 0."

        return True, precio


