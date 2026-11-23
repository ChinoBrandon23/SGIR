class validadorInventario:

    def validar_nombre(self, nombre:str):
        nombre = nombre.strip().capitalize()

        if not nombre or len(nombre) == 0:
            return False, "Error: El nombre no puede estar vacío."

        if  len(nombre) > 35:
            return False, "Error: El nombre excede el límite de 35 caractéres."

        if not nombre.replace(" ", "").isalnum():
            return False, "Error: El nombre no puede contener caractéres especiales."

        return True, nombre

    def validar_umbral(self, umbral: str):
        umbral = umbral.strip()

        try:
            umbral_num = float(umbral)
        except ValueError:
            return False, "Error: El umbral debe ser un valor numérico."

        if umbral_num < 1:
            return False, "Error: El umbral debe ser un número mayor a 1."

        return True, umbral_num

    def validar_nombre_marca(self, marca_nombre: str):
        marca_nombre = marca_nombre.strip().lower()

        if len(marca_nombre) > 20:
            return False, "Error: El nombre de la marca debe ser de 20 caractéres máximo."

        if not marca_nombre.replace(" ", "").isalnum():
            return False, "Error: El nombre de la marca no debe contener caractéres especiales."

        return True, marca_nombre.capitalize()