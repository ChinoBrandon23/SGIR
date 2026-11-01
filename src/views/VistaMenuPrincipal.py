import os
import subprocess

from rich.table import Table

from views.VistaBase import VistaBase
from views.clases_personalizadas.InputEmisor import InputEmisor

class VistaMenuPrincipal(VistaBase):
    def __init__(self, console):
        super().__init__()
        self.console = console
        self.tabla_menu = Table(title="Menú")
        self.input_menu = InputEmisor()

        self.configurar_menu()
        self.mostrar_layout()

    def configurar_menu(self):
        opciones_menu = ["Recetas", "Platillos", "Menús", "Órdenes de compra", "Inventario", "Merma", "Ventas", "Salir"]

        self.tabla_menu.add_column()
        self.tabla_menu.add_column("Opciones", justify="center")
        contador_opciones = 1

        for opcion in opciones_menu:
            self.tabla_menu.add_row(str(contador_opciones), opcion)
            contador_opciones += 1

        self.layout["contenido"].update(self.tabla_menu)

    def mostrar_prompt_menu(self) :
        self.input_menu.imprimir("Ingresa una opción", choices=[str(i) for i in range(1, 9)])

    def mostrar_layout(self):
        subprocess.run('cls' if os.name == 'nt' else 'clear')
        self.console.print(self.layout, justify="center")