import os
import subprocess

import rich
from rich.layout import Layout
from rich.table import Table
from rich.align import Align

from views.VistaBase import VistaBase
from views.clases_personalizadas.InputEmisor import InputEmisor

class VistaMenuPrincipal(VistaBase):
    def __init__(self, console):
        super().__init__()
        self.console = console
        self.tabla_menu = Table()
        self.input_menu = InputEmisor()

        self.layout["contenido"].split_column(Layout(name="banner"), Layout(name="menu"))

        self.configurar_menu()
        self.mostrar_layout()

    def configurar_menu(self):
        opciones_menu = ["Recetas", "Platillos", "Menús", "Compras", "Inventario", "Merma", "Ventas", "Salir"]

        self.tabla_menu.add_column()
        self.tabla_menu.add_column("Opciones", justify="center")
        contador_opciones = 1

        for opcion in opciones_menu:
            self.tabla_menu.add_row(str(contador_opciones), opcion)
            contador_opciones += 1

        self.layout["menu"].update(Align.center(self.tabla_menu, vertical="middle"))

    def imprimir_banner(self):
        banner = '''[magenta]███████╗ ██████╗  ██████╗ ██╗██████╗
██╔════╝██╔═══██╗██╔════╝ ██║██╔══██╗
███████╗██║   ██║██║  ███╗██║██████╔╝
╚════██║██║   ██║██║   ██║██║██╔══██╗
███████║╚██████╔╝╚██████╔╝██║██║  ██║
╚══════╝ ╚═════╝  ╚═════╝ ╚═╝╚═╝  ╚═╝[/magenta]'''

        banner_2 = '''[magenta]███████╗ ██████╗ ██╗██████╗ 
██╔════╝██╔════╝ ██║██╔══██╗
███████╗██║  ███╗██║██████╔╝
╚════██║██║   ██║██║██╔══██╗
███████║╚██████╔╝██║██║  ██║
╚══════╝ ╚═════╝ ╚═╝╚═╝  ╚═╝[/magenta]'''

        self.layout["banner"].update(Align.center(banner, vertical="middle"))

    def imprimir_banner_halloween(self):
        banner = '''[red]██████  ▒█████    ▄████  ██▓ ██▀███  
▒██    ▒ ▒██▒  ██▒ ██▒ ▀█▒▓██▒▓██ ▒ ██▒
░ ▓██▄   ▒██░  ██▒▒██░▄▄▄░▒██▒▓██ ░▄█ ▒
  ▒   ██▒▒██   ██░░▓█  ██▓░██░▒██▀▀█▄  
▒██████▒▒░ ████▓▒░░▒▓███▀▒░██░░██▓ ▒██▒
▒ ▒▓▒ ▒ ░░ ▒░▒░▒░  ░▒   ▒ ░▓  ░ ▒▓ ░▒▓░
░ ░▒  ░ ░  ░ ▒ ▒░   ░   ░  ▒ ░  ░▒ ░ ▒░
░  ░  ░  ░ ░ ░ ▒  ░ ░   ░  ▒ ░  ░░   ░ 
      ░      ░ ░        ░  ░     ░ [/red]'''

        self.layout["banner"].update(Align.center(banner, vertical="middle"))

    def mostrar_prompt_menu(self) :
        self.refrescar_pantalla()
        self.input_menu.imprimir("Ingresa una opción", choices=[str(i) for i in range(1, 9)])

        if self.input_menu.user_input is None or len(self.input_menu.user_input) == 0:
            self.mostrar_prompt_menu()

    def refrescar_pantalla(self):
        try:
            subprocess.run('cls' if os.name == 'nt' else 'clear')
        except FileNotFoundError:
            print(chr(27) + "[2J")
        self.console.print(self.layout, justify="center")

    def mostrar_layout(self):
        try:
            subprocess.run('cls' if os.name == 'nt' else 'clear')
        except FileNotFoundError:
            print(chr(27) + "[2J")
        self.console.print(self.layout, justify="center")