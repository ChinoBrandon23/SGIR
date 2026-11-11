class validadorPlatillos:

    #Valida la creacion de un nuevo platillo
    def crear_platillo(self, nombre: str, categoria: str, receta_base: str, platillos_bd: list) -> tuple[bool, any]:

        #Eliminar los espacios al incio y final de cada valor
        nombre_limpio = nombre.strip()
        categoria_limpia = categoria.strip()
        receta_limpia = receta_base.strip()

        #Verificar que antes de guardar, el objeto tenga nombre, categoria y receta
        if not nombre_limpio or not categoria_limpia or not receta_limpia:
            return False, "Error, el platillo debe tener obligatoriamente nombre, categoria y receta."

        if not (3 <= len(nombre_limpio) <= 25):
            return False, "Error el nombre tiene un largo invalido. Debe tener un rango de 3 a 25 caracteres."

        #Verficar que el nombre del platillo sea unico en toda la BD
        nombres_existentes = [platillo.lower() for platillo in platillos_bd]
        if nombre_limpio.lower() in nombres_existentes:
            return False, f"Error, ya existe un platillo llamado {nombre_limpio} en la base de datos."

        return True, {
            "nombre": nombre_limpio.capitalize(),
            "categoria": categoria_limpia.capitalize(),
            "receta_base": receta_limpia.capitalize()
        }

    #Valida el nombre al crear una nueva categoria de platillos
    def creacion_categoria(self, nombre_categoria: str) -> tuple[bool, str]:

        categoria_limpia = nombre_categoria.strip()

        if categoria_limpia:
            return False, "Error: El nombre de la categoria no puede estar vacio."

        #Verificar el largo del nombre
        if not (3 <= len(categoria_limpia) <= 15):
            return False,"Error: el largo de la categoria es invalido. Debe tener entre 3 y 15 caracteres."

        return True, categoria_limpia.capitalize()
    
    #Valida la edicion del nombre de un platillo exitente.
    def edicion_nombre_platillo(self, nuevo_nombre: str) -> tuple[bool, str]:

        nombre_limpio = nuevo_nombre.strip()

        #Verifica que el nombre del platillo no este vacio
        if not nombre_limpio:
            return False, "Error: El nuevo nombre del platillo no puede estar vacío."

        #Verifica el largo del nombre    
        if not (5 <= len(nombre_limpio) <= 25):
            return False, "Error: El nuevo nombre tiene un largo inválido. Debe tener entre 3 y 25."
            
        return True, nombre_limpio.capitalize()