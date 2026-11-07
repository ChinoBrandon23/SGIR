class RecetaServicio:
    def __init__(self, receta_dao):
        self._receta_dao = receta_dao

    def obtener_recetas(self):
        return self._receta_dao.obtener_recetas()
