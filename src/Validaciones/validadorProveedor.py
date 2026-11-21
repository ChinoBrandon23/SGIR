class validadorProveedor:

    def edicion_proveedor(self, nombre_proveedor: str):

        #Eliminar espacios al inicio y al final
        proveedor_limpio = nombre_proveedor.strip()

        if not proveedor_limpio:
            return False, "Error: El nombre del proveedor no puede quedar vacio."

        #Verifica que el largo del nombre sea el correcto
        if len(proveedor_limpio) > 30:
            return False, "Error: el nombre del proveedor excede el largo permitido (30 caracteres0.)"

        return True, proveedor_limpio.capitalize()