class validadorMarca:

    def edicion_marca(self, nombre_marca: str):

        #Eliminar espacios al inicio y al final
        marca_limpia = nombre_marca.strip()

        if not marca_limpia:
            return False, "Error: El nombre de la marca no puede quedar vacio."

        #Verifica que el largo del nombre sea el correcto
        if len(marca_limpia) > 20:
            return False, "Error: El nombre de la marca excede el largo permitido (20 caracteres0.)"

        return True, marca_limpia.capitalize()