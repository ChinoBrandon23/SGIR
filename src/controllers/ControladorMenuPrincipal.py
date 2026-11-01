import os
import subprocess
import sys

from controllers.ControladorRecetas import ControladorRecetas
from views.VistaMenuPrincipal import VistaMenuPrincipal
from views.VistaRecetas import VistaRecetas

class ControladorMenuPrincipal:
    def __init__(self, vista: VistaMenuPrincipal, servicio=None):
        self.vista = vista
        self.servicio = servicio
        self.vista.input_menu.agregar_escuchante(self.evaluar_input_menu)

        self.abrir_menu_principal()

    def evaluar_input_menu(self, seleccion):
        match seleccion:
            case "1":
                self.abrir_vista_receta()
            case "8":
                try:
                    subprocess.run('cls' if os.name == 'nt' else 'clear')
                except FileNotFoundError:
                    print(chr(27) + "[2J")
                sys.exit()

    def evaluar_input_menu_recetas(self, seleccion:str):
        if seleccion == "m" or seleccion == "M":
            self.abrir_menu_principal()

    def abrir_menu_principal(self):
        self.vista.mostrar_layout()
        self.vista.mostrar_prompt_menu()

    def abrir_vista_receta(self):
        vista = VistaRecetas(self.vista.console)

        vista.input_menu_recetas.agregar_escuchante(self.evaluar_input_menu_recetas)
        vista.input_menu_detalles.agregar_escuchante(self.evaluar_input_menu_recetas)
        vista.input_menu_editar_receta.agregar_escuchante(self.evaluar_input_menu_recetas)

        ControladorRecetas(vista)

