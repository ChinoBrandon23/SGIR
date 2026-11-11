class validadorReceta:
    UNIDADES_VALIDAS = {
        "kilo", "kilos", "kg", "gramo", "gramos", "g", 
        "litro", "litros", "lt", "ml", "pieza", "piezas", 
        "taza", "tazas", "cucharada", "cucharadas"
    }

    def validar_crear_ingrediente(self, cadena_entrada: str, ingredientes_actuales: list) -> tuple[bool,any]:

        #Verificar que se hayan ingresado las comas
        if "," not in cadena_entrada:
            return False, "Error: El formato debe estar separado por comas"

        elementos = [elemento.strip() for elemento in cadena_entrada.split(",")]

        #Verificar que se hayan ingresados los 3 elementos
        if len(elementos) != 3:
            return False, "Error: se esperaban 3 elementos (nombre, cantidad, unidad)"

        nombre, cantidad_str, unidad = elementos

        if not nombre or not cantidad_str or not unidad:
            return False, "Error: ninguno de los elementos pueden estar vacios."

        #Verificar el largo del nombre
        if not (5 <= len(nombre) <= 20):
            return False, "Error: El nombre del ingrediete debe tener entre 5 a 20 caracteres."

        #Validar el nombre ignorando mayusculas y minusculas
        ingredientes_lower = [ing.lower() for ing in ingredientes_actuales]
        if nombre.lower() in ingredientes_lower:
            return False, f"Error: El ingrediente {nombre} ya existe en la receta"

            #Verificar que las cantidades sean numeros
        try:
            Cantidad = float(cantidad_str)
            if Cantidad <= 0:
                return False, "Error la cantidad debe ser mayor a 0."
        except ValueError:
            return False, f"Error: La cantidad {cantidad_str} no es un número válido."
        
        #Verificar que la unidad de medida tenga un largo adecuado y sea válida
        unidad_limpia = unidad.lower()
        if not (2 <= len(unidad_limpia) <= 15):
            return False, "Error: La unidad de medida tiene un largo inválido (debe tener entre 2 y 15 caracteres)."
            
        if unidad_limpia not in self.UNIDADES_VALIDAS:
            return False, f"Error: '{unidad}' no es una unidad de medida reconocida."

        return True, {
            "nombre": nombre.capitalize(),
            "cantidad": cantidad_str,
            "unidad": unidad_limpia
        }

    #Valida el numero de insumo o receta a enlazar.
    def validar_crear_ingrediente(self, cadena_entrdad : str, ids_existentes: list) -> tuple[bool,any]:

        #Valida el numerode insumo o receta
        id_limpio = cadena_entrdad.strip()

        if not id_limpio:
            return False, "Error: Debes ingresar el numero del insumo o receta."

        if not id_limpio.isdigit():
            return False, "Error: no es un numero valido. Ingresa solo numeros enteros."

        id_numero = int(id_limpio)
        if id_numero not in ids_existentes:
            return False, f"Error: no existe ninguna receta o insumo con el numero {id_numero}."

        return True, id_numero

    #Valida la edicion de la cantidad y unidad de un ingrediente
    def editar_ingrediente(self, cadena_entrada: str) -> tuple[bool, any]:

        #Verficar que se ingresaron las comas
        if "," not in cadena_entrada:
            return False, "Error: El formato debe estar separado por comas (ej. Queso,1,taza)."

        elementos = [elemento.strip() for elemento in cadena_entrada.split(",")]

        #Verificar que ingresó exactamente dos valores (cantidad y unidad)
        if len(elementos) != 2:
            return False,"Error: Se esperaban 2 valores (cantidad, unidad)."

        cantidad_str, unidad = elementos

        if not cantidad_str or not unidad:
            return False, "Error: La cantidad o la unidad no pueden estar vacías."

        #Verificar que la cantidad ingresada sea un número
        try:
            cantidad = float(cantidad_str)
            if cantidad <= 0:
                return False, "Error: La cantidad debe ser mayor a 0."
        except ValueError:
                return False, f"Error: La cantidad {cantidad_str} no es un número válido."

        #Verificar que la unidad de medida sea válida y de un largo adecuado
        unidad_limpia = unidad.lower()
        if not (2 <= len(unidad_limpia) <= 15):
            return False, "Error: La unidad de medida tiene un largo inválido (debe tener entre 1 y 15 caracteres)."

        if unidad_limpia not in self.UNIDADES_VALIDAS:
            return False, f"Error: {unidad} no es una unidad reconocida en el sistema."

        return True, {
            "cantidad": cantidad,
            "unidad": unidad_limpia
        }

    #Valida la edicion del nombre de una receta
    def editar_nombre(self, cadena_entrada: str) -> tuple[bool, str]:

        #Eliminar espacios al inicio y final de la cadena
        nombre_limpio = cadena_entrada.strip()
            
        # Verificar que no esté vacío
        if not nombre_limpio:
            return False, "Error: El nombre de la receta no puede estar vacío."
                
        # Verificar que el largo del nombre sea adecuado
        if not (5 <= len(nombre_limpio) <= 25):
            return False, f"Error: El largo del nombre es inválido ({len(nombre_limpio)} caracteres).Debe tener entre 5 y 25."
                
        return True, nombre_limpio.capitalize()

    #Valida la edicion de la cantidad de porciones de la receta.
    def validar_editar_porciones(self, cadena_entrada: str) -> tuple[bool, float]:

        porciones_limpias = cadena_entrada.strip()
        if not porciones_limpias:
            return False, "Error: Debes ingresar el numero de porciones."

        try:
            porciones = float(porciones_limpias)
            if porciones <= 0:
                return False, "Error: El numero de porciones debe ser mayor a 0."
        except ValueError:
            return False, f"Error: {porciones_limpias} no es un numero valido."

        return True, porciones
