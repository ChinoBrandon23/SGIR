class Proveedor:
    def __init__(self, num:int, nombre:str):
        self._num = num
        self._nombre = nombre

    @property
    def num(self):
        return self._num

    @num.setter
    def num(self, value):
        self._num = value

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, value):
        self._nombre = value