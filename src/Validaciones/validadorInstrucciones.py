class validadorInstrucciones:
    def creacion_instruccion(self, id_receta: str, instruccion: str):

        #Eliminar espacion al inicio y al final
        id_limpio = id_receta.strip()
        instruccion_limpia = instruccion.strip()

        #Verificar que el numero de la receta y la instruccion no quedan vacios
        if  not id_limpio:
            return False, "Error: El numero de la receta no puede quedar vacio."

        if not instruccion_limpia:
            return False, "Error: La instruccion de preparacion no puede quedar vacio."

        #Verificar que el numero de la receta sea un numero entero
        if not id_limpio.isdigit():
            return False, "Error: el numero de la receta sea un numero entero."

        id_receta = int(id_limpio)

        #Verificar que la longitud de la instruccion sea adecuada
        if len(instruccion_limpia) > 50:
            return False, "Error: La instruccion excede la longitud adecuada de 50 caracteres."

        return True, {
            "id_receta": id_receta,
            "instruccion": instruccion_limpia.capitalize()
        }