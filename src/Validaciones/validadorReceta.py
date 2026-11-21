from utils.conversor_unidades import ConversorUnidades

class validadorReceta:
    UNIDADES_VALIDAS = {
        "kilo", "kilos", "kg", "gramo", "gramos", "g", 
        "litro", "litros", "lt", "ml", "mililitro", "mililitros"
    }

    def validar_crear_instruccion(self, instruccion:str):
        if not instruccion or len(instruccion) == 0:
            return False, "Error: La instrucción no puede estar vacía."

        if not instruccion.isalnum():
            return False, "Error: La instrucción no puede contener caractéres especiales."

        if len(instruccion) > 50:
            return False, "Error: La instrucción tiene un largo inválido (más de 50 caractéres)."

        return True, instruccion.capitalize()

    def validar_crear_ingrediente(self, nombre: str, cantidad: str, unidad: str, ingredientes: list):

        #Verificar espacios al inicio y al final

        nombre_limpio = nombre.strip()
        cantidad_limpia = cantidad.strip()
        unidad_limpia = unidad.strip()

        if not nombre_limpio or not cantidad_limpia or not unidad_limpia:
            return False, "Error: ninguno de los elementos pueden estar vacios."

        #Verificar el largo del nombre
        if not (5 <= len(nombre_limpio) <= 20):
            return False, "Error: El nombre del ingrediete debe tener entre 5 a 20 caracteres."

        #Validar el nombre ignorando mayusculas y minusculas
        ingredientes_lower = [ing.lower() for ing in ingredientes]
        if nombre_limpio.lower() in ingredientes_lower:
            return False, f"Error: El ingrediente {nombre_limpio} ya existe en la receta."

            #Verificar que las cantidades sean numeros
        try:
            Cantidad = float(cantidad_limpia)
            if Cantidad <= 0:
                return False, "Error: La cantidad debe ser mayor a 0."
        except ValueError:
            return False, f"Error: La cantidad {cantidad_limpia} no es un número válido."
        
        #Verificar que la unidad de medida tenga un largo adecuado y sea válida
        unidad_lower = unidad_limpia.lower()
        if not (2 <= len(unidad_lower) <= 15):
            return False, "Error: La unidad de medida tiene un largo inválido (debe tener entre 2 y 15 caracteres)."
            
        if unidad_lower not in self.UNIDADES_VALIDAS:
            return False, f"Error: '{unidad_limpia}' no es una unidad de medida reconocida."

        return True, {
            "nombre": nombre_limpio.capitalize(),
            "cantidad": cantidad_limpia,
            "unidad": unidad_lower
        }

    #Valida el numero de insumo o receta a enlazar.
    def validar_crear_ingrediente(self, cadena_entrdad : str, ids_existentes: list):

        #Valida el numerode insumo o receta
        id_limpio = cadena_entrdad.strip()

        if not id_limpio:
            return False, "Error: Debes ingresar el numero del insumo o receta."

        if not id_limpio.isdigit():
            return False, "Error: No es un numero valido. Ingresa solo numeros enteros."

        id_numero = int(id_limpio)
        if id_numero not in ids_existentes:
            return False, f"Error: No existe ninguna receta o insumo con el numero {id_numero}."

        return True, id_numero

    #Valida la edicion de la cantidad y unidad de un ingrediente
    def editar_cantidad_ingrediente(self, cantidad_str: str):
        if not cantidad_str:
            return False, "Error: La cantidad no puede estar vacía."

        #Verificar que la cantidad ingresada sea un número
        try:
            cantidad = float(cantidad_str)
            if cantidad <= 0:
                return False, "Error: La cantidad debe ser mayor a 0."
        except ValueError:
                return False, f"Error: La cantidad {cantidad_str} no es un número válido."

        return True, cantidad

    #Valida la edicion de la cantidad y unidad de un ingrediente
    def editar_unidad_ingrediente(self, unidad: str):
        if not unidad:
            return False, "Error: La cantidad o la unidad no pueden estar vacías."

        # Verificar que la unidad de medida sea válida y de un largo adecuado
        if ConversorUnidades.es_valida(unidad):
            unidad_limpia = ConversorUnidades.normalizar(unidad)

            if not (2 <= len(unidad_limpia) <= 15):
                return False, "Error: La unidad de medida tiene un largo inválido (debe tener entre 1 y 15 caracteres)."
        else:
            return False, f"Error: {unidad} no es una unidad reconocida en el sistema."

        return True, unidad_limpia

    #Valida la edicion del nombre de una receta
    def editar_nombre(self, cadena_entrada: str):

        #Eliminar espacios al inicio y final de la cadena
        nombre_limpio = cadena_entrada.strip()

        if not nombre_limpio.isalnum():
            return False, "Error: El nombre de la receta no puede contener caractéres especiales."
            
        # Verificar que no esté vacío
        if not nombre_limpio:
            return False, "Error: El nombre de la receta no puede estar vacío."
                
        # Verificar que el largo del nombre sea adecuado
        if not (5 <= len(nombre_limpio) <= 25):
            return False, f"Error: El largo del nombre es inválido ({len(nombre_limpio)} caracteres).Debe tener entre 5 y 25."
                
        return True, nombre_limpio.capitalize()

    #Valida la edicion de la cantidad de porciones de la receta.
    def validar_editar_porciones(self, cadena_entrada: str):

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
