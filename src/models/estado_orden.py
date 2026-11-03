class EstadoOrden:
    def __init__(self, clave:str, nombre:str):
        self._clave = clave
        self._nombre = nombre

    @property
    def clave(self) -> str:
        return self._clave

    @clave.setter
    def clave(self, value):
        self._clave = value

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, value):
        self._nombre = value